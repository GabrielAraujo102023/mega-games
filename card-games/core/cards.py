from enum import Enum
from typing import Dict


class CardType(Enum):
    TWO = 1
    THREE = 2
    FOUR = 3
    FIVE = 4
    SIX = 5
    SEVEN = 6
    EIGHT = 7
    NINE = 8
    TEN = 9
    JACK = 10
    QUEEN = 11
    KING = 12
    ACE = 13
    JOKER = 14

DEFAULT_CARD_VALUES: Dict[CardType, int] = {
    CardType.TWO: 1,
    CardType.THREE: 2,
    CardType.FOUR: 3,
    CardType.FIVE: 4,
    CardType.SIX: 5,
    CardType.SEVEN: 6,
    CardType.EIGHT: 7,
    CardType.NINE: 8,
    CardType.TEN: 9,
    CardType.JACK: 10,
    CardType.QUEEN: 11,
    CardType.KING: 12,
    CardType.ACE: 13,
    CardType.JOKER: 14
}

class CardSuit(Enum):
    SPADE = 1
    HEART = 2
    DIAMOND = 3
    CLUB = 4

class Card:
    def __init__(self, card_type: CardType, value: int, suit: CardSuit = CardSuit.SPADE) -> None:
        self.card_type = card_type
        self.value = value
        self.suit = suit

    def __eq__(self, other):
        return self.card_type == other.card_type and self.value == other.value and self.suit == other.suit

    def __str__(self) -> str:
        res = ''
        match self.card_type:
            case CardType.TWO:
                res = '2'
            case CardType.THREE:
                res = '3'
            case CardType.FOUR:
                res = '4'
            case CardType.FIVE:
                res = '5'
            case CardType.SIX:
                res = '6'
            case CardType.SEVEN:
                res = '7'
            case CardType.EIGHT:
                res = '8'
            case CardType.NINE:
                res = '9'
            case CardType.TEN:
                res = '10'
            case CardType.JACK:
                res = 'J'
            case CardType.QUEEN:
                res = 'Q'
            case CardType.KING:
                res = 'K'
            case CardType.ACE:
                res = 'A'
            case CardType.JOKER:
                return '🃏'

        match self.suit:
            case CardSuit.SPADE:
                res += '♠'
            case CardSuit.HEART:
                res += '♥'
            case CardSuit.DIAMOND:
                res += '♦'
            case CardSuit.CLUB:
                res += '♣'

        return res