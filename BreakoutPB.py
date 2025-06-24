#Breakout
# Paul B

import pygame, math, random
from pygame.locals import *

ScreenHeight = 600
ScreenWidth = 800
ScoreY = FontSize = int(ScreenHeight/20)
MsgX = ScoreX = ScreenWHalf = ScreenWidth>>1
MsgY = ScreenHHalf = ScreenHeight>>1

Levels = 7  # How many levels or game fields have we created?

PaddleW = int(ScreenWidth/15)
PaddleH = 20
PaddleGap = 20 # From Bottom of screen
PaddleSpeed = 2 # Seems about right.  Number of pixels for each left/right movement

# With the ability to change the angle, we want to avoid an angle that is too horizontal (slow and may get 'stuck')
MaxAngSW = 165/180*math.pi
MaxAngSE = 15/180*math.pi
MaxAngNW = -MaxAngSW
MaxAngNE = -MaxAngSE
MaxAngSWV = 95/180*math.pi
MaxAngSEV = 85/180*math.pi
MaxAngNWV = -MaxAngSWV
MaxAngNEV = -MaxAngSEV
PiHalf = math.pi/2

dAngMax = math.pi/18 #Max angle change off a paddle will be 10 degrees

ExtraBallPts = 100  # How many points needed for extra ball?

class Paddle(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PaddleW, PaddleH), pygame.SRCALPHA)
        # Not sure why this is needed.  According to the documentation "The Surface will be cleared to all black," but if I don't do this then the mask fails
        self.image.fill("black")
        pos = ((ScreenWHalf)-(PaddleW>>1),ScreenHeight-(PaddleH+PaddleGap))
        self.rect = self.image.get_rect(topleft=pos)
        # The paddle shape is a large circle drawn 'below' the surface so that we see the top center of it.
        yoffset = 5 # offsets the center of the circle
        pygame.draw.circle(self.image, "green4", (PaddleW>>1,yoffset+(PaddleH<<2)), PaddleH<<2)
        self.image.set_colorkey("black") # Anything black is masked
        self.mask = pygame.mask.from_surface(self.image)
        self.dx = 0 # At init, paddle is not moving
        # Caclulate how many pixels lower the edge of the paddle is from the middle-top of the paddle.  Needed for collision detection along the vert edges
        self.edgegap = pos[1] + yoffset + ((PaddleH<<2)- math.sqrt((PaddleH<<2)**2-(PaddleW>>1)**2))

    def update(self):
        xpos = self.rect.x + self.dx # Move the paddle if needed
        # Check if paddle is hitting either edge of the screen.  We don't want it to move past.
        if xpos < 0:
            xpos = 0
            if MainBall.dy == 0: # If main ball is riding on top of the paddle then dy=0 and we need to edge detect for the ball, too
                MainBall.dx = 0
        RightEdge = ScreenWidth-self.rect.width
        if xpos > RightEdge:
            xpos = RightEdge
            if MainBall.dy == 0:
                MainBall.dx = 0
        self.rect.x = xpos

BallRadius = 6

class Ball(pygame.sprite.Sprite):

    def __init__(self, pos, rad, angle, speed, color):
        super().__init__()
        self.image = pygame.Surface((rad<<1,rad<<1), pygame.SRCALPHA)
        self.image.fill("black")
        self.rect = self.image.get_rect(center=pos)
        self.color = color
        pygame.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey("black")
        self.mask = pygame.mask.from_surface(self.image)
        self.angle = angle
        self.speed = speed
        self.radius = rad
        self.reorient()
        # Had to add these, because sometimes the angle was flat enough that the dx or dy adder was below 1 and thus when put into the
        # rect position, the dx or dy could be rounded out to 0 since rect uses integers.  Th
        self.cx = self.rect.centerx
        self.cy = self.rect.centery
        # fresh: # If False, the ball just hit another ball.  Needed because the ball collision routine is two nested loops going through each
        #  ball.  So it detects ballx hitting bally and ALSO bally hitting ballx.  I only want the collision routine to be once so this flag
        #  tells me the ball has already gone through the collision routine.
        self.fresh = True
        # isalive: If False, the ball has hit the paddle on the side and is doomed.  Used to avoid repeat paddle hits.
        #  Or the ball has not been hit by an active ball.  Used to allow the horizontal collisions on one of the levels; otherwise, the MAXANG
        #  checks would make them no longer move horizontally.
        self.isalive = False

    def update(self): # Move the ball
        self.cx += self.dx
        self.cy += self.dy
        self.rect.center = ((round(self.cx), round(self.cy)))
        self.fresh = True

    def reorient(self): # We've changed speed or direction.  Recalculate our x and y offset
        self.dx = self.speed*math.cos(self.angle)
        self.dy = self.speed*math.sin(self.angle)

    def angleCorrect(self): # Make sure we aren't moving along the x or y axes
        myAngle = self.angle
        # Check if too horizontal
        if myAngle >= 0:
            myAngle = max(myAngle, MaxAngSE)
            myAngle = min(myAngle, MaxAngSW)
        else:
            myAngle = max(myAngle,MaxAngNW)
            myAngle = min(myAngle, MaxAngNE)
        #Check if too vertical
        myAngleAbs = abs(myAngle)
        if (myAngleAbs < MaxAngSWV) and (myAngleAbs > MaxAngSEV):
            if myAngleAbs > PiHalf:
                myAngleAbs = MaxAngSWV
            else:
                myAngleAbs = MaxAngSEV
            myAngle = myAngleAbs if (myAngle>0) else -myAngleAbs
        self.angle = myAngle
            


