"""
This module tests the performance of different AI agents in a Connect Four game.
"""
import time
import random
import copy
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import sys

# Import the AI agents
import ai_agent
import ai_agent_minimax_only
import gemini_agent

# Constants
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

class AgentTester:
    def __init__(self, board_sizes=[(6, 7)], num_games=10, max_depth=4):
        """
        Initialize the agent tester with configuration parameters.
        
        Args:
            board_sizes: List of tuples (rows, columns) to test.
            num_games: Number of games to run per matchup.
            max_depth: Maximum search depth for minimax algorithms.
        """
        self.board_sizes = board_sizes
        self.num_games = num_games
        self.max_depth = max_depth
        
        # Initialize agents - Alpha-Beta, Minimax, and Gemini.
        self.agents = {
            "Alpha-Beta": self._alpha_beta_move,
            "Minimax": self._minimax_move,
            "Gemini": self._gemini_move
        }
        
        # Metrics storage
        self.metrics = {
            "wins": defaultdict(int),
            "execution_time": defaultdict(list),
            "nodes_evaluated": defaultdict(list),
            "pruning_efficiency": defaultdict(float),
        }
        
        # Reset pruning counters for accurate measurement.
        if hasattr(ai_agent.minimax, 'prune_count'):
            ai_agent.minimax.prune_count = 0
        if hasattr(ai_agent_minimax_only.minimax, 'prune_count'):
            ai_agent_minimax_only.minimax.prune_count = 0

    def _create_board(self, rows, cols):
        """Create an empty board with specified dimensions."""
        return [[EMPTY for _ in range(cols)] for _ in range(rows)]

    def _is_valid_location(self, board, col):
        """Check if a column has space for another piece."""
        return board[0][col] == EMPTY

    def _get_valid_locations(self, board):
        """Get all valid column locations."""
        cols = len(board[0])
        return [col for col in range(cols) if self._is_valid_location(board, col)]

    def _get_next_open_row(self, board, col):
        """Find the next open row in the specified column."""
        rows = len(board)
        for r in range(rows-1, -1, -1):
            if board[r][col] == EMPTY:
                return r
        return None

    def _drop_piece(self, board, row, col, piece):
        """Drop a piece into the board."""
        board[row][col] = piece

    def _winning_move(self, board, piece):
        """Check if the last move resulted in a win."""
        rows = len(board)
        cols = len(board[0])

        # Check horizontal
        for r in range(rows):
            for c in range(cols - 3):
                if all(board[r][c + i] == piece for i in range(4)):
                    return True

        # Check vertical
        for c in range(cols):
            for r in range(rows - 3):
                if all(board[r + i][c] == piece for i in range(4)):
                    return True

        # Check positively sloped diagonals
        for r in range(rows - 3):
            for c in range(cols - 3):
                if all(board[r + i][c + i] == piece for i in range(4)):
                    return True

        # Check negatively sloped diagonals
        for r in range(3, rows):
            for c in range(cols - 3):
                if all(board[r - i][c + i] == piece for i in range(4)):
                    return True

        return False

    def _alpha_beta_move(self, board, piece):
        """Get move using Alpha-Beta agent and measure performance."""
        start_time = time.time()
        
        if hasattr(ai_agent.minimax, 'prune_count'):
            ai_agent.minimax.prune_count = 0
        
        col, _ = ai_agent.get_best_move(board, self.max_depth, piece)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        prune_count = getattr(ai_agent.minimax, 'prune_count', 0)
        self.metrics["execution_time"]["Alpha-Beta"].append(execution_time)
        self.metrics["nodes_evaluated"]["Alpha-Beta"].append(prune_count)
        
        total_possible_nodes = sum(7**d for d in range(1, self.max_depth+1))
        pruning_efficiency = 1 - (prune_count / total_possible_nodes if total_possible_nodes > 0 else 0)
        self.metrics["pruning_efficiency"]["Alpha-Beta"] = pruning_efficiency
        
        return col

    def _minimax_move(self, board, piece):
        """Get move using Minimax agent and measure performance."""
        start_time = time.time()
        
        if hasattr(ai_agent_minimax_only.minimax, 'prune_count'):
            ai_agent_minimax_only.minimax.prune_count = 0
        
        col, _ = ai_agent_minimax_only.get_best_move(board, self.max_depth, piece)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        call_count = getattr(ai_agent_minimax_only.minimax, 'prune_count', 0)
        self.metrics["execution_time"]["Minimax"].append(execution_time)
        self.metrics["nodes_evaluated"]["Minimax"].append(call_count)
        
        return col

    def _gemini_move(self, board, piece):
        """
        Get move using Gemini AI API.
        The 'piece' parameter is ignored since Gemini uses the board state only.
        """
        start_time = time.time()
        col = gemini_agent.get_gemini_move(board)
        end_time = time.time()
        execution_time = end_time - start_time
        self.metrics["execution_time"]["Gemini"].append(execution_time)
        # Gemini does not provide node count or pruning efficiency.
        self.metrics["nodes_evaluated"]["Gemini"].append(0)
        self.metrics["pruning_efficiency"]["Gemini"] = 0
        return col

    def run_game(self, agent1, agent2, rows, cols, starting_player, agent1_piece, agent2_piece):
        """
        Run a single game between two agents with given piece assignments.
        
        Args:
            agent1: Name of the first agent.
            agent2: Name of the second agent.
            rows: Number of board rows.
            cols: Number of board columns.
            starting_player: Who starts (1 for agent1, 2 for agent2).
            agent1_piece: Piece for agent1 (PLAYER_PIECE or AI_PIECE).
            agent2_piece: Piece for agent2.
        Returns:
            1 if the agent using the piece assigned to player 1 wins,
            2 if the agent using the piece assigned to player 2 wins,
            0 for tie.
        """
        board = self._create_board(rows, cols)
        current_player = starting_player
        
        while True:
            valid_locations = self._get_valid_locations(board)
            if not valid_locations:
                return 0  # Tie
            
            if current_player == 1:
                piece = agent1_piece
                agent_name = agent1
            else:
                piece = agent2_piece
                agent_name = agent2
                
            col = self.agents[agent_name](board, piece)
            
            row = self._get_next_open_row(board, col)
            if row is not None:
                self._drop_piece(board, row, col, piece)
                if self._winning_move(board, piece):
                    self.metrics["wins"][agent_name] += 1
                    return current_player
                current_player = 3 - current_player
            else:
                opponent_agent = agent2 if current_player == 1 else agent1
                self.metrics["wins"][opponent_agent] += 1
                return 3 - current_player

    def run_tournament(self):
        """
        Run a tournament between all agents for all board sizes using alternating starting players and piece assignments.
        This will now include Gemini in addition to Alpha-Beta and Minimax.
        """
        agent_names = list(self.agents.keys())
        results = {}
        
        print("Starting tournament...")
        
        for rows, cols in self.board_sizes:
            print(f"\nTesting board size: {rows}x{cols}")
            results[(rows, cols)] = {}
            
            for i, agent1 in enumerate(agent_names):
                for agent2 in agent_names[i+1:]:
                    print(f"  {agent1} vs {agent2}: ", end="")
                    agent1_wins = 0
                    agent2_wins = 0
                    ties = 0
                    
                    for game in range(self.num_games):
                        # Alternate starting player.
                        starting_player = 1 if game % 2 == 0 else 2
                        # Alternate piece assignment so each agent plays both sides.
                        if game % 2 == 0:
                            a1_piece, a2_piece = PLAYER_PIECE, AI_PIECE
                        else:
                            a1_piece, a2_piece = AI_PIECE, PLAYER_PIECE
                            
                        winner = self.run_game(agent1, agent2, rows, cols, starting_player, a1_piece, a2_piece)
                        if winner == 1:
                            agent1_wins += 1
                        elif winner == 2:
                            agent2_wins += 1
                        else:
                            ties += 1
                    
                    print(f"{agent1_wins}-{agent2_wins}-{ties}")
                    results[(rows, cols)][(agent1, agent2)] = (agent1_wins, agent2_wins, ties)
        
        return results

    def calculate_metrics(self):
        """Calculate comprehensive metrics from the raw data."""
        agent_names = list(self.agents.keys())
        metrics_summary = {}
        total_games_per_agent = self.num_games * len(self.board_sizes) * (len(agent_names) - 1)
        
        for agent in agent_names:
            win_percentage = (self.metrics["wins"][agent] / total_games_per_agent * 100
                              if total_games_per_agent > 0 else 0)
            metrics_summary[agent] = {
                "win_percentage": win_percentage,
                "avg_execution_time": (sum(self.metrics["execution_time"][agent]) / len(self.metrics["execution_time"][agent])
                                         if self.metrics["execution_time"][agent] else 0),
                "pruning_efficiency": self.metrics["pruning_efficiency"][agent] if agent in self.metrics["pruning_efficiency"] else 0,
                "total_nodes_evaluated": sum(self.metrics["nodes_evaluated"][agent]) if agent in self.metrics["nodes_evaluated"] else 0,
            }
            
        return metrics_summary

    def generate_report(self, tournament_results, metrics_summary):
        """Generate a comprehensive report of the tournament results and print performance stats."""
        agent_names = list(self.agents.keys())
        
        print("\n" + "=" * 50)
        print("TOURNAMENT RESULTS".center(50))
        print("=" * 50)
        
        for (rows, cols), matchups in tournament_results.items():
            print(f"\nBoard Size: {rows}x{cols}")
            for (agent1, agent2), (a1_wins, a2_wins, ties) in matchups.items():
                print(f"  {agent1} vs {agent2}: {a1_wins}-{a2_wins}-{ties}")
        
        print("\n" + "=" * 50)
        print("PERFORMANCE METRICS".center(50))
        print("=" * 50)
        
        for agent, metrics in metrics_summary.items():
            print(f"\n{agent}:")
            print(f"  Win Percentage: {metrics['win_percentage']:.2f}%")
            print(f"  Average Execution Time: {metrics['avg_execution_time']:.6f} seconds")
            print(f"  Total Nodes Evaluated: {metrics['total_nodes_evaluated']}")
            if agent == "Alpha-Beta":
                print(f"  Pruning Efficiency: {metrics['pruning_efficiency']:.2%}")
        
        print("\n" + "=" * 50)
        print("FINAL PERFORMANCE STATS".center(50))
        print("=" * 50)
        for agent, metrics in metrics_summary.items():
            print(f"{agent} Summary:")
            print(f"  Win %: {metrics['win_percentage']:.2f}%")
            print(f"  Avg Time per Move: {metrics['avg_execution_time']:.6f} sec")
            print(f"  Nodes Evaluated: {metrics['total_nodes_evaluated']}")
            if agent == "Alpha-Beta":
                print(f"  Pruning Efficiency: {metrics['pruning_efficiency']:.2%}")
            print()
        
        self.plot_metrics(metrics_summary)

    def plot_metrics(self, metrics_summary):
        """Plot the metrics for visual comparison."""
        agent_names = list(metrics_summary.keys())
        
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Minimax vs Alpha-Beta vs Gemini Performance Comparison', fontsize=16)
        
        win_percentages = [metrics_summary[agent]["win_percentage"] for agent in agent_names]
        axs[0, 0].bar(agent_names, win_percentages)
        axs[0, 0].set_title('Win Percentage')
        axs[0, 0].set_ylabel('Percentage (%)')
        
        exec_times = [metrics_summary[agent]["avg_execution_time"] for agent in agent_names]
        axs[0, 1].bar(agent_names, exec_times)
        axs[0, 1].set_title('Average Execution Time')
        axs[0, 1].set_ylabel('Time (seconds)')
        
        nodes_evaluated = [metrics_summary[agent]["total_nodes_evaluated"] for agent in agent_names]
        axs[1, 0].bar(agent_names, nodes_evaluated)
        axs[1, 0].set_title('Total Nodes Evaluated')
        axs[1, 0].set_ylabel('Nodes Count')
        
        pruning = [metrics_summary[agent].get("pruning_efficiency", 0) for agent in agent_names]
        axs[1, 1].bar(agent_names, pruning)
        axs[1, 1].set_title('Pruning Efficiency')
        axs[1, 1].set_ylabel('Efficiency (0-1)')
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig('minimax_vs_alphabeta_comparison.png')
        plt.show()

def run_simulation():
    """Run the full simulation with interactive configuration."""
    board_sizes = [(6, 7)]
    num_games = 1
    max_depth = 5
    
    if len(sys.argv) > 1:
        try:
            num_games = int(sys.argv[1])
        except ValueError:
            print(f"Invalid number of games: {sys.argv[1]}, using default: {num_games}")
    
    if len(sys.argv) > 2:
        try:
            max_depth = int(sys.argv[2])
        except ValueError:
            print(f"Invalid max depth: {sys.argv[2]}, using default: {max_depth}")
    
    tester = AgentTester(board_sizes, num_games, max_depth)
    tournament_results = tester.run_tournament()
    metrics_summary = tester.calculate_metrics()
    tester.generate_report(tournament_results, metrics_summary)

if __name__ == "__main__":
    run_simulation()
