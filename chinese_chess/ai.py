import mlx.core as mx
import mlx.nn as nn
import math

class ChessNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(7, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(128 * 9 * 10, 512)
        self.fc2 = nn.Linear(512, 256)
        self.policy_head = nn.Linear(256, 9 * 10 * 9 * 10)
        self.value_head = nn.Linear(256, 1)

    def __call__(self, x):
        x = nn.relu(self.conv1(x))
        x = nn.relu(self.conv2(x))
        x = nn.relu(self.conv3(x))
        x = x.reshape(-1, 128 * 9 * 10)
        x = nn.relu(self.fc1(x))
        x = nn.relu(self.fc2(x))
        policy = self.policy_head(x)
        value = mx.tanh(self.value_head(x))
        return policy, value

class MCTSNode:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.value = 0

class MCTS:
    def __init__(self, model, num_simulations=800, c_puct=1.0):
        self.model = model
        self.num_simulations = num_simulations
        self.c_puct = c_puct

    def get_action(self, state, legal_moves):
        root = MCTSNode(state)

        for _ in range(self.num_simulations):
            node = root
            search_path = [node]

            while node.children:
                node = self.select_child(node)
                search_path.append(node)

            # 確保輸入形狀正確
            model_input = mx.array(node.state)
            model_input = mx.transpose(model_input, (1, 2, 0))  # 從 (7, 9, 10) 轉換為 (9, 10, 7)
            model_input = mx.reshape(model_input, (1, 9, 10, 9))  # 添加批次維度
            policy, value = self.model(model_input)
            policy = mx.reshape(policy, (9, 10, 9, 10))
            value = value.item()

            self.expand(node, policy, legal_moves)
            self.backpropagate(search_path, value)

        return max(root.children, key=lambda c: c.visits).action

    def select_child(self, node):
        return max(node.children, key=lambda c: self.ucb_score(node, c))

    def ucb_score(self, parent, child):
        q_value = 1 - ((child.value / child.visits) + 1) / 2
        return q_value + self.c_puct * math.sqrt(parent.visits) / (1 + child.visits)

    def expand(self, node, policy, legal_moves):
        for move in legal_moves:
            from_pos, to_pos = move
            action_prob = policy[from_pos[0], from_pos[1], to_pos[0], to_pos[1]].item()
            child_state = self.apply_move(node.state, move)
            child = MCTSNode(child_state, parent=node, action=move)
            node.children.append(child)

    def backpropagate(self, search_path, value):
        for node in reversed(search_path):
            node.visits += 1
            node.value += value
            value = 1 - value

    def apply_move(self, state, move):
        # 這裡需要實現移動棋子後的新狀態
        # 為了簡化，這裡返回原狀態，實際應用中需要修改
        return state

def train_network(model, games):
    optimizer = mx.optimizer.Adam(learning_rate=0.001)

    @mx.compile
    def train_step(model, inputs, policy_targets, value_targets):
        def loss_fn(model, inputs, policy_targets, value_targets):
            policy_outputs, value_outputs = model(inputs)
            policy_loss = mx.mean(mx.losses.categorical_crossentropy(policy_targets, policy_outputs))
            value_loss = mx.mean(mx.losses.mean_squared_error(value_targets, value_outputs))
            return policy_loss + value_loss

        loss, grads = mx.value_and_grad(loss_fn)(model, inputs, policy_targets, value_targets)
        optimizer.update(model, grads)
        return loss

    for game in games:
        states, policy_targets, value_targets = process_game(game)
        loss = train_step(model, states, policy_targets, value_targets)
        print(f"Loss: {loss.item()}")

def process_game(game):
    # 將遊戲數據轉換為訓練數據
    # 這裡需要實現將遊戲狀態轉換為神經網絡輸入的邏輯
    # 為了簡化，這裡返回空數據，實際應用中需要修改
    return mx.array([]), mx.array([]), mx.array([])