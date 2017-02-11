# CheckersAI
A Checkers playing Artificial Intelligence, utilizing multiple game playing AI techniques.


## Quick Start
Download this repository:
```
git clone https://github.com/pWhitS/CheckersAI.git
```
Or download the ZIP file above and extract it.






## How does it work?
This repository actually contains [eventually...] two AI checkers players. At a basic level, the first AI player uses an Alpha-Beta search tree to select moves by looking several steps ahead in the game.  The second AI player [will] uses a Monte-Carlo search tree to pseudorandomly simulate possible game play, and pick the next move based on these simulations. 

## Alpha-Beta Player
The Alpha-Beta player comes in two varieties, using two distinct techniques. One utilizes multiprocessing to search multiple branches in the game tree simultaneously. The other uses a simpler, single process, to build the whole game search tree. When played against one another, the multiprocess player typically searches one layer deeper in the tree than the single process player.