class Block(pygame.sprite.Sprite):

    def __init__(self, pos, color, width, height, hits, points, perm):
        # pos - position of block in screen space
        # color - color of block.  Note, if perm is true, then color will be for the outline (with a black center)
        # width, height - of block
        # hits - number of hits the block needs to be destroyed
        # points - number of points of the block when it is destroyed, this can be negative and will be shown as a block with an 'X' through it.
        # perm - block is permanent
        global NumBlocks

        super().__init__()
        self.image = pygame.Surface((width,height), pygame.SRCALPHA)
        self.image.fill("black")
        self.rect = self.image.get_rect(topleft = pos)
        self.points = points # value of this brick
        self.perm = perm
        self.color = color
        if self.perm:
            pygame.draw.rect(self.image, (1,1,1), (0,0,width,height), 0) # we want a very dark (but not black) fill and not masked
            border = 1
        else:
            border = 0
            if points > 0:
                NumBlocks += 1   # Only count blocks that aren't negative value or permanent
        pygame.draw.rect(self.image, color, (0,0,width,height), border)
        if self.points < 0 and not self.perm: # Negative points, so draw an 'X' through the block to warn the player
            pygame.draw.line(self.image,(1,1,1),(0,0),(width,height))
            pygame.draw.line(self.image,(1,1,1),(0,height),(width,0))
        if hits > 1:
            # Note: if a block has multiple hits, then it needs to be > 2 in size (more if you want the count to be legible)
            BlockFont = pygame.font.SysFont(None, height-1)
            HitImg = BlockFont.render(str(hits),True,"black")
            self.image.blit(HitImg, HitImg.get_rect(center=(width>>1, height>>1)))
        self.image.set_colorkey("black")
        self.mask = pygame.mask.from_surface(self.image)
        self.hits = hits # number of hits before block breaks

    def update(self):
        # Update the count in the block if needed
        width = self.rect.width
        height = self.rect.height
        pygame.draw.rect(self.image, self.color, (0,0,width, height), 0)
        BlockFont = pygame.font.SysFont(None, height-1)  # Thus if a block has multiple hits, then it needs to be > 2 in size (more if you want the count to be legible)
        if self.hits > 1:
            HitImg = BlockFont.render(str(self.hits),True,"black")
            self.image.blit(HitImg, HitImg.get_rect(center=(width>>1, height>>1)))
        if self.points < 0:
            pygame.draw.line(self.image,"black",(0,0),(width,height))
            pygame.draw.line(self.image,"black",(0,height),(width,0))

def RotateVel(vx, vy, angle):
    return((vx*math.cos(angle)-vy*math.sin(angle),vx*math.sin(angle)+vy*math.cos(angle)))

def ResolveCollision(ball1, ball2):
    # This code modified from: https://stackoverflow.com/questions/53486422/ball-to-ball-collision-resolution
    #  Basically, determine the delta in the x and y velocities between the two balls.  Our dx and dy of each ball are the those variables.
    #  Then determine the contact angle (angle between the centers of the balls)by using atan2 of that triangle between the dx's and dy's.
    #  The plane is then rotated by the contact angle (along with the dx and dy) to make the contact a vertical plane collision.  This makes the math
    #  easier since we now only have to worry about swapping the dx's and the dy's stay the same (especially since we assume each ball has the same mass).
    #  The dx values are swapped and then we rotate the balls back to the contact angle.
    #  That's all great, in physics, but it can really speed up or slow down the balls.  For example, and let's switch to Newtownian space instead of the
    #  flipped pygame space, you have a ball on the left moving horizontally (e.g. dy = 0, and let's just say dx=1) and the ball on the right is moving
    #  vertically (e.g. dx=0, and let's say dy=1).
    #  Also assume they collide with the same y coordinate for the center of the balls, thus the contact angle would be 0 degrees (atan2(0,x)=0 : Note that
    #  python's atan2 function has the varibles as atan2(y,x) while some other tools, such as excel, use atan2(x,y)).  The math below would make the left
    #  ball stop completely (it already has a dy=0 and now it gets the dx=0 from the other ball) and the right ball gains speed and move at a 45 degree
    #  angle because it keeps its dy=1 and gets the dx=1 from the other ball.
    #  Well, that's a problem because we don't want our balls to stop or really slow down or speed up.  So, I get the new calculated angle of each ball
    #  and then determine the dx and dy to maintain a constant BallSpeed.  We also want to fix any ball that gets pushed too horizontally or vertically.

    # Determine the contact angle of the two balls
    contactAngle = -math.atan2(ball2.cy-ball1.cy, ball2.cx-ball1.cx)

    # Get the normalized velocity vector for each ball
    norm1 = RotateVel(ball1.dx, ball1.dy, contactAngle)
    norm2 = RotateVel(ball2.dx, ball2.dy, contactAngle)

    # Normalized collision (i.e. one dimensional)
    # if we had mass, the eq is newx1 = dx1 * (m1-m2)/(m1+m2) + dx2 * 2 * (m2/(m1+m2)), but since the mass is the same it simplies to newx1 = x2
    # the y velocities stay the same since we noramlized them to the contact actangle
    newv1 = (norm2[0], norm1[1])
    newv2 = (norm1[0], norm2[1])

    #'Un normalize'
    norm1 = RotateVel(newv1[0], newv1[1], -contactAngle)
    norm2 = RotateVel(newv2[0], newv2[1], -contactAngle)

    ball1.angle = math.atan2(norm1[1],norm1[0])
    ball2.angle = math.atan2(norm2[1],norm2[0])
    if ball1.isalive: ball1.angleCorrect()
    if ball2.isalive: ball2.angleCorrect()
    ball1.reorient()
    ball2.reorient()
    return

# Modify the collide_mask function slightly by ignoring a sprite colliding with itself.  Used when multiple balls on the screen
def ExclusiveCollide(sprite1, sprite2):
    """if sprite1 is sprite2:
        return False
    else:
        return pygame.sprite.collide_mask(sprite1, sprite2)"""
    return False if sprite1 is sprite2 else pygame.sprite.collide_mask(sprite1, sprite2)

