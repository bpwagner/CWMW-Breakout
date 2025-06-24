# breakout2
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


GameRunning = True
while GameRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # == means is equal to
            GameRunning = False       # = means Gets... GameRunning variable gets the value false

    if BallX > ScreenWidth - BallRadius or BallX < BallRadius:
        dx *= -1

    if BallY < BallRadius or BallY > ScreenHeight - BallRadius:
        dy *= -1
        

    BallX += dx
    BallY += dy
    BallLocation = (BallX, BallY)

    screen.fill( pygame.Color("black") )
    pygame.draw.circle(screen, pygame.Color("White"), BallLocation, BallRadius)
    
    pygame.display.update()
    clock.tick(fps) #for every second at most 60 frames (loops) can pass
    #print(clock.get_fps())

#out of the while loop
print("Game over")
pygame.quit()

            


            
