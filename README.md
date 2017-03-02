# CheckersAI
A Checkers playing Artificial Intelligence, utilizing multiple game playing AI techniques.
<br>
Skip to the bottom for a <i>quick start</i> guide to play.

## How does it work?

The AI player can take advantage of two different AI algorithms. The first is Alpha-Beta Tree Search with a board position scoring heuristic. The second is Monte-Carlo Tree Search (MCTS) with Upper Confidence Bounds (UCB). In their current implementations, Alpha-Beta is much more efficient and is a much stronger player. 

### Alpha-Beta

Using Minimax with Alpha-Beta pruning, the tree search was able to achieve tree depths between 5 and 10 within 15 seconds. The achievable depth varies throughout the game because the branching factor fluctuates. 

#### Multi-Processing 

There is an implementation of Alpha-Beta taking advantage of multiprocessing. It doesn't seem to make a big difference in tree search depths. 

### MCTS


### Future Implementations...

I am looking into adapting a Convolution Neural Network (CNN) to assist MCTS, or Alpha-Beta, or to play entirely on it own. The plan would be to use Supervised training with the board scoring heuristic as the training metric. After the CNN converges on the Alpha-Beta player's skill level, Reinforcement Learning would be used to further improve the CNN. 


## Quick Start
Download this repository:
```
git clone https://github.com/pWhitS/CheckersAI.git
```
Alternatively, download the ZIP file above and extract it.
<br>

Run the game in a terminal simple by using:
```
$ python run.py
```
The game is setup to run by default as, <i>Human player vs. AI player</i>
<br>

<b>How to Play:</b> <br>
The AI player moves on its own. You just have to wait for it to finish thinking. <br>

For human players, when you are done thinking, first select the piece you want to move, then select the move location. Standard checkers moving rules apply. <br>
<br>
To select a piece or a move location input a column-row pair, such as: <i>A5, C7, H6, or D0</i>. You will be prompted for each as shown below. 
<br>
<img src="https://raw.githubusercontent.com/pWhitS/CheckersAI/master/images/start.png" height=35% width=35%/>

After each move, the updated board is printed. <br>

A jump can be performed by simply selecting the location beyond the jump piece. For example: D4 to B2, as in the example below. Also, multiple jumps of arbitrary length can be achieved by inputing multiple, space delimited, move locations. An example is shown below as well. <br>

<b>Single Jump:</b> <br>
<img src="https://raw.githubusercontent.com/pWhitS/CheckersAI/master/images/jump.png" height=35% width=35%/>
<br>

<b>Multiple (Triple) Jump: </b>  <br>
<img src="https://raw.githubusercontent.com/pWhitS/CheckersAI/master/images/triple_jump.png" height=35% width=35%/>
<br><br>
<b>How to Win, Lose, or Draw:</b><br>
1. Capture all of your opponent's pieces.<br>
2. Force your opponent to have no legal remaining moves.<br>
3. A draw occurs after no captures have taken place for 40 moves. <br>


