from random import randint

'''
CS 229/221 note: This is a translation that we made of the PGMS
from Java to Python with some changes.

Copyright (C) 1995 and 1997 John D. Ramsdell

This file is part of Programmer's Minesweeper (PGMS).

PGMS is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2, or (at your option)
any later version.

PGMS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PGMS; see the file COPYING.  If not, write to
the Free Software Foundation, 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.

@File: minemap.py 
@Use: This class implements a mine map. Uses operations like marking 
    and probing positions as the game is played.
'''

# Out of bounds return code
OUT_OF_BOUNDS = -4


# Marked return code.
MARKED = -3


# Unprobed return code.
UNPROBED = -2


# Boom return code.
BOOM = -1


class MineMap(object):
  
    def __init__(self, mines, rows, columns, realrules):
        self.minesLeft = mines
        self.rows = rows
        self.cols = columns
        self.realrules = realrules
        self.mines = mines

        self.cleared = 0

        self.victory = False
        self.finished = False
        
        # mine_map[y][x] = -1, if cell (x, y) contains a mine or
        # the number of mines adjactent to cell (x, y)
        self.mine_map = []

        # mark_map[y][x] = true when cell (x, y) is marked */
        self.mark_map = []

        # unprobed_map[y][x] = true when cell (x, y) is not probed
        # The code maintains the following relation:
        # mark_map[y][x] == true implies unprobed_map[y][x] == true
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

    # returns random number x, where 0<=x<n
    def pick(self, n):
        return randint(0, n-1)
  
    # returns true if the game has been won
    def won(self):
        return self.victory
  
    # returns true if the game is over, meaning the game is won or lost
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

    # probes a cell (x, y) for a mine and makes the necessary 
    # changes based on the returned value
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
                    tx = self.pick(self.cols)
                    ty = self.pick(self.rows)
                    if not self.mine_map[ty][tx] < 0:
                        break
                # swap
                self.mine_map[ty][tx] = self.mine_map[y][x]
                self.mine_map[y][x] = 0
                self.computeweights();
            else:
                self.finished = True

        self.realrules = False
        if self.mine_map[y][x] != BOOM:
            self.cleared += 1
        return self.mine_map[y][x]
  
    # returns values depending on the state of cell (x, y)
    def look(self, x, y):
        if x < 0 or x >= self.cols or y < 0 or y >= self.rows:
            return OUT_OF_BOUNDS
        elif self.mark_map[y][x]:
            return MARKED
        elif self.unprobed_map[y][x]:
            return UNPROBED
        else:
            return self.mine_map[y][x]

    # marks cell (x, y) as a mine
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

    # returns number of mines left
    def mines_minus_marks(self):
        return self.minesLeft

    # returns the number of rows in the map
    def rows(self):
        return self.rows
  
    # returns the number of columns in the map
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