def CreateBlocksLeft(pos, rows, cols, width, height, gapx, gapy, ColorList, coladd=0, hits=1, points=1):
    # Creates a matrix of blocks with a common left edge
    # pos - top LEFT starting position of these blocks on the screen
    # rows, cols - number of rows and columns to generate
    # width, height - width and height of the blocks
    # gapx, gapy - vertical and horizontal gap between blocks
    # ColorList - a list or list of lists of colors. The function will cycle through the colors in the list.  This must be a list or a list of lists.
    #   ["r", "b"] or [["r"],["g", "b"]] are okay, but ["r",["g", "b"] is not
    # coladd - an adder to the column to create 'triangular' shapes.  0 for a rectangle of blocks, 1 for blocks to increase as you go down, -1 for blocks to decrease going down
    BlockGrp = pygame.sprite.Group()
    if (type(ColorList[0]) is list): # a list of lists, thus a matrix
        MultiList = True
        NumLists = len(ColorList)
    else: # an array
        MultiList = False
        NumColors = len(ColorList)
    for row in range(rows):
        if MultiList: NumColors = len(ColorList[row % NumLists])
        for col in range(cols):
            color = ColorList[row % NumLists][col % NumColors] if MultiList else ColorList[col % NumColors]
            x = pos[0] + col*(gapx + width)
            y = pos[1] + row*(gapy + height)
            BlockGrp.add(Block((x,y), color, width, height, hits, points, False))
        cols += coladd
    return BlockGrp

def CreateBlocksRight(pos, rows, cols, width, height, gapx, gapy, ColorList, coladd=0, hits=1, points=1):
    # Creates a matrix of blocks with a common right edge.  Note that if coladd=0, this will be identical to CreateBlocksLeft by generating a rowsxcols matrix of blocks
    # pos - top RIGHT starting position of the matrix on the srceen
    # ColorList - similar to the one in CreateBlocksLeft, but realize the colors will be assigned from right to left
    # All other variables are equivalent to CreateBlocksLeft
    BlockGrp = pygame.sprite.Group()
    if (type(ColorList[0]) is list): # a list of lists, thus a matrix
        MultiList = True
        NumLists = len(ColorList)
    else: # an array
        MultiList = False
        NumColors = len(ColorList)
    for row in range(rows):
        if MultiList: NumColors = len(ColorList[row % NumLists])
        for col in range(cols):
            color = ColorList[row % NumLists][col % NumColors] if MultiList else ColorList[col % NumColors]
            x = (pos[0]-width)-col*(gapx+width)
            y = pos[1] + row*(gapy+height)
            BlockGrp.add(Block((x,y), color, width, height, hits, points, False))
        cols += coladd
    return BlockGrp

def CreateBlocksByList(pos, width, height, gapx, gapy, TypeListM, PtsListM, ColorListM):
    # Creates a row of len(TypeList) blocks using lists
    # pos - top left starting position
    # width - width of block.  If negative then each block is random between (width/2 and width*1.5), but width of row will be (len(TypeList)*(width+gapx))-gapx
    # height - height of block
    # gapx, gapy - gap between blocks
    # TypeList - a list of the blocks.  Each block is represented by a single character.
    #     A positive integer that represents the number of hits for the block
    #     '*' represents a permanent block
    #     '.' represents no block in that location
    # PtsList - a list of points for each block.  Integer values, including negative.
    # ColorList - a list of colors for each block.
    # Note: if PtsList or ColorList is shorter than TypeList, the index will wrap around
    # If width < 0 (random) the algorithm starts with assuming all blocks are width/2, so the row has an equal amount of empty space to fill the row.
    #   It will then add randint(0,width) to each block so that the new block is total width of width/2 to width*1.5 in length.  That amount is then removed
    #   from the empty space variable (RemainingPixels), and then you go to fit the next block.  The min and max calculations within the randint() statement
    #   help prevent over or underfilling the space remaining.  Basically, if RemainingPixels can only fit the smallest/largest blocks to properly fill, then
    #   that statement ensures that happens.  It essentially scopes the adder value to what is possible per the RemainingPixels.

    BlockGrp = pygame.sprite.Group()
    NumRows = len(TypeListM) if (type(TypeListM[0]) is list) else 1
    posy = 0
    DoRand = width<0
    width = abs(width)
    for row in range(NumRows):
        TypeList = TypeListM if NumRows==1 else TypeListM[row]
        PtsList = PtsListM[row % len(PtsListM)] if type(PtsListM[0]) is list else PtsListM
        ColorList = ColorListM[row % len(ColorListM)] if type(ColorListM[0]) is list else ColorListM
        BlockCnt = len(TypeList)
        NumPoints = len(PtsList)
        NumColors = len(ColorList)
        if DoRand:
            minWidth = width>>1
            RemainingPixels = BlockCnt*minWidth # At a minimum, the row will be filled with BlockCnt*minwidth blocks.  This is the remaining space/buffer/pixels we have for adders
        else:
            bw = width
        posx = 0 # Tracks x-position offset for next block
        for col in range(BlockCnt):
            if DoRand:
                MaxPixels = (BlockCnt-col)*width # The max buffer (remaining pixels) we could have
                adder = random.randint(max(0, RemainingPixels-(MaxPixels-width)), min(width, RemainingPixels))
                bw = minWidth+adder
                RemainingPixels -= adder
            if TypeList[col] != '.': # Not a 'space' or gap in the blocks.
                if TypeList[col] == '*': # This is a permanent block
                    hits = 1 # Setting a value of 1 has the secondary benefit of not drawing the number of hits remaining on the block
                    perm = True
                else:
                    hits = TypeList[col]
                    perm = False
                BlockGrp.add(Block((pos[0]+posx,pos[1]+posy), ColorList[col % NumColors], bw, height, hits, PtsList[col % NumPoints], perm))
            posx += bw+gapx
        posy += height+gapy
    return BlockGrp

