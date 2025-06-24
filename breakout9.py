# breakout9
# Mr Wagner
# date

# what this code does

import pygame
from pygame.locals import *

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


pygame.init()
clock = pygame.time.Clock()
fps = 60

MyBrick1 = Brick((10,10,20,15), "green", 100)
MyBrick2 = Brick((100,50,50,5), "red", 37)
print(MyBrick1)
print(MyBrick2)
print(MyBrick1.color)
print(MyBrick1.rect)
print(MyBrick2.points)


ScreenHeight = 600
ScreenWidth = 800

pygame.display.set_caption("Breakout")
screen = pygame.display.set_mode ( (ScreenWidth, ScreenHeight) )

BallX = 400
BallY = 400
BallLocation= (BallX, BallY)
dx = 3
dy = 3
BallRadius = 6

PaddleX = 400
PaddleY = 550
PaddleW = 80
PaddleH = 20
Paddle_dx = 0
PaddleLocation = (PaddleX, PaddleY, PaddleW, PaddleH)

bricks = MakeBricks(5, 19)

BallRect = pygame.draw.circle(screen, pygame.Color("White"), BallLocation, BallRadius)
PaddleRect = pygame.draw.rect(screen, pygame.Color("blue"), PaddleLocation) 

GameRunning = True
while GameRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # == means is equal to
            GameRunning = False       # = means Gets... GameRunning variable gets the value false
        if event.type == pygame.KEYDOWN:
            if event.key == K_RIGHT:
                Paddle_dx = 5
            if event.key == K_LEFT:
                Paddle_dx = -5
        if event.type == pygame.KEYUP:
            if event.key == K_RIGHT or event.key == K_LEFT:
                Paddle_dx = 0

    for b in bricks:
        if pygame.Rect.colliderect(BallRect, b.rect):
            dy *= -1
            bricks.remove(b)
            break
            

    if BallX > ScreenWidth - BallRadius or BallX < BallRadius:
        dx *= -1

    if BallY < BallRadius or BallY > ScreenHeight - BallRadius:
        dy *= -1
        

    if pygame.Rect.colliderect(BallRect, PaddleRect):
        dy *= -1


    BallX += dx
    BallY += dy
    BallLocation = (BallX, BallY)

    PaddleX += Paddle_dx
    if PaddleX > ScreenWidth - PaddleW:
        PaddleX = ScreenWidth - PaddleW
    if PaddleX < 0:
        PaddleX = 0
    PaddleLocation = (PaddleX, PaddleY, PaddleW, PaddleH)

    screen.fill( pygame.Color("black") )
    BallRect = pygame.draw.circle(screen, pygame.Color("White"), BallLocation, BallRadius)
    PaddleRect = pygame.draw.rect(screen, pygame.Color("blue"), PaddleLocation)

    for b in bricks:
        #pygame.draw.rect(screen, b.color, b.rect)
        b.draw(screen)
        
    
    pygame.display.update()
    clock.tick(fps) #for every second at most 60 frames (loops) can pass
    #print(clock.get_fps())

#out of the while loop
print("Game over")
pygame.quit()

            


            
