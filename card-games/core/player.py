from abc import ABC, abstractmethod
import random
from typing import List, Optional

from core.cards import Card

class Player(ABC):
    def __init__(self, id_: int = 0, name: str = '', hand: Optional[List[Card]] = None) -> None:
        self.id_ = id_
        self.hand = hand
        self.name = name
        self.points = 0

    @abstractmethod
    def get_moves(self, playable_cards: List[Card]) -> List[Card]: ...
        # Get a list of cards sorted by a guess of what would be best or whatever the fuck you want

class Random(Player):
    def __init__(self) -> None:
        super().__init__(name='Random')
    def get_moves(self, playable_cards: List[Card]) -> List[Card]:
        return [random.choice(playable_cards)]

class HighRoler(Player):
    def __init__(self) -> None:
        super().__init__(name='High Roler')
    def get_moves(self, playable_cards: List[Card]) -> List[Card]:
        return [max(playable_cards, key=lambda card: card.value)]

class Dummy(Player):
    def __init__(self) -> None:
        super().__init__(name='Dummy')
    def get_moves(self, playable_cards: List[Card]) -> List[Card]:
        return [min(playable_cards, key=lambda card: card.value)]

class Alternate(Player):
    def __init__(self) -> None:
        super().__init__(name='Alternate')
    max_ = True
    def get_moves(self, playable_cards: List[Card]) -> List[Card]:
        if self.max_:
            self.max_ = False
            return [max(playable_cards, key=lambda card: card.value)]
        self.max_ = True
        return [min(playable_cards, key=lambda card: card.value)]