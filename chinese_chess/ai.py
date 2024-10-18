import math
import mlx.core as mx

def manual_conv2d(x, weight, bias):
    batch, in_channels, height, width = x.shape
    out_channels, in_channels, kernel_height, kernel_width = weight.shape

    padded_x = mx.pad(x, ((0, 0), (0, 0), (1, 1), (1, 1)), mode='constant')

    output = mx.zeros((batch, out_channels, height, width))

    for i in range(height):
        for j in range(width):
            patch = padded_x[:, :, i:i+kernel_height, j:j+kernel_width]
            for c in range(out_channels):
                output[:, c, i, j] = mx.sum(patch * weight[c], axis=(1, 2, 3))

    return output + bias.reshape(1, -1, 1, 1)

def manual_linear(x, weight, bias):
    return mx.matmul(x, weight.T) + bias

class ChessNet:
    def __init__(self):
        # 卷積層權重和偏置
        self.conv1_weight = mx.random.normal((32, 1, 3, 3))
        self.conv1_bias = mx.zeros((32,))
        self.conv2_weight = mx.random.normal((64, 32, 3, 3))
        self.conv2_bias = mx.zeros((64,))
        self.conv3_weight = mx.random.normal((128, 64, 3, 3))
        self.conv3_bias = mx.zeros((128,))

        # 全連接層權重和偏置
        self.fc1_weight = mx.random.normal((512, 128 * 9 * 90))
        self.fc1_bias = mx.zeros((512,))
        self.fc2_weight = mx.random.normal((256, 512))
        self.fc2_bias = mx.zeros((256,))
        self.policy_head_weight = mx.random.normal((9 * 10 * 9 * 10, 256))
        self.policy_head_bias = mx.zeros((9 * 10 * 9 * 10,))
        self.value_head_weight = mx.random.normal((1, 256))
        self.value_head_bias = mx.zeros((1,))

    def __call__(self, x):
        print("Input shape:", x.shape)
        print("Input dtype:", x.dtype)

        x = x.reshape(-1, 1, 9, 90)
        print("After reshape:", x.shape)

        # Conv1
        x = manual_conv2d(x, self.conv1_weight, self.conv1_bias)
        print("After conv1:", x.shape)
        x = mx.maximum(x, 0)  # ReLU

        # Conv2
        x = manual_conv2d(x, self.conv2_weight, self.conv2_bias)
        print("After conv2:", x.shape)
        x = mx.maximum(x, 0)  # ReLU

        # Conv3
        x = manual_conv2d(x, self.conv3_weight, self.conv3_bias)
        print("After conv3:", x.shape)
        x = mx.maximum(x, 0)  # ReLU

        x = x.reshape(-1, 128 * 9 * 90)
        print("Before fc1:", x.shape)

        # FC1
        x = manual_linear(x, self.fc1_weight, self.fc1_bias)
        x = mx.maximum(x, 0)  # ReLU

        # FC2
        x = manual_linear(x, self.fc2_weight, self.fc2_bias)
        x = mx.maximum(x, 0)  # ReLU

        # Policy head
        policy = manual_linear(x, self.policy_head_weight, self.policy_head_bias)

        # Value head
        value = mx.tanh(manual_linear(x, self.value_head_weight, self.value_head_bias))

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

            # 确保输入形状正确
            model_input = mx.array(node.state)

            # 检查输入形状并进行必要的调整
            if model_input.shape == (9, 9, 10):
                # 如果输入形状为 (9, 9, 10)，添加一个通道维度使其变为 (9, 9, 10, 1)
                model_input = mx.expand_dims(model_input, axis=-1)
                # 然后转置为 (1, 1, 9, 90)，这样可以被解释为一个 9x90 的单通道输入
                model_input = mx.transpose(model_input, (3, 2, 0, 1))
                model_input = mx.reshape(model_input, (1, 1, 9, 90))
            else:
                raise ValueError(f"Unexpected input shape: {model_input.shape}. Expected (9, 9, 10).")

            policy, value = self.model(model_input)
            policy = mx.reshape(policy, (9, 10, 9, 10))
            value = value.item()

            self.expand(node, policy, legal_moves)
            self.backpropagate(search_path, value)

        return max(root.children, key=lambda c: c.visits).action

    def select_child(self, node):
        if not node.children:
            return node  # 如果節點沒有子節點，直接返回該節點
        return max(node.children, key=lambda c: self.ucb_score(node, c))

    def ucb_score(self, parent, child):
        if child.visits == 0:
            return float('inf')  # 返回無窮大，確保未訪問的節點會被選中
        q_value = 1 - ((child.value / child.visits) + 1) / 2
        return q_value + self.c_puct * child.prior * (math.sqrt(parent.visits) / (1 + child.visits))

    def expand(self, node, policy, legal_moves):
        for move in legal_moves:
            if move in policy:
                prob = policy[move]
                child = MCTSNode(self.get_next_state(node.state, move), parent=node, action=move, prior=prob)
                node.children.append(child)

    def backpropagate(self, path, value):
        for node in reversed(path):
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