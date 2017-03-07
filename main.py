import os
import sys

from copy import copy,deepcopy

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *

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
			#qp.drawEllipse(location[0]*horizontal_step+shadow_offset,location[1]*vertical_step+shadow_offset,40,40)

	def eval_board(self,board):
		score = 0

		to_win = [["X","X","N"],["X","N","X"],["N","X","X"]]
		to_block = [["O","O","N"],["O","N","O"],["N","O","O"]]

		approach_win = [["X","N","."],["X",".","N"],["N",".","X"],["N","X","."],[".","X","N"],[".","N","X"]]
		block_approach = [["O","N","."],["O",".","N"],["N",".","O"],["N","O","."],[".","O","N"],[".","N","O"]]

		for col in board:
			if col in to_win: return 1000
			if col in to_block: return 1010
			if col in approach_win: score = 50
			if col in block_approach: score = 100

		for row in range(3):
			cur_row = []
			for col in range(3):
				cur_row.append(board[col][row])
			if cur_row in to_win: return 1000
			if cur_row in to_block: return 1010
			if cur_row in approach_win:
				if score<50: score = 50
			if cur_row in block_approach:
				if score<100: score = 100

		if board[1][1] in ["X","N"]:
			if board[0][0] in ["X","N"] and board[2][2] in ["X","N"]:
				return 1000
			if board[0][2] in ["X","N"] and board[2][0] in ["X","N"]:
				return 1000

		if board[1][1] in ["O","N"]:
			if board[0][0] in ["O","N"] and board[2][2] in ["O","N"]:
				return 1010
			if board[0][2] in ["O","N"] and board[2][0] in ["O","N"]:
				return 1010

		if board[1][1] == "N":
			if score<150: score = 150

		return score

	def get_next_move(self):

		possible_states = []
		possible_state_moves = []

		for row in range(3):
			for col in range(3):
				if self.cells[col][row]==".":
					state_copy = deepcopy(self.cells)
					state_copy[col][row] = "N"
					possible_states.append(state_copy)
					possible_state_moves.append([col,row])

		if len(possible_states)==0:
			return

		best_eval = -1
		best_move = -1

		for scenario,move in zip(possible_states,possible_state_moves):
			evaluation = self.eval_board(scenario)
			if evaluation>best_eval:
				best_eval = evaluation
				best_move = move 

		if best_move != -1:
			self.algo_picked_cells.append(best_move)
		else:
			self.done = True
			print("STALEMATE")
	
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

class main_window(QWidget):

    def __init__(self,parent=None):
        super(main_window,self).__init__()
        self.init_vars()
        self.init_ui()

    def init_vars(self):
        self.num_moves = 0

    def init_ui(self):
        self.setFixedWidth(300)
        self.setFixedHeight(325)
        self.setWindowTitle("Tic-Tac-Toe Trainer")
        self.layout = QVBoxLayout(self)
        self.grid = tic_tac_toe_board()
        self.layout.addWidget(self.grid)
        self.button = QPushButton("Reset")
        self.button.clicked.connect(self.grid.clear)
        self.layout.addWidget(self.button)
        self.show()


def main():
    global pyqt_app

    pyqt_app = QApplication(sys.argv)
    _ = main_window()
    sys.exit(pyqt_app.exec_())

if __name__ == '__main__':
    main()