from checkers import *
from util import *
from AlphaBetaAI import *
from AlphaBetaMultiProcAI import *  # NOT UPDATED, PROBABLY BUGGY
from MonteCarloAI import * 


################
# INITIALIZE THE AI PLAYERS
#
# board: instance of the Checkers game board
# depth: The depth of the game tree to search
# eval_fn: The evaluation function to use
# timeout: The maximum time to search the game tree. Returns best answer on timeout.
################

# BASIC AI PLAYERS
# Anything more than 3 is risky (very slow) in the mid game...
basic_player = lambda board: alpha_beta(board, depth=4, eval_fn=basic_evaluate)

# Cuts off search at timeout
progressive_player = lambda board: progressive_deepener(board,
													  search_fn=alpha_beta,
													  eval_fn=basic_eval_memoized,
													  get_next_moves_fn=get_ordered_moves_helper,
													  timeout=10)

# Longer times are necessary to get good sampling
# Current implimentation is slow and not very good
mcts_player = lambda board: monte_carlo_search(board, get_all_next_moves, timeout=15)


# ADVANCED AI PLAYERS
# Combinations of techniques. Very experimental.

# Nothing here yet...


## PLAY AGAINST THE AI PLAYERS
# run_game(human_player, basic_player)
# run_game(basic_player, human_player)

run_game(human_player, progressive_player)
# run_game(progressive_player, human_player)


## PLAY AI AGAINST THEMSELVES
# run_game(progressive_player, basic_player)
# run_game(basic_player, progressive_player)
# run_game(progressive_player, progressive_player)




