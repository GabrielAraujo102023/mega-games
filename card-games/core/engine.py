from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import time

from core.game import Game


@dataclass
class EngineConfig:
    depth: int = 5
    mode: str = 'auto'                       # 'minimax' | 'paranoid' | 'auto'
    teams: Optional[List[List[int]]] = None  # e.g. [[0,2],[1,3]] — None means free-for-all
    maximizing_player: int = 0               # reference player index for paranoid mode
    time_limit_ms: Optional[int] = None      # None = fixed depth, set for iterative deepening
    n_samples: int = 20                      # opponent hand reconstructions per best_move call


class MinimaxEngine:
    def __init__(self, config: EngineConfig = EngineConfig()):
        self.config = config
        self._transposition_table: Dict[int, Tuple[float, int]] = {}  # hash -> (score, depth)
        self._start_time: Optional[float] = None
        self._time_limit_sec: Optional[float] = (
            config.time_limit_ms / 1000.0 if config.time_limit_ms else None
        )

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def best_move(self, state: Game) -> Any:
        # Entry point — returns the best move for the current player via determinization + search.
        self._start_time = time.time()
        self._transposition_table.clear()

        samples = self._get_samples(state)
        move_scores: Dict[int, float] = {}  # move_index -> cumulative score across samples

        for sample in samples:
            move_scores = self._search_sample(sample, move_scores)
            if self._time_exceeded():
                break

        moves = state.get_legal_moves()
        best_idx = max(move_scores, key=lambda i: move_scores[i])
        return moves[best_idx]

    # ------------------------------------------------------------------ #
    #  Determinization                                                     #
    # ------------------------------------------------------------------ #

    def _get_samples(self, state: Game) -> List[Game]:
        # Generates n_samples reconstructed states with plausible opponent hands.
        if not hasattr(state, 'reconstruct_opponent_hands'):
            return [state]
        samples = []
        for _ in range(self.config.n_samples):
                samples.append(state)
        return samples if samples else [state]

    def _search_sample(self, state: Game, move_scores: Dict[int, float]) -> Dict[int, float]:
        # Runs minimax on one sample and accumulates scores per move index.
        moves = state.get_legal_moves()
        current = state.get_current_player_id()
        mode = self._resolve_mode(state)
        alpha, beta = float('-inf'), float('inf')

        if self._time_limit_sec:
            scores = self._iterative_deepening(state, moves, mode, current)
        else:
            scores = self._search_moves(state, moves, mode, current, self.config.depth, alpha, beta)

        for i, score in scores.items():
            move_scores[i] = move_scores.get(i, 0.0) + score

        return move_scores

    def _search_moves(self,
                      state: Game,
                      moves: List[Any],
                      mode: str,
                      current: int,
                      depth: int,
                      alpha: float,
                      beta: float) -> Dict[int, float]:
        # Evaluates all moves at the root and returns {move_index: score}.
        scores = {}
        for i, move in enumerate(moves):
            child = state.apply_move(move)
            if mode == 'minimax':
                val = self._minimax(child, depth - 1, alpha, beta, False, current)
            else:
                is_max = (child.get_current_player() == self.config.maximizing_player)
                val = self._paranoid(child, depth - 1, alpha, beta, is_max)
            scores[i] = val
            alpha = max(alpha, val)
            if self._time_exceeded():
                break
        return scores

    # ------------------------------------------------------------------ #
    #  Iterative deepening                                                 #
    # ------------------------------------------------------------------ #

    def _iterative_deepening(self,
                              state: Game,
                              moves: List[Any],
                              mode: str,
                              current: int) -> Dict[int, float]:
        # Searches increasing depths until time runs out, returning the deepest complete result.
        best_scores: Dict[int, float] = {i: 0.0 for i in range(len(moves))}
        for depth in range(1, self.config.depth + 1):
            if self._time_exceeded():
                break
            self._transposition_table.clear()
            scores = self._search_moves(state, moves, mode, current, depth, float('-inf'), float('inf'))
            if not self._time_exceeded():
                best_scores = scores  # only commit complete searches
        return best_scores

    # ------------------------------------------------------------------ #
    #  Core search algorithms                                             #
    # ------------------------------------------------------------------ #

    def _minimax(self,
                 state: Game,
                 depth: int,
                 alpha: float,
                 beta: float,
                 maximizing: bool,
                 max_player: int) -> float:
        # Standard two-sided minimax with alpha-beta pruning and transposition table.
        cached = self._check_cache(state, depth)
        if cached is not None:
            return cached

        if depth == 0 or state.is_terminal() or self._time_exceeded():
            return state.evaluate()[max_player]

        moves = state.get_legal_moves()
        if not moves:
            return state.evaluate()[max_player]

        if maximizing:
            value = float('-inf')
            for move in moves:
                child = state.apply_move(move)
                value = max(value, self._minimax(child, depth - 1, alpha, beta, False, max_player))
                alpha = max(alpha, value)
                if beta <= alpha:
                    break  # beta cutoff
        else:
            value = float('inf')
            for move in moves:
                child = state.apply_move(move)
                value = min(value, self._minimax(child, depth - 1, alpha, beta, True, max_player))
                beta = min(beta, value)
                if beta <= alpha:
                    break  # alpha cutoff

        self._store_cache(state, depth, value)
        return value

    def _paranoid(self,
                  state: Game,
                  depth: int,
                  alpha: float,
                  beta: float,
                  maximizing: bool) -> float:
        # Paranoid minimax for N players: one maximizer, all others treated as minimizers.
        # Preserves alpha-beta pruning. Score is maximizer's value a minus sum of all others.
        cached = self._check_cache(state, depth)
        if cached is not None:
            return cached

        if depth == 0 or state.is_terminal() or self._time_exceeded():
            return self._paranoid_score(state)

        moves = state.get_legal_moves()
        if not moves:
            return self._paranoid_score(state)

        if maximizing:
            value = float('-inf')
            for move in moves:
                child = state.apply_move(move)
                is_max = child.get_current_player() == self.config.maximizing_player
                value = max(value, self._paranoid(child, depth - 1, alpha, beta, is_max))
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
        else:
            value = float('inf')
            for move in moves:
                child = state.apply_move(move)
                is_max = child.get_current_player() == self.config.maximizing_player
                value = min(value, self._paranoid(child, depth - 1, alpha, beta, is_max))
                beta = min(beta, value)
                if beta <= alpha:
                    break

        self._store_cache(state, depth, value)
        return value

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _resolve_mode(self, state: Game) -> str:
        # Selects algorithm automatically based on player count and team configuration.
        if self.config.mode != 'auto':
            return self.config.mode
        if state.get_num_players() == 2:
            return 'minimax'
        if self.config.teams:
            return 'minimax'  # encode team game as two opposing sides
        return 'paranoid'

    def _paranoid_score(self, state: Game) -> float:
        # Computes paranoid evaluation: maximizing player's score a minus sum of all others.
        scores = state.evaluate()
        mp = self.config.maximizing_player
        return scores[mp] - sum(s for i, s in enumerate(scores) if i != mp)

    def _get_team(self, player_idx: int) -> Optional[int]:
        # Returns the team index of a player, or None if teams are not configured.
        if not self.config.teams:
            return None
        for team_idx, team in enumerate(self.config.teams):
            if player_idx in team:
                return team_idx
        return None

    def _is_same_team(self, player_a: int, player_b: int) -> bool:
        # Returns True if both players belong to the same configured team.
        if not self.config.teams:
            return False
        return self._get_team(player_a) == self._get_team(player_b)

    def _check_cache(self, state: Game, depth: int) -> Optional[float]:
        # Returns cached score if state was seen at equal or greater depth, else None.
        if not hasattr(state, '__hash__'):
            return None
        try:
            h = hash(state)
            if h in self._transposition_table:
                cached_score, cached_depth = self._transposition_table[h]
                if cached_depth >= depth:
                    return cached_score
        except TypeError:
            pass
        return None

    def _store_cache(self, state: Game, depth: int, value: float):
        # Stores a computed score in the transposition table keyed by state hash.
        if not hasattr(state, '__hash__'):
            return
        try:
            h = hash(state)
            existing = self._transposition_table.get(h)
            if existing is None or depth >= existing[1]:
                self._transposition_table[h] = (value, depth)
        except TypeError:
            pass

    def _time_exceeded(self) -> bool:
        # Returns True if the configured time budget has been exhausted.
        if self._time_limit_sec is None or self._start_time is None:
            return False
        return (time.time() - self._start_time) >= self._time_limit_sec