def CreateLevel(lvl):
    global Balls
    global AllSprites

    BlockGrp = pygame.sprite.Group()
    iter, field = divmod(lvl,Levels)

    match field:

        case 0: # Classic rainbow blocks
            BlockGap = 2
            Rows = 7
            Cols = 10
            CList = [["red"],["orange"],["yellow"],["green"],["blue"],["indigo"],["violet"]]
            BlockGrp.add(CreateBlocksLeft((0, 100+10*iter),Rows,Cols, (ScreenWidth-BlockGap*(Cols-1))/Cols,15,BlockGap,BlockGap, CList,0,1,1))
            pygame.display.set_caption("Breakout - Level "+str(Level)+": Classic Rainbow Blocks")

        case 1: # A matrix of blocks with a diamond shaped hole.  In the hole is a peramanent block.
            BlockGap = 2
            Rows = 5
            Cols = 5
            Height = 15
            CList = [[(255,0,0)],[(255,60,60)],[(255,120,120)],[(255,160,160)],[(255,220,220)]]
            BlockGrp.add(CreateBlocksLeft((0,100+10*iter),Rows, Cols,((ScreenWidth>>1)-BlockGap*(Cols-1))/Cols,Height,BlockGap,BlockGap, CList,-1))
            CList = [[(0,255,0)],[(60,255,60)],[(120,255,120)],[(160,255,160)],[(220,255,220)]]
            BlockGrp.add(CreateBlocksRight((ScreenWidth,100+10*iter),Rows, Cols,((ScreenWidth>>1)-BlockGap*(Cols-1))/Cols,Height,BlockGap,BlockGap, CList,-1))
            CList = [[(220,220,255)],[(160,160,255)],[(120,120,255)],[(60,60,255)],[(0,0,255)]]
            Cols = 1
            BlockGrp.add(CreateBlocksLeft((0,100+(Height+BlockGap)*Rows+10*iter),Rows, Cols,((ScreenWidth>>1)-BlockGap*(5-1))/5,Height,BlockGap,BlockGap, CList,1))
            CList = [[(255,255,220)],[(255,255,160)],[(255,255,120)],[(255,255,60)],[(255,255,0)]]
            BlockGrp.add(CreateBlocksRight((ScreenWidth,100+(Height+BlockGap)*Rows+10*iter),Rows, Cols,((ScreenWidth>>1)-BlockGap*(5-1))/5,Height,BlockGap,BlockGap, CList, 1))
            # Permanent Block
            Width = 80
            Height = 80
            BlockGrp.add(Block(((ScreenWidth>>1)-(Width>>1),100+((15+2)*Rows)-Height/2+10*iter), (0,255,255), Width, Height,1,1,True))
            pygame.display.set_caption("Breakout - Level "+str(Level)+": Big Permanent Block")

        case 2: # Layers of blocks - some of them requiring multiple hits.  A gap between two groupings allows for some strategic ball hitting.
            BlockGap = 2
            TList = [[3,3,3,3,3,3,3,3,3,3],\
                     [2,2,2,2,1,1,2,2,2,2],\
                     [1,1,1,1,1,1,1,1,1,1],\
                     ['.'],\
                     ['.'],\
                     ['.'],\
                     [3,3,3,3,1,1,3,3,3,3],\
                     [2,2,2,2,1,1,2,2,2,2],\
                     [1,1,1,1,1,1,1,1,1,1]]
            PList = [[3],\
                     [2,2,2,2,1,1,2,2,2,2],\
                     [1],\
                     [0],\
                     [0],\
                     [0],\
                     [3,3,3,3,1,1,3,3,3,3],\
                     [2,2,2,2,1,1,2,2,2,2],\
                     [1]]
            CList = [["deepskyblue4"],\
                     ["deepskyblue3", "deepskyblue3", "deepskyblue3", "deepskyblue3", "deepskyblue", "deepskyblue", "deepskyblue3", "deepskyblue3", "deepskyblue3", "deepskyblue3" ],\
                     ["deepskyblue"],\
                     ["red"],\
                     ["red"],\
                     ["red"],\
                     ["deepskyblue4", "deepskyblue4", "deepskyblue4", "deepskyblue4", "deepskyblue", "deepskyblue", "deepskyblue4", "deepskyblue4", "deepskyblue4", "deepskyblue4" ],\
                     ["deepskyblue3", "deepskyblue3", "deepskyblue3", "deepskyblue3", "deepskyblue", "deepskyblue", "deepskyblue3", "deepskyblue3", "deepskyblue3", "deepskyblue3" ],\
                     ["deepskyblue"]]
            BlockGrp.add(CreateBlocksByList((0, 100+iter*10), int(ScreenWidth/10), 10, BlockGap, BlockGap, TList, PList, CList))
            pygame.display.set_caption("Breakout - Level "+str(Level)+": Multiple Hit Blocks")

        case 3: # Use the random size capability to build a matrix of blocks with a rectangular hole.
            BlockGap = 0
            TList = [[1,3,3,3,3,3,3,3,3,3,1],\
                     [1,2,2,2,2,2,2,2,2,2,1],\
                     [1,1,1,1,1,1,1,1,1,1,1]]
            PList = [[3],\
                     [2],\
                     [1]]
            CList = [["deepskyblue4", "deepskyblue1"],\
                     ["firebrick", "firebrick1"],\
                     ["gold4"]]
            BlockWidth = int(ScreenWidth/11)
            BlockHeight = 12
            Xoffset = (ScreenWidth-BlockWidth*11)/2
            #the x offset for the starting position is because the 800 pixel screen width is not evenly divisible by 11, so this balances the gap on left and right
            BlockGrp.add(CreateBlocksByList((Xoffset, 100+iter*10), -BlockWidth, BlockHeight, BlockGap, BlockGap, TList, PList, CList))
            TList = [[1,2,3,4],\
                     [2,3,4,1],\
                     [3,4,1,2],\
                     [4,1,2,3]]
            PList = [[1,2,3,4],\
                     [2,3,4,1],\
                     [3,4,1,2],\
                     [4,1,2,3]]
            CList = [["mediumorchid","mediumpurple"],\
                     ["seagreen","seagreen1"],\
                     ["turquoise1","turquoise4"],\
                     ["violetred4", "violetred1"]]
            BlockGrp.add(CreateBlocksByList((Xoffset, 100+3*BlockHeight+iter*10), -BlockWidth, BlockHeight, BlockGap, BlockGap, TList, PList, CList))
            TList = [[4,3,2,1],\
                     [1,4,3,2],\
                     [2,1,4,3],\
                     [3,2,1,4]]
            PList = [[4,3,2,1],\
                     [1,4,3,2],\
                     [2,1,4,3],\
                     [3,2,1,4]]
            CList = [["mediumorchid","mediumpurple"],\
                     ["seagreen","seagreen1"],\
                     ["turquoise1","turquoise4"],\
                     ["violetred4", "violetred1"]]
            BlockGrp.add(CreateBlocksByList((Xoffset+BlockWidth*7, 100+3*BlockHeight+iter*10), -BlockWidth, BlockHeight, BlockGap, BlockGap, TList, PList, CList))
            TList = [[1,3,3,3,3,3,3,3,3,3,1],\
                     [1,2,2,2,2,2,2,2,2,2,2],\
                     [1,1,1,1,1,1,1,1,1,1,1]]
            PList = [[3],\
                     [2],\
                     [1]]
            CList = [["khaki","khaki4"],\
                     ["purple1","plum3"],\
                     ["lawngreen"]]
            BlockGrp.add(CreateBlocksByList((Xoffset, 100+7*BlockHeight+iter*10), -BlockWidth, BlockHeight, BlockGap, BlockGap, TList, PList, CList))
            pygame.display.set_caption("Breakout - Level "+str(Level)+": Randomly Sized Blocks")

        case 4: # Extra balls moving horizontally.  Need to hit them to make active. Some various matrices of blocks
            BlockGap = 0
            TList = [[1,'.',1,'.',1,'.',1],\
                     ['.',1,'.',1,'.',1],\
                     [1,'.',1,'.',1,'.',1],\
                     ['.',1,'.',1,'.',1],\
                     [1,'.',1,'.',1,'.',1],\
                     ['.','*','.','*','.','*']]
            PList = [1]
            CList = ["darkorange3"]
            BlockGrp.add(CreateBlocksByList((0, 50+iter*10), 40, 15, BlockGap, BlockGap, TList, PList, CList))
            BlockGrp.add(CreateBlocksByList((520, 50+190+iter*10), 40, 15, BlockGap, BlockGap, TList, PList, CList))
            CList = ["deeppink4"]
            BlockGrp.add(CreateBlocksByList((520, 50+iter*10), 40, 15, BlockGap, BlockGap, TList, PList, CList))
            BlockGrp.add(CreateBlocksByList((0, 50+190+iter*10), 40, 15, BlockGap, BlockGap, TList, PList, CList))
            TList = [[2,2,2,2,2,2],\
                     [2,2,2,2,2,2],\
                     [2,2,2,2,2,2]]
            PList = [2]
            CList = [["red"],["white"],["blue"]]
            BlockGrp.add(CreateBlocksByList((290, 50+110+iter*10), 40, 20, BlockGap, BlockGap, TList, PList, CList))

            # Add the balls
            newBall = Ball((40,150+iter*10),BallRadius,0,BallSpeedStart,"aqua")
            newBall.reorient()
            newBall.add(AllSprites,Balls)
            newBall = Ball((80, 150+iter*10),BallRadius,0,BallSpeedStart,"chartreuse4")
            newBall.reorient()
            newBall.add(AllSprites,Balls)
            newBall = Ball((520,230+iter*10), BallRadius,math.pi, BallSpeedStart, "darksalmon")
            newBall.reorient()
            newBall.add(AllSprites,Balls)
            newBall = Ball((560,230+iter*10), BallRadius,math.pi, BallSpeedStart, "lightgreen")
            newBall.reorient()
            newBall.add(AllSprites,Balls)
            pygame.display.set_caption("Breakout - Level "+str(Level)+": Multi-Ball!")

        case 5: #Introduce negative point blocks.  They are on top of some 'buckets' that hold extra balls.  Blocks are based upon Arkanoid Level 3
            for lcv in range(2):
                BlockGrp.add(Block((0+lcv*(ScreenWidth-30),300+iter*10),"maroon1",30,20,1,-5,False))
                BlockGrp.add(Block((30+lcv*(ScreenWidth-66),320+iter*10),"gold",6,40,1,1,True))
                BlockGrp.add(Block((0+lcv*(ScreenWidth-36), 360+iter*10),"gold",36,6,1,1,True))
                newBall = Ball((15+lcv*(ScreenWidth-30),340+iter*10),3+lcv*6,0,0,"indianred")
                newBall.add(AllSprites,Balls)
            BlockGap = 2
            TList = [[3,3,3,3,3,3,3,3,3,3,3],\
                     [1,1,1,'*','*','*','*','*','*','*','*'],\
                     [2,2,2,2,2,2,2,2,2,2,2],\
                     ['*','*','*','*','*','*','*','*',1,1,1],\
                     [1,1,1,1,1,1,1,1,1,1,1],\
                     [1,1,1,'*','*','*','*','*','*','*','*'],\
                     [1,1,1,1,1,1,1,1,1,1,1],\
                     ['*','*','*','*','*','*','*','*',1,1,1]]
            PList = [[3],[1],[2],[1],[1],[1],[1],[1]]
            CList = [["green"],\
                     ["white","white","white","gold","gold","gold","gold","gold","gold","gold","gold"],\
                     ["darkred"],\
                     ["gold","gold","gold","gold","gold","gold","gold","gold","white","white","white"],\
                     ["pink"],\
                     ["blue","blue","blue","gold","gold","gold","gold","gold","gold","gold","gold"],\
                     ["blue"],\
                     ["gold","gold","gold","gold","gold","gold","gold","gold","blue","blue","blue"]]
            BlockWidth = int((ScreenWidth-11*BlockGap)/11)
            Xoffset = (ScreenWidth-(BlockWidth+BlockGap)*11)/2
            BlockHeight = 15
            BlockGrp.add(CreateBlocksByList((Xoffset, 30+iter*10), BlockWidth, BlockHeight, BlockGap, BlockHeight, TList, PList, CList))
            pygame.display.set_caption("Breakout - Level "+str(Level)+": Gotta Lose Points To Get Extra Balls")

        case 6: #Negative blocks and positive.  Skills to limit hitting the number of negative blocks
            TList = [1,'.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.',1]
            PList = [-10]
            CList = ["hotpink"]
            BlockGap = 3
            lenTL = len(TList)
            BlockWidth = int((ScreenWidth-lenTL*BlockGap)/lenTL)
            Xoffset = (ScreenWidth-(BlockWidth+BlockGap)*lenTL)/2
            BlockHeight = 8
            BlockGrp.add(CreateBlocksByList((Xoffset, 4), BlockWidth, BlockHeight, BlockGap, 0, TList, PList, CList))
            ch = '*' if random.choice((True, False)) else '.'
            TList = [[ch,ch,ch,ch,ch,1,1,ch,ch,ch,ch,ch],\
                     [ch,ch,ch,ch,1,1,1,1,ch,ch,ch,ch],\
                     [ch,ch,ch,1,1,1,1,1,1,ch,ch,ch],\
                     [ch,ch,1,1,1,1,1,1,1,1,ch,ch],\
                     [ch,1,1,1,1,1,1,1,1,1,1,ch],\
                     [ch,1,1,1,1,1,1,1,1,1,1,ch],\
                     [ch,ch,1,1,1,1,1,1,1,1,ch,ch],\
                     [ch,ch,ch,1,1,1,1,1,1,ch,ch,ch],\
                     [ch,ch,ch,ch,1,1,1,1,ch,ch,ch,ch],\
                     [ch,ch,ch,ch,ch,1,1,ch,ch,ch,ch,ch]]
            PList = [[-1],[1]]
            CList = [["darkred"],["darkorange3"],["darkgoldenrod3"],["darkgreen"],["darkblue"],["gray85"],["lightskyblue"],["lightgreen"],["lightgoldenrod1"],["lightsalmon"],["lightpink"]]
            BlockHeight = 14
            BlockWidth = int((ScreenWidth-12*BlockGap)/12)
            BlockGrp.add(CreateBlocksByList((Xoffset, 50+iter*10), BlockWidth, BlockHeight, BlockGap, BlockGap, TList, PList, CList))
            pygame.display.set_caption("Breakout - Level "+str(Level)+": Skill Shots - Avoid Negative Blocks")

    return BlockGrp

