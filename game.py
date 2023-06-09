import pygame
from common.game_constants import *
from common.game_state import *
from common.game_controllers import *
import copy


class AbstractGame:
    __innerState: GameState
    controller: None
    graphics: pygame.Surface

    def __init__(self, ctr) -> None:
        self.__innerState = GameState()
        self.controller = ctr

        # Initialize Pygame
        pygame.init()
        self.graphics = pygame.display.set_mode(
            (GAME_WIDTH, GAME_HEIGHT))
        # Set game title
        pygame.display.set_caption("Advanced AI Game")
        self.clock = pygame.time.Clock()

    def GetCurrentState(self) -> GameState:
        return copy.deepcopy(self.__innerState)

    def __str__(self) -> str:
        return f'State: {self.__innerState}'

    def UpdateFrame(self) -> None:
        action: GameActions = self.controller.GetAction(
            self.GetCurrentState())
        self.__innerState.Update(action)

    def DrawFrame(self):
        self.graphics.fill(BACKGROUND)
        pygame.draw.rect(
            self.graphics,
            GOAL_COLOR,
            self.GetPygameRect(
                self.__innerState.GoalLocation)
        )
        pygame.draw.rect(
            self.graphics,
            PLAYER_COLOR,
            self.GetPygameRect(
                self.__innerState.PlayerEntity.entity)
        )
        for enemy in self.__innerState.EnemyCollection:
            enemy: Enemy
            pygame.draw.rect(
                self.graphics,
                ENEMY_COLOR,
                self.GetPygameRect(enemy.entity)
            )
        pygame.display.update()

    def Delay(self):
        self.clock.tick(FPS)

    def GetPygameRect(self, rect: GameRectangle) -> pygame.Rect:
        return pygame.Rect(rect.x, rect.y, rect.width, rect.height)


if __name__ == '__main__':
    my_game: AbstractGame
    print('Welcome to AI Assignment 4 program!\n')
    print('1. Run game on your AI model')
    print('2. Try the game by controlling with keyboard')
    x = input("Enter your choice: ")
    if x[0] == '2':
        my_game = AbstractGame(KeyboardController())
    else:
        ai_controller = AIController()
        print('AI controller initialized!\nNow training...')
        ai_controller.TrainModel()
        print('AI controller is trained!\nNow evaluating...')
        result = ai_controller.EvaluateModel()
        print(
            f'On Evaluation, player died {result[0]} times, while reaching the goal {result[1]} times')

        if input('Would you like to see how this model performs on the game (y/n)?').lower()[0] != 'y':
            exit()
        my_game = AbstractGame(ai_controller)

    # Set game loop flag
    game_loop = True
    # Main game loop
    while game_loop:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_loop = False

        my_game.DrawFrame()
        my_game.UpdateFrame()
        my_game.Delay()

    # Quit Pygame
    pygame.quit()
