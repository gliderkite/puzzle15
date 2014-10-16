#! /usr/bin/env python


from random import shuffle
from math import sqrt
from functools import total_ordering
from heapq import heappop, heappush



def dist(puzzle, idx1, idx2):
  """Get the distance between two cells (as the number of moves)."""
  size = int(sqrt(len(puzzle)))
  # difference of row and column number
  rdiff = abs((idx1 // size) - (idx2 // size))
  cdiff = abs((idx1 % size) - (idx2 % size))
  return rdiff + cdiff


def hamming_dist(puzzle):
  """Return the number of misplaced tiles."""
  return len([i for i, v in enumerate(puzzle) if v != i+1 and v != len(puzzle)])


def manhattan_dist(puzzle):
  """Return the sum of the distances of the tiles from their goal positions."""
  return sum([dist(puzzle, i, v-1) for i, v in enumerate(puzzle) if v != len(puzzle)])


def is_solvable(puzzle):
  """Check if the puzzle is solvable."""
  # count the number of inversions
  inversions = 0
  for i, v in [(i, v) for i, v in enumerate(puzzle) if v != len(puzzle)]:
    j = i + 1
    while j < len(puzzle):
      if puzzle[j] < v:
        inversions += 1
      j += 1
  # check if the puzzle is solvable
  size = int(sqrt(len(puzzle)))
  # grid width is odd and number of inversion even -> solvable
  if size % 2 != 0 and inversions % 2 == 0:
    return True
  # grid width is even
  if size % 2 == 0:
    emptyrow = size - puzzle.index(len(puzzle)) // size
    return (emptyrow % 2 != 0) == (inversions % 2 == 0)
  return False


def is_solved(puzzle):
  """Return True is the puzzle is solved, False otherwise."""
  # simply check if the list is sorted
  return all(puzzle[i] < puzzle[i + 1] for i in range(len(puzzle) - 1))




def _neighbors(puzzle, location):
  """Get the indexes of the neighbors cells."""
  size = int(sqrt(len(puzzle)))
  #  above cell
  if location - size >= 0:
    yield (location - size)
  # left cell
  if (location % size) - 1 >= 0:
    yield (location - 1)
  # right cell
  if (location % size) + 1 < size:
    yield (location + 1)
  # below cell
  if location + size < len(puzzle):
    yield (location + size)


def _swap(puzzle, moves, x, y):
  """Swap two cells of the puzzle and store the move."""
  # the move has to be (non empty cell, empty cell)
  x, y = (x, y) if puzzle[y] == len(puzzle) else (y, x)
  puzzle[x], puzzle[y] = puzzle[y], puzzle[x]
  moves.append((x, y))


def _hitch(puzzle, location, immovables):
  """Get the index of the cell that blocks the cell in location from
  its final position, otherwise returns None."""
  dest = puzzle[location] - 1
  close = [i for i in _neighbors(puzzle, location)
           if puzzle[i] not in immovables and puzzle[i] != len(puzzle)
           and dist(puzzle, i, dest) < dist(puzzle, location, dest)]
  if close:
    # returns the hitch with the minimum distance from the final position
    return min(close, key=lambda i: dist(puzzle, i, dest))


def _approach(puzzle, moves, location):
  """Check if the empty cell is one of the neighbors of the cell in location,
  if the empty cell is closer to the cell final position _swap the empty cells
  with the cell in location."""
  empty = puzzle.index(len(puzzle))
  # if the empty cell is between the cell neighbors
  if empty in _neighbors(puzzle, location):
    dest = puzzle[location] - 1
    # compare distance between actual location / empty cell and final position
    if dist(puzzle, empty, dest) < dist(puzzle, location, dest):
      # approach the cell in location
      _swap(puzzle, moves, empty, location)
      return True
  return False


def _is_movable(puzzle, location):
  """Check if the empty cell is one of the neighbors of the cell in location."""
  return puzzle.index(len(puzzle)) in _neighbors(puzzle, location)


def _slide_empty_rec(puzzle, moves, location, immovables):
  """Apply a recursive algorithm to slide the empty cell."""
  # if this cell can't be moved try to move one of its neighbor
  if not _is_movable(puzzle, location):
    immovables.add(puzzle[location])
    # for each neighbors that could be moved (prevent infinite loops)
    close = [x for x in _neighbors(puzzle, location) 
             if puzzle[x] not in immovables]
    # first the cells closer to the empty one (shortest path)
    close.sort(key=lambda e: dist(puzzle, e, puzzle.index(len(puzzle))))
    for n in close:
      if _slide_empty_rec(puzzle, moves, n, immovables):
        # now the empty cell is a neighbor of the cell in location
        _slide_empty_rec(puzzle, moves, location, immovables)
        return True
    return False
  else:
    immovables.discard(puzzle[location])
    # swap with the empty cell
    _swap(puzzle, moves, puzzle.index(len(puzzle)), location)
  return True


def _slide_empty(puzzle, moves, location, immovables=None):
  """Replace the cell in location with the empty one."""
  # init the set of the cells that can't be moved
  unmov = set(immovables) if immovables else set()
  return _slide_empty_rec(puzzle, moves, location, unmov)


def _place(puzzle, moves, piece, immovables=None):
  """Try to place a specific piece of the puzzle."""
  idx = puzzle.index(piece)
  unmovables = immovables or set([i + 1 for i in range(piece)])
  # while the piece is not in its final position
  while idx != piece - 1:
    # try a simple approach swapping with the empty cell
    if not _approach(puzzle, moves, idx):
      # search the hitch
      h = _hitch(puzzle, idx, unmovables)
      # tries to slide the empty cell in place of the hitch
      if not _slide_empty(puzzle, moves, h, unmovables):
        return False
    # update piece location
    idx = puzzle.index(piece)
  return True


def _place_3(puzzle8, moves):
  """Place the piece number 3 in a puzzle 8."""
  if _place(puzzle8, moves, 3):
    return True
  # check if the piece is under its final location
  if puzzle8.index(3) != 5:
    return False
  # place the empty cell in the first location
  _slide_empty(puzzle8, moves, 0, set((2, 3)))
  # place 3 in its final location
  _slide_empty(puzzle8, moves, 5, set((puzzle8[4],)))
  # place 2 and 1
  _slide_empty(puzzle8, moves, 0, set((1, 3)))
  _swap(puzzle8, moves, 0, 3)
  return True


def _place_5(puzzle8, moves):
  """Place the piece number 5 in a puzzle 8."""
  if _place(puzzle8, moves, 5):
    return True
  # check if the piece is under its final location
  if puzzle8.index(5) != 7:
    return False
  # place the empty cell above 5
  _slide_empty(puzzle8, moves, 4, set((5,)))
  # approach 5 to its final location
  _swap(puzzle8, moves, 4, 7)
  # rotate the bottom right square once
  _slide_empty(puzzle8, moves, 5, set((5,)))
  _swap(puzzle8, moves, 5, 4)
  # place the empty cell in the bottom left corner
  _slide_empty(puzzle8, moves, 6, set((puzzle8[7],)))
  # place 5 and 6
  _slide_empty(puzzle8, moves, 4, set((4,)))
  _swap(puzzle8, moves, 5, 4)
  _swap(puzzle8, moves, 5, 8)
  return True


def _place_6(puzzle8, moves):
  """Place the piece number 6 in a puzzle 8."""
  if _place(puzzle8, moves, 6):
    return True
  # check the location of 6
  location = puzzle8.index(6)
  if location == 8:
    # place the empty cell in the first location
    _slide_empty(puzzle8, moves, 3, set((5, 6)))
    # place 6 in its final location
    _slide_empty(puzzle8, moves, 8, set((puzzle8[7],)))
    # place 5 and 4
    _slide_empty(puzzle8, moves, 4, set((6,)))
    _swap(puzzle8, moves, 3, 4)
    _swap(puzzle8, moves, 3, 6)
  elif location == 7 and puzzle8.index(9) == 6:
    # place the empty cell above 6
    _slide_empty(puzzle8, moves, 4, set((6,)))
    # _swap the empty cell with 6
    _swap(puzzle8, moves, 7, 4)
    # place the empty cell in the final location of 6
    _slide_empty(puzzle8, moves, 5, set((6,)))
    # place 6, 5 and 4
    _swap(puzzle8, moves, 5, 4)
    _swap(puzzle8, moves, 3, 4)
    _swap(puzzle8, moves, 6, 3)
  else:
    return False
  return True


def solve8_heuristic(puzzle8):
  """Solve a 8 puzzle using heuristic."""
  # check the size of the puzzle
  if len(puzzle8) != 9:
    raise ValueError('Invalid size')
  # check if the puzzle is solvable
  if not is_solvable(puzzle8) or is_solved(puzzle8):
    return None
  moves = []
  p8 = list(puzzle8)
  # place one piece after the other
  _place(p8, moves, 1)
  _place(p8, moves, 2)
  _place_3(p8, moves)
  _place(p8, moves, 4)
  _place_5(p8, moves)
  _place_6(p8, moves)
  _place(p8, moves, 7)
  _place(p8, moves, 8)
  return tuple(moves) if is_solved(p8) else None


def solve3_heuristic(puzzle3):
  """Solve a 3 puzzle using heuristic."""
  # check the size of the puzzle
  if len(puzzle3) != 4:
    raise ValueError('Invalid size')
  # check if the puzzle is solvable
  if not is_solvable(puzzle3) or is_solved(puzzle3):
    return None
  moves = []
  p3 = list(puzzle3)
  # place one piece after the other
  for i in [1, 2, 3]:
    _place(p3, moves, i)
  return tuple(moves) if is_solved(p3) else None


def _place_13(puzzle15, moves):
  """Place the piece number 13 in a puzzle 15."""
  if _place(puzzle15, moves, 13, set((1, 2, 3, 4, 5, 9, 13))):
    return True
  # check if the piece is next to its final location
  if puzzle15.index(13) != 13:
    return False
  # remove the second element from the column
  _slide_empty(puzzle15, moves, 4, set((1, 2, 3, 4, 9, 13)))
  # place the emtpy cell in the final position
  _slide_empty(puzzle15, moves, 12)
  # place 13 in its final position
  _swap(puzzle15, moves, 13, 12)
  # place the empty cell above 13
  _slide_empty(puzzle15, moves, 8, set((13,)))
  # place cells 9 and 5
  _swap(puzzle15, moves, 4, 8)
  _swap(puzzle15, moves, 4, 5)
  return True


def _place_4(puzzle15, moves):
  """Place the piece number 4 in a puzzle 15."""
  if _place(puzzle15, moves, 4):
    return True
  # check if the piece is under its final location
  if puzzle15.index(4) != 7:
    return False
  # remove the second element from the row
  _slide_empty(puzzle15, moves, 1, set((1, 3, 4)))
  # place the emtpy cell in the final position
  _slide_empty(puzzle15, moves, 3, set((1,)))
  # place 4 in its final position
  _swap(puzzle15, moves, 7, 3)
  # place the empty cell next to 4
  _slide_empty(puzzle15, moves, 2, set((4,)))
  # place cells 3 and 2
  _swap(puzzle15, moves, 2, 1)
  _swap(puzzle15, moves, 1, 5)
  return True


def _puzzle8(puzzle15):
  """Return the bottom right puzzle 8 from a puzzle 15."""
  map8 = {6:1, 7:2, 8:3, 10:4, 11:5, 12:6, 14:7, 15:8, 16:9}
  return [map8[v] for v in puzzle15 if v in map8]


def _puzzle15(puzzle15, moves, puzzle8, moves8):
  """Return the bottom right puzzle 8 from a puzzle 15."""
  map15 = {1:6, 2:7, 3:8, 4:10, 5:11, 6:12, 7:14, 8:15, 9:16}
  pos = lambda i: (i % 3) + 1 + (4 * ((i // 3) + 1))
  # place the cells in the 15 puzzle
  for i, v in enumerate(puzzle8):
    puzzle15[pos(i)] = map15[v]
  # add the moves used to solve the 8 puzzle
  for m in moves8:
    moves.append((pos(m[0]), pos(m[1])))


def solve15_heuristic(puzzle15, subOpt=False):
  """Solve a 15 puzzle using heuristic."""
  # check the size of the puzzle
  if len(puzzle15) != 16:
    raise ValueError('Invalid size')
  # check if the puzzle is solvable
  if not is_solvable(puzzle15) or is_solved(puzzle15):
    return False
  moves = []
  immovables = set()
  p15 = list(puzzle15)
  # place the first row
  for p in [1, 2, 3]:
    immovables.add(p)
    _place(p15, moves, p, immovables)
  _place_4(p15, moves)
  # place the first column
  for p in [5, 9]:
    immovables.add(p)
    _place(p15, moves, p, immovables)
  _place_13(p15, moves)
  # build and solve the sub-puzzle 8
  p8 = _puzzle8(p15)
  m8 = solve(p8) if subOpt else solve8_heuristic(p8)
  if not m8:
    return None
  # fill the puzzle 15, here the 8 puzzle must be solved by using m8 steps
  _puzzle15(p15, moves, range(1, 10), m8)
  # return moves if the puzzle is solved, None otherwise
  return tuple(moves) if is_solved(p15) else None



@total_ordering
class Puzzle:
  """Represent the current configuration of a puzzle."""


  def __init__(self, puzzle, steps, priority, lastStep=None):
    self.puzzle = puzzle
    self.steps = steps
    self.priority = priority
    self.lastStep = lastStep[::-1] if lastStep else None

  def __eq__(self, other):
    """Check if both instances have the same priority."""
    return self.priority == other.priority

  def __lt__(self, other):
    """Check if this instance has a lower priority."""
    return self.priority < other.priority

  def __repr__(self):
    """Return a string representation of this instance."""
    info = 'Puzzle: {}\nSteps: {}\nPriority: {}'
    return info.format(self.puzzle, len(self.steps), self.priority)

  
  def valid_moves(self):
    """Return a list of possible moves."""
    empty = self.puzzle.index(len(self.puzzle))
    # get all the neighbors of the empty cell
    for n in _neighbors(self.puzzle, empty):
      step = (n, empty)
      if step != self.lastStep:
        yield step

  def apply_move(self, move, priority):
    """Apply the move to the current puzzle and return the new configuration."""
    puzzle = list(self.puzzle)
    steps = list(self.steps)
    x, y = move
    puzzle[x], puzzle[y] = puzzle[y], puzzle[x]
    steps.append(move)
    return Puzzle(puzzle, steps, priority, move)



def _compute_priority(puzzle, move, p):
  """Compute the new priority after the move specified."""
  x, empty = move
  idx = puzzle[x] - 1
  return p - dist(puzzle, x, idx) + dist(puzzle, empty, idx)



def solve(puzzle, solutionFound=None, lowerBound=None):
  """Solve the puzzle and returns the steps made.
  Calls solutionFound every time a new valid solution is found.
  Stop the search if a soluzione with a number of steps lower or equal to
  the lowerBound if found. If lowerBound is equal to -1 returns the first
  solution."""
  # check if the puzzle is solvable
  if not is_solvable(puzzle) or is_solved(puzzle):
    return None
  # compute a first heuristic solution
  if len(puzzle) == 16:
    bestSteps = solve15_heuristic(puzzle, subOpt=True)
  elif len(puzzle) == 9:
    bestSteps = solve8_heuristic(puzzle)
  elif len(puzzle) == 4:
    bestSteps = solve3_heuristic(puzzle)
  else:
    bestSteps = None
  # print and/or return the first solution
  if bestSteps:
    if solutionFound:
      solutionFound(tuple(bestSteps))
    if lowerBound and (lowerBound == -1 or len(bestSteps) <= lowerBound):
      return bestSteps
  # init the frontier with the original puzzle
  frontier = []
  heappush(frontier, Puzzle(puzzle, [], manhattan_dist(puzzle)))
  # add new steps while the frontier is not empty
  while frontier:
    # get the next puzzle configuration
    currState = heappop(frontier)
    # check if the puzzle is solved
    if is_solved(currState.puzzle):
      # callback for the new solution
      if solutionFound:
        solutionFound(tuple(currState.steps))
      # update the best solution
      bestSteps = tuple(currState.steps)
      # stop search if we reach the lower bound
      if lowerBound and len(bestSteps) <= lowerBound:
        break
    # iterate over all possible moves
    for move in currState.valid_moves():
      # compute the priority of the puzzle after the move
      # the priority represents the minimum number of steps required
      # in order to reach the final configuration (the solved puzzle)
      priority = _compute_priority(currState.puzzle, move, currState.priority)
      # add the new configuration only if we can reach a better solution
      if not bestSteps or (len(currState.steps) + 1 + priority) < len(bestSteps):
        heappush(frontier, currState.apply_move(move, priority))
  # search is over, returns the best steps found
  return bestSteps


def display(puzzle):
  """Print a formatted grid."""
  size = int(sqrt(len(puzzle)))
  print((('{:4d}' * size + '\n') * size).format(*puzzle))


def spuzzle(size):
  """Returns a new valid random puzzle."""
  puzzle = [i+1 for i in range(size ** 2)]
  # shuffle the puzzle until it's solvable
  shuffle(puzzle)
  while not is_solvable(puzzle):
    shuffle(puzzle)
  return puzzle