# breakout7
# Mr Wagner
# date

# what this code does

import pygame
from pygame.locals import *

def PrintImAwesome(n):
    for i in range(n):
        print("I'm Awesome")
    return "Yes, you are!"

def MakeBricks(rows, cols):
    mybricks = []
    BrickWidth = 35
    BrickHeight = 20
    BrickSpacing = 5
    BrickInitialShift = 20
    for r in range(rows):
        for c in range(cols):
            mybricks.append((c * (BrickWidth + BrickSpacing) + BrickInitialShift, \
                             r * (BrickHeight + BrickSpacing) + BrickInitialShift, \
                             BrickWidth, BrickHeight))
    return mybricks


pygame.init()
clock = pygame.time.Clock()
fps = 60

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

message = PrintImAwesome(5)
print(message)

bricks = MakeBricks(5, 19)
print(len(bricks))

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

    for brick in bricks:
        if pygame.Rect.colliderect(BallRect, brick):
            dy *= -1
            bricks.remove(brick)
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

    for BrickIndex in range(len(bricks)):
        pygame.draw.rect(screen, pygame.Color("cyan"), bricks[BrickIndex])
        
    
    pygame.display.update()
    clock.tick(fps) #for every second at most 60 frames (loops) can pass
    #print(clock.get_fps())

#out of the while loop
print("Game over")
pygame.quit()

            


            
