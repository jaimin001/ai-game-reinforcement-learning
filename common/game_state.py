import common.game_constants as game_constants
from enum import Enum
import random

class GameActions(Enum):
    No_action = 0
    Up = 1
    Down = 2
    Left = 3
    Right = 4

class GameObservation(Enum):
    Nothing = 0
    Enemy_Attacked = -1
    Reached_Goal = 1

class GameState:
    PlayerEntity : game_constants.Player
    GoalLocation : game_constants.GameRectangle
    EnemyCollection : list # list of (Enemy)
    Boundary : game_constants.GameRectangle
    Current_Observation: GameObservation

    def __init__(self) -> None:
        assert type(game_constants.GAME_SEED)==int, 'Ensure that the game seed is initialized as an integer'
        random.seed(game_constants.GAME_SEED) # Ensure that seed is initalized
        self.Boundary = game_constants.GameRectangle(
            0, 0, 
            game_constants.GAME_WIDTH, 
            game_constants.GAME_HEIGHT)
        self.PlayerEntity = game_constants.Player(
            game_constants.GameRectangle(
                0, 0, 
                game_constants.PLAYER_SIZE, 
                game_constants.PLAYER_SIZE),
            game_constants.Vector(),
            game_constants.GAME_FRICTION,
            game_constants.GAME_ACC_FACTOR
        ) 
        self.GoalLocation = game_constants.GameRectangle(
            0, 0, 
            game_constants.GOAL_SIZE,
            game_constants.GOAL_SIZE)
        self.Reset_Goal()
        es = game_constants.ENEMY_SIZE
        ex = game_constants.GAME_WIDTH - es
        ey = game_constants.GAME_HEIGHT - es
        sx = game_constants.PLAYER_SIZE * 2
        self.EnemyCollection = []
        import math
        for _ in range(game_constants.ENEMY_COUNT):
            tau = math.pi * 2
            phi = random.uniform(0, tau)
            vx = math.cos(phi) * game_constants.ENEMY_SPEED
            vy = math.sin(phi) * game_constants.ENEMY_SPEED
            enemy = game_constants.Enemy(
                game_constants.GameRectangle(
                    random.randint(sx, ex),
                    random.randint(sx, ey),
                    es, es),
                game_constants.Vector(vx, vy)
            )
            # it is ensured that enemies do not spawn
            # near the player and inside the boundary
            # with a random speed and location
            self.EnemyCollection.append(enemy)

    def Reset_Goal(self)->None:
        gw = game_constants.GAME_WIDTH
        gh = game_constants.GAME_HEIGHT
        s = game_constants.GOAL_SIZE
        self.GoalLocation.x = random.randint(0, gw - s)
        self.GoalLocation.y = random.randint(0, gh - s)
    

    def __str__(self) -> str:
        return "{"+f'Player: {self.PlayerEntity}, Goal: {self.GoalLocation}, Enemies: {self.EnemyCollection}, Boundary: {self.Boundary}'+"}"

    # Updates one frame of the game. 
    # Input argument : The action enum 
    # Output : GameObservation enum
    def Update(self, action:GameActions) -> GameObservation :
        input_vector = game_constants.Vector(0, 0)
        if action == GameActions.Up:
            input_vector = game_constants.Vector(0, -1)
        if action == GameActions.Down:
            input_vector = game_constants.Vector(0, 1)
        if action == GameActions.Left:
            input_vector = game_constants.Vector(-1, 0)
        if action == GameActions.Right:
            input_vector = game_constants.Vector(1, 0)

        self.Current_Observation = GameObservation.Nothing

        self.PlayerEntity.Move(input_vector, self.Boundary)
        new_loc = self.PlayerEntity.entity
        
        if game_constants.CheckIntersect(new_loc, self.GoalLocation):
            self.Reset_Goal()
            self.Current_Observation = GameObservation.Reached_Goal

        for enemy in self.EnemyCollection:
            enemy : game_constants.Enemy
            enemy.Move(self.Boundary)
            if game_constants.CheckIntersect(enemy.entity, new_loc):
                self.Reset_Goal()
                self.Current_Observation = GameObservation.Enemy_Attacked

        return self.Current_Observation