pygame.init()

# These items determine how quickly and how much the game speeds up based upon the number of blocks hit
BlockSpeedUp = 5 # Number of Blocks that get hit (roughly, since there is an adjustment if many balls are active) that causes a speed up in fps
fpsIncrement = 10 # The amount of additional frames/second the game speeds up when BlockSpeedUp blocks are hit
StartFPS = 120
fps = StartFPS # We'll be using fps to control game speed instead of ball speed.  This prevents a ball overshooting an object and embedding itself.

clock = pygame.time.Clock()

pygame.display.set_caption("Breakout")
screen = pygame.display.set_mode((ScreenWidth,ScreenHeight))
MyFont = pygame.font.SysFont(None, FontSize)

GameRunning = True
GamePaddle = Paddle()
AllSprites = pygame.sprite.Group(GamePaddle)
StartAngle = -45/180*math.pi
BallSpeedStart = 1 # This makes the max dx and dy of ball to be a 1, which should eliminate the ball moving into a brick/ball/paddle.
BlocksRemoved = 0 

MainBall = Ball((GamePaddle.rect.centerx,GamePaddle.rect.top-BallRadius+5),BallRadius, StartAngle, 0, "white")
MainBall.isalive = True
NumBalls = 1
AllSprites.add(MainBall)
Balls = pygame.sprite.Group(MainBall)

