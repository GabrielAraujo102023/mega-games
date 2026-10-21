from abc import ABC, abstractmethod
from typing import Any, Dict, List
import random
import copy

from core.cards import Card, CardSuit, CardType, DEFAULT_CARD_VALUES
from core.player import Player
from personas.personas import get_random_personas


class Game(ABC):
    def __init__(self,
                 game_name: str,
                 n_players: int,
                 unused_card_types: List[CardType],
                 card_values: Dict[CardType, int],
                 starting_cards: int,
                 main_character: int = -1,
                 n_decks: int = 1,
                 jokers_per_deck: int = 0,
                 use_personas: bool = False,
                 ) -> None:
        self.game_name = game_name
        self.n_players = n_players
        self.unused_card_types = unused_card_types
        self.n_decks = n_decks
        self.card_values = card_values
        self.starting_cards = starting_cards
        self.jokers_per_deck = jokers_per_deck
        self.main_character = main_character
        self.use_personas = use_personas

        self.played_cards: List[Card] = []
        self.current_round = 0
        self.current_player_idx = 0

        self.deck = self.generate_deck()
        self.deck_size = len(self.deck)
        self.players = self.generate_players()

    def generate_deck(self) -> List[Card]:
        deck = []
        ignored_types = list(self.unused_card_types)
        add_jokers = CardType.JOKER not in ignored_types and self.jokers_per_deck > 0

        if add_jokers:
            for _ in range(self.n_decks):
                for _ in range(self.jokers_per_deck):
                    deck.append(Card(CardType.JOKER, self.card_values[CardType.JOKER]))
            ignored_types.append(CardType.JOKER)

        for card_type in DEFAULT_CARD_VALUES.keys():
            if card_type not in ignored_types:
                for _ in range(self.n_decks):
                    for suit in CardSuit:
                        deck.append(Card(card_type, self.card_values[card_type], suit))

        random.shuffle(deck)
        return deck

    def generate_players(self) -> List[Player]:
        players = []
        game_player = self.get_game_player()
        if not self.use_personas:
            for _ in range(self.n_players):
                players.append(game_player)
            return players

        personas = get_random_personas(self.game_name, 3, self.init_player_hand)
        for i in range(self.n_players):
            if i == self.main_character:
                players.append(game_player)
            else:
                persona = personas.pop(0)
                persona._id = i
                players.append(persona)
        return players

    def draw_card(self, n: int) -> List[Card]:
        cards = self.deck[:n]
        self.deck = self.deck[n:]
        self.deck_size = max(0, self.deck_size - n)
        return cards

    def advance_turn(self, steps: int = 1):
        self.current_player_idx = (self.current_player_idx + steps) % self.n_players
        self.current_round += 1

    def record_played(self, card: Card):
        self.played_cards.append(card)

    def clone(self) -> 'Game':
        return copy.copy(self)

    def get_score(self) -> List[int]:
        score = []
        for p in self.players:
            score.append(p.points)

        return score

    def get_all_cards(self) -> List[Card]:
        all_cards = []
        for player in self.players:
            all_cards.extend(player.hand)
        all_cards.extend(self.deck)
        all_cards.extend(self.played_cards)
        return all_cards

    def get_unknown_cards(self) -> List[Card]:
        my_hand_ids = {id(c) for c in self.players[self.current_player_idx].hand}
        played_ids = {id(c) for c in self.played_cards}
        return [
            c for c in self.get_all_cards()
            if id(c) not in my_hand_ids and id(c) not in played_ids
        ]

    def remove_card(self, player_id: int, card: Card):
        self.players[player_id].hand.remove(card)

    def get_winner(self) -> str:
        # Returns a string with the name of the winner. Might need to be overridden by the game
        return sorted(self.players, key=lambda player: player.points)[-1].name

    def is_main_character(self, player: Player) -> bool:
        return player.id_ == self.main_character

    def get_legal_moves(self) -> List[Card]:
        player = self.get_current_player()
        playable_cards = self.get_playable_cards(player)
        return player.get_moves(playable_cards)

    # ------------------------------------------------------------------ #
    #  Engine interface — non-abstract                                     #
    # ------------------------------------------------------------------ #

    def get_current_player_id(self) -> int:
        return self.current_player_idx

    def get_current_player(self) -> Player:
        return self.players[self.current_player_idx]

    def get_current_player_and_pass(self) -> Player:
        p = self.get_current_player()
        self.advance_turn()
        return p

    def get_num_players(self) -> int:
        return self.n_players

    # ------------------------------------------------------------------ #
    #  Abstract interface — must be implemented per game                  #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def get_playable_cards(self, player) -> List[Card]: ...
        # get the list of cards that can be played this round

    @abstractmethod
    def apply_move(self, move: Any) -> 'Game':
        # Returns a new game state with the given move applied. Must never mutate self.
        # Always start with: new = self.clone()
        ...

    @abstractmethod
    def is_terminal(self) -> bool:
        # Returns True if the game is over and the tree should stop expanding.
        ...

    @abstractmethod
    def evaluate(self) -> List[float]:
        # Returns a score vector of length n_players, one value per player.
        # At terminal nodes: exact outcome. At depth cutoff: heuristic estimate.
        # Use played_cards to infer opponent hand strength where relevant.
        ...

    @abstractmethod
    def print_move(self) -> Dict[str, Any]:
        # Returns the current game state as a map to be printed to JSON
        ...

    @abstractmethod
    def get_game_player(self) -> Player:
        # Returns a pro gamer for the game
        ...

    @abstractmethod
    def init_player_hand(self, player: Player) -> Player:
        # Function that will initiate a player
        ...


    # ------------------------------------------------------------------ #
    #  Hash — implement in subclass for transposition table support       #
    # ------------------------------------------------------------------ #

    # Override __hash__ in your game subclass to enable transposition table caching.
    # Include every field that would cause a different decision if it were different:
    #   - always:  player hands, player scores, current_player_idx
    #   - usually: current trick, trump suit, played_cards (if evaluate() uses it directly)
    #   - never:   deck contents below surface, history not affecting moves or evaluation
    #
    # Pattern:
    #   def __hash__(self):
    #       return hash((
    #           tuple(tuple((c.card_type, c.suit) for c in p.hand) for p in self.players),
    #           tuple(p.points for p in self.players),
    #           self.current_player_idx,
    #           ... game-specific fields ...
    #       ))