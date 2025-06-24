# breakout10
# Mr Wagner
# date

# what this code does

#import for the pygame stuff
import pygame
from pygame.locals import *

#all of my classes
class Brick:
    '''This class defines a brick
    the attributes for the brick are as follows
    rect - rectangle
    color - color of the brick
    points - how many points the brick is worth
    '''

    #constructor - makes the object
    def __init__(self, rect, color, points):
        self.rect = rect
        self.color = color
        self.points = points

    def __str__(self):
        return f"Brick: {self.rect} {self.color} {self.points}"

    def draw(self, screen):
        return pygame.draw.rect(screen, self.color, self.rect)


#Here are all the funcitons
def MakeBricks(rows, cols):
    myColors = ["red", "orange", "yellow", "green", "blue", "violet"]
    #print(myColors[2])
    mybricks = []
    BrickWidth = 35
    BrickHeight = 20
    BrickSpacing = 5
    BrickInitialShift = 20
    for r in range(rows):
        for c in range(cols):
            BrickRect = (c * (BrickWidth + BrickSpacing) + BrickInitialShift, \
                             r * (BrickHeight + BrickSpacing) + BrickInitialShift, \
                             BrickWidth, BrickHeight)
            NewBrick = Brick(BrickRect, myColors[r], 100)
            mybricks.append(NewBrick)
    return mybricks

#initializing our pygame stuff
pygame.init()
clock = pygame.time.Clock()
fps = 60

#defining our pygame screen
ScreenHeight = 600
ScreenWidth = 800
pygame.display.set_caption("Breakout")
screen = pygame.display.set_mode ( (ScreenWidth, ScreenHeight) )

#defining the ball
BallX = 400
BallY = 400
BallLocation= (BallX, BallY)
dx = 3
dy = 3
BallRadius = 6

#defining the paddle
PaddleX = 400
PaddleY = 550
PaddleW = 80
PaddleH = 20
Paddle_dx = 0
PaddleLocation = (PaddleX, PaddleY, PaddleW, PaddleH)

#makeing our bricks
bricks = MakeBricks(5, 19)

#initial drawing commands
BallRect = pygame.draw.circle(screen, pygame.Color("White"), BallLocation, BallRadius)
PaddleRect = pygame.draw.rect(screen, pygame.Color("blue"), PaddleLocation) 

#game loop
GameRunning = True
while GameRunning:
    #events... keyboard
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # == means is equal to
            GameRunning = False       # = means Gets... GameRunning variable gets the value false
        if event.type == pygame.KEYDOWN:
            if event.key == K_RIGHT:
                Paddle_dx = 7
            if event.key == K_LEFT:
                Paddle_dx = -7
        if event.type == pygame.KEYUP:
            if event.key == K_RIGHT or event.key == K_LEFT:
                Paddle_dx = 0

    #check for ball/brick interaction
    for b in bricks:
        if pygame.Rect.colliderect(BallRect, b.rect):
            dy *= -1
            bricks.remove(b)
            break

    #bounce ball off walls and floor and ceiling
    if BallX > ScreenWidth - BallRadius or BallX < BallRadius:
        dx *= -1
    if BallY < BallRadius or BallY > ScreenHeight - BallRadius:
        dy *= -1
        
    #ball / paddle interaction
    TempWidth = PaddleRect.w // 6
    dxList = [-7, -5, -3, 3, 5, 7]
    for i in range(6):
        TempRect = PaddleRect.copy()
        TempRect.w = TempWidth
        TempRect.x = TempRect.x + TempWidth * i
        if pygame.Rect.colliderect(BallRect, TempRect):
            dy *= -1
            dx = dxList[i]
            break





    #updating the ball position
    BallX += dx
    BallY += dy
    BallLocation = (BallX, BallY)

    #update the paddle position
    PaddleX += Paddle_dx
    if PaddleX > ScreenWidth - PaddleW:
        PaddleX = ScreenWidth - PaddleW
    if PaddleX < 0:
        PaddleX = 0
    PaddleLocation = (PaddleX, PaddleY, PaddleW, PaddleH)

    #drawing commands
    screen.fill( pygame.Color("black") )
    BallRect = pygame.draw.circle(screen, pygame.Color("White"), BallLocation, BallRadius)
    PaddleRect = pygame.draw.rect(screen, pygame.Color("blue"), PaddleLocation)

    for b in bricks:
        #pygame.draw.rect(screen, b.color, b.rect)
        b.draw(screen)
        
    #final update
    pygame.display.update()
    clock.tick(fps) #for every second at most 60 frames (loops) can pass
    #print(clock.get_fps())

#out of the while loop
print("Game over")
pygame.quit()

            


            
