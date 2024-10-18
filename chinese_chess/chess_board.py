import pygame
import mlx.core as mx
from chess_pieces import General, Advisor, Elephant, Horse, Chariot, Cannon, Soldier

class ChessBoard:
    def __init__(self, width, height, red_at_bottom=True):
        self.red_at_bottom = red_at_bottom

        self.WIDTH = width
        self.HEIGHT = height
        self.BOARD_SIZE_W = 720
        self.BOARD_SIZE_H = 810
        self.MARGIN_W = (self.WIDTH - self.BOARD_SIZE_W) // 2
        self.MARGIN_H = (self.HEIGHT - self.BOARD_SIZE_H) // 2
        self.GRID_SIZE_W = self.BOARD_SIZE_W // 8
        self.GRID_SIZE_H = self.BOARD_SIZE_H // 9

        self.BACKGROUND_COLOR = (255, 248, 220)  # Light yellow
        self.LINE_COLOR = (200, 0, 0)  # Red
        self.MARK_COLOR = (200, 0, 0)  # Red

        self.font = pygame.font.Font("font/font2.ttf", 36)
        self.pieces = []
        self.setup_pieces()
        self.selected_piece = None
        self.dragging = False

        self.piece_to_channel = {
            "General": 0,
            "Advisor": 1,
            "Elephant": 2,
            "Horse": 3,
            "Chariot": 4,
            "Cannon": 5,
            "Soldier": 6
        }

    def get_state(self):
        state = mx.zeros((7, 9, 10))  # 7 kinds of chess pieces, 9 * 10 chess board
        for piece in self.pieces:
            x, y = piece.position
            piece_type = type(piece).__name__
            color = 1 if piece.color == "red" else -1
            channel = self.piece_to_channel[piece_type]
            state[channel, x, y] = color
        return state

    def setup_pieces(self):
        self.pieces = []
        bottom_color = "red" if self.red_at_bottom else "black"
        top_color = "black" if self.red_at_bottom else "red"

        # Bottom pieces
        self.pieces.extend([
            General(bottom_color, (4, 9)),
            Advisor(bottom_color, (3, 9)), Advisor(bottom_color, (5, 9)),
            Elephant(bottom_color, (2, 9)), Elephant(bottom_color, (6, 9)),
            Horse(bottom_color, (1, 9)), Horse(bottom_color, (7, 9)),
            Chariot(bottom_color, (0, 9)), Chariot(bottom_color, (8, 9)),
            Cannon(bottom_color, (1, 7)), Cannon(bottom_color, (7, 7)),
            Soldier(bottom_color, (0, 6)), Soldier(bottom_color, (2, 6)),
            Soldier(bottom_color, (4, 6)), Soldier(bottom_color, (6, 6)),
            Soldier(bottom_color, (8, 6)),
        ])

        # Top pieces
        self.pieces.extend([
            General(top_color, (4, 0)),
            Advisor(top_color, (3, 0)), Advisor(top_color, (5, 0)),
            Elephant(top_color, (2, 0)), Elephant(top_color, (6, 0)),
            Horse(top_color, (1, 0)), Horse(top_color, (7, 0)),
            Chariot(top_color, (0, 0)), Chariot(top_color, (8, 0)),
            Cannon(top_color, (1, 2)), Cannon(top_color, (7, 2)),
            Soldier(top_color, (0, 3)), Soldier(top_color, (2, 3)),
            Soldier(top_color, (4, 3)), Soldier(top_color, (6, 3)),
            Soldier(top_color, (8, 3)),
        ])

    def count_pieces_between(self, start, end):
        x1, y1 = start
        x2, y2 = end
        count = 0
        if x1 == x2:  # Vertical movement
            for y in range(min(y1, y2) + 1, max(y1, y2)):
                if self.is_piece_at((x1, y)):
                    count += 1
        elif y1 == y2:  # Horizontal movement
            for x in range(min(x1, x2) + 1, max(x1, x2)):
                if self.is_piece_at((x, y1)):
                    count += 1
        return count

    def is_within_board(self, position):
        x, y = position
        return 0 <= x <= 8 and 0 <= y <= 9

    def is_within_palace(self, position, color):
        x, y = position
        if (color == "red" and self.red_at_bottom) or (color == "black" and not self.red_at_bottom):
            return 3 <= x <= 5 and 7 <= y <= 9
        else:
            return 3 <= x <= 5 and 0 <= y <= 2

    def is_general_facing_general(self, new_position=None):
        red_general = next((p for p in self.pieces if isinstance(p, General) and p.color == "red"), None)
        black_general = next((p for p in self.pieces if isinstance(p, General) and p.color == "black"), None)

        if not red_general or not black_general:
            return False

        if new_position:
            if isinstance(self.get_piece_at(new_position), General):
                if self.get_piece_at(new_position).color == "red":
                    red_general.position = new_position
                else:
                    black_general.position = new_position

        if red_general.position[0] != black_general.position[0]:
            return False

        min_y = min(red_general.position[1], black_general.position[1])
        max_y = max(red_general.position[1], black_general.position[1])

        for y in range(min_y + 1, max_y):
            if self.get_piece_at((red_general.position[0], y)):
                return False

        return True

    def is_in_check(self, color):
        general = next((p for p in self.pieces if isinstance(p, General) and p.color == color), None)
        if not general:
            return False

        for piece in self.pieces:
            if piece.color != color and piece.is_valid_move(general.position, self):
                return True
        return False

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False

        general = next((p for p in self.pieces if isinstance(p, General) and p.color == color), None)
        for piece in self.pieces:
            if piece.color == color:
                for x in range(9):
                    for y in range(10):
                        if piece.is_valid_move((x, y), self):
                            # Try the move
                            original_position = piece.position
                            captured_piece = self.get_piece_at((x, y))
                            if captured_piece:
                                self.pieces.remove(captured_piece)
                            piece.position = (x, y)

                            still_in_check = self.is_in_check(color)

                            # Undo the move
                            piece.position = original_position
                            if captured_piece:
                                self.pieces.append(captured_piece)

                            if not still_in_check:
                                return False
        return True

    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False

        for piece in self.pieces:
            if piece.color == color:
                for x in range(9):
                    for y in range(10):
                        if piece.is_valid_move((x, y), self):
                            return False
        return True

    def is_piece_at(self, position):
        return any(piece.position == position for piece in self.pieces)

    def get_piece_at(self, position):
        for piece in self.pieces:
            if piece.position == position:
                return piece
        return None

    def is_path_clear(self, start, end):
        x1, y1 = start
        x2, y2 = end
        if x1 == x2:  # Vertical movement
            for y in range(min(y1, y2) + 1, max(y1, y2)):
                if self.is_piece_at((x1, y)):
                    return False
        elif y1 == y2:  # Horizontal movement
            for x in range(min(x1, x2) + 1, max(x1, x2)):
                if self.is_piece_at((x, y1)):
                    return False
        return True

    def is_general_captured(self):
        red_general = any(p for p in self.pieces if isinstance(p, General) and p.color == "red")
        black_general = any(p for p in self.pieces if isinstance(p, General) and p.color == "black")
        return not (red_general and black_general)

    def get_winner(self):
        if not any(p for p in self.pieces if isinstance(p, General) and p.color == "red"):
            return "black"
        if not any(p for p in self.pieces if isinstance(p, General) and p.color == "black"):
            return "red"
        return None

    def update_piece_position(self, piece, new_position):
        piece.position = new_position

    def get_piece_at_pos(self, pos):
        for piece in self.pieces:
            x = self.MARGIN_W + piece.position[0] * self.GRID_SIZE_W
            y = self.MARGIN_H + piece.position[1] * self.GRID_SIZE_H
            if ((pos[0] - x) ** 2 + (pos[1] - y) ** 2) <= 30 ** 2:
                return piece
        return None

    def draw(self, screen, mouse_pos):
        screen.fill(self.BACKGROUND_COLOR)

        # Draw vertical lines
        for i in range(9):
            x = self.MARGIN_W + i * self.GRID_SIZE_W
            if i == 0 or i == 8:
                pygame.draw.line(screen, self.LINE_COLOR, (x, self.MARGIN_H), (x, self.HEIGHT - self.MARGIN_H), 2)
            else:
                pygame.draw.line(screen, self.LINE_COLOR, (x, self.MARGIN_H), (x, self.MARGIN_H + self.GRID_SIZE_H * 4), 2)
                pygame.draw.line(screen, self.LINE_COLOR, (x, self.MARGIN_H + self.GRID_SIZE_H * 5), (x, self.HEIGHT - self.MARGIN_H), 2)

        # Draw horizontal lines
        for i in range(10):
            y = self.MARGIN_H + i * self.GRID_SIZE_H
            pygame.draw.line(screen, self.LINE_COLOR, (self.MARGIN_W, y), (self.WIDTH - self.MARGIN_W, y), 2)

        # Draw diagonal lines in the palace
        pygame.draw.line(screen, self.LINE_COLOR, (self.MARGIN_W + 3 * self.GRID_SIZE_W, self.MARGIN_H),
                         (self.MARGIN_W + 5 * self.GRID_SIZE_W, self.MARGIN_H + 2 * self.GRID_SIZE_H), 2)
        pygame.draw.line(screen, self.LINE_COLOR, (self.MARGIN_W + 5 * self.GRID_SIZE_W, self.MARGIN_H),
                         (self.MARGIN_W + 3 * self.GRID_SIZE_W, self.MARGIN_H + 2 * self.GRID_SIZE_H), 2)
        pygame.draw.line(screen, self.LINE_COLOR, (self.MARGIN_W + 3 * self.GRID_SIZE_W, self.HEIGHT - self.MARGIN_H),
                         (self.MARGIN_W + 5 * self.GRID_SIZE_W, self.HEIGHT - self.MARGIN_H - 2 * self.GRID_SIZE_H), 2)
        pygame.draw.line(screen, self.LINE_COLOR, (self.MARGIN_W + 5 * self.GRID_SIZE_W, self.HEIGHT - self.MARGIN_H),
                         (self.MARGIN_W + 3 * self.GRID_SIZE_W, self.HEIGHT - self.MARGIN_H - 2 * self.GRID_SIZE_H), 2)

        # Draw "river" text
        text = self.font.render("楚河            漢界", True, self.LINE_COLOR)
        text_rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        screen.blit(text, text_rect)

        # Mark positions for soldiers/pawns and cannons
        mark_positions = [
            # Black soldiers (卒)
            (0, 3), (2, 3), (4, 3), (6, 3), (8, 3),
            # Red soldiers (兵)
            (0, 6), (2, 6), (4, 6), (6, 6), (8, 6),
            # Black cannons (砲)
            (1, 2), (7, 2),
            # Red cannons (砲)
            (1, 7), (7, 7)
        ]

        for col, row in mark_positions:
            x = self.MARGIN_W + col * self.GRID_SIZE_W + 1
            y = self.MARGIN_H + row * self.GRID_SIZE_H
            pygame.draw.circle(screen, self.MARK_COLOR, (x, y), 6)

        for piece in self.pieces:
            if piece == self.selected_piece and self.dragging:
                x, y = mouse_pos
            else:
                x = self.MARGIN_W + piece.position[0] * self.GRID_SIZE_W
                y = self.MARGIN_H + piece.position[1] * self.GRID_SIZE_H
            color = (255, 0, 0) if piece.color == "red" else (0, 0, 0)
            pygame.draw.circle(screen, (255, 255, 255), (x, y), 30)  # White background
            pygame.draw.circle(screen, color, (x, y), 30, 2)  # Colored border
            text = self.font.render(piece.get_name(), True, color)
            text_rect = text.get_rect(center=(x, y))
            screen.blit(text, text_rect)

    def get_state(self):
        # 將棋盤狀態轉換為神經網絡的輸入格式
        state = mx.zeros((9, 9, 10))
        for piece in self.pieces:
            x, y = piece.position
            piece_type = type(piece).__name__
            color = 1 if piece.color == "red" else -1
            channel = self.piece_to_channel[piece_type]
            state[channel, x, y] = color
        return state

    def get_legal_moves(self, color):
        # 獲取所有合法移動
        legal_moves = []
        for piece in self.pieces:
            if piece.color == color:
                for x in range(9):
                    for y in range(10):
                        if piece.is_valid_move((x, y), self):
                            legal_moves.append((piece.position, (x, y)))
        return legal_moves

    def make_move(self, move):
        from_pos, to_pos = move
        piece = self.get_piece_at(from_pos)
        if piece:
            captured_piece = self.get_piece_at(to_pos)
            if captured_piece:
                self.pieces.remove(captured_piece)
            self.update_piece_position(piece, to_pos)

    def is_game_over(self):
        return self.is_checkmate("red") or self.is_checkmate("black") or self.is_stalemate("red") or self.is_stalemate(
            "black")

