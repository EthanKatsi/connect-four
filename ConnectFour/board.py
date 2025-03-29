"""
This is the code that implements all the connect 4 code other than the AI agent
"""
import pygame
import sys
import ai_agent
import gemini_agent

# constants
ROW_COUNT = 6
COLUMN_COUNT = 7
SQUARESIZE = 100
WIDTH = COLUMN_COUNT * SQUARESIZE
HEIGHT = (ROW_COUNT + 1) * SQUARESIZE
SIZE = (WIDTH, HEIGHT)
RADIUS = int(SQUARESIZE / 2 - 5)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREY = (128, 128, 128)
PURPLE = (255, 130, 251)

def create_board(rows, cols):
    board = [[0] * cols for _ in range(rows)]
    return board

# draws the connect 4 board in 6 rows by 7 columns - O(m*n)
def draw_board(board, screen):
    screen.fill((0, 0, 0))  # Clear screen

    for row in range(len(board)):  # Use dynamic row count
        for col in range(len(board[row])):  # Use dynamic column count
            pygame.draw.rect(screen, (0, 0, 255), (col * SQUARESIZE, row * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, (0, 0, 0), (col * SQUARESIZE + SQUARESIZE // 2, row * SQUARESIZE + SQUARESIZE + SQUARESIZE // 2), RADIUS)

    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == 1:
                pygame.draw.circle(screen, (255, 0, 0), (col * SQUARESIZE + SQUARESIZE // 2, (row + 1) * SQUARESIZE + SQUARESIZE // 2), RADIUS)
            elif board[row][col] == 2:
                pygame.draw.circle(screen, (255, 255, 0), (col * SQUARESIZE + SQUARESIZE // 2, (row + 1) * SQUARESIZE + SQUARESIZE // 2), RADIUS)

    pygame.display.update()

# bar at the top of the screen showing player turn and restart button
def top_bar(screen, current_player, selected_ai, font_size, button_font_size):
    # displays whos turn it is in the top left corner
    font = pygame.font.SysFont("arial", font_size)
    if current_player == 1:
        label = font.render("Player 1's Turn", True, RED)
    else:
        label = font.render("Player 2's Turn", True, YELLOW)
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
    screen.blit(label, (40, 10))

    # restart button in the top right corner
    button_font = pygame.font.SysFont("arial", button_font_size)
    restart_label = button_font.render("Restart", True, YELLOW)
    label_rect = restart_label.get_rect()
    x = WIDTH - label_rect.width - 20
    y = (SQUARESIZE - label_rect.height) // 2

    # grey rectangle behind restart button
    rect_background = pygame.Rect(x - 10, y - 5, label_rect.width + 20, label_rect.height + 10)
    pygame.draw.rect(screen, GREY, rect_background)
    screen.blit(restart_label, (x, y))

    # ai suggestion button beside restart button
    ai_label = button_font.render("| Get AI Suggestion", True, PURPLE)
    ai_rect = ai_label.get_rect()
    x_ai = WIDTH - ai_rect.width - 125
    y_ai = (SQUARESIZE - ai_rect.height) // 2
    ai_bg = pygame.Rect(x_ai - 10, y_ai - 5, ai_rect.width + 20, ai_rect.height + 10)
    pygame.draw.rect(screen, GREY, ai_bg)
    screen.blit(ai_label, (x_ai, y_ai))

    # button to change which ai you use (minimax or gemini) - click the button to change which ai you are using
    ai_select_label = button_font.render(selected_ai, True, PURPLE)
    ai_select_rect = ai_select_label.get_rect()
    x_select = WIDTH - ai_rect.width - 110 - ai_select_rect.width - 30
    y_select = (SQUARESIZE - ai_select_rect.height) // 2
    ai_select_bg = pygame.Rect(x_select - 10, y_select - 5, ai_select_rect.width + 20, ai_select_rect.height + 10)
    pygame.draw.rect(screen, GREY, ai_select_bg)
    screen.blit(ai_select_label, (x_select, y_select))
    
    pygame.display.update()
    return rect_background, ai_bg, ai_select_bg

# displays the player who won the game, restart button, and exit button
def winner_label(screen, winning_player, font_size, button_font_size):
    font = pygame.font.SysFont("arial", font_size)
    if winning_player == 1:
        label = font.render("Player 1 wins!", True, RED)
    else:
        label = font.render("Player 2 wins!", True, YELLOW)

    # grey background so text is easier to read
    text_rect = label.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    text_bg_rect = text_rect.inflate(20, 20)
    pygame.draw.rect(screen, BLACK, text_bg_rect)
    screen.blit(label, text_rect)

    # restart button + background
    button_font = pygame.font.SysFont("arial", button_font_size)
    restart_label = button_font.render("Restart", True, YELLOW)
    restart_rect = restart_label.get_rect(center=(WIDTH // 2, text_rect.bottom + 50))
    pygame.draw.rect(screen, GREY, restart_rect.inflate(20, 10))
    screen.blit(restart_label, restart_rect)

    # exit button + background
    exit_label = button_font.render("Exit Game", True, RED)
    exit_rect = exit_label.get_rect(center=(WIDTH // 2, text_rect.bottom + 120))
    pygame.draw.rect(screen, GREY, exit_rect.inflate(20, 10))
    screen.blit(exit_label, exit_rect)

    pygame.display.update()
    return restart_rect, exit_rect

# if a player gets 4 in a row they win the game - O(m*n)
def winning_move(board, piece):
    rows = len(board)
    cols = len(board[0]) if rows > 0 else 0
    
    # Check horizontal locations
    for r in range(rows):
        for c in range(cols - 3):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][c + 3] == piece:
                return True

    # Check vertical locations
    for c in range(cols):
        for r in range(rows - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][c] == piece:
                return True

    # Check positively sloped diagonals
    for r in range(rows - 3):
        for c in range(cols - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                return True

    # Check negatively sloped diagonals
    for r in range(3, rows):
        for c in range(cols - 3):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                return True
    return False

# main function for when the game is being played
def main():
    pygame.init()
    
    # Ask user for grid size
    ROW_COUNT = int(input("Enter number of rows (default 6): ") or 6)
    COLUMN_COUNT = int(input("Enter number of columns (default 7): ") or 7)

    # Calculate dynamic square size based on requested dimensions
    MAX_WIDTH = 1200  # Maximum window width
    MAX_HEIGHT = 800  # Maximum window height
    MIN_SQUARESIZE = 40  # Minimum size for squares
    DEFAULT_SQUARESIZE = 100  # Default size
    
    # Calculate optimal square size
    SQUARESIZE = min(
        DEFAULT_SQUARESIZE,
        MAX_WIDTH // max(COLUMN_COUNT, 7),
        MAX_HEIGHT // max(ROW_COUNT + 1, 7)  # +1 for the top bar
    )
    SQUARESIZE = max(SQUARESIZE, MIN_SQUARESIZE)  # Ensure minimum size
    
    # Recalculate other constants based on dynamic square size
    WIDTH = COLUMN_COUNT * SQUARESIZE
    HEIGHT = (ROW_COUNT + 1) * SQUARESIZE
    SIZE = (WIDTH, HEIGHT)
    RADIUS = int(SQUARESIZE / 2 - 5)
    
    # Adjust font sizes based on square size
    FONT_SIZE = max(20, int(SQUARESIZE * 0.3))
    BUTTON_FONT_SIZE = max(16, int(SQUARESIZE * 0.25))
    WINNER_FONT_SIZE = max(30, int(SQUARESIZE * 0.5))

    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Connect 4")

    def create_board():
        return [[0 for _ in range(COLUMN_COUNT)] for _ in range(ROW_COUNT)]

    board = create_board()
    draw_board(board, screen)
    
    current_player = 1
    selected_ai = "Minimax"  
    restart_button_rect, ai_suggestion_rect, ai_select_rect = top_bar(screen, current_player, selected_ai, FONT_SIZE, BUTTON_FONT_SIZE)

    running = True
    game_over = False
    winner_restart_rect = None
    winner_exit_rect = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                position_x, position_y = event.pos

                # Restart button
                if restart_button_rect.collidepoint(position_x, position_y):
                    board = create_board()
                    draw_board(board, screen)
                    current_player = 1
                    game_over = False
                    restart_button_rect, ai_suggestion_rect, ai_select_rect = top_bar(screen, current_player, selected_ai, FONT_SIZE, BUTTON_FONT_SIZE)
                    continue

                # AI Selection Button
                if ai_select_rect.collidepoint(position_x, position_y):
                    if selected_ai == "Minimax":
                        selected_ai = "Gemini"
                    else:
                        selected_ai = "Minimax"
                    restart_button_rect, ai_suggestion_rect, ai_select_rect = top_bar(screen, current_player, selected_ai, FONT_SIZE, BUTTON_FONT_SIZE)
                    continue
                
                if ai_suggestion_rect.collidepoint(position_x, position_y):
                    if selected_ai == "Minimax":
                        if current_player == 1:
                            column, _ = ai_agent.get_best_move(board, depth = 5, piece = ai_agent.PLAYER_PIECE)  # player 1's turn uses PLAYER_PIECE
                        else:
                            column, _ = ai_agent.get_best_move(board, depth = 5, piece = ai_agent.AI_PIECE)  # player 2's turn uses AI_PIECE
                    
                    else:
                        column = gemini_agent.get_gemini_move(board)

                    # if a non full column is returned then it finds the next open row in that column
                    if column is not None:
                        row = ai_agent.get_next_open_row(board, column)
                        
                        if row is not None:
                            print("AI suggests for player", current_player, "column", column, "row", row)  # print ai suggestion for debugging
                            circle_x = column * SQUARESIZE + SQUARESIZE / 2
                            circle_y = row * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2
                            pygame.draw.circle(screen, PURPLE, (circle_x, circle_y), RADIUS)
                            pygame.display.update()
                        # if the row that the ai generatess is none, skips the ai generation (for the gemini ai)
                        else:
                            print("Suggested column", column, "is full. No open row available.")

                # Click inside the grid
                if position_y >= SQUARESIZE:
                    column = position_x // SQUARESIZE
                    for row in range(ROW_COUNT - 1, -1, -1):
                        if board[row][column] == 0:
                            board[row][column] = current_player
                            draw_board(board, screen)

                            if winning_move(board, current_player):
                                winner_restart_rect, winner_exit_rect = winner_label(screen, current_player, WINNER_FONT_SIZE, BUTTON_FONT_SIZE)
                                game_over = True
                            else:
                                current_player = 2 if current_player == 1 else 1
                                restart_button_rect, ai_suggestion_rect, ai_select_rect = top_bar(screen, current_player, selected_ai, FONT_SIZE, BUTTON_FONT_SIZE)
                            break

                if game_over:
                    if winner_restart_rect and winner_restart_rect.collidepoint(position_x, position_y):
                        board = create_board()
                        draw_board(board, screen)
                        current_player = 1
                        restart_button_rect, ai_suggestion_rect, ai_select_rect = top_bar(screen, current_player, selected_ai, FONT_SIZE, BUTTON_FONT_SIZE)
                        game_over = False

                    if winner_exit_rect and winner_exit_rect.collidepoint(position_x, position_y):
                        running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
