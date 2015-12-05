import sys
import minemap

class PGMS(object):

	def __init__(self,s = None,mines = 40,rows = 16,cols = 16,hinted = False,realrules = False):
		self.s = s
		self.mines = mines
		self.rows = rows
		self.cols = cols
		self.hinted = hinted
		self.realrules = realrules

	def percent(self,n,d):
		return (200*n + d)/float(2*d)



def main(args):
	game = PGMS()
	strategy_name = "cspstrategy.CSPStrategy"
	game_name = 'intermediate'
	mines = 40
	rows = 16
	cols = 16
	hinted = False
	realrules = False
	trys = 1
	sets = 1

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
				print "Wrong input"
				sys.exit(0)
			else:
				rows = int(args[i+1])
				cont = True
		elif args[i] == '-c':
			if i+1 >= len(args):
				print "Wrong input"
				sys.exit(0)
			else:
				cols = int(args[i+1])
				cont = True
		elif args[i] == '-m':
			if i+1 >= len(args):
				print "Wrong input"
				sys.exit(0)
			else:
				mines = int(args[i+1])
				cont = True
		elif args[i] == '-s':
			if i+1 >= len(args):
				print "Wrong input"
				sys.exit(0)
			else:
				strategy_name = args[i+1]
				cont = True
		elif args[i] == '-n':
			if i+1 >= len(args):
				print "Wrong input"
				sys.exit(0)
			else:
				trys = int(args[i+1])
				cont = True
		elif args[i] == '-S':
			if i+1 >= len(args):
				print "Wrong input"
				sys.exit(0)
			else:
				sets = int(args[i+1])
				cont = True
		else:
			print "Wrong input"
			sys.exit(0)

	if rows < 1 or cols < 1 or mines < 1:
		print "Wrong input"
		sys.exit(0)

	module = __import__(strategy_name.split('.')[0])
	s = getattr(module,strategy_name.split('.')[1])()

	sumN = 0
	sumsqr = 0
	game_count = 0
	for seti in range(1,sets+1):
		# print "Set: %s" % seti
		wins = 0
		for n in range(1,trys+1):
			m = minemap.MineMap(mines,rows,cols,realrules)
			if not hinted:
				s.play1(m)
			else:
				hint = m.hint()
				s.play2(m,hint[0],hint[1])

			game_count += 1

			if m.won():
				wins += 1
		sumN += wins
		sumsqr += wins**2
	print "In %s sets of %s tries (%s) games total:" % (sets,trys,sets*trys)
	mean = sumN / float(sets)
	print " Mean wins: %s/%s (%s percent)" % (mean, trys, int(100.0*mean/trys+0.5) )
	var = (sumsqr - (sumN**2)/float(sets))/sets
	print " Standard deviation: %s" % var**(0.5)
	print " Stanfard error of the mean: %s" % (var/sets)**(0.5)

if __name__ == "__main__":
    main(sys.argv[1:])

		