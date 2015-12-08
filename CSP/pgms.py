import minemap, sys

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

@File: pgms.py 
@Use: This program represents the actual Programmer's Minesweeper (PGMS) game 
'''

def main(args):
	strategy_name = "cspstrategy.CSPStrategy"
	game_name = 'intermediate'
	mines = 40
	rows = 16
	cols = 16
	hinted = False
	realrules = True
	trys = 1
	sets = 1
	module = __import__(strategy_name.split('.')[0])

	cont = False
	for i in range(len(args)):
		if cont:
			cont = False
			continue
		if args[i] == '-H':
			hinted = True
		elif args[i] == '-R':
			realrules = True
		elif args[i] == '-i':
			game_name = 'intermediate'
			mines = 40
			rows = 16
			cols = 16
		elif args[i] == '-e':
			game_name = 'expert'
			mines = 99
			rows = 16
			cols = 30
		elif args[i] == '-b':
			game_name = 'beginner'
			mines = 10
			rows = 8
			cols = 8
		elif args[i] == '-r':
			if i+1 >= len(args):
				raise Exception("Wrong input")
			else:
				rows = int(args[i+1])
				cont = True
		elif args[i] == '-c':
			if i+1 >= len(args):
				raise Exception("Wrong input")
			else:
				cols = int(args[i+1])
				cont = True
		elif args[i] == '-m':
			if i+1 >= len(args):
				raise Exception("Wrong input")
			else:
				mines = int(args[i+1])
				cont = True
		elif args[i] == '-s':
			if i+1 >= len(args):
				raise Exception("Wrong input")
			else:
				strategy_name = args[i+1]
				cont = True
		elif args[i] == '-n':
			if i+1 >= len(args):
				raise Exception("Wrong input")
			else:
				trys = int(args[i+1])
				cont = True
		elif args[i] == '-S':
			if i+1 >= len(args):
				raise Exception("Wrong input")
			else:
				sets = int(args[i+1])
				cont = True
		elif args[i] == '-v':
			module.VERBOSE = True
		elif args[i] == '-real':
			if i+1 >= len(args):
				raise Exception("Wrong input")
			else:
				if args[i+1] == ('y' or 'Y'):
					realrules = True
				elif args[i+1] == ('n' or 'N'):
					realrules = False
		else:
			raise Exception("Wrong input")

	if rows < 1 or cols < 1 or mines < 1 or mines >= rows*cols:
		raise Exception("Wrong input")

	
	

	sumN = 0.0
	sumsqr = 0.0
	numCleared = 0.0
	numTotal = 0.0
	game_count = 0
	for seti in range(1,sets+1):

		wins = 0
		for n in range(1,trys+1):
			s = getattr(module,strategy_name.split('.')[1])()
			m = minemap.MineMap(mines,rows,cols,realrules)
			if not hinted:
				s.play1(m)
			else:
				hint = m.hint()
				s.play2(m,hint[0],hint[1])

			game_count += 1

			if m.won():
				wins += 1
			numCleared += m.cleared
			numTotal += cols*rows - mines

		sumN += wins
		sumsqr += wins**2

	print str(rows), "by", str(cols),"board with", str(mines),"mines"
	print "In %s sets of %s tries (%s) games total:" % (sets,trys,sets*trys)
	mean = sumN / sets
	print " Mean wins: %s/%s (%s%%)" % (int(mean), trys, int(100.0*mean/trys+0.5) )
	print " Mean %% of board cleared: %s/%s (%s%%)" % (int(numCleared),int(numTotal),int(100*numCleared/numTotal))
	

if __name__ == "__main__":
    main(sys.argv[1:])

		