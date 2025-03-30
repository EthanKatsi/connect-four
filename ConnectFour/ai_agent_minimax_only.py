"""
This is the code that implements the AI agent to predict the next best move per each turn using the minimax algorithm without alpha-beta pruning
"""
import random
import math

AI_PIECE = 2
PLAYER_PIECE = 1
EMPTY = 0
WINDOW_LENGTH = 4
PURPLE = (128, 0, 128)


def is_valid_location(board, col):
    return board[0][col] == EMPTY

def get_valid_locations(board):
    COLUMN_COUNT = len(board[0])
    return [col for col in range(COLUMN_COUNT) if is_valid_location(board, col)]

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def get_next_open_row(board, col):
    ROW_COUNT = len(board)
    for r in range(ROW_COUNT-1, -1, -1):
        if board[r][col] == EMPTY:
            return r

def winning_move(board, piece):
    ROW_COUNT = len(board)
    COLUMN_COUNT = len(board[0])

    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT - 3):
            if all(board[r][c + i] == piece for i in range(4)):
                return True
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True
    for r in range(3, ROW_COUNT):
        for c in range(COLUMN_COUNT - 3):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True
    return False

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
    
    # Prioritize winning moves and blocking opponent wins
    if window.count(piece) == 4:
        score += 1000
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 50
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 10
    
    # Block opponent's potential wins
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 80
    elif window.count(opp_piece) == 2 and window.count(EMPTY) == 2:
        score -= 20
    
    return score

def score_position(board, piece):
    ROW_COUNT = len(board)
    COLUMN_COUNT = len(board[0])
    score = 0
    
    # Prefer center column
    center_array = [board[r][COLUMN_COUNT//2] for r in range(ROW_COUNT)]
    center_count = center_array.count(piece)
    score += center_count * 6
    
    # Evaluate horizontal
    for r in range(ROW_COUNT):
        row_array = [board[r][c] for c in range(COLUMN_COUNT)]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)
    
    # Evaluate vertical
    for c in range(COLUMN_COUNT):
        col_array = [board[r][c] for r in range(ROW_COUNT)]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)
    
    # Evaluate positive diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
    
    # Evaluate negative diagonal
    for r in range(3, ROW_COUNT):
        for c in range(COLUMN_COUNT-3):
            window = [board[r-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
    
    return score

def minimax(board, depth, maximizing_player, piece):
    COLUMN_COUNT = len(board[0])

    if not hasattr(minimax, 'prune_count'):
        minimax.prune_count = 0

    valid_locations = get_valid_locations(board)
    is_terminal = len(valid_locations) == 0 or winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE)
    
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -100000000)
            else:  # Game is over, no more valid moves
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, piece))

    # Order moves by center preference
    valid_locations.sort(key=lambda x: abs(x - COLUMN_COUNT//2))
    
    if maximizing_player: # maximizing player first
        value = -math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = [row[:] for row in board]
            drop_piece(temp_board, row, col, piece)
            new_score = minimax(temp_board, depth-1, False, piece)[1]
            if new_score > value: # count number of recursive calls for better understanding
                minimax.prune_count += 1
                print(f"Total recursive calls: {minimax.prune_count}) | Depth: {depth}, Column: {col}")
                value = new_score
                best_col = col
        return best_col, value
    else:  # Minimizing player
        value = math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = [row[:] for row in board]
            drop_piece(temp_board, row, col, PLAYER_PIECE if piece == AI_PIECE else AI_PIECE)
            new_score = minimax(temp_board, depth-1, True, piece)[1]
            if new_score < value:
                value = new_score
                best_col = col
        return best_col, value

def get_best_move(board, depth=5, piece=AI_PIECE):
    valid_locations = get_valid_locations(board)
    
    # Check for immediate win or block
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = [row[:] for row in board]
        drop_piece(temp_board, row, col, piece)
        if winning_move(temp_board, piece):
            return col, PURPLE
    
    # Check if opponent can win next move
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = [row[:] for row in board]
        drop_piece(temp_board, row, col, opp_piece)
        if winning_move(temp_board, opp_piece):
            return col, PURPLE
    
    # If no immediate win/block, use minimax
    col, _ = minimax(board, depth, True, piece)
    return col, PURPLE