#This is the pathTracking mode, also called the monsters mode.
#In this mode, the player is supposed to reach the target within the shortest 
#move. Also, the player should not touch the target, otherwise, both the 
#target and the monster disapears.
#the shorter the move, the higher the score. I calculate the distance by 
#adding up the distance between handPosition and previousHandPosition each
#time the run function runs.

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
        #CITATION: the background image is made by me by powerPoint
        self.BG = pygame.image.load("pathTrackingBG.png")
        self.BG = pygame.transform.scale(self.BG, (1920, 1080))
        self.headX, self.headY = -30, -30
        self.mask = mask
        if self.mask != None:
            self.mask = pygame.transform.scale(self.mask, (300, 300))
        self.screenWidth = 1920
        self.screenHeight = 1080
        self.currentScore = 0
        self.distanceTraveled = 0
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

        self.mons1 = [-100,-100]
        self.mons2 = [-100, -100]
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
        #CITATION:  the following font is copied and revise from website:
        #https://programtalk.com/python-examples/pygame.font.SysFont/
        self.font = pygame.font.SysFont('mono', 24, bold=True)
        
        #CITATION: the following monster image is from
        #https://www.123rf.com/photo_61158809_stock-vector-c
        #artoon-alien-monster-graphic-mutant-character-colorful-
        #toy-cute-alien-monster-cute-cartoon-creature.html
        self.mons1img = pygame.image.load("mons1.png")
        #CITATION: the following monster image is from 
        #https://www.iconfinder.com/icons/3390196/cute_monster
        #_fuzzy_monster_monster_cartoon_monster_character_toy_monster_icon
        self.mons2img = pygame.image.load("mons2.png")
        
        #Scale the image
        self.mons1img = pygame.transform.scale(self.mons1img, (200, 200))
        self.mons2img = pygame.transform.scale(self.mons2img, (150, 150))
        
        self.leftTotalDis = 0
        self.rightTotalDis = 0

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
        #this userPos stores the positions of user's left hand, 
        #right hand, and head.
        self.userPos = [[self.curLeftHandX, self.screenHeight - \
        self.curLeftHandHeight], [self.curRightHandX, self.screenHeight \
        - self.curRightHandHeight]]

    def drawMask(self):
        if self.mask != None:
            self.frameSurface.blit(self.mask,(960 + 1400 * self.headX - 80,  540 - 1300 * self.headY - 170))
        
        
    def trackTotalDis(self,hand):
        if hand == "left":
            preX = self.prevLeftHandX
            preY = self.prevLeftHandHeight
            thisTimeDis = self.calculateDis(self.userPos[0][0], self.userPos[0][1], preX, self.screenHeight - preY)
            if thisTimeDis > 500:
                thisTimeDis = 0
            if thisTimeDis < 3:
                thisTimeDis = 0
            self.leftTotalDis += thisTimeDis
        else:
            preX = self.prevRightHandX
            preY  = self.prevRightHandHeight
            thisTimeDis = self.calculateDis(self.userPos[1][0], self.userPos[1][1], preX, self.screenHeight - preY)
            if thisTimeDis > 500:
                thisTimeDis = 0
            if thisTimeDis < 3:
                thisTimeDis = 0
            print("right", round(self.userPos[1][0], 1), round(self.userPos[1][1], 1), round(preX, 1), round(self.screenHeight - preY, 1))
            self.rightTotalDis += thisTimeDis
        


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
    
    def ifTouchMons1(self, x, y):
        margin = 30
        if x > self.mons1[0] + margin and x < self.mons1[0] + 200 - margin and \
        y > self.mons1[1] + margin and y < self.mons1[1] + 200 - margin:
            return True
        return False
        
    def ifTouchMons2(self, x, y):
        marginSmall = 10
        marginBig = 40
        if x > self.mons2[0] + marginSmall and x < self.mons2[0] + 150  + marginSmall and \
        y > self.mons2[1] + marginSmall and y < self.mons2[1] + 150 - marginBig:
            return True
        return False

    
    def randomGenerate(self):
        margin = 40
        
        ranLeftHandX = self.curLeftHandX
        ranLeftHandY = self.curLeftHandHeight
        
        #use while loop and isValidNewPos helper function to continue 
        #generating new position until it is valid.
        while not self.isValidNewPos(ranLeftHandX, ranLeftHandY,\
         self.curLeftHandX, self.curLeftHandHeight) or not \
         self.isInBox(ranLeftHandX, ranLeftHandY):
            ranLeftHandX = random.randint(margin * 5, self.screenWidth / 2)
            ranLeftHandY = random.randint(margin, self.screenHeight / 2)
            
        ranRightHandX = self.prevRightHandX
        ranRightHandY = self.prevRightHandHeight
        
        while not self.isValidNewPos(ranRightHandX, ranRightHandY, \
        self.curRightHandX, self.curRightHandHeight):
            ranRightHandX = random.randint(self.screenWidth / 2, \
            self.screenWidth - margin)
            ranRightHandY = random.randint(0, self.screenHeight / 2)
            

            
        return [[ranLeftHandX, ranLeftHandY], [ranRightHandX, ranRightHandY]]
        
    def generateMons(self):
        mons1X = random.randint(int(min(self.curLeftHandX,200, self.robPos[0]\
        [0])),int(max(self.curLeftHandX, self.robPos[0][0])))
        mons1Y = random.randint(int(min(self.screenHeight - \
        self.curLeftHandHeight, self.robPos[0][1])), \
        int(max(self.screenHeight -self.curLeftHandHeight, self.robPos[0][1])))
        mons1 = [int(mons1X), int(mons1Y)]
        
        mons2X = random.randint(int(min(self.curRightHandX, \
        self.robPos[1][0])), int(max(self.curRightHandX, self.robPos[1][0])))
        mons2Y = random.randint(int(min(self.screenHeight - \
        self.curRightHandHeight, self.robPos[1][1])),int( min(self.\
        screenHeight - self.curRightHandHeight, self.robPos[1][1])))
        mons2 = [int(mons2X), int(mons2Y)]

        
        return mons1, mons2
    
    def drawMons(self):
        if len(self.mons1) == 2 and  len(self.mons2) == 2:
            self.frameSurface.blit(self.mons1img, (self.mons1[0], \
            self.mons1[1]))
            self.frameSurface.blit(self.mons2img, (self.mons2[0], \
            self.mons2[1]))
        

    
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
        self.frameSurface.blit(text, (int(x - marg), int(y - marg)))
        
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
        text = font1.render("Score:" + str(round(self.score,1)), 1, (0, 0, 0))
        text2 = font1.render("Time:" + str(round(30 - thisTime, 1)), \
        1, (0, 0, 0))
        text3 = font1.render("Score:" + str(round(self.currentScore, 1)), \
        1, (0,0,0))
        text4 = font1.render("Total", 1, (0,0,0))
        text5 = font1.render("Current", 1, (0,0,0))

        self.frameSurface.blit(text2, (130,400))
        self.frameSurface.blit(text4, (130, 470))
        self.frameSurface.blit(text, (130,500))
        self.frameSurface.blit(text5, (130, 570))
        self.frameSurface.blit(text3, (130, 600))

    
    #draw a white background for the info
    def drawInfoBackGround(self):
        backGround = pygame.image.load("bull.png")
        backGround = pygame.transform.scale(backGround, (400, 800))
        pygame.draw.rect(self.frameSurface, (255, 255, 255), \
        (100, 350, 270, 300))
        self.frameSurface.blit(backGround, (50, 50))

    
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
                        
                        self.trackTotalDis("left")
                        self.trackTotalDis("right")
                        
                        #store the previous information
                        self.prevLeftHandHeight = self.curLeftHandHeight
                        self.prevLeftHandX = self.curLeftHandX
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
            allowError = 0.03
            if thisTime % 4 < allowError:
                self.robPos = self.randomGenerate()
                self.mons1, self.mons2 = self.generateMons()
                

            
            #if both targets are touched, then generate new targets.
            twoEmpty = [[-20, -20], [-20, -20]]
            if self.robPos == twoEmpty:
                self.robPos = self.randomGenerate()
                self.mons1, self.mons2 = self.generateMons()
                
                
                
            self.drawRob()

                    
                    
            #whether touch the monster
            leftHand = self.userPos[0]
            resMons1left = self.ifTouchMons1(leftHand[0], leftHand[1])
            resMons2left = self.ifTouchMons2(leftHand[0], leftHand[1])
            
            rightHand = self.userPos[1]
            resMons1right = self.ifTouchMons1(rightHand[0], rightHand[1])
            resMons2right = self.ifTouchMons2(rightHand[0], rightHand[1])
            
            leftRes = resMons1left or resMons1right
            rightRes = resMons2left or resMons2right
            
            if leftRes ==  True:
                self.robPos[0] = [-20, -20]
                self.mons1 = [-100, -100]
            
            if rightRes == True:
                self.robPos[1] = [-20, -20]
                self.mons2 = [-100, -100]

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
                    if idx == 0:
                        self.distanceTraveled = self.leftTotalDis
                    else:
                        self.distanceTraveled = self.rightTotalDis
                    
                    self.currentScore = 10000 / self.distanceTraveled
                    
                    self.score += self.currentScore
                    self.robPos[idx] = [-20, -20]
                    if  idx == 0:
                        self.leftTotalDis = 0
                    else:
                        self.rightTotalDis = 0
                    print(self.score)
                    
            
            self.drawInfoBackGround()
            self.drawInfo(thisTime)
            self.drawMons()
            
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

def runPathTracking(mask):
    game = GameRuntime(mask)
    game.startPage()
    #CITATION: the syntax of the next two lines is from:
    #https://stackoverflow.com/questions/7746263/
    #how-can-i-play-an-mp3-with-pygame
    pygame.mixer.music.load("BGM.MP3")
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play()
    game.run()
