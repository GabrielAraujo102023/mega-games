import random
from typing import List, Callable

from core.player import Player, Random, HighRoler, Dummy, Alternate

DEFAULT_PERSONAS = [Random(), HighRoler(), Dummy(), Alternate()]

def add_game_personas(game_name: str) -> List[Player]:
    # Add other game's personas here
    match game_name:
        case _:
            return []

def get_random_personas(game_name: str, n_persona: int, init_hand_func: Callable[[Player], Player]) -> List[Player]:
    res = []
    available_personas = DEFAULT_PERSONAS + add_game_personas(game_name)
    personas = available_personas.copy()
    l = len(personas)
    for i in range(n_persona):
        p = personas.pop(random.randrange(l))
        res.append(init_hand_func(p))
        l -= 1
        if l == 0:
            personas = available_personas.copy()
    return res
