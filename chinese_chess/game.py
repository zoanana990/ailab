import pygame
import sys
import os
import mlx.core as mx
from chess_board import ChessBoard
from ai import ChessNet, MCTS, train_network

class GameWindow:
    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Chinese Chess")
        self.font = pygame.font.Font(None, 36)
        self.mode = None
        self.board = None
        self.current_player = None
        self.game_over = False
        self.winner = None
        self.setup_mode_selection()
        self.ai_training = False
        self.ai_game_count = 0
        self.model_red = ChessNet()
        self.model_black = ChessNet()
        self.mcts_red = MCTS(self.model_red)
        self.mcts_black = MCTS(self.model_black)

    def start_ai_training(self):
        self.ai_training = True
        self.training_games = []
        self.ai_game_count = 0
        self.board = ChessBoard(self.width, self.height)
        self.current_player = "red"

    def play_ai_vs_ai_game(self):
        if not self.board.is_game_over():
            state = self.board.get_state()
            legal_moves = self.board.get_legal_moves(self.current_player)
            if self.current_player == "red":
                action = self.mcts_red.get_action(state, legal_moves)
            else:
                action = self.mcts_black.get_action(state, legal_moves)

            # 执行移动
            self.board.make_move(action)

            # 切换玩家
            self.current_player = self.get_opposite_color(self.current_player)

            # 绘制当前游戏状态
            self.draw_game()
            pygame.display.flip()
            pygame.time.wait(500)  # 添加短暂延迟，使得棋局变化可见
        else:
            # 游戏结束，记录游戏状态并开始新游戏
            self.training_games.append(self.board.get_game_history())
            self.ai_game_count += 1
            self.board = ChessBoard(self.width, self.height)
            self.current_player = "red"

            if self.ai_game_count % 10 == 0:  # 每10局游戏训练一次
                train_network(self.model_red, self.training_games)
                train_network(self.model_black, self.training_games)
                self.save_models()
                self.training_games = []  # 清空训练游戏列表

    def setup_mode_selection(self):
        self.buttons = [
            {"text": "Human vs AI", "rect": pygame.Rect(250, 300, 300, 50), "color": (200, 200, 200)},
            {"text": "Human vs Human", "rect": pygame.Rect(250, 370, 300, 50), "color": (200, 200, 200)},
            {"text": "AI Training", "rect": pygame.Rect(250, 440, 300, 50), "color": (200, 200, 200)}
        ]

    def play_ai_game(self):
        self.board = ChessBoard(self.width, self.height)
        game_states = []
        current_player = "red"

        while not self.board.is_game_over():
            state = self.board.get_state()
            legal_moves = self.board.get_legal_moves(current_player)
            action = self.mcts.get_action(state, legal_moves)
            self.board.make_move(action)
            game_states.append((state, action, current_player))
            current_player = self.get_opposite_color(current_player)

        return game_states

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
                    self.mode = "ai_training"
                    self.start_ai_training()

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
        clock = pygame.time.Clock()
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
                    elif event.button == 1 and self.mode == "human_vs_human":  # Left mouse button
                        self.handle_game_click(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP and not self.game_over and self.mode == "human_vs_human":
                    if event.button == 1:  # Left mouse button
                        self.handle_game_release(event.pos)

            if self.mode is None:
                self.draw_mode_selection()
            elif self.mode == "human_vs_human":
                self.draw_game()
            elif self.mode == "ai_training" and self.ai_training:
                self.play_ai_vs_ai_game()
                self.draw_ai_training_info()

            pygame.display.flip()
            clock.tick(60)

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

    def draw_ai_training_info(self):
        info_surface = pygame.Surface((200, 100))
        info_surface.fill((255, 255, 255))
        font = pygame.font.Font(None, 24)
        text = font.render(f"Games: {self.ai_game_count}", True, (0, 0, 0))
        info_surface.blit(text, (10, 10))
        text = font.render(f"Player: {self.current_player}", True, (0, 0, 0))
        info_surface.blit(text, (10, 40))
        self.screen.blit(info_surface, (self.width - 210, 10))

    def save_models(self):
        if not os.path.exists('models'):
            os.makedirs('models')
        mx.save('models/model_red.npz', self.model_red.parameters())
        mx.save('models/model_black.npz', self.model_black.parameters())
        print(f"Models saved after {self.ai_game_count} games")

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