# AI Connect 4
We created a 2 player turn based Connect 4 game with an AI agent using Minimax with alpha-beta pruning and the Gemini AI api that tells you the next best move using python and the pygame library.

## How to setup/run
Install the pygame library:
```plaintext
pip install pygame
```

Install Gemini AI:
```plaintext
pip install google-genai
```

Make sure to get an API key from the Google AI Studio website:

https://aistudio.google.com/

Ensure all the files (```board.py```, ```ai_agent.py```, ```gemini_agent.py```) are all in the same directory

Run ```board.py``` in the terminal

## Features
- You can choose the grid size before the game starts
- You can alternate between the minimax and gemini AI's by clicking "Minimax" at the top
- Click "Get AI Suggestion" to get the AI's suggestion on the best move you should make
- You can reset the game if you click the "Restart" button in the top right corner
