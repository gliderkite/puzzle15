puzzle15
======
A Python module that allows to solve the [15-puzzle](http://en.wikipedia.org/wiki/15_puzzle).


How to Play
======
The 15-puzzle is a sliding puzzle that consists of a frame of numbered square tiles in random order with one tile missing. The puzzle also exists in other sizes, particularly the smaller 8-puzzle.
The object of the puzzle is to place the tiles in order by making sliding moves that use the empty space.

![puzzle15 image](http://i59.tinypic.com/106zsli.jpg)


Requirements
======
In order to play the 15-puzzle you have to download and install [Python (2.X version)](https://www.python.org/downloads/) and the [wxPython](http://www.wxpython.org/download.php) GUI library.


Launch the game
======
Once you have correctly installed wxPython you can simply run the script by typing (on Unix-based systems):
```bash
./wxPuzzle15.py
```

Use the puzzle15 module
======
If you just want to use the puzzle15 module, that allows you to solve the puzzle, you have to
```python
import puzzle15
```
and use its functions, for example:
```python
# get a random configuration of a solvable 15-puzzle (a 4x4 grid)
# a valid configuration is a list of integers between 1 and the total
# number of tiles (16 for the 15-puzzle, the "empty cell" is included)
puzzle = puzzle15.spuzzle(size=4)
# find an optimal solution
# that is, the sequence of moves made to solve the puzzle
steps = puzzle15.solve(puzzle)
```
Other valid configurations are the 8-puzzle (3x3 grid) and the 3-puzzle (2x2 grid). Moreover, you can specify a lower bound which, if reached, stops the search; or you can set a function that will be called every time a new solution is found:
```python
# find the first solution with a number of moves less or equal to the lower bound
steps = puzzle15.solve(puzzle, lowerBound=80)

from __future__ import print_function   # python 2.X
display = lambda s: print(s)
# solve the puzzle and call "display" every time new solution is found
steps = puzzle15.solve(puzzle, solutionFound=display)
```
If the lower bound specified is equal to -1 the function solve returns the first solution found.