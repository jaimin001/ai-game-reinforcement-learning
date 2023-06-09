GAME_WIDTH = 800
GAME_HEIGHT = 600
PLAYER_SIZE = 20

GAME_FRICTION = 0.05
GAME_ACC_FACTOR = 0.6

GOAL_SIZE = 10

ENEMY_SIZE = 25
ENEMY_COUNT = 7
ENEMY_SPEED = 4

BACKGROUND = (0x00, 0x50, 0x50)
ENEMY_COLOR = (0xfc, 0x20, 0x20)
PLAYER_COLOR = (0x20, 0xfc, 0x20)
GOAL_COLOR = (0x20, 0xfc, 0xfc)

FPS = 30

# You can play around with these constants, but for evaluation
# of your code, the original values will be used.


# The fixed game seed that your game must be based on.
# It must be unique among all class members.
GAME_SEED = 20#'Assign your integer unique seed value here'

class GameRectangle:
    x: int
    y: int
    width: int
    height: int

    def __init__(self, _x, _y, _w, _h) -> None:
        self.x = _x
        self.y = _y
        self.width = _w
        self.height = _h

    def __str__(self) -> str:
        return f'<<{self.x}, {self.y}, {self.width}, {self.height}>>'
    
def CheckIntersect(a:GameRectangle, b:GameRectangle)->bool:
    if b.x > a.x + a.width or a.x > b.x + b.width:
        return False
    if b.y > a.y + a.height or a.y > b.y + b.height:
        return False
    return True


class Vector:
    x: float
    y: float

    def __init__(self, a=0, b=0) -> None:
        self.x = a
        self.y = b

    def __str__(self) -> str:
        return f'({self.x}, {self.y})'


# Moves a rectangle with constant speed, and handles bounce logic with a given boundary
def Move(rect:GameRectangle, v:Vector, boundary: GameRectangle) -> None:
    # Move with constant velocity
    rect.x = rect.x + v.x
    rect.y = rect.y + v.y

    def Clamp(rv:int, bv:int, rs:int, bs:int, vv:float)->tuple[int, float]:
        if rv <= bv or rv + rs >= bv + bs:
            vv = -vv
            if rv <= bv:
                rv = bv + 1
            else:
                rv = bv + bs - rs - 1
        return (rv, vv)

    # Bouncing in X-axis
    (rect.x, v.x) = Clamp(rect.x, boundary.x, rect.width, boundary.width, v.x)

    # Bouncing in Y-axis
    (rect.y, v.y) = Clamp(rect.y, boundary.y, rect.height, boundary.height, v.y)
    
    return (rect, v)


class Enemy:
    entity: GameRectangle
    velocity: Vector

    def __init__(self, rect: GameRectangle, vel: Vector) -> None:
        self.entity = rect
        self.velocity = vel

    def __str__(self):
        return f'(Entity: {self.entity}, Velocity: {self.velocity})'

    def Move(self, boundary: GameRectangle) -> None:
        (self.entity, self.velocity) = Move(self.entity, self.velocity, boundary)


class Player:
    entity: GameRectangle
    velocity: Vector
    friction: float
    acc_factor: float

    def __init__(self, rect: GameRectangle, vel: Vector, fr:float, af) -> None:
        self.entity = rect
        self.velocity = vel
        self.friction = fr
        self.acc_factor = af

    def __str__(self):
        return f'(Entity: {self.entity}, Velocity: {self.velocity}, friction:{self.friction})'

    def Move(self, acc:Vector, boundary: GameRectangle) -> None:
        def handle_axis(vv:float, av:float, vf:float, af:float)->float:
            return vv + (av * af) - (vv * vf)
        
        self.velocity.x = handle_axis(self.velocity.x, acc.x, self.friction, self.acc_factor)

        self.velocity.y = handle_axis(self.velocity.y, acc.y, self.friction, self.acc_factor)

        (self.entity, self.velocity) = Move(self.entity, self.velocity, boundary)