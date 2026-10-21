import json
from datetime import datetime

from core.engine import MinimaxEngine, EngineConfig
import sys
from sueca.sueca import Sueca

GAME_NAME = ''
N_GAMES = 1
ID = 0
DEPTH = 10

def parse_args():
    global GAME_NAME, N_GAMES, ID, DEPTH
    if len(sys.argv) < 2:
        sys.exit('Usage: main.py <game name> (Optional  ->  NUMBER_OF_GAMES, PLAYER_NUMBER, DEPTH)')
    GAME_NAME = sys.argv[1]
    if len(sys.argv) == 2:
        print('Optional arguments -> NUMBER_OF_GAMES, PLAYER_NUMBER, DEPTH. Using default arguments (1, -1, 10)')
    else:
        N_GAMES = int(sys.argv[2])
        ID = int(sys.argv[3])
        DEPTH = int(sys.argv[4])

def load_game():
    match GAME_NAME:
        case 'sueca':
            return Sueca(main_character=ID - 1)
        case _:
            sys.exit(f'Invalid game name: {GAME_NAME}')

def build_engine() -> MinimaxEngine:
    conf = EngineConfig(
        depth=DEPTH,
        teams=[[0,2],[1,3]],
        mode='minimax'
    )
    return MinimaxEngine(conf)

def run_game(game_id, game, engine: MinimaxEngine) -> dict: # returns result: moves, scores, winner
    moves = []
    while not game.is_terminal():
        best_move = engine.best_move(game)
        game.apply_move(best_move)
        moves.append(game.print_move())
    return {'game_id': game_id, 'moves': moves, 'winner': game.get_winner(), 'score': game.get_score()}

def run_simulation():  # runs N games, aggregates results
    game = load_game()
    engine = build_engine()
    results = []
    for game_id in range(N_GAMES):
        results.append(run_game(game_id, game, engine))
    print_results(results)

def print_results(results: list):
    now = datetime.now()
    with open(f'./results/results_{GAME_NAME}_{now.microsecond}.json', 'w') as f:
        json.dump(results, f)

def main():
    parse_args()
    run_simulation()


if __name__ == '__main__':
    main()