# breakout16

# Mr Wagner
# date

# what this code does

#import for the pygame stuff
import pygame
from pygame.locals import *
import random

#brick kinds
NORMAL = 0
INVINCIBLE = 1
COUNTDOWN = 2
FALLING = 3

#all of my classes
class Brick:
    '''This class defines a brick
    the attributes for the brick are as follows
    rect - rectangle
    color - color of the brick
    points - how many points the brick is worth
    '''

    #constructor - makes the object
    def __init__(self, rect, color, points, kind = NORMAL):
        self.rect = rect #(x,y,w,h)
        self.color = color
        self.points = points
        self.kind = kind
        self.countdown = 0
        self.ShowText = False
        self.falling = False
        if self.kind == COUNTDOWN:
            self.ShowText = True
            self.countdown = 5
            self.BrickText = TextBox(self.rect[0] + 12, self.rect[1] + 3, 25, \
                                     pygame.Color("black"), self.color)
        if self.kind == FALLING:
            self.ShowText = True
            self.BrickText = TextBox(self.rect[0] + 4, self.rect[1] + 3, 25, \
                                     pygame.Color("black"), self.color)

    def __str__(self):
        return f"Brick: {self.rect} {self.color} {self.points}"

    def draw(self, screen):
        temp = pygame.draw.rect(screen, self.color, self.rect)
        if self.kind == COUNTDOWN:
            self.BrickText.draw(screen, f"{self.countdown}")
        if self.kind == FALLING:
            self.BrickText.y = self.rect[1] + 3
            self.BrickText.draw(screen, f"{self.points}")
        return temp

class TextBox:
    def __init__(self, x,y, size, \
                 color = pygame.Color("white"), \
                 bg_color = pygame.Color("black")):
        self.x = x
        self.y = y
        self.font = pygame.font.Font(None, size)
        self.color = color
        self.bg_color = bg_color

    def draw(self, screen, text):
        text_bitmap = self.font.render(text, True, self.color, self.bg_color)
        screen.blit(text_bitmap, (self.x, self.y))

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
            rnd = random.randint(1,100)
            if rnd >= 95:
                NewBrick = Brick(BrickRect, pygame.Color("gray"), 0, INVINCIBLE)
            elif rnd >= 90:
                NewBrick = Brick(BrickRect, myColors[r], 50, COUNTDOWN)
            elif rnd >= 85:
                NewBrick = Brick(BrickRect, pygame.Color("hotpink"),100,FALLING)
            else:
                NewBrick = Brick(BrickRect, myColors[r], (rows-r) * 10)
            mybricks.append(NewBrick)
    return mybricks

def NoMoreBricks(bricks):
    if len(bricks) == 0:
        return True
    else:
        for b in bricks:
            if b.kind != INVINCIBLE:
                return False
        return True

#initializing our pygame stuff
pygame.init()
clock = pygame.time.Clock()
fps = 60

#defining our pygame screen
ScreenHeight = 600
ScreenWidth = 800
pygame.display.set_caption("Breakout")
screen = pygame.display.set_mode ( (ScreenWidth, ScreenHeight) )

#defining the paddle
PaddleX = 400
PaddleY = 530
PaddleW = 80
PaddleH = 20
Paddle_dx = 0
PaddleCounter = 0
PaddleLocation = (PaddleX, PaddleY, PaddleW, PaddleH)

#defining the ball
BallX = PaddleX + PaddleW // 2
BallY = PaddleY - 10
BallLocation= (BallX, BallY)
dx = 0
dy = 0
BallRadius = 6

#makeing our bricks
bricks = MakeBricks(5, 19)

#initial drawing commands
BallRect = pygame.draw.circle(screen, pygame.Color("White"), BallLocation, BallRadius)
PaddleRect = pygame.draw.rect(screen, pygame.Color("blue"), PaddleLocation)


score = 0
txtScore = TextBox(20, 560, 30)
balls = 5
txtBalls = TextBox(700,560,30)
txtMessage = TextBox(300,560,30, pygame.Color("black"), pygame.Color("white"))

