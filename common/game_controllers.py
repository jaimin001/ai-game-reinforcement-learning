import common.game_constants as game_constants
import common.game_state as game_state
import pygame
from tqdm import tqdm 
import math
import random
from copy import deepcopy
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class KeyboardController:
    def GetAction(self, state:game_state.GameState) -> game_state.GameActions:
        keys = pygame.key.get_pressed()
        action = game_state.GameActions.No_action
        if keys[pygame.K_LEFT]:
            action = game_state.GameActions.Left
        if keys[pygame.K_RIGHT]:
            action = game_state.GameActions.Right
        if keys[pygame.K_UP]:
            action = game_state.GameActions.Up
        if keys[pygame.K_DOWN]:
            action = game_state.GameActions.Down
        return action
### ------- You can make changes to this file from below this line --------------


#### defined deep q learning model
class QNetwork(nn.Module):
    def __init__(self, state_dims, action_dims):
        super().__init__()
        self.fc1 = nn.Linear(state_dims, 64)
        self.fc2 = nn.Linear(64, 128)
        self.fc3 = nn.Linear(128, 256)
        self.fc4 = nn.Linear(256, 128)
        self.fc5 = nn.Linear(128, 64)
        self.fc6 = nn.Linear(64, action_dims)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = torch.relu(self.fc4(x))
        x = torch.relu(self.fc5(x))
        x = self.fc6(x)
        return x

class AIController:
    def __init__(self) -> None:

        self.state_dims = (game_constants.ENEMY_COUNT * 6 + 12)
        self.action_dims = 5
        self.deep_q_learning_model = QNetwork(self.state_dims, self.action_dims)
        self.learning_rate = 1e-9
        self.optimizer = torch.optim.Adam(self.deep_q_learning_model.parameters(), lr=self.learning_rate)
    
    def compute_features(self, state):
        player_info = [state.PlayerEntity.entity.height, state.PlayerEntity.entity.width, state.PlayerEntity.friction, state.PlayerEntity.acc_factor, \
            state.PlayerEntity.entity.x, state.PlayerEntity.entity.y, state.PlayerEntity.velocity.x, state.PlayerEntity.velocity.y]
        goal_info = [state.GoalLocation.x, state.GoalLocation.y, state.GoalLocation.height, state.GoalLocation.width]
        enemy_info = [[e.entity.x, e.entity.y, e.entity.height, e.entity.width, e.velocity.x, e.velocity.y] for e in state.EnemyCollection]
        return player_info, goal_info, enemy_info

    def GetAction(self, state):
        player_info, goal_info, enemy_info = self.compute_features(state)
        input_state = torch.tensor([float(f) for feature_list in [player_info, goal_info, *enemy_info] for f in feature_list]).unsqueeze(0).float()
        
        # decing which action to take
        action = torch.argmax(torch.softmax(self.deep_q_learning_model(input_state), dim=1), 1)
        action_value = action.item()
        return game_state.GameActions(int(action_value))

    def forwardPass(self, state):
        player_info, goal_info, enemy_info = self.compute_features(state)
        input_state = torch.tensor([float(f) for feature_list in [player_info, goal_info, *enemy_info] for f in feature_list]).unsqueeze(0).float()
        return self.deep_q_learning_model(input_state)

    
    def calculate_loss(self, state, action, next_state, reward):
        with torch.no_grad():
            q_targets = reward + 0.95*self.forwardPass(next_state).max(1)[0].unsqueeze(1)
        q_expected = self.forwardPass(state)[:, action].view((1, 1))

        loss = F.mse_loss(q_expected, q_targets)

        return loss



    def TrainModel(self):
        chances = 0
        state = game_state.GameState()
        current_state = deepcopy(state)
        
        while chances <= 1000:
            avoid_enemy = 0 
            chances += 1

            eps_threshold = 0.01 + (1 - 0.01) * math.exp(-1 * chances / 0.95)
            if eps_threshold > random.random():
                action = game_state.GameActions(random.randint(0, 4))
            else:
                action = self.GetAction(current_state)

            agentPoint = [state.PlayerEntity.entity.x, state.PlayerEntity.entity.y]
            goalPoint = [state.GoalLocation.x, state.GoalLocation.y]
            hwAgent = [state.PlayerEntity.entity.width, state.PlayerEntity.entity.height]
            hwGoal = [state.GoalLocation.width, state.GoalLocation.height]
            x_dis = ((agentPoint[0] + 0.5*hwAgent[0]) - (goalPoint[0] + 0.5*hwGoal[0]))**2
            y_dis = ((agentPoint[1] + 0.5*hwAgent[1]) - (goalPoint[1] +0.5*hwGoal[1]))**2
            distance_term = math.sqrt(x_dis + y_dis)

            if state.Update(action).value == -1:
                avoid_enemy = -100
            
            ## reward calculation
            goal_reward = 1000/distance_term
            idle_penalty = -1e-2*distance_term - 3
            reward = avoid_enemy + goal_reward + idle_penalty

            loss = self.calculate_loss(current_state, action.value, state, reward)

            loss.backward()
            self.optimizer.step()
            current_state = deepcopy(state)


### ------- You can make changes to this file from above this line --------------

    # This is a custom Evaluation function. You should not change this function
    # You can add other methods, or other functions to perform evaluation for
    # yourself. However, this evalution function will be used to evaluate your model
    def EvaluateModel(self):
        attacked = 0
        reached_goal = 0
        state = game_state.GameState()
        for _ in tqdm(range(100000)):
            action = self.GetAction(state)
            obs = state.Update(action)
            if(obs==game_state.GameObservation.Enemy_Attacked):
                attacked += 1
            elif(obs==game_state.GameObservation.Reached_Goal):
                reached_goal += 1
        return (attacked, reached_goal)



