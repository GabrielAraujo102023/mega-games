from core.game import Game
from core.cards import CardType, Card, CardSuit
from typing import Any, List, Dict, Optional

from core.player import Player
from core.utils import partition

SUECA = 'sueca'
SUECA_CARD_VALUES = {
    CardType.TWO: 0,
    CardType.THREE: 0,
    CardType.FOUR: 0,
    CardType.FIVE: 0,
    CardType.SIX: 0,
    CardType.JACK: 2,
    CardType.QUEEN: 3,
    CardType.KING: 4,
    CardType.SEVEN: 10,
    CardType.ACE: 11,
}

class Sueca(Game):
    def __init__(self, main_character: int):
        super().__init__(
            game_name=SUECA,
            n_players=4,
            unused_card_types=[CardType.EIGHT, CardType.NINE, CardType.TEN, CardType.JOKER],
            card_values=SUECA_CARD_VALUES,
            starting_cards=10,
            main_character=main_character,
            use_personas=True,
        )

        self.current_suit: Optional[CardSuit] = None
        self.trump_suit: Optional[CardSuit] = None
        self.table: Dict[int, Card] = {} # Map of (player ID -> card they played this round)

    def get_game_player(self) -> Player:
        return Ze(game=self, id_=self.main_character, name='Zé', hand=self.draw_card(10))

    def is_trump(self, card: Card) -> bool:
        return self.trump_suit == card.suit

    def is_starting_turn(self) -> bool:
        return self.table == {}

    def matches_suit(self, card: Card) -> bool:
        return card.suit == self.current_suit

    def is_ours(self, player) -> bool:
        """does the player win this round?"""
        if len(self.table) != 3:
            return False
        opponent1 = self.table[self.get_opponent1(player).id_]
        opponent2 = self.table[self.get_opponent2(player).id_]
        partner = self.table[self.get_partner(player).id_]
        we_have_trump = self.is_trump(partner) and not self.is_trump(opponent1) and not self.is_trump(opponent2)
        we_have_higher = opponent1.value < partner.value > opponent2.value and (opponent1.suit == opponent2.suit == partner.suit)
        return we_have_higher or we_have_trump

    def get_playable_cards(self, player) -> List[Card]:
        matched, unmatched = partition(player.hand, lambda c: self.matches_suit(c))
        return unmatched if len(matched) == 0 else matched

    @staticmethod
    def get_partner(player) -> Player:
        return player.id_ - 2

    @staticmethod
    def get_opponent1(player) -> Player:
        return player.id_ - 1

    @staticmethod
    def get_opponent2(player) -> Player:
        return player.id_ - 3

    def reset(self):
        self.table = {}
        self.current_suit = None
        self.trump_suit = self.players[3].hand[0].suit

    def add_up_points(self):
        winner = self.is_ours(self.players[1])
        points = sum(self.table.values())
        self.players[winner].points += points
        self.players[winner + 2].points += points


    def apply_move(self, move: Card) -> 'Sueca':
        new = self.clone()
        player = new.get_current_player()
        if move not in player.hand:
            print('asd')

        if len(new.table) == 4:
            self.add_up_points()
            new.reset()

        # if not new.is_starting_turn():
        #     new.advance_turn()
        # else:
        #     new.current_suit = move.suit

        if new.is_starting_turn():
            new.current_suit = move.suit

        new.table[player.id_] = move
        new.remove_card(player.id_, move)

        return new

    def is_terminal(self) -> bool:
        return all(len(p.hand) == 0 for p in self.players)

    @staticmethod
    def team_evals(cur_player: Player, player_eval: float, op_eval: float) -> List[float]:
        return \
            [player_eval, op_eval, player_eval, op_eval] if cur_player.id_ == 0 or cur_player.id_ == 2 \
            else [op_eval, player_eval, op_eval, player_eval]

    def rank_hands(self, player, partner, op1, op2):
        eval_ = 0
        team_cards = player.hand + partner.hand
        op_cards = op1.hand + op2.hand

        for suit in CardSuit:
            worth = 1 if suit != self.trump_suit else 2
            suit_team_cards, team_cards = partition(team_cards, lambda card: card.suit == suit)
            suit_op_cards, op_cards = partition(op_cards, lambda card: card.suit == suit)
            suit_team_cards.sort(key=lambda card: card.value, reverse=True)
            suit_op_cards.sort(key=lambda card: card.value, reverse=True)

            # If they have more cards than us, subtract that difference
            if len(suit_team_cards) < len(suit_op_cards):
                for i, c in enumerate(suit_team_cards):
                    eval_ += worth if c.value > suit_op_cards[i].value else -worth
                eval_ -= len(suit_op_cards[len(suit_team_cards) - 1:]) * worth
            elif len(suit_team_cards) > len(suit_op_cards):
                for i, c in enumerate(suit_op_cards):
                    eval_ -= worth if c.value > suit_team_cards[i].value else -worth
                eval_ += len(suit_team_cards[len(suit_op_cards) - 1:]) * worth



        return eval_

    def evaluate(self) -> List[float]:
        if self.is_terminal():
            player = self.players[0]
            opponent = self.players[1]
            if player.points == opponent.points:
                return [1, 1, 1, 1]
            if player.points > opponent.points:
                return self.team_evals(player, player_eval=999, op_eval=0)
            return self.team_evals(player, player_eval=0, op_eval=999)

        player = self.get_current_player()
        op1 = self.players[self.get_opponent1(player)]
        op2 = self.players[self.get_opponent2(player)]
        partner = self.players[self.get_partner(player)]
        evaluation = 0
        evaluation += self.rank_hands(player, partner, op1, op2)
        evaluation += player.points - op1.points

        return self.team_evals(player, player_eval=evaluation, op_eval=-evaluation)

    def _print_table(self):
        table = []
        for i in range(4):
            if i not in self.table:
                table.append(' - ')
            else:
                table.append(f' {self.table[i]} ')

    def print_move(self) -> Dict[str, Any]:
        res = {'table': self._print_table()}
        for p in self.players:
            res[p.name] = p.hand
        return res

    def init_player_hand(self, player) -> Player:
        player.hand = self.draw_card(10)
        return player

    def __hash__(self) -> int:
        ...
        # TODO

class Ze(Player):
    def __init__(self, game: Sueca, id_: int = 0, name: str = '', hand: Optional[List[Card]] = None):
        super().__init__(id_, name, hand)
        self.game = game

    def get_moves(self, playable_cards: List[Card]) -> List[Card]:
        if self.game.is_starting_turn():
            return sorted(self.hand, key=lambda c: c.value, reverse=True)

        # return a sorted list of cards by value, with trumps sorted separately at the end
        if self.game.is_ours(self):
            return sorted(playable_cards, key=lambda c: (self.game.is_trump(c), -c.value))
        return sorted(playable_cards, key=lambda c: (not self.game.is_trump(c), -c.value))
