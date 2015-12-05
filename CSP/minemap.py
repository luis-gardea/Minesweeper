from random import randint

# //  Copyright (C) 1995 and 1997 John D. Ramsdell

# // This file is part of Programmer's Minesweeper (PGMS).

# // PGMS is free software; you can redistribute it and/or modify
# // it under the terms of the GNU General Public License as published by
# // the Free Software Foundation; either version 2, or (at your option)
# // any later version.

# // PGMS is distributed in the hope that it will be useful,
# // but WITHOUT ANY WARRANTY; without even the implied warranty of
# // MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# // GNU General Public License for more details.

# // You should have received a copy of the GNU General Public License
# // along with PGMS; see the file COPYING.  If not, write to
# // the Free Software Foundation, 59 Temple Place - Suite 330,
# // Boston, MA 02111-1307, USA.

# /**
#  * Out of bounds return code.
#  * @see Map#look
#  */
OUT_OF_BOUNDS = -4

# /**
#  * Marked return code.
#  * @see Map#look
#  */
MARKED = -3

# /**
#  * Unprobed return code.
#  * @see Map#look
#  */
UNPROBED = -2

# /**
#  * Boom return code.
#  * @see Map#look
#  */
BOOM = -1


# // /**
# //  * The class Map implements a mine map.  A strategy operates on a mine
# //  * map. By invoking the operations of probing and marking, the strategy
# //  * attempts to place the mine map in a state in which every cell that does
# //  * not contain a mine has been probed, without probing a cell that does
# //  * contain a mine.
# //  * @see Strategy
# //  * @version February 1997
# //  * @author John D. Ramsdell
# //  */
class MineMap(object):
  
  # /**
  #  * Create a mine map.
  #  * @param mines number of mines in mine map
  #  * @param rows        rows in map
  #  * @param columns     columns in map
  #  * @return    a mine map
  #  */
  def __init__(self, mines, rows, columns, realrules):
    self.minesLeft = mines
    self.rows = rows
    self.cols = columns
    self.realrules = realrules

    self.victory = False
    self.finished = False
    
    # /* mine_map[y][x] = -1, if cell (x, y) contains a mine or
    #  *                   n, where n is the number of mines in adjacent cells.
    #  */
    self.mine_map = []

    # /* mark_map[y][x] = true when cell (x, y) is marked */
    self.mark_map = []

    # /* unprobed_map[y][x] = true when cell (x, y) is not probed
    # * The code maintains the following relation:
    # * mark_map[y][x] == true implies unprobed_map[y][x] == true
    # */
    self.unprobed_map = []
    
    for y in range(self.rows):
      self.mine_map.append([])
      self.mark_map.append([])
      self.unprobed_map.append([])
      for x in range(self.cols):
        self.mine_map[y].append([])
        self.mark_map[y].append([])
        self.unprobed_map[y].append([])

        self.mine_map[y][x] = 0
        self.mark_map[y][x] = False
        self.unprobed_map[y][x] = True
    
    if mines/2 >= self.rows * self.cols: # Odd parameters
      self.finished = True    # Just punt
    else:
      k = 0
      while k < mines: # Place mines randomly
        x = self.pick(self.cols)
        y = self.pick(self.rows)
        if self.mine_map[y][x] >= 0:
          self.mine_map[y][x] = BOOM
          k += 1
      self.computeweights();

  # Compute weights
  def computeweights(self):
    for y in range(self.rows):
      for x in range(self.cols):
	      if (self.mine_map[y][x] >= 0):
    		  w = 0;
    		  y0 = max(0, y - 1)
    		  y1 = min(self.rows, y + 2)
    		  x0 = max(0, x - 1)
    		  x1 = min(self.cols, x + 2)
    		  for yw in range(y0, y1):
    		      for xw in range(x0, x1):
    			      if self.mine_map[yw][xw] < 0: w += 1
    		  self.mine_map[y][x] = w

  # /**
  #  * Inefficient recursive floodfill algorithm.  
  #  * bitmap[y][x] must be true.
  #  * @param bitmap array of true values to fill
  #  * @param sx start x position
  #  * @param sy start y position
  #  * @return number of connected true values
  #  */
  # def floodfill(self, bitmap, sx, sy):
  #     sum = 1
  #     self.bitmap[sy][sx] = False
  #     for (int y=Math.max(0,sy-1); y<Math.min(r,sy+2); ++y)
	 #     for (int x=Math.max(0,sx-1); x<Math.min(c,sx+2); ++x)
	 #      if bitmap[y][x]:
		#       sum+=floodfill(bitmap,x,y);
  #     return sum;
  # }

  # # /**
  # #  * Get a hint.
  # #  * @return           two element array of hint (column,row)
  # #  */
  # def hint(self):
  #     boolean[][] possibles = new boolean[r][c];
  #     boolean done = false;
  #     for (int i=0; (i<9)&&(!done); ++i) {
	 #  for (int y = 0; y < r; y++)
	 #      for (int x = 0; x < c; x++) {
		#   possibles[y][x] = (mine_map[y][x]==i);
		#   if (possibles[y][x])
		#       done=true;
	 #      }
  #     }
  #     if (!done)
	 #  return null; // should never happen!

  #     // find largest connected component of possibles
  #     int[] result = new int[2];
  #     int best=0;
  #     for (int y = 0; y < r; y++)
	 #  for (int x = 0; x < c; x++)
	 #      if (possibles[y][x]) {
		#   int sum = floodfill(possibles,x,y);
		#   if (sum>best) {
		#       best=sum;
		#       result[0]=x;
		#       result[1]=y;
		#   }
	 #      }
  #     return result;
  # }

  # /**
  #  * Pick a number at random.
  #  * @param n           a positive number (not checked)
  #  * @return            a nonnegative number less than n
  #  */
  def pick(self, n):
    return randint(0, n-1)
  
  # /**
  #  * Has this game been won?
  #  * A game is won if every cell which does not contain a mine has 
  #  * been probed, but no cell with a mine has been probed.
  #  */
  def won(self):
    return self.victory
  
  # /**
  #  * Is this game finished?
  #  * The game is finished if it has been won or if a cell with a 
  #  * mine has been probed.
  #  */
  def done(self):
    if self.finished:
      return True

    for y in range(self.rows):
      for x in range(self.cols):
        if (self.mine_map[y][x] < 0) != self.unprobed_map[y][x]:
          return False

    self.finished = True
    self.victory = True
    return True

  # /**
  #  * Probe a cell for a mine.
  #  * <ul>
  #  * <li> If the game is finished, probe behaves like look.
  #  * <li> If the cell does not exist, <code>OUT_OF_BOUNDS</code>
  #  * is returned.
  #  * <li>If the cell is marked, <code>MARKED</code> is returned.
  #  * <li>If the cell has a mine, <code>BOOM</code> is returned
  #  * and the game is lost.
  #  * <li>Otherwise, the number of adjacent mines is returned.
  #  * </ul>
  #  * @param x        x coordinate of cell
  #  * @param y        y coordinate of cell
  #  */
  def probe(self, x, y):
    if self.finished:
      return self.look(x, y)
    elif x < 0 or x >= self.cols or y < 0 or y >= self.rows:
      return OUT_OF_BOUNDS
    elif self.mark_map[y][x]:
      return MARKED
    self.unprobed_map[y][x] = False
    if self.mine_map[y][x] < 0:
      if self.realrules:
	      # find non-mine
        while True:
          tx = pick(self.cols)
          ty = pick(self.rows)
          if not self.mine_map[ty][tx] < 0:
            break
	        # swap
          self.mine_map[ty][tx] = self.mine_map[y][x]
          self.mine_map[y][x] = 0
          self.computeweights();
      else:
	      self.finished = True

    self.realrules = False
    return self.mine_map[y][x]
  
  # /**
  #  * Look at a cell.
  #  * <ul>
  #  * <li> If the cell does not exist, <code>OUT_OF_BOUNDS</code>
  #  * is returned.
  #  * <li>If the cell is marked, <code>MARKED</code> is returned.
  #  * <li>If the cell has not been probed, <code>UNPROBED</code> 
  #  * is returned.
  #  * <li>If the cell has a probed mine, <code>BOOM</code> is returned.
  #  * <li>Otherwise, the number of adjacent mines is returned.
  #  * </ul>
  #  * @param x        x coordinate of cell
  #  * @param y        y coordinate of cell
  #  */
  def look(self, x, y):
    if x < 0 or x >= self.cols or y < 0 or y >= self.rows:
      return OUT_OF_BOUNDS
    elif self.mark_map[y][x]:
      return MARKED
    elif self.unprobed_map[y][x]:
      return UNPROBED
    else:
      return self.mine_map[y][x]

  # /**
  #  * Mark a cell.
  #  * <ul>
  #  * <li> If the game is finished, mark behaves like look.
  #  * <li> If the cell does not exist, <code>OUT_OF_BOUNDS</code>
  #  * is returned.
  #  * <li>If the cell is marked, <code>MARKED</code> is returned.
  #  * <li>If the cell has not been probed, the cell is marked
  #  * and <code>MARKED</code> is returned.
  #  * <li>Otherwise, the number of adjacent mines is returned.
  #  * </ul>
  #  * @param x        x coordinate of cell
  #  * @param y        y coordinate of cell
  #  */
  def mark(self, x, y): 
    if self.finished:
      return self.look(x, y)
    elif x < 0 or x >= self.cols or y < 0 or y >= self.rows:
      return OUT_OF_BOUNDS
    elif self.mark_map[y][x]:
      return MARKED
    elif self.unprobed_map[y][x]:
      self.minesLeft -= 1
      self.mark_map[y][x] = True
      return MARKED
    else:
      return self.mine_map[y][x]

  # /**
  #  * Unmark a cell.
  #  * <ul>
  #  * <li> If the game is finished, unmark behaves like look.
  #  * <li> If the cell does not exist, <code>OUT_OF_BOUNDS</code>
  #  * is returned.
  #  * <li>If the cell is marked, the cell is unmarked
  #  * and <code>UNPROBED</code> is returned.
  #  * <li>If the cell has not been probed,  
  # * <code>UNPROBED</code> is returned.
  #  * <li>Otherwise, the number of adjacent mines is returned.
  #  * </ul>
  #  * @param x        x coordinate of cell
  #  * @param y        y coordinate of cell
  #  */
  def unmark(self, x, y):
    if self.finished:
      return self.look(x, y)
    elif x < 0 or x >= self.cols or y < 0 or y >= self.rows:
      return OUT_OF_BOUNDS
    elif self.mark_map[y][x]:
      self.minesLeft += 1
      self.mark_map[y][x] = False
      return UNPROBED
    elif self.unprobed_map[y][x]:
      return UNPROBED
    else:
      return self.mine_map[y][x]

  # /**
  #  * Provide the number of mines minus the 
  #  * number of marks in this mine map.
  #  */ 
  def mines_minus_marks(self):
    return self.minesLeft
  
  # /**
  #  * Provide the number of rows in this mine map.
  #  */ 
  def rows(self):
    return self.rows
  
  # /**
  #  * Provide the number of columns in this mine map.
  #  */ 
  def columns(self):
    return self.cols

  # /**
  #  * Display the mine map on the standard output stream.
  #  * Used only for debugging.
  #  */
#   public void display() {
#     for (int y = 0; y < r; y++) {
#       int z = r - 1 - y;
#       System.out.print(z % 10 + ":");
#       for (int x = 0; x < c; x++)
# 	if (mark_map[z][x])
# 	  if (mine_map[z][x] < 0)
# 	    System.out.print("-");
# 	  else
# 	    System.out.print("?");
# 	else if (mine_map[z][x] < 0)
# 	  System.out.print("X");
# 	else if (unprobed_map[z][x])
# 	  System.out.print(" ");
# 	else
# 	  System.out.print(mine_map[z][x]);
#       System.out.println();
#     }
#     System.out.print("  ");
#     for (int x = 0; x < c; x++)
#       System.out.print(x % 10);
#   }
# }

