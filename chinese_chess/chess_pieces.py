from abc import ABC, abstractmethod

class ChessPiece(ABC):
    def __init__(self, color, position):
        self.color = color
        self.position = position

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def is_valid_move(self, new_position, board):
        pass

class General(ChessPiece):
    def get_name(self):
        return "帥" if self.color == "red" else "將"

    def is_valid_move(self, new_position, board):
        if not board.is_within_palace(new_position, self.color):
            return False
        dx = abs(new_position[0] - self.position[0])
        dy = abs(new_position[1] - self.position[1])
        return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)

class Advisor(ChessPiece):
    def get_name(self):
        return "仕" if self.color == "red" else "士"

    def is_valid_move(self, new_position, board):
        if not board.is_within_palace(new_position, self.color):
            return False
        dx = abs(new_position[0] - self.position[0])
        dy = abs(new_position[1] - self.position[1])
        return dx == 1 and dy == 1

class Elephant(ChessPiece):
    def get_name(self):
        return "相" if self.color == "red" else "象"

    def is_valid_move(self, new_position, board):
        if (self.color == "red" and new_position[1] > 4) or (self.color == "black" and new_position[1] < 5):
            return False
        dx = abs(new_position[0] - self.position[0])
        dy = abs(new_position[1] - self.position[1])
        if dx != 2 or dy != 2:
            return False
        # Check if the elephant's eye is blocked
        eye_x = (self.position[0] + new_position[0]) // 2
        eye_y = (self.position[1] + new_position[1]) // 2
        return not board.is_piece_at((eye_x, eye_y))

class Horse(ChessPiece):
    def get_name(self):
        return "馬"

    def is_valid_move(self, new_position, board):
        dx = abs(new_position[0] - self.position[0])
        dy = abs(new_position[1] - self.position[1])
        if (dx == 2 and dy == 1) or (dx == 1 and dy == 2):
            # Check if the horse's leg is blocked
            leg_x = self.position[0] + (1 if new_position[0] > self.position[0] else -1) if dx == 2 else self.position[0]
            leg_y = self.position[1] + (1 if new_position[1] > self.position[1] else -1) if dy == 2 else self.position[1]
            return not board.is_piece_at((leg_x, leg_y))
        return False

class Chariot(ChessPiece):
    def get_name(self):
        return "車" if self.color == "red" else "俥"

    def is_valid_move(self, new_position, board):
        dx = new_position[0] - self.position[0]
        dy = new_position[1] - self.position[1]
        return (dx == 0 or dy == 0) and board.is_path_clear(self.position, new_position)

class Cannon(ChessPiece):
    def get_name(self):
        return "炮" if self.color == "red" else "包"

    def is_valid_move(self, new_position, board):
        if not board.is_within_board(new_position):
            return False

        dx = new_position[0] - self.position[0]
        dy = new_position[1] - self.position[1]

        if dx == 0 or dy == 0:  # Move in straight line
            pieces_between = board.count_pieces_between(self.position, new_position)
            target_piece = board.get_piece_at(new_position)

            if target_piece:
                # Capture: must jump over exactly one piece
                return pieces_between == 1 and target_piece.color != self.color
            else:
                # Move: path must be clear
                return pieces_between == 0

        return False

class Soldier(ChessPiece):
    def get_name(self):
        return "兵" if self.color == "red" else "卒"

    def is_valid_move(self, new_position, board):
        dx = new_position[0] - self.position[0]
        dy = new_position[1] - self.position[1]
        if self.color == "red":
            if self.position[1] < 5:  # Not crossed river
                return dx == 0 and dy == 1
            else:  # Crossed river
                return (dx == 0 and dy == 1) or (abs(dx) == 1 and dy == 0)
        else:  # black
            if self.position[1] > 4:  # Not crossed river
                return dx == 0 and dy == -1
            else:  # Crossed river
                return (dx == 0 and dy == -1) or (abs(dx) == 1 and dy == 0)