#!/usr/bin/python
"""
This program plays Othello using the minimax algorithm to
find the best move at each turn. The algorithm searches all
legal moves until a certain depth and scores by counting
player piece surplus along with if the game is won, lost, or tied.

Author: Cole Koryto
"""

import sys
import json
import socket
import time
import numpy as np
import random
import copy

NUM_ROWS = 8
NUM_COLUMNS = 8
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
WIN_SCORE = 100
LOSE_SCORE = -100
SEARCH_DEPTH = 5        # maximum search depth of minimax algorithm, begins to not meet default time requirement at 7+


# uses the minimax algorithm to search a given depth of game possibilities and finds the highest scoring move
def minimax_score(player, board, cur_depth, player_turn):

    # ends search if no more depth left to explore
    opponent = player + (player % 2) * 2 - 1    # converts 1 -> 2 and 2 -> 1
    cur_player_surplus = np.count_nonzero(board == player) - np.count_nonzero(board == opponent)
    if cur_depth == 0:
        return cur_player_surplus

    # gets the current state of the game and checks if in an end condition
    cur_state = check_game_over(board)
    if cur_state == 0:          # game not done
        pass
    elif cur_state == 1:        # player1 won
        if player == 1:
            return WIN_SCORE + cur_player_surplus
        else:
            return LOSE_SCORE + cur_player_surplus
    elif cur_state == 2:        # player2 won
        if player == 2:
            return WIN_SCORE + cur_player_surplus
        else:
            return LOSE_SCORE + cur_player_surplus
    if cur_state == 3:          # tie
        return 0

    # if player's turn, check the score of all possible legal moves since game is not over
    if player_turn:
        legal_moves = generate_legal_moves(player, board)

        # passes if no legal moves and finds best score otherwise
        max_score = LOSE_SCORE
        if len(legal_moves) == 0:
            max_score = minimax_score(player, board, cur_depth - 1, False)
        else:
            for move in legal_moves:
                new_board = play_move(player, board, move)
                score = minimax_score(player, new_board, cur_depth - 1, False)
                max_score = max(max_score, score)
        return max_score

    # if opponents turn, make a random legal move and return player's best score
    else:
        legal_moves = generate_legal_moves(opponent, board)

        # passes if no legal moves and makes random move otherwise
        if len(legal_moves) == 0:
            rang_score = minimax_score(player, board, cur_depth - 1, True)
        else:
            random_move = random.choice(legal_moves)
            new_board = play_move(opponent, board, random_move)
            rang_score = minimax_score(player, new_board, cur_depth - 1, True)
        return rang_score


# makes the provided legal move on the board and changes board as needed
def play_move(cur_player, board, move):

    # copies board and makes move getting possible capture directions
    new_board = copy.deepcopy(board)
    cur_opponent = cur_player + (cur_player % 2) * 2 - 1  # converts 1 -> 2 and 2 -> 1
    new_board[move[0]][move[1]] = cur_player
    _, capture_dirs = get_capture_details(cur_player, new_board, move[0], move[1])

    # makes any possible captures based on move
    for row_delta, column_delta in capture_dirs:
        flip_row = move[0] + row_delta
        flip_col = move[1] + column_delta

        while new_board[flip_row][flip_col] == cur_opponent:
            new_board[flip_row][flip_col] = cur_player
            flip_row += row_delta
            flip_col += column_delta

    # returns new board state after move and any possible captures
    return new_board


# checks if the current game is over: 0 = not done, 1 = player1 wins, 2 = player2 wins, 3 = tie
def check_game_over(board):

    # checks if either player has moves left to make, if so game is not done
    player1_legal_moves = generate_legal_moves(1, board)
    if len(player1_legal_moves) > 0:
        return 0
    player2_legal_moves = generate_legal_moves(2, board)
    if len(player2_legal_moves) > 0:
        return 0

    # finds winner if game is done
    return find_winner(board)


