from typing import List, Dict

from stockfish import Stockfish
from chess import Board

import os

STOCKFISH_PATH = 'stockfish-files/stockfish-macos-m1-apple-silicon'
STARTING_POSITION = ''
STOCKFISH = Stockfish(STOCKFISH_PATH)

def get_top_legal_moves(board1: Board, board2: Board) -> List[List[Dict]]:
    global STOCKFISH
    top_moves = []
    legal_moves = list(set([move.uci() for move in board1.legal_moves]) & set([move.uci() for move in board2.legal_moves]))
    if len(legal_moves) == 0:
        return []
    for i, b in enumerate([board1, board2]):
        top_moves.append([])
        STOCKFISH.set_fen_position(b.fen())
        all_legal_moves = [move.uci() for move in b.legal_moves]
        moves = STOCKFISH.get_top_moves(num_top_moves=len(all_legal_moves))
        for m in moves:
            if m['Move'] in legal_moves:
                top_moves[-1].append(m)
        top_moves[-1].sort(key=lambda m: m['Move'])
    return top_moves

def get_best_move(top_moves: List[List[Dict]]):
    if len(top_moves) == 0:
        return ''
    highest_avg = -32768
    move_to_play = ''
    for i, m in enumerate(top_moves[0]):
        if m['Mate']:
            return m['Move']
        avg = (m['Centipawn'] + top_moves[1][i]['Centipawn']) / 2
        if avg > highest_avg:
            highest_avg = avg
            move_to_play = m['Move']
    return move_to_play

def main():
    global STOCKFISH
    board1 = Board()
    board2 = Board()
    while not board1.is_checkmate() and not board2.is_checkmate():
        move = get_best_move(get_top_legal_moves(board1, board2))
        if move == '':
            print('No legal moves left.')
            return
        os.system('clear')
        board1.push_uci(move)
        board2.push_uci(move)
        print(f'Board 1:\nA B C D E F G H\n\n{board1}\n\nBoard 2:\nA B C D E F G H\n\n{board2}\nPlayed: {move}')
        legal1 = [m.uci() for m in board1.legal_moves]
        legal2 = [m.uci() for m in board2.legal_moves]
        while True:
            player_move = input('Your moves: ').split(' ')
            if len(player_move) != 2 or player_move[0] not in legal1 or player_move[1] not in legal2:
                print('Invalid move')
            else:
                break
        board1.push_uci(player_move[0])
        board2.push_uci(player_move[1])



if __name__ == '__main__':
    main()