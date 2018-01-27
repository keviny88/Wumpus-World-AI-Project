# ======================================================================
# FILE:        MyAI.py
#
# AUTHOR:      Abdullah Younis
#
# DESCRIPTION: This file contains your agent class, which you will
#              implement. You are responsible for implementing the
#              'getAction' function and any helper methods you feel you
#              need.
#
# NOTES:       - If you are having trouble understanding how the shell
#                works, look at the other parts of the code, as well as
#                the documentation.
#
#              - You are only allowed to make changes to this portion of
#                the code. Any changes to other portions of the code will
#                be lost when the tournament runs your code.
# ======================================================================

from Agent import Agent
from collections import deque

class Square:

    def __init__(self):
        self.visited = False
        self.empty = False
        self.wumpus = 0
        self.pit = 0
        self.count = 0
        self.adj_danger = 0
        self.wumpus_killed = False


    def score(self):
        score= 0
        if self.wumpus_killed:
            score += 5
        if self.empty:
            score += 10
        if not self.visited:
            score += 5
        score -= self.wumpus
        score -= self.pit
        score -= self.count
        score -= self.adj_danger
        return score


class Board:


    def __init__(self):
        self.max_row = 9
        self.max_col = 9
        self.row = 9
        self.col = 9
        self.perm_height = False
        self.perm_width = False
        self.location = [0,0]
        self.board = [[Square() for j in range(self.max_col)] for i in range(self.max_row)]
        self.total_visited = 1

    def update_location(self, new_location):
        self.location = new_location

    def print_board(self):
        """
        Prints our current knowledge of game board
        """
        print("row: " + str(self.col))
        print("col: " + str(self.row))
        top_line = "     "
        for c in range(self.col):
            top_line += str(c) + "   "
        for row in range(self.row-1,-1,-1):
        # for row in range(self.row):
            line = str(row) + "  "
            for col in range(self.col):
                if [row,col] == self.location:
                    line += "[ @]"
                else:
                    score = str(self.board[row][col].score())
                    if len(score) == 2:
                        line = line + "[" + str(self.board[row][col].score()) + "]"
                    else:
                        line = line + "[ " + str(self.board[row][col].score()) + "]"
            print(line)
        print(top_line + '\n');

    def get_possible(self):
        """
        Returns list of possible square coordinates to update
        return = [right, down, left, up]
        """
        poss_coords = [(self.location[0], self.location[1] + 1, 0) , (self.location[0] - 1, self.location[1], 1),
                       (self.location[0], self.location[1] - 1, 2), (self.location[0] + 1, self.location[1], 3)]
        coords = []
        for row,col,dir in poss_coords:
            add = True
            if (row >= 0) and (col >= 0):
                # Failed width check
                # print(row,col)
                # print("checking perm width: ", self.perm_width, col, self.col)
                if self.perm_width and col >= self.col:
                    # print("FAILED WITDH ", "self.perm_width " ,self.perm_width, " row < self.row", row < self.row)
                    add = False
                if self.perm_height and row >= self.row:
                    # print("FAILED HEIGHT ", "self.perm_height ", self.perm_height, " col < self.col", col < self.col)
                    add = False
                if add:
                    # print("added ", (row,col))
                    coords.append([row,col,dir])
        # print(coords)
        return coords

    def get_surr_avg(self, r, c):
        """
        Returns list of possible square coordinates to update
        return = [right, down, left, up]
        """
        poss_coords = [(r, c + 1, 0) , (r - 1, c, 1),
                       (r, c - 1, 2), (r + 1, c, 3)]
        size= 0
        total = 0
        for row,col,dir in poss_coords:
            add = True
            if (row >= 0) and (col >= 0):
                # Failed width check
                # print(row,col)
                # print("checking perm width: ", self.perm_width, col, self.col)
                if self.perm_width and col >= self.col:
                    # print("FAILED WITDH ", "self.perm_width " ,self.perm_width, " row < self.row", row < self.row)
                    add = False
                if self.perm_height and row >= self.row:
                    # print("FAILED HEIGHT ", "self.perm_height ", self.perm_height, " col < self.col", col < self.col)
                    add = False
                if add:
                    # print("added ", (row,col))
                    total += self.board[row][col].score()
                    size += 1
        # print(coords)
        return total/size

    def update_probabilities(self, stench, breeze, scream, prev_move, direction, prev_location):
        coords = self.get_possible()

        # update probability of current if all adjacent squares are bad options


        self.board[self.location[0]][self.location[1]].count += 2
        if scream:
            print("scream heard, wumpus dead")
            self.wumpus_dead()
        elif not scream and prev_move == Agent.Action.SHOOT:
            print("no scream but shot")
            if self.location == [0,0]:
                print("****** starting shot but missed *******")
                self.wumpus_dead()
                self.board[0][1].wumpus = 20
            else:
                # If we shoot and miss, but are not at start
                # Setting the coordinate in front of us (that we missed at), the wumpus value to False
                print("MISSED, BUT ASSUME WUMPUS LOCATION")
                if direction == 0:
                    self.board[self.location[0]][self.location[1] + 1].wumpus = False
                elif direction == 1:
                    self.board[self.location[0]-1][self.location[1]].wumpus = False
                elif direction == 2:
                    self.board[self.location[0]][self.location[1] - 1].wumpus = False
                elif direction == 3:
                    self.board[self.location[0]+1][self.location[1]].wumpus = False

                #Taking a list of coordinates, and setting the next highest wumpus value assumed to be much higher

                scores = []
                for coord in coords:
                    scores.append(self.board[coord[0]][coord[1]].wumpus)
                max_score = scores[0]
                max_index = 0
                for i in range(1, len(scores)):
                    if scores[i] > max_score:
                        max_score = scores[i]
                        max_index = i

                target_coord = coords[max_index]
                self.board[target_coord[0]][target_coord[1]].wumpus += 20
                return

        if self.board[self.location[0]][self.location[1]].visited is not True:
            self.board[self.location[0]][self.location[1]].wumpus_killed = False
            self.total_visited += 1
            self.board[self.location[0]][self.location[1]].visited = True
            self.board[self.location[0]][self.location[1]].empty = True
            for i in range(len(coords)):
                square = self.board[coords[i][0]][coords[i][1]]
                if not square.visited or not square.empty:
                    if stench and square.wumpus is not False:
                        print("STENCH")
                        square.wumpus += 3
                    elif not stench:
                        square.wumpus = False
                    if breeze and square.pit is not False:
                        print("BREEZE")
                        square.pit += 3
                    elif not breeze:
                        square.pit = False
                    if not stench and not breeze:
                        square.empty = True
                        # square.pit = 0
                        # square.wumpus = 0
            adj_danger = True
            for coord in coords:
                if coord[:2] != prev_location and self.board[coord[0]][coord[1]].score() >= 5:
                    adj_danger = False
            if adj_danger:
                print("adj danger found ***************************************")
                self.board[self.location[0]][self.location[1]].adj_danger += 0

    def wumpus_dead(self):
        for row in self.board:
            for square in row:
                if square.wumpus >= 2 and square.pit == False:
                    square.wumpus_killed = True
                    square.empty = True
                square.wumpus = False


