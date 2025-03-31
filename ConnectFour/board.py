"""
This is the code that implements all the connect 4 code other than the AI agent
"""
import pygame
import sys
import ai_agent
import ai_agent_minimax_only
import gemini_agent

# default slider ranges
default_rows = 6
default_columns = 7
squaresize = 80
top_bar_height = 120

# constants
row_count = default_rows
column_count = default_columns
width = column_count * squaresize
height = top_bar_height + row_count * squaresize
size = (width, height)
radius = int(squaresize / 2 - 5)
blue = (0, 0, 255)
black = (0, 0, 0)
red = (255, 0, 0)
yellow = (255, 255, 0)
grey = (128, 128, 128)
purple = (255, 130, 251)

selected_ai = "Alpha-Beta"
ai_map = {
    "Alpha-Beta": ai_agent,
    "Minimax": ai_agent_minimax_only,
    "Gemini": gemini_agent
}

# before the game starts, asks the user what size grid they would like to use
def choose_grid_size():
    valid_grid_sizes = [(4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10)]
    current_index = 2 # default grid size is 6, 7 (2nd index)
    screen = pygame.display.set_mode((700, 500))
    pygame.display.set_caption("Choose Grid Size")
    font = pygame.font.SysFont("arial", 32)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_index = (current_index - 1) % len(valid_grid_sizes)
                elif event.key == pygame.K_RIGHT:
                    current_index = (current_index + 1) % len(valid_grid_sizes)
                elif event.key == pygame.K_RETURN:
                    return valid_grid_sizes[current_index]

        rows, cols = valid_grid_sizes[current_index]
        screen.fill(black)
        screen.blit(font.render(f"Grid Size: {rows} x {cols}", True, yellow), (50, 100))
        screen.blit(font.render("Use LEFT/RIGHT arrows to choose, ENTER to start", True, purple), (20, 150))
        pygame.display.update()

def create_board():
    return [[0 for _ in range(column_count)] for _ in range(row_count)]

# draws the connect 4 board - O(m*n)
def draw_board(board, screen):
    for c in range(column_count):
        for r in range(row_count):
            pygame.draw.rect(screen, blue, (c * squaresize, r * squaresize + top_bar_height, squaresize, squaresize))
            color = black if board[r][c] == 0 else red if board[r][c] == 1 else yellow
            pygame.draw.circle(screen, color, (int(c * squaresize + squaresize / 2), int(r * squaresize + top_bar_height + squaresize / 2)), radius)
    pygame.display.update()

