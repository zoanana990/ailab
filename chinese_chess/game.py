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
        self.font = pygame.font.Font(None, 36)
        self.mode = None
        self.setup_mode_selection()

    def setup_mode_selection(self):
        self.buttons = [
            {"text": "Human vs AI", "rect": pygame.Rect(250, 300, 300, 50), "color": (200, 200, 200)},
            {"text": "Human vs Human", "rect": pygame.Rect(250, 370, 300, 50), "color": (200, 200, 200)},
            {"text": "AI Training", "rect": pygame.Rect(250, 440, 300, 50), "color": (200, 200, 200)}
        ]

    def draw_mode_selection(self):
        self.screen.fill((255, 255, 255))
        for button in self.buttons:
            pygame.draw.rect(self.screen, button["color"], button["rect"])
            text = self.font.render(button["text"], True, (0, 0, 0))
            text_rect = text.get_rect(center=button["rect"].center)
            self.screen.blit(text, text_rect)
        pygame.display.flip()

    def handle_mode_selection(self, pos):
        for button in self.buttons:
            if button["rect"].collidepoint(pos):
                if button["text"] == "Human vs Human":
                    self.mode = "human_vs_human"
                    self.start_game()
                elif button["text"] == "Human vs AI":
                    print("Human vs AI mode not implemented yet")
                elif button["text"] == "AI Training":
                    print("AI Training mode not implemented yet")

    def start_game(self):
        self.red_at_bottom = True
        self.board = ChessBoard(self.width, self.height, self.red_at_bottom)
        self.current_player = "red"
        self.game_over = False

    def reset_game(self):
        if self.game_over:
            self.red_at_bottom = not self.red_at_bottom
            self.current_player = "black" if self.current_player == "red" else "red"
        self.board = ChessBoard(self.width, self.height, self.red_at_bottom)
        self.game_over = False

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.mode is None:
                        self.handle_mode_selection(event.pos)
                    elif self.game_over:
                        self.reset_game()
                    elif event.button == 1:  # Left mouse button
                        self.handle_game_click(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP and not self.game_over and self.mode:
                    if event.button == 1:  # Left mouse button
                        self.handle_game_release(event.pos)

            if self.mode is None:
                self.draw_mode_selection()
            else:
                self.draw_game()

    def handle_game_click(self, pos):
        piece = self.board.get_piece_at_pos(pos)
        if piece and piece.color == self.current_player:
            self.board.selected_piece = piece
            self.board.dragging = True

    def handle_game_release(self, pos):
        self.board.dragging = False
        if self.board.selected_piece:
            new_pos = self.get_board_position(pos)
            if new_pos and self.board.selected_piece.is_valid_move(new_pos, self.board):
                self.make_move(new_pos)
            self.board.selected_piece = None

    def draw_game(self):
        self.board.draw(self.screen, pygame.mouse.get_pos())
        self.draw_current_player()
        if self.game_over:
            self.draw_game_over_message()
        pygame.display.flip()

    def make_move(self, new_pos):
        original_position = self.board.selected_piece.position
        captured_piece = self.board.get_piece_at(new_pos)
        if captured_piece:
            self.board.pieces.remove(captured_piece)
        self.board.update_piece_position(self.board.selected_piece, new_pos)

        if self.board.is_general_captured():
            self.game_over = True
            self.winner = self.get_opposite_color(self.current_player)
        elif self.board.is_general_facing_general(new_pos):
            self.game_over = True
            self.winner = self.get_opposite_color(self.current_player)
        else:
            self.current_player = self.get_opposite_color(self.current_player)

    def get_opposite_color(self, color):
        return "black" if color == "red" else "red"

    def get_board_position(self, screen_pos):
        x = round((screen_pos[0] - self.board.MARGIN_W) / self.board.GRID_SIZE_W)
        y = round((screen_pos[1] - self.board.MARGIN_H) / self.board.GRID_SIZE_H)
        if 0 <= x <= 8 and 0 <= y <= 9:
            return (x, y)
        return None

    def draw_current_player(self):
        text = self.font.render(f"Current Player: {self.current_player.capitalize()}", True, (0, 0, 0))
        self.screen.blit(text, (10, 10))

    def draw_game_over_message(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        message = f"{self.winner.capitalize()} wins the game!"
        text = self.font.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2 - 20))
        self.screen.blit(text, text_rect)

        instruction = "Click anywhere to start a new game"
        instruction_text = self.font.render(instruction, True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect(center=(self.width // 2, self.height // 2 + 20))
        self.screen.blit(instruction_text, instruction_rect)