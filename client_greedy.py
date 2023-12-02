#!/usr/bin/python
"""
This program plays Othello using a greedy algorithm to
find the best move at each turn. The algorithm looks at all
legal moves and chooses the move that will capture the most
opponent pieces on that turn.

Author: Cole Koryto
"""

import sys
import json
import socket
import time
import random

NUM_ROWS = 8
NUM_COLUMNS = 8
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


# determines if any piece can be captured from the given square and the number that can be captured
def get_capture_details(player, board, row, column):

    # runs through each possible direction ensuring a capture run is possible
    capture = False
    total_captured = 0
    opponent = player + (player % 2) * 2 - 1    # converts 1 -> 2 and 2 -> 1
    for row_delta, column_delta in DIRECTIONS:

        # checks if off board
        if not on_grid(row, column, row_delta, column_delta):
            continue

        # checks for opponent piece
        if board[row + row_delta][column + column_delta] == opponent:
            
            # check line to ensure friendly piece on other side
            friendly_found = False
            cur_row = row + row_delta
            cur_column = column + column_delta
            cur_capped = 0
            while not friendly_found:

                # checks if friendly piece found yet
                if board[cur_row][cur_column] == player:
                    friendly_found = True

                # if not friendly, ensures there is still a run of opponent pieces
                elif board[cur_row][cur_column] == opponent:
                    cur_capped += 1
                # break if empty square
                else:
                    break

                # checks if next square off board
                if not on_grid(cur_row, cur_column, row_delta, column_delta):
                    break
                else:
                    # updates checking position
                    cur_row += row_delta
                    cur_column += column_delta

            # updates capture state and adds to total captured
            if friendly_found:
                capture = True
                total_captured += cur_capped

    # returns if can capture and total captured
    return capture, total_captured


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
    capped_in_move = []
    for row in range(NUM_COLUMNS):
        for column in range(NUM_COLUMNS):

            # skips occupied squares
            if board[row][column] != 0:
                continue

            # finds if move can capture on square
            capture, total_captured = get_capture_details(player, board, row, column)
            if capture:
                legal_moves.append([row, column])
                capped_in_move.append(total_captured)

    # returns valid legal moves and the number captured in each move
    return legal_moves, capped_in_move


def get_move(player, board):

    # gets all possible legal moves and the number they capture
    legal_moves, capped_in_move = generate_legal_moves(player, board)

    # finds move that captures the most pieces
    most_capped = max(capped_in_move)

    # finds move that captures most and chooses between the best move randomly if many have the most captured
    if capped_in_move.count(most_capped) > 1:
        best_indices = [i for i, num_capped in enumerate(capped_in_move) if num_capped == most_capped]
        best_move = legal_moves[random.choice(best_indices)]
    else:
        best_move = legal_moves[capped_in_move.index(most_capped)]

    # returns best move that captures the most pieces
    return best_move


# formats move response to be sent to game server
def prepare_response(move):
    response = '{}\n'.format(move).encode()
    print('sending {!r}'.format(response))
    return response


# plays the game using a greedy agent
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