Msg = ""
# NumBlocks = 0

while GameRunning: # User has not exited
    StartGame = True
    Level = 0
    Paused = False

    while Level < Levels*3 and GameRunning:
        if StartGame:
            Score = 0
            NumLives = 5
            StartGame = False
            NumBlocks = 0
            ActiveGame = False
        if NumBlocks == 0: # New Level
            Msg = Msg+"Press Space Bar To Start"
            Blocks = CreateLevel(Level)
            #NumBlocks = len(Blocks) # This worked until I added the negative and permanent blocks.  We don't want to force hitting the negatives.
            AllSprites.add(Blocks, Balls)
            Balls.update()

        # Collision detect ball with walls, floor, and ceiling
        for b in Balls:
            BallX = b.rect.x
            BallY = b.rect.y
            if BallY <= 0: # Ceiling
                b.angle *= -1
                b.angleCorrect()
                b.reorient()
            elif BallY > ScreenHeight+(b.radius<<1): # Floor
                NumBalls-=1
                b.speed = 0
                b.reorient()
                Balls.remove(b)
                AllSprites.remove(b)
                if NumBalls == 0:
                    ActiveGame = False
                    NumLives -= 1
                    Msg = "Press Space Bar To Continue"
                    if NumLives == 0:
                        Msg = "Game Over!  " + Msg
                    else: # We have depleted all of our active balls on the screen, so reset with one ball.
                        MainBall.add(Balls, AllSprites)
                        MainBall.rect.center = (GamePaddle.rect.centerx,GamePaddle.rect.top-BallRadius+5)
                        MainBall.dx = GamePaddle.dx
                        MainBall.speed = BallSpeedStart
                        MainBall.cx = GamePaddle.rect.centerx
                        MainBall.cy = GamePaddle.rect.top-BallRadius+5
                        MainBall.angle = StartAngle
                        MainBall.isalive = True
                        BallX = MainBall.rect.x
                        BallY = MainBall.rect.y
                        NumBalls = 1
                        fps = StartFPS # Go back to most slow speed
                        BlocksRemoved = 0 # Reset our ball speed counter
            if BallX <= 0: # left wall
                BallX = -BallX
                m1 = math.pi if b.angle > 0 else -math.pi
                b.angle = m1-b.angle
                b.reorient()
            elif BallX >= ScreenWidth-(b.radius<<1): # right wall
                # We went past the edge, now bring it just as much over.  Equation is simplified ScrW-((xpos+radius*2)-ScrW
                #BallX = (ScreenWidth<<1) - (BallX+(b.radius<<2))  
                m1 = math.pi if b.angle > 0 else -math.pi
                b.angle = m1-b.angle
                b.reorient()
            b.rect.topleft = (BallX, BallY)

        # Collision detect balls against paddle
        BallHitList = pygame.sprite.spritecollide(GamePaddle, Balls, False, pygame.sprite.collide_mask)
        for b in BallHitList:
            if b.fresh and b.isalive:
                b.fresh = False
                # Only change if ball is coming downward.  There was a 'bug' in that the collision would occur while
                #  the ball was going upward due to odd paddle shape
                if b.angle > 0:  
                    xDelta = GamePaddle.rect.x+(GamePaddle.rect.width>>1)-(b.rect.x+b.radius)
                    PadPercent = xDelta/((GamePaddle.rect.width>>1)+b.radius)
                    # If the center of the ball is more than the ball's y-distance per frame, then we are somehow beneath the top of the paddle
                    # more than we should be.  I interpret this to mean either we hit the side of the paddle or we slid the paddle into the ball
                    # So, we should keep the ball going downward, but the angle bounces off the side.
                    # Also, as the ball is closer to edge of the paddle, the y-contact point on the ball moves from ball.bottom (on the
                    # middle of the paddle (or one that is perfectly flat) to ball.centery)
                    ballyContact = b.rect.bottom - b.radius*abs(PadPercent) # Ideally we'd do math to follow the curve, but assuming linear
                    if (ballyContact-GamePaddle.edgegap)> (b.dy): # If more than b.dy into the paddle, then too low
                        b.angle = math.pi-b.angle
                        b.isalive = False # The ball is now dead and doomed.  Want to avoid it reacting to another paddle hit.
                        b.reorient()
                    else:
                        b.angle = -(b.angle+(dAngMax*PadPercent))
                        #BallAngle needs to be bounded to MAXANGNW and MAXANGNE
                        b.angleCorrect()
                        b.reorient()
                        
        # Collision detect against blocks
        for b in Balls:
            BlockHitList = pygame.sprite.spritecollide(b, Blocks, False, pygame.sprite.collide_mask)
            for blk in BlockHitList:
                if b.rect.right-blk.rect.left <= 1 or blk.rect.right-b.rect.left <= 1: # Hit left or right side of block
                    # Similar to the block code below.  Have to adjust for overhit or sometimes ball sticks to the side due to rounding error
                    if (b.rect.right-blk.rect.left <= 1): # We hit the left side of the block
                        b.cx += (blk.rect.left - b.rect.right)
                    else:
                        b.cx += (blk.rect.right - b.rect.left)
                    m1 = math.pi if b.angle>0 else -math.pi
                    b.angle = m1-b.angle
                    b.reorient()
                elif blk.rect.bottom-b.rect.top <= 1 or b.rect.bottom-blk.rect.top <= 1: # We hit top or bottom of block
                    if (blk.rect.bottom - b.rect.top) <= 1: #we hit the bottom of the block, now adjust for the overhit.  Had to add this code because sometimes ball would stick to the edge
                        b.cy += (blk.rect.bottom - b.rect.top)
                    else:
                        b.cy += (blk.rect.top - b.rect.bottom)
                    b.angle = -b.angle
                    b.reorient()
                else: # Corner case - Physically, this code should work even when not a corner; however, collide_mask returns the FIRST pixel
                        #  in the first sprite that is collided, and a ball with a radius of 6 happens to be drawn with a top edge of 4 pixels.
                        #  Thus, if the ball hits a block squarely, there are actually 4 pixels in contact (while in the real world there would
                        #  be just one point of contact).  Plus, with 4 pixels, the ball's center is actually between the 2nd and 3rd pixels.
                        #  Between that half pixel offset and getting the first pixel (seems to be the furthest left) the contact angle calc
                        #  could be 15 degrees off.  And, when all the math below occurs, it looks unnatural.  A work around would be to get
                        #  all of the collided pixels and average them out, but that is not how the function works.
                        # So, we use it for the corners and it's okay.  People kind of expect a corner bounce to be a little weird.
                        # This code just determines the contact angle and bounces it off of a plane normal to that contact angle.
                        #  The space is rotated so that it emulates a ball hitting a vertical plane and we only need to negate dx,
                        #  and then we rotate the space back
                    ContactX, ContactY = pygame.sprite.collide_mask(blk, b)
                    ContactX += blk.rect.x
                    ContactY += blk.rect.y
                    contactAngle = -math.atan2(b.cy-ContactY, b.cx-ContactX)
                    ndx, ndy = RotateVel(b.dx, b.dy, contactAngle)
                    ndx = -ndx
                    b.dx, b.dy = RotateVel(ndx, ndy,-contactAngle)
                    b.angle = math.atan2(b.dy, b.dx)
                    b.angleCorrect()
                    b.reorient()
                if not blk.perm:
                    blk.hits -=1
                    if blk.hits == 0:
                        Score += blk.points
                        blk.remove(Blocks, AllSprites)
                        BlocksRemoved += 1
                        if blk.points > 0:
                            if (Score-blk.points)//ExtraBallPts < Score//ExtraBallPts: NumLives += 1  # Extra Life every 200 points
                            NumBlocks -= 1 # We only count blocks that are worth points
                        else:
                            if (Score % ExtraBallPts) - ExtraBallPts >= blk.points: NumLives = max(0,NumLives-1) # Remove Extra Life
                        if BlocksRemoved >= NumBalls*BlockSpeedUp: # We speed up the balls every BlockSpeedUp blocks for each active ball
                            fps = min(fps+fpsIncrement,400)
                            BlocksRemoved = 0
                        if NumBlocks == 0:
                            # Reset main ball
                            MainBall.cx, MainBall.cy = MainBall.rect.center = (GamePaddle.rect.centerx,GamePaddle.rect.top-MainBall.radius+5)
                            MainBall.dy = MainBall.speed = 0
                            MainBall.dx = GamePaddle.dx
                            MainBall.isalive = True
                            MainBall.angle = StartAngle
                            ActiveGame = False
                            Level += 1
                            Msg = "Level "+str(Level)+" Cleared!  "
                            AllSprites.remove(Blocks,Balls)
                            # Clear out the permanent and negative blocks
                            Blocks.empty()
                            # Clear out the extra balls
                            Balls.empty()
                            MainBall.add(Balls,AllSprites) # In case another ball destroyed the last block
                            NumBalls = 1
                            if Level == Levels*3:
                                Msg = "YOU WON!!  "+Msg
                    else:
                        blk.update() # Only called if a block with multiple hits didn't get destroyed.  Update the number on the block


        #Collision detect balls against balls
        for b1 in Balls:
            BallHitList = pygame.sprite.spritecollide(b1, Balls, False, ExclusiveCollide)
            for b2 in BallHitList:
                if b2.fresh:
                    # Check if we are hitting an inactive ball, and thus our ball count would increase.
                    if b1.isalive == False and b2.isalive:
                        NumBalls+=1 # A new ball is active
                        b1.isalive = True
                        # Check if this is a planted stationary ball.  If so, give it some direction opposite of colliding ball to help with collision math because
                        #  an non-moving ball calculates to an angle of atan(0,0)=0, which always cause a horizontal bounce.
                        if b1.speed == 0:
                            b1.speed = b2.speed
                            b1.angle = b2.angle + math.pi
                            b1.reorient()
                            b1.update()
                    # Since we don't know which ball was the alive ball got hit, we need to check the other one, too.
                    elif b2.isalive == False and b1.isalive:
                        NumBalls +=1
                        b2.isalive = True
                        # Check if this is a planted stationary ball.
                        if b2.speed == 0:
                            b2.speed = b1.speed
                            b2.angle = b1.angle + math.pi
                            b2.reorient()
                            b2.update()
                    b1.fresh = b2.fresh = False
                    ResolveCollision(b1, b2)  # Apparenty, the function passes by reference so, no need to return values.

        # Event Manager
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameRunning = False
            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    GamePaddle.dx = PaddleSpeed
                    if MainBall.dy == 0 and not Paused: MainBall.dx = PaddleSpeed # if the ball is not moving (dy=0) then move the ball with the paddle during start
                if event.key == K_LEFT:
                    GamePaddle.dx = -PaddleSpeed
                    if MainBall.dy == 0 and not Paused: MainBall.dx = -PaddleSpeed
            if event.type == KEYUP:
                if event.key == K_RIGHT or event.key == K_LEFT:
                    GamePaddle.dx = 0
                    if MainBall.dy == 0: MainBall.dx = 0
                if event.key == K_x:
                    NumBlocks = 0
                    AllSprites.remove(Blocks, Balls)
                    Level+=1
                    Blocks.empty()
                    Balls.empty()
                    Balls.add(MainBall)
                    MainBall.cx, MainBall.cy = MainBall.rect.center = (GamePaddle.rect.centerx,GamePaddle.rect.top-MainBall.radius+5)
                    MainBall.dy = MainBall.speed = 0
                    MainBall.dx = GamePaddle.dx
                    MainBall.isalive = True
                    MainBall.angle = StartAngle
                    Msg = ""
                if event.key == K_SPACE:
                    if NumLives == 0:
                        StartGame = ActiveGame = True
                    elif ActiveGame:  
                        for b in Balls:
                            b.speed = int(Paused)
                            b.reorient()
                        # Really should freeze/unfreeze the paddle, too, but this allows a cheat/helps in debug
                        Paused = not Paused 
                        Msg = "Paused" if Paused else ""              
                    else:
                        MainBall.speed = BallSpeedStart
                        MainBall.reorient()
                        MainBall.update()
                        ActiveGame = True
                        Msg = ""
                       

        GamePaddle.update()
        Balls.update()

        screen.fill((20,20,20))
        AllSprites.draw(screen)
        TextImg = MyFont.render(str(Score).zfill(2),True, "cadetblue")
        screen.blit(TextImg, TextImg.get_rect(center=(ScoreX,ScoreY)))
        TextImg = MyFont.render(str(Msg),True,"cadetblue")
        screen.blit(TextImg, TextImg.get_rect(center=(MsgX,MsgY)))
        for b in range(NumLives-1): #Draw the extra lives at the bottom of the screen
            pygame.draw.circle(screen, "white", (10+b*((BallRadius<<1)+3),ScreenHeight-10), BallRadius, 1)
        pygame.display.update()
        clock.tick(fps)

print("Game Over, Man")
pygame.quit()
exit
