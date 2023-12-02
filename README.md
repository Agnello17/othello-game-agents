# othello-game-agents
Code for Minimax and Greedy game agents to play Othello.
Developed with Python 3.11

# Agent Overview
This project contains two different agents to play Othello. The first agent is the Greedy agent, and the second is the Minimax agent. 

The Greedy plays Othello using a greedy algorithm to find the best move at each turn. The algorithm looks at all legal moves and chooses the move that will capture the most opponent pieces on that turn. The code for this agent can be found in client_greedy.py.

The Minimax agent plays Othello using the minimax algorithm to find the best move at each turn. The algorithm searches all legal moves until a certain depth of turns into the future and scores a move by counting player piece surplus along with whether the game is won, lost, or tied. The code for this agent can be found in client_minimax.py.

# Using Agents
Either agent can be used by starting the game server provided by Atomic Object and running the Python file relevant to a particular agent. The agent will continue playing games until the game server is shut down. 

# Agent Performance
Both the Greedy agent and the Minimax agent will beat a random agent around 75%-80% of the time, but the Minimax agent is significantly slower compared to the Greedy agent due to its high computation cost relative to the Greedy agent. The win rate of the Minimax agent could be significantly improved by increasing the maximum depth. However, since increasing the depth increases computation cost exponentially, the depth can only be increased so far on any particular machine before the Minimax agent loses due to the time constraint. The maximum possible depth depends on the machine running the agent.
