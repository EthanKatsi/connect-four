"""
This is the code that implements the AI agent to predict the next best move per each turn using the Gemini AI api
"""
from google import genai
from google.genai import types

API_KEY = "AIzaSyCozuD6q9Q2uyAKlMi3f9fWN7v_0wataZY"
MODEL = "gemini-2.0-flash"

# converts the board in board.py to a string so the gemini ai can read it well
def board_to_string(board):
    symbol_map = {0: ".", 1: "X", 2: "O"}  # X is player 1 and O is player 2
    lines = []
    for row in board:
        line = " ".join(symbol_map[cell] for cell in row)
        lines.append(line)
    return "\n".join(lines)

# uses gemini ai to generate the best move on the board
def get_gemini_move(board):
    client = genai.Client(api_key = API_KEY)
    board_str = board_to_string(board)
    rows = len(board)
    columns = len(board[0])
    prompt = (
        f"You are a Connect 4 expert. The board is a grid with {rows} rows and {columns} columns. "
        "Given the current board state below, please return only the best column number (0-indexed) to drop the next piece. "
        "Do not include any extra text.\n\n"
        f"{board_str}"
    )
    
    contents = [
        types.Content(
            role = "user",
            parts = [types.Part.from_text(text = prompt)]
        )
    ]
    
    generate_content_config = types.GenerateContentConfig(
        response_mime_type = "text/plain",
    )

    # gets the answer the ai generates as a text
    for chunk in client.models.generate_content_stream(
        model = MODEL,
        contents = contents,
        config = generate_content_config,
    ):
        move_text = chunk.text.strip()
        try:
            move = int(move_text)
            return move
        except ValueError:
            print("Error parsing Gemini move output:", move_text)
            return None
    return None