class MyAI ( Agent ):
    # 0 right, 1 down, 2 left, 3 up

    def __init__ ( self ):
        self.board = Board()
        self.direction = 0
        self.hasArrow = True
        self.score = 0
        self.prev_location = [-1, -1]
        self.prev_move = None
        self.current_location = [0,0]
        self.return_stack = [[0,0]]
        self.move_queue = deque()
        self.foundGold = False

    def get_limit(self):
        if self.board.total_visited < 4:
            return 3
        elif self.board.total_visited < 8 and self.board.total_visited >= 4:
            return 6
        else:
            return 6

    def getAction( self, stench, breeze, glitter, bump, scream ):
        if self.prev_location == [-1, -1] and (breeze):
            # print("CLIMBING OUT!!!")
            return Agent.Action.CLIMB
        elif self.prev_location == [-1,-1] and stench:
            print("shot at start ---------")
            self.shoot_at([1,0])
        self.update_board()
        self.update_location(bump)
        count_visited = self.board.board[self.current_location[0]][self.current_location[1]].count
        if self.foundGold and self.current_location == [0,0]:
            print("CLIMBING OUT!!!")
            return Agent.Action.CLIMB
        elif glitter:
            print("FOUND GOLD GLITTER")
            self.foundGold = True
            self.move_queue.clear()
            # self.return_stack.append(Agent.Action.TURN_LEFT)
            # self.return_stack.append(Agent.Action.TURN_LEFT)
            self.prev_move = Agent.Action.GRAB
            return self.prev_move
        elif self.move_queue:
            # print("MOVE QUEUE EXISTS: before pop ", len(self.move_queue))
            self.prev_move = self.move_queue.popleft()
            # self.add_return(self.prev_move)
            return self.prev_move
        elif self.foundGold:
            print("RETURNING")
            if self.current_location == self.return_stack[-1] and len(self.return_stack) > 1:
                # print("popping off return ", self.return_stack[-1])
                self.return_stack.pop()
            return self.move_to(self.return_stack.pop())
        elif count_visited >= self.get_limit():
            self.foundGold = True
            # self.move_queue.append(Agent.Action.TURN_LEFT)
            # self.prev_move = Agent.Action.TURN_LEFT
            if self.current_location == self.return_stack[-1] and len(self.return_stack) > 1:
                # print("popping off return ", self.return_stack[-1])
                self.return_stack.pop()
            self.move_to(self.return_stack.pop())
            return self.prev_move
        else:
            self.board.update_probabilities(stench, breeze, scream, self.prev_move, self.direction, self.prev_location)
            coords = self.board.get_possible()
            self.choose_move(coords)
            # self.add_return(self.prev_move)
        return self.prev_move

    def add_return(self, move):
        if move == Agent.Action.FORWARD:
            self.return_stack.append(move)
        elif move == Agent.Action.TURN_LEFT:
            self.return_stack.append(Agent.Action.TURN_RIGHT)
        elif move == Agent.Action.TURN_RIGHT:
            self.return_stack.append(Agent.Action.TURN_LEFT)





    # ======================================================================
    # Helper functions
    # ======================================================================
    #Updates the board location values to match AI
    def update_board(self):
        self.board.update_location(self.current_location)

    #Updates the current location and prev location values
    def update_location(self, bump):
        self.prev_location = [self.current_location[0], self.current_location[1]]
        if bump:
            print("BUMP")
            if self.direction == 0:
                self.board.perm_width = True
                self.board.col = self.current_location[1] + 1
            elif self.direction == 3:
                self.board.perm_height = True
                self.board.row = self.current_location[0] + 1
        elif self.prev_move == Agent.Action.FORWARD:
            print("MOVING FORWARD")
            if self.direction == 0:
                self.current_location[1] += 1
            elif self.direction == 1:
                self.current_location[0] -= 1
            elif self.direction == 2:
                self.current_location[1] -= 1
            else:
                self.current_location[0] += 1
        elif self.prev_move == Agent.Action.TURN_RIGHT:
            print("TURNING RIGHT")
            self.direction += 1
            self.direction %= 4
        elif self.prev_move == Agent.Action.TURN_LEFT:
            print("TURNING LEFT")
            self.direction -= 1
            if self.direction == -1:
                self.direction = 3
        elif (self.prev_move == Agent.Action.GRAB) or (self.prev_move == Agent.Action.SHOOT):
            # print("shot or grabbed")
            pass

        # print("previous: " + str(self.prev_location))
        # print("current: " + str(self.current_location))
        # print("has arrow: ", self.hasArrow)

        if self.prev_location != self.current_location:
            # print("before: ", self.return_stack)
            try:
                index = self.return_stack.index(self.current_location)
                # print("index ", index, self.return_stack[:index+1])
                self.return_stack = self.return_stack[:index+1]
            except:
                self.return_stack.append(list(self.current_location))
            # print("after: ", self.return_stack)

        # self.board.print_board()

    def choose_move(self,coord_list):
        # 0 right, 1 down, 2 left, 3 up
        if self.hasArrow:
            for coord in coord_list:
                if self.board.board[coord[0]][coord[1]].wumpus >= 6:
                    return self.shoot_at(coord)

        forward_score = 0
        scores = []
        for coord in coord_list:
            s = self.board.board[coord[0]][coord[1]].score()

            # If a score is below 5, do not add average, effectively eliminiating it as a choice
            if s >= 5:
                s += self.board.get_surr_avg(coord[0], coord[1])

            if self.direction == coord[2]:
                forward_score = coord[:2] + [s]
            scores.append(s)
        max_score = scores[0]
        max_index = 0
        for i in range(1,len(scores)):
            if scores[i] > max_score:
                max_score = scores[i]
                max_index = i
        if forward_score != 0 and max_score == forward_score[2]:
            target_coord = forward_score[:2]
        else:
            target_coord = coord_list[max_index]
        return self.move_to(target_coord)

        # moves = deque()

    def move_to(self, target_coord):
        if self.current_location == target_coord:
            # print("(climbing)Target same as current: ", target_coord)
            self.prev_move = Agent.Action.CLIMB
            return self.prev_move
        target_direction = None
        r = target_coord[0] - self.current_location[0]
        c = target_coord[1] - self.current_location[1]
        if r == 1:
            target_direction = 3
        elif r == -1:
            target_direction = 1
        elif c == 1:
            target_direction = 0
        elif c == -1:
            target_direction = 2

        if target_direction == self.direction:

            self.prev_move = Agent.Action.FORWARD
        elif ((target_direction + 1) % 4) == self.direction:
            self.move_queue.append(Agent.Action.FORWARD)
            self.prev_move = Agent.Action.TURN_LEFT
        elif ((target_direction - self.direction) % 4) == 2:
            self.move_queue.append(Agent.Action.TURN_RIGHT)
            self.move_queue.append(Agent.Action.FORWARD)
            self.prev_move = Agent.Action.TURN_RIGHT
        elif ((self.direction + 1) % 4) == target_direction:
            self.move_queue.append(Agent.Action.FORWARD)
            self.prev_move = Agent.Action.TURN_RIGHT

        return self.prev_move

    def shoot_at(self, target_coord):
        print("shooting at square %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%", target_coord)
        self.hasArrow = False
        r = target_coord[0] - self.current_location[0]
        c = target_coord[1] - self.current_location[1]
        if r == 1:
            target_direction = 3
        elif r == -1:
            target_direction = 1
        elif c == 1:
            target_direction = 0
        elif c == -1:
            target_direction = 2

        if target_direction == self.direction:

            self.prev_move = Agent.Action.SHOOT
        elif ((target_direction + 1) % 4) == self.direction:
            self.move_queue.append(Agent.Action.SHOOT)
            self.prev_move = Agent.Action.TURN_LEFT
        elif ((target_direction - self.direction) % 4) == 2:
            self.move_queue.append(Agent.Action.TURN_RIGHT)
            self.move_queue.append(Agent.Action.SHOOT)
            self.prev_move = Agent.Action.TURN_RIGHT
        elif ((self.direction + 1) % 4) == target_direction:
            self.move_queue.append(Agent.Action.SHOOT)
            self.prev_move = Agent.Action.TURN_RIGHT

        return self.prev_move







