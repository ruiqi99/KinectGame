#this is a double mode.
#it is similar to the fruit the mode, the difference is that I use kinect to
#keep track of two players at the same time. 
#the player who gets more points wins the game.

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

    def __init__(self):
        pygame.init()
        #load the info page
        #CITATION: the background image is made by me by powerPoint
        self.BG = pygame.image.load("doubleBG.png")
        self.BG = pygame.transform.scale(self.BG, (1920, 1080))
        
        #load some images
        #CITATION: the pineapple image is  from:
        #https://www.pinclipart.com/pindetail/iimimh_pineapple
        #-cartoon-pineapple-transparent-background-clipart/
        self.pineapple = pygame.image.load("pineapple.png")
        #CITATION: the strawberry image is from:
        #https://www.kisspng.com/png-strawberry-aedmaasikas-
        #cartoon-cartoon-strawberry-205602/
        self.strawberry = pygame.image.load("strawberry.png")
        #CITATION: the basket image is from:
        #https://mastergolflivestream.com/image/clipart-fruit-\
        #fruit-bowl/152731.html
        self.basket = pygame.image.load("basket.png")
        #CITATION: the bulletin board picture is from:
        #https://www.vectorstock.com/royalty-free-vector
        #/a-lion-holding-an-empty-bulletin-board-vector-1484077
        self.infoBoard = pygame.image.load("bull.png")
        self.scoreBack = pygame.image.load("doublescore.png")
        
        
        #scale the image
        self.pineapple = pygame.transform.scale(self.pineapple,(70, 110))
        self.strawberry = pygame.transform.scale(self.strawberry, (80, 80))
        self.basket = pygame.transform.scale(self.basket, (700, 340))
        self.infoBoard = pygame.transform.scale(self.infoBoard, (350, 700))
        self.scoreBack = pygame.transform.scale(self.scoreBack, (800, 200))
        
        #a list of fruits
        self.listOfFruits = [self.strawberry, self.pineapple]
        
        #set the initial value of basket, hand position, pre hand position
        self.basketX = 750
        self.basketY = 620
        self.screenWidth = 1920
        self.screenHeight = 1080
        self.AcurRightHandHeight = 500
        self.AcurRightHandX = 500
        self.AcurLeftHandHeight = 500
        self.AcurLeftHandX = 500
        
        self.BcurRightHandHeight = 500
        self.BcurRightHandX = 500
        self.BcurLeftHandHeight = 500
        self.BcurLeftHandX = 500

        
        #keep track of what fruit each hand is grabbing
        self.ArightGrabbingFruit = None
        self.AleftGrabbingFruit = None
        self.AisLeftPicking = False
        self.AisRightPicking = False
        
        self.BrightGrabbingFruit = None
        self.BleftGrabbingFruit = None
        self.BisLeftPicking = False
        self.BisRightPicking = False
        
        self.gameover = False
        self.paused = False
        self.robPos = [[]]
        self.Ascore = 0
        self.Bscore = 0
        
        #keep track of if each hand is grabbing
        self.AleftGrabbing = False
        self.ArightGrabbing = False
        
        self.BleftGrabbing = False
        self.BrightGrabbing = False
        
        
        self.end = False
        self.firstTime = True
        self.timeRemain = 30
        
        #define some colors
        self.pink = (180, 120, 130)
        self.white = (255, 255, 255)
        self.blue = (97, 170, 195)
        self.pinkpink = (249, 140, 128)
        
        #define the size of target
        self.robRadLarge = 40
        self.robRadSmall = 25
        
        #CITATION: the idea of playList is from:
        #https://github.com/jtaceron/Kinect-Fruit-
        #Ninja/blob/master/Fruit_Ninja.py
        self.player = [-1, -1]
        self.previousID = -1
        #CITATION:  the following font is copied and revise from website:
        #https://programtalk.com/python-examples/pygame.font.SysFont/
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
        
        self.tracked = []
        
        
        #this userPos stores the positions of user's left hand, 
        #right hand, and head.
        self.AuserPos = [[self.AcurLeftHandX, self.screenHeight - \
        self.AcurLeftHandHeight], [self.AcurRightHandX, self.screenHeight \
        - self.AcurRightHandHeight]]
        
        self.BuserPos = [[self.BcurLeftHandX, self.screenHeight - \
        self.BcurLeftHandHeight], [self.BcurRightHandX, self.screenHeight \
        - self.BcurRightHandHeight]]
        

    # a start page
    def startPage(self):
        while self.firstTime == True:
            #CITATION: the next four lines are from 
            #https://pythonprogramming.net/pygame-button-function-events/
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                    

            pygame.draw.rect(self.frameSurface, (255, 255, 255, 100), \
        (0, 0, 1920, 1080))
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
                #break

            hToW = float(self.frameSurface.get_height()) / self.\
            frameSurface.get_width()
            targetHeight = int(hToW * self.screen.get_width())
            surfaceToDraw = pygame.transform.scale(self.frameSurface\
            , (self.screen.get_width(), targetHeight));
            self.screen.blit(surfaceToDraw, (0,0))
            surfaceToDraw = None # memory save
            pygame.display.update()
    #draw the basket
    def drawBasket(self):
        self.frameSurface.blit(self.basket, (self.basketX, self.basketY))
    #detect whether a position is in the basket
    def isInBasket(self, x, y):
        if x > self.basketX and x < self.basketX + 400 and y > self.basketY\
        and y < self.basketY + 300:
            return True
        return False
    
    def drawScoreBack(self):
        self.frameSurface.blit(self.scoreBack, (560, 0))

    def drawColorFrame(self, frame, targetSurface):
        targetSurface.lock()
        address = self.kinect.surface_as_array(targetSurface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        targetSurface.unlock()
    
    #this function draws two blue dots at the user's hands
    def drawDot(self):
        #userA

        if self.player[0] == 1:
            for idx in range(0, len(self.AuserPos)):
                if idx == 0:
                    if self.AisLeftPicking:
                        self.frameSurface.blit(self.AleftGrabbingFruit\
                        ,(int(self.AuserPos[idx][0]),\
                         int(self.AuserPos[idx][1])))
                    else:
                        pygame.draw.circle(self.frameSurface, 
                            self.blue, 
                            (int(self.AuserPos[idx][0]), 
                            int(self.AuserPos[idx][1])), self.robRadLarge)
                
                if idx == 1:
                    if self.AisRightPicking:
                        self.frameSurface.blit(self.ArightGrabbingFruit\
                        ,(int(self.AuserPos[idx][0]), \
                        int(self.AuserPos[idx][1])))
                    else:
                        pygame.draw.circle(self.frameSurface, 
                            self.blue, 
                            (int(self.AuserPos[idx][0]), 
                            int(self.AuserPos[idx][1])), self.robRadLarge)
        #userB 
        if self.player[1] == 1:               
            for idx in range(0, len(self.BuserPos)):
                if idx == 0:
                    if self.BisLeftPicking:
                        self.frameSurface.blit(self.BleftGrabbingFruit\
                        ,(int(self.BuserPos[idx][0]), \
                        int(self.BuserPos[idx][1])))
                    else:
                        pygame.draw.circle(self.frameSurface, 
                            self.blue, 
                            (int(self.BuserPos[idx][0]), 
                            int(self.BuserPos[idx][1])), self.robRadLarge)
                
                if idx == 1:
                    if self.BisRightPicking:
                        self.frameSurface.blit(self.BrightGrabbingFruit\
                        ,(int(self.BuserPos[idx][0]), \
                        int(self.BuserPos[idx][1])))
                    else:
                        pygame.draw.circle(self.frameSurface, 
                            self.blue, 
                            (int(self.BuserPos[idx][0]), 
                            int(self.BuserPos[idx][1])), self.robRadLarge)




    #randomly generate fruit position
    def randomGenerate(self):
        margin = 20
        height = 200

        ranPosX = random.randint(margin, self.screenWidth - margin)
        ranPosY = random.randint(150, 200)
        fruitType = random.choice([self.pineapple, self.strawberry])

        return self.robPos.append([ranPosX, ranPosY, fruitType])
    
    #this functions draws the  targets.
    def drawRob(self):
        if self.robPos != [[]] and len(self.robPos) != 0:
            for item in self.robPos:

                if item != []:
                    x, y, fruit = item
                    if fruit == None:
                        continue
                    self.frameSurface.blit(fruit ,(int(x), int(y)))
            
        
    #calculate the distance between two points
    def calculateDis(self, ax, ay, bx, by):
        dis = ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5
        return dis
    def isBPicking(self):

        #detect whether the user touch the target
        #if so, move the target to [-20, -20], where the user cannot see
        for idxOut in range(0, len(self.BuserPos)):
            userX, userY = self.BuserPos[idxOut]
            userY = self.screenHeight - userY
            
            if self.robPos != []:
                
                for idx in range(0, len(self.robPos)):
                    if self.robPos[idx] != []:
                        fruitX, fruitY, fruit = self.robPos[idx]
                        res = self.isCollide(userX + 30, fruitX,\
                        self.screenHeight - userY + 30, fruitY)
                        
                        if res == True:
                            if idxOut == 0:
                                ifGrabbing = self.BleftGrabbing
                                hand = "left"
                            else:
                                ifGrabbing = self.BrightGrabbing
                                hand = "right"
                            
                            
                            if ifGrabbing == False:
                                continue
                            else:
                                if hand == "left":
                                    if self.BleftGrabbingFruit == None:
                                        self.BisLeftPicking = True
                                        self.BleftGrabbingFruit = fruit
                                        self.robPos[idx] = [-20, -20, None]                 
                                else:
                                    if self.BrightGrabbingFruit == None:
                                        self.BisRightPicking = True
                                        self.BrightGrabbingFruit = fruit
                                        self.robPos[idx] = [-20, -20, None]                       
                                        
                                            
    def isAPicking(self):

        #detect whether the user touch the target
        #if so, move the target to [-20, -20], where the user cannot see
        for idxOut in range(0, len(self.AuserPos)):
            userX, userY = self.AuserPos[idxOut]
            userY = self.screenHeight - userY
            
            if self.robPos != []:
                
                for idx in range(0, len(self.robPos)):
                    if self.robPos[idx] != []:
                        fruitX, fruitY, fruit = self.robPos[idx]
                        res = self.isCollide(userX + 30, fruitX,\
                        self.screenHeight - userY + 30, fruitY)
                        
                        if res == True:
                            if idxOut == 0:
                                ifGrabbing = self.AleftGrabbing
                                hand = "left"
                            else:
                                ifGrabbing = self.ArightGrabbing
                                hand = "right"
                            
                            
                            if ifGrabbing == False:
                                continue
                            else:
                                if hand == "left":
                                    if self.AleftGrabbingFruit == None:
                                        self.AisLeftPicking = True
                                        self.AleftGrabbingFruit = fruit
                                        self.robPos[idx] = [-20, -20, None]                 
                                else:
                                    if self.ArightGrabbingFruit == None:
                                        self.AisRightPicking = True
                                        self.ArightGrabbingFruit = fruit
                                        self.robPos[idx] = [-20, -20, None]                       

    
    #a helper function, it detects whether two position intersects
    
    def isCollide(self, x1, y1, x2, y2):
        allowError = 50
        dis = self.calculateDis(x1, x2, y1, y2)
        if dis < allowError:
            return True
        return False
        
    #draw the information: current score and time remaining
    def drawInfo(self):
        pygame.font.init()
        #CITATION:  the following font is copied and revise from website:
        #https://programtalk.com/python-examples/pygame.font.SysFont/
        font1 = pygame.font.SysFont('mono', 45, bold=True)
        text = font1.render(str(self.Ascore), 1, (255, 255, 255))
        text2 = font1.render(str(self.Bscore), 
        1, (255, 255, 255))
        self.frameSurface.blit(text, (700, 110))
        self.frameSurface.blit(text2, (1170, 110))
    
    #draw a white background for the info
    def drawInfoBackGround(self):
        pygame.draw.rect(self.frameSurface, (255, 255, 255), \
        (120, 200, 240, 460))
        self.frameSurface.blit(self.infoBoard, (70, 70))
    
    #this function draws information on the bulletin board
    def drawSample(self):
        samplePineapple = pygame.transform.scale(self.pineapple, (80, 110))
        sampleStrawberry = pygame.transform.scale(self.strawberry, (85, 85))
        
        self.frameSurface.blit(samplePineapple, (140, 460))
        self.frameSurface.blit(sampleStrawberry, (140, 570))
        
        pygame.font.init()
        #CITATION:  the following font is copied and revise from website:
        #https://programtalk.com/python-examples/pygame.font.SysFont/
        font1 = pygame.font.SysFont('mono', 39, bold=True)
        text = font1.render(":5", 1, (0, 0, 0))
        text2 = font1.render(":2", 1, (0, 0, 0))
        self.frameSurface.blit(text, (230, 500))
        self.frameSurface.blit(text2, (230, 590))
    
    def APutInBasket(self):
        #put in basket
        for idx in range(0, len(self.AuserPos)):
            userX, userY = self.AuserPos[idx]
            if self.isInBasket(userX, userY):
                if idx == 0 and self.AleftGrabbingFruit != None:
                    if self.AleftGrabbingFruit == self.strawberry:
                        self.Ascore += 2
                        self.AisLeftPicking = False
                        self.AleftGrabbingFruit = None
                    elif self.AleftGrabbingFruit == self.pineapple:
                        self.AisLeftPicking = False
                        self.Ascore += 5
                        self.AleftGrabbingFruit = None
                if idx == 1 and self.ArightGrabbingFruit != None:
                    if self.ArightGrabbingFruit == self.strawberry:
                        self.AisRightPicking = False
                        self.Ascore += 2
                        self.ArightGrabbingFruit = None
                    elif self.ArightGrabbingFruit == self.pineapple:
                        self.AisRightPicking = False
                        self.Ascore += 5
                        self.ArightGrabbingFruit = None
    def BPutInBasket(self):
        #put in basket
        for idx in range(0, len(self.BuserPos)):
            userX, userY = self.BuserPos[idx]
            if self.isInBasket(userX, userY):
                if idx == 0 and self.BleftGrabbingFruit != None:
                    if self.BleftGrabbingFruit == self.strawberry:
                        self.Bscore += 2
                        self.BisLeftPicking = False
                        self.BleftGrabbingFruit = None
                    elif self.BleftGrabbingFruit == self.pineapple:
                        self.BisLeftPicking = False
                        self.Bscore += 5
                        self.BleftGrabbingFruit = None
                if idx == 1 and self.BrightGrabbingFruit != None:
                    if self.BrightGrabbingFruit == self.strawberry:
                        self.BisRightPicking = False
                        self.Bscore += 2
                        self.BrightGrabbingFruit = None
                    elif self.BrightGrabbingFruit == self.pineapple:
                        self.BisRightPicking = False
                        self.Bscore += 5
                        self.BrightGrabbingFruit = None
 
        
    def run(self):
        pygame.font.init()

        while not self.done:
            self.new.fill((255, 120, 234))

            thisTime = pygame.time.get_ticks() / 1000

            self.timeRemain = int(60 - thisTime)
            if thisTime > 60:
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
                #CITATION: the syntax of keeping track of multiple players is 
                #originally from the following website. 
                #It is revised to fit in my program:
                #https://github.com/jtaceron/Kinect-Fruit-
                #Ninja/blob/master/Fruit_Ninja.py
                if self.bodies is not None: 
                    firstTime = True
                    for i in range(0, self.kinect.max_body_count):
                        body = self.bodies.bodies[i]
                        
                        
                        
                        
                        if not body.is_tracked: 
                            continue 
                            
                        if firstTime == True:
                            firstTime = False
                            self.player[0] = 1
                            #CITATION: the syntax of next line and the idea of 
                            #using body.tracking_id is from
                            #https://gitlab.eecs.umich.edu/EECS498-Brad4/Per
                            #ssist/blob/f0105d7839d737f9b123331ceb8abdf4703
                            #ccd2f/PersonDetector.py
                            self.firstID = body.tracking_id

                            joints = body.joints 
                            
        
                            basicPosY = self.screenHeight / 2
                            basicPosX = self.screenWidth / 2
                            ratio = 1600
        
                            if joints[PyKinectV2.JointType_HandRight].\
                            TrackingState != PyKinectV2.\
                            TrackingState_NotTracked:
                                self.AcurRightHandHeight = basicPosY +\
                                    joints[PyKinectV2.JointType_HandRight].\
                                    Position.y * ratio
                                self.AcurRightHandX = basicPosX +\
                                    joints[PyKinectV2.JointType_HandRight].\
                                    Position.x * ratio
                            
                            if joints[PyKinectV2.JointType_HandLeft].\
                            TrackingState != PyKinectV2.\
                            TrackingState_NotTracked:
                                self.AcurLeftHandHeight = basicPosY \
                                + joints[PyKinectV2.JointType_HandLeft].\
                                Position.y * ratio
                                self.AcurLeftHandX = basicPosX + joints\
                                [PyKinectV2.JointType_HandLeft].\
                                Position.x * ratio
                            #CITATION:syntax of the next eight lines is from:
                            #https://github.com/Te12944265
                            #-AMAHA/ESCAPE/blob/master/StartGame.py
                            if body.hand_left_state == 3:
                                self.AleftGrabbing = True
                            else:
                                self.AleftGrabbing = False
                            if body.hand_right_state == 3:
                                self.ArightGrabbing = True
                            else:
                                self.ArightGrabbing = False

                             
                            self.AuserPos = [[self.AcurLeftHandX, \
                            self.screenHeight - self.AcurLeftHandHeight],\
                            [self.AcurRightHandX, \
                            self.screenHeight - self.AcurRightHandHeight]]
                            
                        if firstTime == False:

                            self.player[1] = 1

                            joints = body.joints 
                            thisID = body.tracking_id
                            print(thisID)
                            # save the hand positions
                            basicPosY = self.screenHeight / 2
                            basicPosX = self.screenWidth / 2
                            ratio = 1600
        
                            if joints[PyKinectV2.JointType_HandRight].\
                            TrackingState != PyKinectV2.\
                            TrackingState_NotTracked:
                                self.BcurRightHandHeight = basicPosY +\
                                    joints[PyKinectV2.JointType_HandRight].\
                                    Position.y * ratio
                                self.BcurRightHandX = basicPosX +\
                                    joints[PyKinectV2.JointType_HandRight].\
                                    Position.x * ratio
                            
                            if joints[PyKinectV2.JointType_HandLeft].\
                            TrackingState != PyKinectV2.\
                            TrackingState_NotTracked:
                                self.BcurLeftHandHeight = basicPosY \
                                + joints[PyKinectV2.JointType_HandLeft].\
                                Position.y * ratio
                                self.BcurLeftHandX = basicPosX + joints\
                                [PyKinectV2.JointType_HandLeft].\
                                Position.x * ratio
                            #CITATION: the syntax of the next eight lines is from:
                            #https://github.com/Te12944265
                            #-AMAHA/ESCAPE/blob/master/StartGame.py
                            if body.hand_left_state == 3:
                                self.BleftGrabbing = True
                            else:
                                self.BleftGrabbing = False
                            if body.hand_right_state == 3:
                                self.BrightGrabbing = True
                            else:
                                self.BrightGrabbing = False

                            
                            self.BuserPos = [[self.BcurLeftHandX, \
                            self.screenHeight \
                            - self.BcurLeftHandHeight],[self.BcurRightHandX, \
                            self.screenHeight - self.BcurRightHandHeight]] 
                            
                            if thisID < self.firstID:
                                temp = self.AuserPos
                                self.AuserPos = self.BuserPos
                                self.BuserPos = temp
                                
                                temp = self.AleftGrabbing
                                self.AleftGrabbing = self.BleftGrabbing
                                self.BleftGrabbing = temp
                                
                                temp = self.ArightGrabbing
                                self.ArightGrabbing = self.BrightGrabbing
                                self.BrightGrabbing = temp

            
            self.drawDot()
            self.drawBasket()
            
            #generate new targets every five seconds
            allowError = 0.02
            if thisTime % 2 < allowError:
                self.randomGenerate()
                
            self.basketX += 2
            if self.basketX > 1000:
                self.basketX = 650

                
            #if both targets are touched, then generate new targets.
            twoEmpty = [[-20, -20, None], [-20, -20, None]]
            if self.robPos == twoEmpty:
                self.randomGenerate()
                
            
            self.drawRob()
            self.APutInBasket()
            self.BPutInBasket()
            self.isAPicking()
            self.isBPicking()
            self.drawScoreBack()
            self.drawInfo()

            
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
        
def runDouble():
    game = GameRuntime()
    #game.startPage()
    #CITATION: the syntax of the next two lines is from:
    #https://stackoverflow.com/questions/7746263/
    #how-can-i-play-an-mp3-with-pygame
    pygame.mixer.music.load("BGM.MP3")
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play()
    game.run()
