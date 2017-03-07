import os
import sys

from copy import copy,deepcopy

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import random

pyqt_app = ""

class tic_tac_toe_board(QWidget):
	def __init__(self):
		super(tic_tac_toe_board,self).__init__()
		self.init_cells()
		self.shadow = [-1,-1]
		self.draw_shadow = False
		self.user_clicked_location = [-1,-1]
		self.clicked_cells = []
		self.algo_picked_cells = []
		self.over = False
		self.first_move = "USER"

		self.setMouseTracking(True)

	def init_cells(self):
		self.cells = []
		for _ in range(3):
			cur_row = []
			for _ in range(3):
				cur_row.append(".")
			self.cells.append(cur_row)

	def enterEvent(self,event):
		self.draw_shadow = True

	def leaveEvent(self,event):
		self.draw_shadow = False

	def user_won(self):
		for col in self.cells:
			if col == ["O","O","O"]:
				return True
		for row in range(3):
			cur_row = []
			for col in range(3):
				cur_row.append(self.cells[col][row])
			if cur_row == ["O","O","O"]:
				return True
		if self.cells[1][1]=="O":
			if self.cells[0][0]=="O" and self.cells[2][2]=="O":
				return True
			if self.cells[0][2]=="O" and self.cells[2][0]=="O":
				return True
		return False

	def mousePressEvent(self,event):
		if self.shadow != [-1,-1] and self.over==False:
			if self.shadow not in self.clicked_cells and self.shadow not in self.algo_picked_cells:
				self.clicked_cells.append(copy(self.shadow))
				self.repaint()
				self.setEnabled(False)
				if self.user_won()==False:
					if self.game_over()==False:
						self.get_next_move()
					else:
						print("STALEMATE")
				else:
					print("USER WON")
					self.over = True
				self.repaint()
				if self.algo_won():
					print("ALGO WON")
					self.over = True

				self.setEnabled(True)

	def game_over(self):
		for col in range(3):
			for row in range(3):
				if self.cells[row][col]==".":
					return False
		return True

	def mouseMoveEvent(self,e):
		x = e.x()
		y = e.y()
		x_cell = x/self.h_step
		y_cell = y/self.v_step
		if x_cell in [0,1,2] and y_cell in [0,1,2]:
			self.shadow = [int(x_cell),int(y_cell)]
		self.repaint()

	def clear(self):
		self.over = False
		self.clicked_cells = []
		self.algo_picked_cells = []
		for row in range(3):
			for column in range(3):
				self.cells[column][row] = "."
		self.repaint()
		if self.first_move=="ALGO":
			self.setEnabled(False)
			self.get_next_move()
			self.repaint()
			self.setEnabled(True)

	def paintEvent(self,e):
		qp = QPainter()
		qp.begin(self)
		self.drawWidget(qp)
		qp.end()

	def drawWidget(self,qp):
		width = self.size().width()
		height = self.size().height()

		horizontal_step = int(round(width/3))
		vertical_step = int(round(height/3))

		self.h_step = horizontal_step
		self.v_step = vertical_step

		pen = QPen(QColor(0,0,0),1,Qt.SolidLine)

		qp.drawLine(horizontal_step,0,horizontal_step,height) # left vertical
		qp.drawLine(2*horizontal_step,0,2*horizontal_step,height) # right vertical

		qp.drawLine(0,vertical_step,width,vertical_step) # top horizontal
		qp.drawLine(0,vertical_step*2,width,vertical_step*2) # bottom horizontal

		shadow_offset = 25

		if self.draw_shadow:
			if self.shadow != [-1,-1]:
				pen = QPen(QColor(211,211,211),5,Qt.SolidLine)
				qp.setPen(pen)
				qp.drawEllipse(self.shadow[0]*horizontal_step+shadow_offset,self.shadow[1]*vertical_step+shadow_offset,40,40)

		pen = QPen(QColor(0,0,0),10,Qt.SolidLine)
		qp.setPen(pen)

		for location in self.clicked_cells:
			self.cells[location[0]][location[1]] = "O"
			qp.drawEllipse(location[0]*horizontal_step+shadow_offset,location[1]*vertical_step+shadow_offset,40,40)

		x_offset = 20

		for location in self.algo_picked_cells:
			self.cells[location[0]][location[1]] = "X"
			qp.drawLine(location[0]*horizontal_step+x_offset,location[1]*vertical_step+x_offset,location[0]*horizontal_step+horizontal_step-x_offset,location[1]*vertical_step+vertical_step-x_offset)
			qp.drawLine(location[0]*horizontal_step+x_offset,location[1]*vertical_step+x_offset+53,location[0]*horizontal_step+horizontal_step-x_offset,location[1]*vertical_step+vertical_step-x_offset-53)

	def board_complete(self,board):
		for col in range(3):
			for row in range(3):
				if board[row][col]==".":
					return False
		return True

	def eval_board(self,board,me="X",opp="O"):

		if self.board_complete(board): return -1

		to_win = [[me,me,"N"],[me,"N",me],["N",me,me]]
		to_block = [[opp,opp,"N"],[opp,"N",opp],["N",opp,opp]]

		approach_win = [[me,"N","."],[me,".","N"],["N",".",me],["N",me,"."],[".",me,"N"],[".","N",me]]
		block_approach = [[opp,"N","."],[opp,".","N"],["N",".",opp],["N",opp,"."],[".",opp,"N"],[".","N",opp]]

		to_win_score = 1010
		to_block_score = 1000

		approach_win_score = 50
		block_approach_score = 100

		center_score = 150
		corner_score = 120

		score = 0

		for col in board:
			if col in to_win:
				if score<to_win_score: score = to_win_score
			if col in to_block:
				if score<to_block_score: score = to_block_score

			if col in approach_win: 
				if score<approach_win_score:
					score = approach_win_score
			if col in block_approach: 
				if score<block_approach_score:
					score = block_approach_score

		for row in range(3):
			cur_row = []
			for col in range(3):
				cur_row.append(board[col][row])

			if cur_row in to_win: 
				if score<to_win_score: score = to_win_score
			if cur_row in to_block: 
				if score<to_block_score: score = to_block_score

			if cur_row in approach_win:
				if score<approach_win_score: score = approach_win_score
			if cur_row in block_approach:
				if score<block_approach_score: score = block_approach_score

		if board[1][1] in [me,"N"]:
			if board[0][0] in [me,"N"] and board[2][2] in [me,"N"]:
				if score<to_win_score: score = to_win_score
			if board[0][2] in [me,"N"] and board[2][0] in [me,"N"]:
				if score<to_win_score: score = to_win_score

		if board[1][1] in [opp,"N"]:
			if board[0][0] in [opp,"N"] and board[2][2] in [opp,"N"]:
				if score<to_block_score: score = to_block_score
			if board[0][2] in [opp,"N"] and board[2][0] in [opp,"N"]:
				if score<to_block_score: score = to_block_score

		if board[1][1] == "N":
			if score<center_score: score = center_score

		if board[0][0]=="N" or board[0][2]=="N" or board[2][0]=="N" or board[2][2]=="N":
			if score<corner_score: score = corner_score

		return score

	def get_next_move(self,board=None,me="X",opp="O"):

		possible_states = []
		possible_state_moves = []

		if board==None:
			base_case = True 
			board = self.cells 
		else:
			base_case = False

		for row in range(3):
			for col in range(3):
				if board[col][row]==".":
					state_copy = deepcopy(board)
					state_copy[col][row] = "N"
					possible_states.append(state_copy)
					possible_state_moves.append([col,row])

		if len(possible_states)==0:
			return -1

		if len(possible_states)==9:
			selection = random.choice(possible_state_moves)
			self.algo_picked_cells.append(selection)
			return

		best_eval = -1
		best_move = []

		for scenario,move in zip(possible_states,possible_state_moves):
			evaluation = self.eval_board(scenario)
			if evaluation>best_eval:
				best_eval = evaluation
				best_move = []
				best_move.append(move)
			elif evaluation==best_eval:
				best_move.append(move)

		if len(best_move)>1:
			if best_eval==1010:
				best_move = random.choice(best_move)
			else:
				#print("here2")
				hardest_for_opponent = 1000000
				hardest_moves = []
				set_best = False

				for option in best_move:
					state = deepcopy(possible_states[possible_state_moves.index(option)])
					state[option[0]][option[1]] = me
					opponent_move = self.get_next_move(board=state,me=opp,opp=me)
					if opponent_move==-1:
						best_move = option
						set_best = True
						break
						if not base_case: return -1 

					state[opponent_move[0]][opponent_move[1]] = opp
					my_next_move = self.get_next_move(board=state,me=me,opp=opp)
					if my_next_move==-1:
						#print("here")
						if not base_case: return -1
						#else: print("here5")

					state[my_next_move[0]][my_next_move[1]]
					easiness_for_opponent = self.eval_board(state,me=opp,opp=me)
					opponent_move = self.get_next_move(board=state,me=opp,opp=me)
					if opponent_move==-1:
						#print("here2")
						best_move = option 
						set_best = True
						break
					state[opponent_move[0]][opponent_move[1]] = opp 
					my_next_move = self.get_next_move(board=state,me=me,opp=opp)
					if my_next_move==-1:
						#print("here3")
						continue
					state[my_next_move[0]][my_next_move[1]] = me 
					easiness_for_opponent = self.eval_board(board=state,me=opp,opp=me)

					if easiness_for_opponent<hardest_for_opponent:
						hardest_for_opponent = easiness_for_opponent
						hardest_moves = []
						hardest_moves.append(option)
					elif easiness_for_opponent==hardest_for_opponent:
						hardest_moves.append(option)

				if not set_best: 
					if len(hardest_moves)>=1:
						best_move = random.choice(hardest_moves)
					else:
						return -1

		else:
			best_move = best_move[0]

		if base_case:
			if best_move != -1:
				self.algo_picked_cells.append(best_move)
			else:
				self.done = True
				print("STALEMATE")
		else:
			return best_move
	
	def algo_won(self):
		for col in self.cells:
			if col == ["X","X","X"]:
				return True
		for row in range(3):
			cur_row = []
			for col in range(3):
				cur_row.append(self.cells[col][row])
			if cur_row == ["X","X","X"]:
				return True
		if self.cells[1][1]=="X":
			if self.cells[0][0]=="X" and self.cells[2][2]=="X":
				return True
			if self.cells[0][2]=="X" and self.cells[2][0]=="X":
				return True
		return False

	def ai_first(self):
		self.first_move = "ALGO"
		self.clear()

	def user_first(self):
		self.first_move = "USER"
		self.clear()


