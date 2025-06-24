# breakout5
# Mr Wagner
# date

# what this code does

import pygame
from pygame.locals import *

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

brick1 = (20,20,35,20)

ListOfBricks = []
ListOfBricks.append((60,20,35,20))
ListOfBricks.append((100,20,35,20))
ListOfBricks.append((140,20,35,20))
ListOfBricks.append((180,20,35,20))
print(ListOfBricks)

bricks = []
#for BrickIndex in range(10):
#    bricks.append((BrickIndex*40 +20, 50, 35, 20))

BrickSize = 45
BrickSpacing = 5
BrickInitialShift = 20
for BrickIndex in range(10):
    bricks.append((BrickIndex * (BrickSize + BrickSpacing) + BrickInitialShift, \
                   50, BrickSize, 20))

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

    pygame.draw.rect(screen, pygame.Color("purple"), brick1)
    #pygame.draw.rect(screen, pygame.Color("pink"), ListOfBricks[0])
    #pygame.draw.rect(screen, pygame.Color("pink"), ListOfBricks[1])
    #pygame.draw.rect(screen, pygame.Color("pink"), ListOfBricks[2])
    #pygame.draw.rect(screen, pygame.Color("pink"), ListOfBricks[3])

    for BrickIndex in range(4):
        pygame.draw.rect(screen, pygame.Color("green"),ListOfBricks[BrickIndex])

    for BrickIndex in range(10):
        pygame.draw.rect(screen, pygame.Color("cyan"), bricks[BrickIndex])
        
    
    pygame.display.update()
    clock.tick(fps) #for every second at most 60 frames (loops) can pass
    #print(clock.get_fps())

#out of the while loop
print("Game over")
pygame.quit()

            


            