NewGame = True
NewBall = False

#game loop
GameRunning = True
while GameRunning:
    #events... keyboard
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # == means is equal to
            GameRunning = False       # = means Gets... GameRunning variable gets the value false
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE or event.key == K_q:
                GameRunning = False
            if event.key == K_RIGHT:
                Paddle_dx = 7
            if event.key == K_LEFT:
                Paddle_dx = -7
            if event.key == K_n and NewGame:
                dx = random.choice([6,-6])
                dy = -6
                score = 0
                balls = 5
                bricks = MakeBricks (5,19)
                PaddleW = 80
                NewGame = False
            if event.key == K_SPACE and NewBall:
                dx = random.choice([6,-6])
                dy = -6
                PaddleW = 80
                NewBall = False

        if event.type == pygame.KEYUP:
            if event.key == K_RIGHT or event.key == K_LEFT:
                Paddle_dx = 0

    #check for ball/brick interaction
    for b in bricks:
        if pygame.Rect.colliderect(BallRect, b.rect):
            dy *= -1
            if b.kind == NORMAL:
                score += b.points
                bricks.remove(b)
            elif b.kind == COUNTDOWN:
                b.countdown -= 1
                if b.countdown == 0:
                    score += b.points
                    bricks.remove(b)
            elif b.kind == FALLING:
                b.falling = True
            else:
                pass
            if NoMoreBricks(bricks):
            #if len(bricks) == 0:
                NewBall = True
                dx = 0
                dy = 0
                BallX = PaddleX + PaddleW // 2
                BallY = PaddleY - 10
                bricks = MakeBricks(5,19)
            break

    #bounce ball off walls and floor and ceiling
    if BallX > ScreenWidth - BallRadius: #right side of screen
        dx *= -1
        # bug fix
        BallX = ScreenWidth - BallRadius
    if BallX < BallRadius: #left side of the screen
        dx *= -1
        #bug fix
        BallX = BallRadius

    if BallY < BallRadius: #top of the screen
        dy *= -1
    #bottom of the screen
    if BallY > ScreenHeight - BallRadius:
        balls -= 1
        dx = 0
        dy = 0
        BallX = PaddleX + PaddleW //2
        BallY = PaddleY - 10
        if balls == 0:
            NewGame = True
        else:
            NewBall = True

        
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

    #brick/paddle interaction
    for b in bricks:
        if b.kind == FALLING and b.falling:
            if pygame.Rect.colliderect(PaddleRect, b.rect):
                score += b.points
                PaddleW *= 2
                PaddleCounter = 300
                bricks.remove(b)
            else:
                b.rect = (b.rect[0], b.rect[1] + 5, b.rect[2], b.rect[3])
                if b.rect[1] > ScreenHeight:
                    bricks.remove(b)

    #updating the ball position
    if NewBall or NewGame:
        BallX = PaddleX + PaddleW // 2
        BallY = PaddleY - 10
    else:
        BallX += dx
        BallY += dy
    BallLocation = (BallX, BallY)

    #update the paddle position
    PaddleX += Paddle_dx
    PaddleCounter -= 1
    if PaddleCounter < 0:
        PaddleW = 80
    if PaddleX > ScreenWidth - PaddleW:
        PaddleX = ScreenWidth - PaddleW
    if PaddleX < 0:
        PaddleX = 0
    PaddleLocation = (PaddleX, PaddleY, PaddleW, PaddleH)

    #drawing commands
    screen.fill( pygame.Color("black") )
    BallRect = pygame.draw.circle(screen, pygame.Color("White"), BallLocation, BallRadius)
    PaddleRect = pygame.draw.rect(screen, pygame.Color("blue"), PaddleLocation)

    txtScore.draw(screen, f"Score: {score}")
    txtBalls.draw(screen, f"Balls: {balls}")
    if NewGame:
        txtMessage.draw(screen, "Press N for new game.")
    if NewBall:
        txtMessage.draw(screen, "Press SPACE for new ball.")


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

            


            