# bar at the top of the screen showing player turn and restart button
def top_bar(screen, current_player, selected_ai):
    pygame.draw.rect(screen, black, (0, 0, width, top_bar_height))
 
    # displays whos turn it is in the top left corner
    font = pygame.font.SysFont("arial", 36)
    player_label = font.render(f"Player {current_player}'s Turn", True, red if current_player == 1 else yellow)
    label_rect = player_label.get_rect(center=(width // 2, 30))
    screen.blit(player_label, label_rect)

     # ai suggestion button beside restart button
    button_font = pygame.font.SysFont("arial", 22)
    
     # button to change which ai you use (minimax, Alphha-Beta or gemini) - click the button to change which ai you are using
    ai_select_label = button_font.render(selected_ai, True, purple)
    ai_label = button_font.render("Get AI Suggestion", True, purple)
   
    restart_label = button_font.render("Restart", True, yellow)

    #calculates positions and draw buttons with grey backgrounds
    total_width = ai_select_label.get_width() + ai_label.get_width() + restart_label.get_width() + 80
    start_x = (width - total_width) // 2
    y = top_bar_height - restart_label.get_height() - 20

    ai_select_bg = pygame.Rect(start_x - 10, y - 5, ai_select_label.get_width() + 20, ai_select_label.get_height() + 10)
    pygame.draw.rect(screen, grey, ai_select_bg)
    screen.blit(ai_select_label, (start_x, y))


    ai_x = start_x + ai_select_label.get_width() + 30
    ai_bg = pygame.Rect(ai_x - 10, y - 5, ai_label.get_width() + 20, ai_label.get_height() + 10)
    pygame.draw.rect(screen, grey, ai_bg)
    screen.blit(ai_label, (ai_x, y))


    restart_x = ai_x + ai_label.get_width() + 30
    restart_bg = pygame.Rect(restart_x - 10, y - 5, restart_label.get_width() + 20, restart_label.get_height() + 10)
    pygame.draw.rect(screen, grey, restart_bg)     # grey rectangle behind restart button
    screen.blit(restart_label, (restart_x, y))

    pygame.display.update()
    return restart_bg, ai_bg, ai_select_bg

# displays the player who won the game, restart button, and exit button
def winning_move(board, piece):
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

def main():
    global row_count, column_count, width, height, size, radius, selected_ai
    pygame.init()
    
    #choose grid size and calculate window dimensions and piece radius
    row_count, column_count = choose_grid_size()
    width, height = column_count * squaresize, top_bar_height + row_count * squaresize
    size = (width, height)
    radius = int(squaresize / 2 - 5)

    # sets up the display window and title
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Connect 4")

    # creates and draws the initial game board
    board = create_board()
    draw_board(board, screen)
    current_player = 1

    # draws the top control bar (restart, AI suggestion, AI select buttons)
    restart_button_rect, ai_suggestion_rect, ai_select_rect = top_bar(screen, current_player, selected_ai)
    game_over = False

    while True:
        for event in pygame.event.get():
            # handles quitting the game
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # handles mouse click events
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                # resets the board and game state
                if restart_button_rect.collidepoint(x, y):
                    board = create_board()
                    draw_board(board, screen)
                    current_player = 1
                    game_over = False
                    restart_button_rect, ai_suggestion_rect, ai_select_rect = top_bar(screen, current_player, selected_ai)
                    continue

                # toggles the selected AI algorithm
                if ai_select_rect.collidepoint(x, y):
                    selected_ai = ("Minimax" if selected_ai == "Alpha-Beta" else "Gemini" if selected_ai == "Minimax" else "Alpha-Beta")
                    restart_button_rect, ai_suggestion_rect, ai_select_rect = top_bar(screen, current_player, selected_ai)
                    continue

                # displays the AI’s recommended move
                if ai_suggestion_rect.collidepoint(x, y):
                    agent = ai_map[selected_ai]
                    if selected_ai == "Gemini":
                        col = agent.get_gemini_move(board)
                    else:
                        piece = agent.PLAYER_PIECE if current_player == 1 else agent.AI_PIECE
                        col, _ = agent.get_best_move(board, 5, piece)
                    if col is not None:
                        # gets the next available row for the chosen column
                        row = agent.get_next_open_row(board, col) if selected_ai != "Gemini" else next((r for r in range(row_count - 1, -1, -1) if board[r][col] == 0), None)
                        if row is not None:
                            # draws a circle to indicate the AI’s suggestion
                            pygame.draw.circle(screen, purple, (int(col * squaresize + squaresize / 2), int(row * squaresize + top_bar_height + squaresize / 2)), radius)
                            pygame.display.update()

                # processes a click on the board area (below the top bar)
                if y >= top_bar_height:
                    col = x // squaresize
                    # drops the piece in the lowest available row for that column
                    for row in range(row_count - 1, -1, -1):
                        if board[row][col] == 0:
                            board[row][col] = current_player
                            draw_board(board, screen)
                            # checks if the current move wins the game
                            if winning_move(board, current_player):
                                font = pygame.font.SysFont("arial", 60)
                                label = font.render(f"Player {current_player} wins!", True, red if current_player == 1 else yellow)
                                rect = label.get_rect(center=(width // 2, height // 2))
                                bg_rect = rect.inflate(20, 20)
                                pygame.draw.rect(screen, black, bg_rect)
                                screen.blit(label, rect)
                                pygame.display.update()
                                game_over = True
                            else:
                                # switches players and update the top bar for the new turn
                                current_player = 2 if current_player == 1 else 1
                                restart_button_rect, ai_suggestion_rect, ai_select_rect = top_bar(screen, current_player, selected_ai)
                            break

        # if the game is over, wait 3 seconds and then restart the game
        if game_over:
            pygame.time.wait(3000)
            board = create_board()
            draw_board(board, screen)
            current_player = 1
            game_over = False
            restart_button_rect, ai_suggestion_rect, ai_select_rect = top_bar(screen, current_player, selected_ai)

# run the main function if this script is executed directly
if __name__ == "__main__":
    main()
