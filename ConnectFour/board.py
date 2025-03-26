"""
This is the code that implements all the connect 4 code other than the AI agent
"""
import pygame
import sys
import ai_agent  # imports ai_agent.py

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

def create_board():
    board = [[0 for _ in range(COLUMN_COUNT)] for _ in range(ROW_COUNT)]
    return board

# draws the connect 4 board in 6 rows by 7 columns - O(m*n)
def draw_board(board, screen):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            if board[r][c] == 0:
                color = BLACK
            elif board[r][c] == 1:
                color = RED
            elif board[r][c] == 2:
                color = YELLOW

            pygame.draw.circle(screen, color, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()

# bar at the top of the screen showing player turn and restart button
def top_bar(screen, current_player):
    # displays whos turn it is in the top left corner
    font = pygame.font.SysFont("arial", 42)
    if current_player == 1:
        label = font.render("Player 1's Turn", True, RED)
    else:
        label = font.render("Player 2's Turn", True, YELLOW)
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
    screen.blit(label, (40, 10))

    # restart button in the top right corner
    button_font = pygame.font.SysFont("arial", 30)
    restart_label = button_font.render("Restart", True, YELLOW)
    label_rect = restart_label.get_rect()
    x = WIDTH - label_rect.width - 20
    y = (SQUARESIZE - label_rect.height) // 2

    # grey rectangle behind restart button
    rect_background = pygame.Rect(x - 10, y - 5, label_rect.width + 20, label_rect.height + 10)
    pygame.draw.rect(screen, GREY, rect_background)
    screen.blit(restart_label, (x, y))
    
    pygame.display.update()
    return rect_background

# displays the player who won the game, restart button, and exit button
def winner_label(screen, winning_player):
    # displays who won the game
    font = pygame.font.SysFont("arial", 60)
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
    button_font = pygame.font.SysFont("arial", 40)
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
    # 4 in a row horizontally
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT - 3):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][c + 3] == piece:
                return True

    # 4 in a row vertically
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][c] == piece:
                return True

    # 4 in a row diagonally from bottom
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                return True

    # 4 in a row diagonally from top
    for r in range(3, ROW_COUNT):
        for c in range(COLUMN_COUNT - 3):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                return True
    return False

# main function for when the game is being played - O(1)
def main():
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Connect 4")

    board = create_board()
    draw_board(board, screen)
    current_player = 1  # player 1 starts
    restart_button = top_bar(screen, current_player)  # restart button at the top right corner
    running = True
    game_over = False
    restart_rect = None  # restart button when game is over
    exit_rect = None  # exit button when game is over

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                position_x, position_y = event.pos

                # if you click restart button
                if restart_button.collidepoint(position_x, position_y):
                    board = create_board()
                    draw_board(board, screen)
                    current_player = 1
                    game_over = False
                    restart_button = top_bar(screen, current_player)
                    continue

                # if the game is going on
                if not game_over:
                    # only allow clicks in the 6x7 grid (not in the top bar)
                    if position_y >= SQUARESIZE:
                        column = int(position_x // SQUARESIZE)
                        # when a player clicks a column, it starts from the bottom row
                        for row in range (ROW_COUNT - 1, -1, -1):
                            if board[row][column] == 0:  # if slot is empty (0), place a piece
                                board[row][column] = current_player
                                draw_board(board, screen)

                                # if a player gets 4 in a row, the game is over
                                if winning_move(board, current_player):
                                    restart_rect, exit_rect = winner_label(screen, current_player)
                                    game_over = True
                                else:
                                    if current_player == 1:
                                        current_player = 2
                                    else:
                                        current_player = 1
                                    restart_button = top_bar(screen, current_player)
                                break

                # if the game is over, restart and exit buttons are displayed
                else:
                    if restart_rect and restart_rect.collidepoint(event.pos):
                        board = create_board()
                        draw_board(board, screen)
                        current_player = 1
                        restart_button = top_bar(screen, current_player)
                        game_over = False
                        
                    if exit_rect and exit_rect.collidepoint(event.pos):
                        running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