class main_window(QWidget):

    def __init__(self,parent=None):
        super(main_window,self).__init__()
        self.init_vars()
        self.init_ui()

    def init_vars(self):
        self.num_moves = 0

    def init_ui(self):
        self.setFixedWidth(300)
        self.setFixedHeight(350)
        self.setWindowTitle("Tic-Tac-Toe Trainer")
        self.layout = QVBoxLayout(self)
        if os.name=="nt": self.layout.addSpacing(25)
        self.grid = tic_tac_toe_board()
        self.layout.addWidget(self.grid)
        self.button = QPushButton("Reset")
        self.button.clicked.connect(self.grid.clear)
        self.layout.addWidget(self.button)

        self.menu_bar = QMenuBar(self)
        self.menu_bar.setFixedWidth(300)
        self.game_menu = self.menu_bar.addMenu("Game")
        self.game_menu.addAction("AI Goes First",self.grid.ai_first)
        self.game_menu.addAction("You Go First",self.grid.user_first)
        self.game_menu.addSeparator()
        self.game_menu.addAction("Clear",self.grid.clear)

        self.show()


def main():
    global pyqt_app

    pyqt_app = QApplication(sys.argv)
    _ = main_window()
    sys.exit(pyqt_app.exec_())

if __name__ == '__main__':
    main()