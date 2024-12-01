import numpy as np
import gym
from gym import spaces
import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque

class TradingEnv(gym.Env):
    """
    Custom Trading Environment for Reinforcement Learning.
    """

    def __init__(self, data, initial_balance=1000000):
        super(TradingEnv, self).__init__()
        self.data = data
        self.initial_balance = initial_balance
        self.current_step = 0
        self.balance = initial_balance
        self.positions = 0  # Number of stocks held
        self.total_value = initial_balance
        self.max_steps = len(data)

        # Action space: 0 (Hold), 1 (Buy), 2 (Sell)
        self.action_space = spaces.Discrete(3)

        # Observation space: OHLCV + balance + positions
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(len(data.columns) + 2,), dtype=np.float32
        )

    def reset(self):
        self.current_step = 0
        self.balance = self.initial_balance
        self.positions = 0
        self.total_value = self.initial_balance
        return self._get_observation()

    def _get_observation(self):
        return np.concatenate(
            [self.data.iloc[self.current_step].values, [self.balance, self.positions]]
        )

    def step(self, action):
        current_price = self.data.iloc[self.current_step]["Close"]
        transaction_cost = 0.001  # Example: 0.1% transaction cost per trade

        if action == 1:  # Buy
            self.positions += 1
            self.balance -= current_price * (1 + transaction_cost)

        elif action == 2:  # Sell
            if self.positions > 0:
                self.positions -= 1
                self.balance += current_price * (1 - transaction_cost)

        self.current_step += 1
        done = self.current_step >= self.max_steps - 1

        # Update portfolio value
        self.total_value = self.balance + self.positions * current_price

        # Reward: Portfolio value change
        reward = self.total_value - self.initial_balance

        return self._get_observation(), reward, done, {}

    def render(self):
        print(f"Step: {self.current_step}, Balance: {self.balance}, Positions: {self.positions}, Total Value: {self.total_value}")


class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, 128)
        self.fc4 = nn.Linear(128, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        return self.fc4(x)

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.learning_rate = 0.001

        self.model = DQN(state_size, action_size).float()
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        state = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        act_values = self.model(state)
        return torch.argmax(act_values).item()

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return

        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                next_state = torch.tensor(next_state, dtype=torch.float32).unsqueeze(0)
                target = reward + self.gamma * torch.max(self.model(next_state)).item()

            state = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            target_f = self.model(state).detach().clone()
            target_f[0][action] = target

            output = self.model(state)
            loss = self.criterion(output, target_f)

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
