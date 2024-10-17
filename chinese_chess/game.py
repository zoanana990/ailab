import pygame
import sys
from chess_board import ChessBoard

class GameWindow:
    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Chinese Chess")
        self.board = ChessBoard(self.width, self.height)
        self.current_player = "red"  # Red moves first
        self.font = pygame.font.Font(None, 36)

    def run(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        piece = self.board.get_piece_at_pos(event.pos)
                        if piece and piece.color == self.current_player:
                            self.board.selected_piece = piece
                            self.board.dragging = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left mouse button
                        self.board.dragging = False
                        if self.board.selected_piece:
                            new_pos = self.get_board_position(event.pos)
                            if new_pos and self.board.selected_piece.is_valid_move(new_pos, self.board):
                                self.make_move(new_pos)
                            self.board.selected_piece = None

            self.board.draw(self.screen, mouse_pos)
            self.draw_current_player()
            pygame.display.flip()

    def make_move(self, new_pos):
        original_position = self.board.selected_piece.position
        captured_piece = self.board.get_piece_at(new_pos)
        if captured_piece:
            self.board.pieces.remove(captured_piece)
        self.board.update_piece_position(self.board.selected_piece, new_pos)

        if self.board.is_general_facing_general():
            print(f"{self.current_player.capitalize()} loses due to exposing their general!")
            self.end_game(self.get_opposite_color(self.current_player))
        elif self.board.is_checkmate(self.get_opposite_color(self.current_player)):
            print(f"{self.current_player.capitalize()} wins by checkmate!")
            self.end_game(self.current_player)
        elif self.board.is_stalemate(self.get_opposite_color(self.current_player)):
            print("The game is a draw due to stalemate!")
            self.end_game(None)
        else:
            self.current_player = self.get_opposite_color(self.current_player)

    def get_opposite_color(self, color):
        return "black" if color == "red" else "red"

    def end_game(self, winner):
        if winner:
            print(f"{winner.capitalize()} wins the game!")
        else:
            print("The game is a draw!")
        pygame.quit()
        sys.exit()

    def get_board_position(self, screen_pos):
        x = round((screen_pos[0] - self.board.MARGIN_W) / self.board.GRID_SIZE_W)
        y = round((screen_pos[1] - self.board.MARGIN_H) / self.board.GRID_SIZE_H)
        if 0 <= x <= 8 and 0 <= y <= 9:
            return (x, y)
        return None

    def draw_current_player(self):
        text = self.font.render(f"Current Player: {self.current_player.capitalize()}", True, (0, 0, 0))
        self.screen.blit(text, (10, 10))