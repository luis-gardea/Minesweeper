from Tkinter import *
import sys, minemap

mycolor = '#%02x%02x%02x' % (64, 204, 208)

purple = 128, 0, 128
orange = 255, 127, 0
red = 255, 0, 0

number_sq = '#%02x%02x%02x' % (0.5*255, 0.5*255, 0.5*255)
unclicked_sq = '#%02x%02x%02x' % (0.25*255, 0.25*255, 0.25*255)
bomb_sq = '#%02x%02x%02x' % (red)
zero_sq = '#%02x%02x%02x' % (0.75*255, 0.75*255, 0.75*255)
flag_sq = '#%02x%02x%02x' % (purple)


class App:
	def __init__(self, master,args):
		self.scale = 30
		self.m = None
		self.strategy_name = "cspstrategy.CSPStrategy"
		self.game_name = 'intermediate'
		self.mines = 40
		self.rows = 16
		self.cols = 16
		self.module = __import__(self.strategy_name.split('.')[0])

		cont = False
		for i in range(len(args)):
			if cont:
				cont = False
				continue
			elif args[i] == '-i':
				self.game_name = 'intermediate'
				self.mines = 40
				self.rows = 16
				self.cols = 16
			elif args[i] == '-e':
				self.game_name = 'expert'
				self.mines = 99
				self.rows = 16
				self.cols = 30
			elif args[i] == '-b':
				self.game_name = 'beginner'
				self.mines = 10
				self.rows = 8
				self.cols = 8
			elif args[i] == '-r':
				if i+1 >= len(args):
					raise Exception("Wrong input")
				else:
					self.rows = int(args[i+1])
					cont = True
			elif args[i] == '-c':
				if i+1 >= len(args):
					raise Exception("Wrong input")
				else:
					self.cols = int(args[i+1])
					cont = True
			elif args[i] == '-m':
				if i+1 >= len(args):
					raise Exception("Wrong input")
				else:
					self.mines = int(args[i+1])
					cont = True
			elif args[i] == '-s':
				if i+1 >= len(args):
					raise Exception("Wrong input")
				else:
					self.strategy_name = args[i+1]
					cont = True
			elif args[i] == '-v':
				self.module.VERBOSE = True
			elif args[i] == '-noreal':
				realrules = False
			else:
				raise Exception("Wrong input")

		if self.rows < 1 or self.cols < 1 or self.mines < 1 or self.mines >= self.rows*self.cols:
			raise Exception("Wrong input")

		
		self.frame = Frame(master)
		self.frame.pack()
		self.canvas = Canvas(master, width=self.cols*self.scale+15,height=self.rows*self.scale+15)
		self.canvas.pack()

		self.button = Button(self.frame, text="QUIT", fg="red", command=self.frame.quit)
		self.button.pack(side=RIGHT)

		self.hi_there = Button(self.frame, text="Play", command = self.play_game)
		self.hi_there.pack(side=LEFT)

		self.squares = {}
		for x in range(self.cols):
			for y in range(self.rows):
				color = zero_sq
				self.squares[(x,y)]=self.canvas.create_rectangle(x*self.scale+10,y*self.scale+10,\
					(x+1)*self.scale+10,(y+1)*self.scale+10,fill=color,outline=color)

	
	def play_game(self):
		self.squares = {}
		for x in range(self.cols):
			for y in range(self.rows):
				color = zero_sq
				self.squares[(x,y)]=self.canvas.create_rectangle(x*self.scale+10,y*self.scale+10,\
					(x+1)*self.scale+10,(y+1)*self.scale+10,fill=color,outline=color)

		self.s = getattr(self.module,self.strategy_name.split('.')[1])()
		self.m = minemap.MineMap(self.mines,self.rows,self.cols)
				
		self.s.play1(self.m)	

		self.display_game()		

		numCleared = self.m.cleared
		numTotal = self.cols*self.rows - self.mines

		print 'Playing on',self.rows,'by',self.cols,'board -'
		if self.m.won():
			print "  Game was won:",'uncovered',numCleared,'of',numTotal,'tiles'
		else:
			print "  Game was lost:",'uncovered',numCleared,'of',numTotal,'tiles'

	def display_game(self):
		while len(self.m.moves) > 0:
			pos = self.m.moves.pop(0)
			color = number_sq
			val = self.m.mine_map[pos[1]][pos[0]]
			if val == 0:
				color = unclicked_sq
			if self.m.mark_map[pos[1]][pos[0]]:
				color = flag_sq
				val = 'x'
			elif val == minemap.BOOM:
				color = bomb_sq
				val = 'x'
			self.canvas.itemconfig(self.squares[pos],fill=color,outline=color)
			self.canvas.create_text((pos[0]+0.5)*self.scale+10,(pos[1]+0.5)*self.scale+10,text=str(val))
		if not self.m.won():
			for x in range(self.cols):
				for y in range(self.rows):
					if self.m.mine_map[y][x] == minemap.BOOM and not self.m.mark_map[y][x]:
						self.canvas.itemconfig(self.squares[(x,y)],fill=bomb_sq)
						self.canvas.create_text((x+0.5)*self.scale+10,(y+0.5)*self.scale+10,text='x')
		

def main(args):
	root = Tk()
	app = App(root,args)
	app.play_game()
	
	root.mainloop()
	
if __name__ == "__main__":
    main(sys.argv[1:])