# finds the winner of a game given it is done: 1 = player1 wins, 2 = player2 wins, 3 = tie
def find_winner(board):
    player1_count = np.count_nonzero(board == 1)
    player2_count = np.count_nonzero(board == 2)
    if player1_count > player2_count:
        return 1
    elif player1_count < player2_count:
        return 2
    return 3


# determines if any piece can be captured from the given square and returns the directions in which capture is possible
def get_capture_details(cur_player, board, row, column):

    # runs through each possible direction ensuring a capture run is possible
    capture = False
    capture_dirs = []
    cur_opponent = cur_player + (cur_player % 2) * 2 - 1    # converts 1 -> 2 and 2 -> 1
    for row_delta, column_delta in DIRECTIONS:

        # checks if off board
        if not on_grid(row, column, row_delta, column_delta):
            continue

        # checks for opponent piece
        if board[row + row_delta][column + column_delta] == cur_opponent:

            # check line to ensure friendly piece on other side
            friendly_found = False
            cur_row = row + row_delta
            cur_column = column + column_delta
            while not friendly_found:

                # checks if friendly piece found yet
                if board[cur_row][cur_column] == cur_player:
                    friendly_found = True

                # if not friendly, ensures there is still a run of opponent pieces
                elif board[cur_row][cur_column] != cur_opponent:
                    break

                # checks if next square off board
                if not on_grid(cur_row, cur_column, row_delta, column_delta):
                    break
                else:
                    # updates checking position
                    cur_row += row_delta
                    cur_column += column_delta

            # updates capture state and adds capture direction
            if friendly_found:
                capture = True
                capture_dirs.append((row_delta, column_delta))

    # returns if can capture and capture directions
    return capture, capture_dirs


# helper function to determine if square is off the grid
def on_grid(row, column, row_delta, column_delta):
    if (row + row_delta < 0) or (row + row_delta >= NUM_ROWS):
        return False
    elif (column + column_delta < 0) or (column + column_delta >= NUM_COLUMNS):
        return False
    else:
        return True


# generates all legal moves the agent can make
def generate_legal_moves(player, board):
    legal_moves = []
    for row in range(NUM_COLUMNS):
        for column in range(NUM_COLUMNS):

            # skips occupied squares
            if board[row][column] != 0:
                continue

            # finds if move can capture on square
            capture, _ = get_capture_details(player, board, row, column)
            if capture:
                legal_moves.append([row, column])

    # returns all valid legal moves
    return legal_moves


# gets the best move based on highest scoring move from minimax algorithm
def get_move(player, board):

    # gets all possible legal moves and the number they capture
    board = np.array(board)
    legal_moves = generate_legal_moves(player, board)

    # finds the best move with the minimax algorithm
    best_move = None
    best_val = -9999999
    for move in legal_moves:
        new_board = play_move(player, board, move)
        move_val = minimax_score(player, new_board, SEARCH_DEPTH, False)
        if move_val >= best_val:
            best_move = move
            best_val = move_val

    # returns move found with best score
    return best_move


# formats move response to be sent to game server
def prepare_response(move):
    response = '{}\n'.format(move).encode()
    print('sending {!r}'.format(response))
    return response


# plays the game using a minimax agent
def play_game():
    port = int(sys.argv[1]) if (len(sys.argv) > 1 and sys.argv[1]) else 1337    # player1 port = 1337, player2 port = 1338
    host = sys.argv[2] if (len(sys.argv) > 2 and sys.argv[2]) else socket.gethostname()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # continually tries to connect to game server and send responses
    try:
        sock.connect((host, port))
        while True:
            data = sock.recv(1024)
            if not data:
                print('connection to server closed')
                break
            json_data = json.loads(str(data.decode('UTF-8')))
            board = json_data['board']
            maxTurnTime = json_data['maxTurnTime']
            player = json_data['player']
            print(player, maxTurnTime, board)

            move = get_move(player, board)
            response = prepare_response(move)
            sock.sendall(response)
    finally:
        sock.close()


if __name__ == "__main__":
    while True:
        try:
            play_game()
        except Exception as e:
            print("Waiting 1 second and trying to connect again")
            time.sleep(1)
