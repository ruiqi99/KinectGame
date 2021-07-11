#this is the basic mode. In this mode, I use the kinect to keep track of 
#hand movement.
#The user should target the L target with their left hand, and R target with 
#their right hand to earn points.


#CITATION: the frame work is from:
#https://github.com/fletcher-marsh/kinect_python
from pykinect2 import PyKinectV2, PyKinectRuntime
from pykinect2.PyKinectV2 import *

import ctypes
import _ctypes
import pygame
import sys
import math
import random

class GameRuntime(object):

    def __init__(self, mask):
        pygame.init()
        self.mask = mask
        if self.mask != None:
            self.mask = pygame.transform.scale(self.mask, (300, 300))
        #CITATION: the background image is made by me by powerPoint
        self.BG = pygame.image.load("BasicBG.png")
        self.BG = pygame.transform.scale(self.BG, (1920, 1080))
        self.screenWidth = 1920
        self.screenHeight = 1080
        self.curRightHandHeight = 500
        self.curRightHandX = 500
        self.curLeftHandHeight = 500
        self.curLeftHandX = 500
        self.prevLeftHandHeight = 0
        self.prevLeftHandX = 0
        self.prevRightHandHeight = 0
        self.prevRightHandX = 0
        self.gameover = False
        self.paused = False
        self.robPos = []
        self.bonus = []
        self.score = 0
        self.end = False
        self.firstTime = True
        self.timeRemain = 30
        self.pink = (180, 120, 130)
        self.white = (255, 255, 255)
        self.blue = (97, 170, 195)
        self.pinkpink = (249, 140, 128)
        self.robRadLarge = 40
        self.robRadSmall = 25
        self.font = pygame.font.SysFont('mono', 24, bold=True)
        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()
        # Set the width and height of the window [width/2, height/2]
        self.screen = pygame.display.set_mode((960, 540), \
        pygame.HWSURFACE|pygame.DOUBLEBUF, 32)
        # Loop until the user clicks the close button.
        self.done = False
        # Kinect runtime object, we want color and body frames 
        self.kinect = PyKinectRuntime.PyKinectRuntime\
        (PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)
        # back buffer surface for getting Kinect color frames, 32bit color, 
        #width and height equal to the Kinect color frame size
        self.frameSurface = pygame.Surface((self.kinect.color_frame_desc.Width\
        , self.kinect.color_frame_desc.Height), 0, 32)
        #self.semiTrans = pygame.Surface((self.kinect.color_frame_desc.Width\
        #, self.kinect.color_frame_desc.Height),pygame.SRCALPHA , 32)
        self.new = pygame.Surface((self.kinect.color_frame_desc.Width\
        , self.kinect.color_frame_desc.Height), 0, 32)
        # here we will store skeleton data 
        self.bodies = None
        self.headX, self.headY = -30, -30
        #this userPos stores the positions of user's left hand, 
        #right hand, and head.
        self.userPos = [[self.curLeftHandX, self.screenHeight - \
        self.curLeftHandHeight], [self.curRightHandX, self.screenHeight \
        - self.curRightHandHeight]]
        
    def drawMask(self):
        if self.mask != None:
            self.frameSurface.blit(self.mask,(960 + 1400 * self.headX - 80,  540 - 1300 * self.headY - 170))
        

    def drawColorFrame(self, frame, targetSurface):
        targetSurface.lock()
        address = self.kinect.surface_as_array(targetSurface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        targetSurface.unlock()
    
    #this function draws two blue dots at the user's hands
    def drawDot(self):
        for item in self.userPos:
            pygame.draw.circle(self.frameSurface, 
                          self.blue, 
                          (int(item[0]), 
                           int(item[1])), self.robRadLarge)

    #this function randomly generate new targets(it also makes sure that the 
    #new position should have some distance from the user's hand)
    def isInBox(self, x, y):
        if x < 400 and y < 200 :
            return False
        return True
    
    def randomGenerate(self):
        margin = 40
        
        ranLeftHandX = self.curLeftHandX
        ranLeftHandY = self.curLeftHandHeight
        
        #use while loop and isValidNewPos helper function to continue 
        #generating new position until it is valid.
        while not self.isValidNewPos(ranLeftHandX, ranLeftHandY,\
         self.curLeftHandX, self.curLeftHandHeight) or not \
         self.isInBox(ranLeftHandX, ranLeftHandY):
            ranLeftHandX = random.randint(margin, self.screenWidth / 2)
            ranLeftHandY = random.randint(margin, self.screenHeight / 2)
            
        ranRightHandX = self.prevRightHandX
        ranRightHandY = self.prevRightHandHeight
        
        while not self.isValidNewPos(ranRightHandX, ranRightHandY, \
        self.curRightHandX, self.curRightHandHeight):
            ranRightHandX = random.randint(self.screenWidth / 2, \
            self.screenWidth - margin)
            ranRightHandY = random.randint(0, self.screenHeight / 2)
            
        return [[ranLeftHandX, ranLeftHandY], [ranRightHandX, ranRightHandY]]
    
    def generateBonus(self):
        ranX = random.randint(0 , self.screenWidth)
        ranY = random.randint(0 , self.screenHeight)
        return [ranX, ranY]
        
    
    def drawBonus(self):
        pygame.draw.circle(self.frameSurface, 
                          self.pinkpink, 
                          (int(self.bonus[0]), 
                           int(self.bonus[1])), self.robRadLarge)
    
    #this functions draws the  targets.
    def drawRob(self):
        for item in self.robPos:
            pygame.draw.circle(self.frameSurface, 
                          self.pink, 
                          (int(item[0]), 
                           int(item[1])), self.robRadLarge)

            
            pygame.draw.circle(self.frameSurface, 
                          self.white, 
                          (int(item[0]), 
                           int(item[1])), self.robRadSmall)
            index = self.robPos.index(item)
            
            #this helper function draw left and draw right draws L and R on 
            #the target
            if index == 0:
                self.drawLeft(item[0], item[1])
            else:
                self.drawRight(item[0], item[1])
                           
    def drawLeft(self, x, y):
        marg = 20
        pygame.font.init()
        #CITATION:  the following font is copied and revise from website:
        #https://programtalk.com/python-examples/pygame.font.SysFont/
        font1 = pygame.font.SysFont('mono', 50, bold = True, italic = True)
        text = font1.render("L", 1, (0,0,0))
        self.frameSurface.blit(text, (x - marg, y - marg))
        
        
    def drawRight(self, x, y):
        marg = 20
        pygame.font.init()
        #CITATION:  the following font is copied and revise from website:
        #https://programtalk.com/python-examples/pygame.font.SysFont/
        font1 = pygame.font.SysFont('mono', 50, bold = True, italic = True)
        text = font1.render("R", 1, (0, 0, 0))
        self.frameSurface.blit(text, (x - marg, y - marg))
        
    #calculate the distance between current hand position and the new target
    #pass if the distance is large enough
    def isValidNewPos(self, ax, ay, prevax, prevay):
        rad = 500
        dis = self.calculateDis(ax, ay, prevax, prevay)
        if dis >= rad:
            return True
        return False
        
    #calculate the distance between two points
    def calculateDis(self, ax, ay, bx, by):
        dis = ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5
        return dis
                           
                           
    def isCollide(self, x1, y1, x2, y2):
        allowError = 40
        dis = self.calculateDis(x1, x2, y1, y2)
        if dis < allowError:
            print("Congrat!")
            return True
        return False
        
    #draw the information: current score and time remaining
    def drawInfo(self, thisTime):
        pygame.font.init()
        #CITATION:  the following font is copied and revise from website:
        #https://programtalk.com/python-examples/pygame.font.SysFont/
        font1 = pygame.font.SysFont('mono', 39, bold=True)
        text = font1.render("Score:" + str(self.score), 1, (0, 0, 0))
        text2 = font1.render("Time:" + str(round(30 - thisTime, 1)), \
        1, (0, 0, 0))
        self.frameSurface.blit(text, (100,100))
        self.frameSurface.blit(text2, (100,150))
    
    #draw a white background for the info
    def drawInfoBackGround(self):
        pygame.draw.rect(self.frameSurface, (255, 255, 255), \
        (0, 0, 400, 200))
    
    #a start page, user move mouse over start button to start
    #will add more features
    def stop(self):
        while self.paused == True:
            #CITATION: the next four lines are from 
            #https://pythonprogramming.net/pygame-button-function-events/
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            margin = 200
            textMargin = 230
            width = 1600
                    
            nameAx, nameAy, nameBx, nameBy = margin, margin ,width - \
            margin, margin
            pygame.draw.rect(self.frameSurface, (0,0,0), \
            (nameAx, nameAy, nameBx, nameBy))
            
            boxAx, boxAy, boxBx, boxBy = 400, 500, 930, 200
            pygame.draw.rect(self.frameSurface, (0,0,0), \
            (boxAx, boxAy, boxBx, boxBy))
            
            pygame.font.init()
            fontSize = 110
            fontColR, fontColG, fontColB = 232, 171, 0
            #CITATION:  the following font is copied and revise from website:
            #https://programtalk.com/python-examples/pygame.font.SysFont/
            font1 = pygame.font.SysFont('mono', fontSize, bold=True)
            text = font1.render("Paused" , 1, \
            (fontColR, fontColG, fontColB))
            self.frameSurface.blit(text, (textMargin, textMargin))
            
            text2MarX, text2MarY = 650, 550
            fontSize = 130
            #CITATION:  the following font is copied and revise from website:
            #https://programtalk.com/python-examples/pygame.font.SysFont/
            font1 = pygame.font.SysFont('mono', fontSize, bold=True)
            text2 = font1.render("Restart" , 1, \
            (fontColR, fontColG, fontColB))
            self.frameSurface.blit(text2, (text2MarX, text2MarY))
            
            mouse = pygame.mouse.get_pos()
            xMin = 195
            xMax = 660
            yMin = 246
            yMax = 349
            if xMin < mouse[0] < xMax and yMin < mouse[1] < yMax:
                self.paused = False
                break

            hToW = float(self.frameSurface.get_height()) / self.\
            frameSurface.get_width()
            targetHeight = int(hToW * self.screen.get_width())
            surfaceToDraw = pygame.transform.scale(self.frameSurface\
            , (self.screen.get_width(), targetHeight));
            self.screen.blit(surfaceToDraw, (0,0))
            surfaceToDraw = None # memory save
            pygame.display.update()

    
    def startPage(self):
        while self.firstTime == True:
            #CITATION: the next four lines are from 
            #https://pythonprogramming.net/pygame-button-function-events/
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                    

            pygame.draw.rect(self.frameSurface, (255, 255, 255, 100), \
        (0, 0, self.kinect.color_frame_desc.Width\
        , self.kinect.color_frame_desc.Height))
            margin = 200
            textMargin = 230
            width = 1600
            self.frameSurface.blit(self.BG, (0,0))
            
            
            boxAx, boxAy, boxBx, boxBy = 1580, 880, 930, 200
            pygame.draw.rect(self.frameSurface, (0,0,0), \
            (boxAx, boxAy, boxBx, boxBy))
            
            pygame.font.init()
            fontColR, fontColG, fontColB = 232, 171, 0

            text2MarX, text2MarY = 1620, 940
            fontSize = 70
            #CITATION:  the following font is copied and revise from website:
            #https://programtalk.com/python-examples/pygame.font.SysFont/
            font1 = pygame.font.SysFont('mono', fontSize, bold=True)
            text2 = font1.render("Start" , 1, \
            (fontColR, fontColG, fontColB))
            self.frameSurface.blit(text2, (text2MarX, text2MarY))
            
            mouse = pygame.mouse.get_pos()
            xMin = 1580
            xMax = 2000
            yMin = 880
            yMax = 2000
            if xMin < mouse[0] * 2 < xMax and yMin < mouse[1] * 2 < yMax:
                self.firstTime = False
                break

            hToW = float(self.frameSurface.get_height()) / self.\
            frameSurface.get_width()
            targetHeight = int(hToW * self.screen.get_width())
            surfaceToDraw = pygame.transform.scale(self.frameSurface\
            , (self.screen.get_width(), targetHeight));
            self.screen.blit(surfaceToDraw, (0,0))
            surfaceToDraw = None # memory save
            pygame.display.update()

    def endPage(self):
        while self.end == True:
            #CITATION: the next four lines are from 
            #https://pythonprogramming.net/pygame-button-function-events/
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            
            pygame.draw.rect(self.frameSurface, (255, 255, 255, 100), \
        (0, 0, self.kinect.color_frame_desc.Width\
        , self.kinect.color_frame_desc.Height))
            margin = 200
            textMargin = 230
            width = 1600
            
            nameAx, nameAy, nameBx, nameBy = margin, margin ,width - \
            margin, margin
            pygame.draw.rect(self.frameSurface, (0,0,0), \
            (nameAx, nameAy, nameBx, nameBy))
            
            boxAx, boxAy, boxBx, boxBy = 400, 500, 930, 200
            pygame.draw.rect(self.frameSurface, (0,0,0), \
            (boxAx, boxAy, boxBx, boxBy))
            
            pygame.font.init()
            fontSize = 110
            fontColR, fontColG, fontColB = 232, 171, 0
            #CITATION:  the following font is copied and revise from website:
            #https://programtalk.com/python-examples/pygame.font.SysFont/
            font1 = pygame.font.SysFont('mono', fontSize, bold=True)
            text = font1.render("Time Up!" , 1, \
            (fontColR, fontColG, fontColB))
            self.frameSurface.blit(text, (textMargin, textMargin))
            
            text2MarX, text2MarY = 650, 550
            fontSize = 130
            font1 = pygame.font.SysFont('mono', fontSize, bold=True)
            text2 = font1.render("Quit" , 1, \
            (fontColR, fontColG, fontColB))
            self.frameSurface.blit(text2, (text2MarX, text2MarY))
            
            mouse = pygame.mouse.get_pos()
            xMin = 195
            xMax = 660
            yMin = 246
            yMax = 349
            if xMin < mouse[0] < xMax and yMin < mouse[1] < yMax:
                self.end = True
                break

            hToW = float(self.frameSurface.get_height()) / self.\
            frameSurface.get_width()
            targetHeight = int(hToW * self.screen.get_width())
            surfaceToDraw = pygame.transform.scale(self.frameSurface\
            , (self.screen.get_width(), targetHeight));
            self.screen.blit(surfaceToDraw, (0,0))
            surfaceToDraw = None # memory save
            pygame.display.update()

    def run(self):
        pygame.font.init()
        # -------- Main Program Loop -----------


        while not self.done:
            self.new.fill((255, 120, 234))

            thisTime = pygame.time.get_ticks() / 1000

            self.timeRemain = int(30 - thisTime)
            if thisTime > 30:
                self.end = True
                self.endPage()
                self.done = True

            
            pygame.display.flip()
            self.screen.blit(self.frameSurface, (0, 0))
            #self.screen.blit(self.semiTrans, (0,0))

            # --- Main event loop
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self.done = True 
                #CITATION: the following two lines:
                #https://stackoverflow.com/questions/30744237
                #/how-to-create-a-pause-button-in-pygame
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = True
                        self.stop()

                    # Flag that we are done so we exit this loop
            # We have a color frame. Fill out back buffer surface 
            #with frame's data 

            if self.kinect.has_new_color_frame():
                frame = self.kinect.get_last_color_frame()
                self.drawColorFrame(frame, self.frameSurface)
                frame = None # memory save
                
            if self.kinect.has_new_body_frame(): 
                self.bodies = self.kinect.get_last_body_frame()

                if self.bodies is not None: 
                    for i in range(0, self.kinect.max_body_count):
                        body = self.bodies.bodies[i]
    
                        if not body.is_tracked: 
                            continue 

                        joints = body.joints 
                        # save the hand positions
                        basicPosY = self.screenHeight / 2
                        basicPosX = self.screenWidth / 2
                        ratio = 1600
                        if joints[PyKinectV2.JointType_HandRight].\
                        TrackingState != PyKinectV2.TrackingState_NotTracked:
                            self.curRightHandHeight = basicPosY +\
                             joints[PyKinectV2.JointType_HandRight].\
                             Position.y * ratio
                            self.curRightHandX = basicPosX +\
                             joints[PyKinectV2.JointType_HandRight].\
                             Position.x * ratio
                            
                            
                        if joints[PyKinectV2.JointType_HandLeft].\
                        TrackingState != PyKinectV2.TrackingState_NotTracked:
                            self.curLeftHandHeight = basicPosY \
                            + joints[PyKinectV2.JointType_HandLeft].\
                            Position.y * ratio
                            self.curLeftHandX = basicPosX + joints\
                            [PyKinectV2.JointType_HandLeft].Position.x * ratio
                        
                        
                        self.userPos = [[self.curLeftHandX, self.screenHeight \
                        - self.curLeftHandHeight],[self.curRightHandX, \
                        self.screenHeight - self.curRightHandHeight]] 
                        
                        #store the previous information
                        self.prevLeftHandHeight = self.curLeftHandHeight
                        self.prevLeftHandX = self.curRightHandX
                        self.prevRightHandHeight = self.curRightHandHeight
                        self.prevRightHandX = self.curRightHandX
                        #CITATION: the following code of tracking head is from:
                        #https://github.com/jtaceron/Kinect-Fruit-Ninja
                        if joints[PyKinectV2.JointType_Head].TrackingState != PyKinectV2.TrackingState_NotTracked:
                            self.headX = joints[PyKinectV2.JointType_Head].Position.x  
                            self.headY = joints[PyKinectV2.JointType_Head].Position.y 

            self.drawMask()
            self.drawDot()
            #generate new targets every five seconds
            allowError = 0.02
            if thisTime % 5 < allowError:
                self.robPos = self.randomGenerate()
                
            if thisTime % 8 < allowError:
                self.bonus = self.generateBonus()
            
            #if both targets are touched, then generate new targets.
            twoEmpty = [[-20, -20], [-20, -20]]
            if self.robPos == twoEmpty:
                self.robPos = self.randomGenerate()
                
                
                
            self.drawRob()
            if self.bonus != None:
                if len(self.bonus) == 2:
                    self.drawBonus()

            #detect whether the user touch the target
            #if so, move the target to [-20, -20], where the user cannot see
            for idx in range(0, len(self.userPos)):
                userX, userY = self.userPos[idx]
                userY = self.screenHeight - userY
                if len(self.robPos) >idx:
                    robX, robY = self.robPos[idx]
                else:
                    break
                res = self.isCollide(userX, robX, self.screenHeight \
                - userY, robY)
                if res == True:
                    self.score += 1
                    self.robPos[idx] = [-20, -20]
                    print(self.score)
                    
                    
                    
            if self.bonus != None and len(self.bonus) == 2:
                for idx in range(0, len(self.userPos)):
                    userX, userY = self.userPos[idx]
                    bonusRes = self.isCollide(userX, self.bonus[0], \
                    userY, self.bonus[1])
                
                    if bonusRes == True:
                        self.score += 2
                        self.bonus = []
                        print(self.score)
                        break

            
            self.drawInfoBackGround()
            self.drawInfo(thisTime)
            
            hToW = float(self.frameSurface.get_height()) / self.frameSurface.\
            get_width()
            targetHeight = int(hToW * self.screen.get_width())
            surfaceToDraw = pygame.transform.scale(self.frameSurface, \
            (self.screen.get_width(), targetHeight));
            self.screen.blit(surfaceToDraw, (0,0))
            surfaceToDraw = None # memory save
            pygame.display.update()

            # --- Limit t o 60 frames per second
            self.clock.tick(60)
        # Close our Kinect sensor, close the window and quit.
        self.kinect.close()
        pygame.quit()
def runBasic(mask):
    game = GameRuntime(mask);
    game.startPage()
    #CITATION: the syntax of the next two lines is from:
    #https://stackoverflow.com/questions/7746263/
    #how-can-i-play-an-mp3-with-pygame
    pygame.mixer.music.load("BGM.MP3")
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play()
    game.run()
