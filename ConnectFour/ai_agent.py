"""
This is the code that implements the AI agent to predict the next best move per each turn using the minimax algorithm with alpha-beta pruning
"""
import numpy as np
import random
import math
import pygame

AI_PIECE = 2
PLAYER_PIECE = 1
EMPTY = 0
WINDOW_LENGTH = 4
PURPLE = (128, 0, 128)

def is_valid_location(board, col):
    return 0 <= col < len(board[0]) and board[0][col] == 0

def get_valid_locations(board):
    column_count = len(board[0])
    return [col for col in range(column_count) if is_valid_location(board, col)]

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def get_next_open_row(board, col):
    for r in range(len(board)-1, -1, -1):
        if board[r][col] == 0:
            return r
    return None  # Return None if no available row

def winning_move(board, piece):
    row_count = len(board)
    column_count = len(board[0])
    
    for r in range(row_count):
        for c in range(column_count - 3):
            if all(board[r][c + i] == piece for i in range(4)):
                return True
    
    for c in range(column_count):
        for r in range(row_count - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True
    
    for r in range(row_count - 3):
        for c in range(column_count - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True
    
    for r in range(3, row_count):
        for c in range(column_count - 3):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True
    
    return False

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
    
    if window.count(piece) == 4:
        score += 1000
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 50
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 10
    
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 80
    elif window.count(opp_piece) == 2 and window.count(EMPTY) == 2:
        score -= 20
    
    return score

def score_position(board, piece):
    score = 0
    row_count = len(board)
    column_count = len(board[0])
    
    center_array = [board[r][column_count//2] for r in range(row_count)]
    score += center_array.count(piece) * 6
    
    for r in range(row_count):
        row_array = board[r]
        for c in range(column_count - 3):
            score += evaluate_window(row_array[c:c+WINDOW_LENGTH], piece)
    
    for c in range(column_count):
        col_array = [board[r][c] for r in range(row_count)]
        for r in range(row_count - 3):
            score += evaluate_window(col_array[r:r+WINDOW_LENGTH], piece)
    
    for r in range(row_count - 3):
        for c in range(column_count - 3):
            score += evaluate_window([board[r+i][c+i] for i in range(WINDOW_LENGTH)], piece)
    
    for r in range(3, row_count):
        for c in range(column_count - 3):
            score += evaluate_window([board[r-i][c+i] for i in range(WINDOW_LENGTH)], piece)
    
    return score

def minimax(board, depth, alpha, beta, maximizing_player, piece):
    valid_locations = get_valid_locations(board)
    is_terminal = len(valid_locations) == 0 or winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE)
    
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -100000000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, piece))
    
    valid_locations.sort(key=lambda x: abs(x - len(board[0])//2))
    
    if maximizing_player:
        value = -math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            if row is None:
                continue  # Skip this column if it's full
            
            temp_board = [row[:] for row in board]
            drop_piece(temp_board, row, col, piece)
            new_score = minimax(temp_board, depth-1, alpha, beta, False, piece)[1]
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta: # highlight the pruned branches for better understanding
                print(f"Pruning branch at depth {depth} for column {col} with alpha = {alpha} and beta = {beta}")
                break
        return best_col, value
    else:
        value = math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            if row is None:
                continue  # Skip this column if it's full

            temp_board = [row[:] for row in board]
            drop_piece(temp_board, row, col, PLAYER_PIECE if piece == AI_PIECE else AI_PIECE)
            new_score = minimax(temp_board, depth-1, alpha, beta, True, piece)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value

def get_best_move(board, depth=5, piece=AI_PIECE):
    valid_locations = get_valid_locations(board)
    
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = [row[:] for row in board]
        drop_piece(temp_board, row, col, piece)
        if winning_move(temp_board, piece):
            return col, PURPLE
    
    # If no immediate win/block, use minimax
    col, _ = minimax(board, depth, -math.inf, math.inf, True, piece)
    return col, PURPLE
