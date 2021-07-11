#This is the pick fruit mode. In this mode, the player can earn points by
#picking fruits. The kinect keep track of the hands' position and whether 
#the hand is making a fist. If the player is making a fist, he can move a
#fruit, and put it into the basket. A strawberry worth two points while
#a pineapple worth five points.


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
        self.BG = pygame.image.load("pickFruitBG.png")
        self.BG = pygame.transform.scale(self.BG, (1920, 1080))
        self.headX, self.headY = -30, -30
        self.mask = mask
        if self.mask != None:
            self.mask = pygame.transform.scale(self.mask, (300, 300))
        
        #load some images
        strawberry = pygame.image.load("strawberry.png")
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
        
        
        #scale the image
        self.pineapple = pygame.transform.scale(self.pineapple,(70, 110))
        self.strawberry = pygame.transform.scale(self.strawberry, (80, 80))
        self.basket = pygame.transform.scale(self.basket, (500, 340))
        self.infoBoard = pygame.transform.scale(self.infoBoard, (350, 700))
        
        
        self.listOfFruits = [self.strawberry, self.pineapple]
        
        #set the initial value of basket, hand position, pre hand position
        self.basketX = 750
        self.basketY = 620
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
        
        #keep track of what fruit each hand is grabbing
        self.rightGrabbingFruit = None
        self.leftGrabbingFruit = None
        self.isLeftPicking = False
        self.isRightPicking = False
        
        self.gameover = False
        self.paused = False
        self.robPos = [[]]
        self.score = 0
        
        #keep track of if each hand is grabbing
        self.leftGrabbing = False
        self.rightGrabbing = False
        self.end = False
        self.firstTime = True
        self.timeRemain = 60
        
        #define some colors
        self.pink = (180, 120, 130)
        self.white = (255, 255, 255)
        self.blue = (97, 170, 195)
        self.pinkpink = (249, 140, 128)
        
        #define the size of target
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
        #this userPos stores the positions of user's left hand, 
        #right hand, and head.
        self.userPos = [[self.curLeftHandX, self.screenHeight - \
        self.curLeftHandHeight], [self.curRightHandX, self.screenHeight \
        - self.curRightHandHeight]]
        
    def drawMask(self):
        if self.mask != None:
            self.frameSurface.blit(self.mask,(960 + 1400 * self.headX - 80,  540 - 1300 * self.headY - 170))
        
            
    #draw the basket
    def drawBasket(self):
        self.frameSurface.blit(self.basket, (self.basketX, self.basketY))
    #detect whether a position is in the basket
    def isInBasket(self, x, y):
        if x > self.basketX and x < self.basketX + 400 and y > self.basketY\
        and y < self.basketY + 300:
            return True
        return False
    

    def drawColorFrame(self, frame, targetSurface):
        targetSurface.lock()
        address = self.kinect.surface_as_array(targetSurface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        targetSurface.unlock()
    
    #this function draws two blue dots at the user's hands
    def drawDot(self):

        for idx in range(0, len(self.userPos)):
            if idx == 0:
                if self.isLeftPicking:
                    self.frameSurface.blit(self.leftGrabbingFruit\
                    ,(int(self.userPos[idx][0]), int(self.userPos[idx][1])))
                else:
                    pygame.draw.circle(self.frameSurface, 
                        self.blue, 
                        (int(self.userPos[idx][0]), 
                        int(self.userPos[idx][1])), self.robRadLarge)
            
            if idx == 1:
                if self.isRightPicking:
                    self.frameSurface.blit(self.rightGrabbingFruit\
                    ,(int(self.userPos[idx][0]), int(self.userPos[idx][1])))
                else:
                    pygame.draw.circle(self.frameSurface, 
                        self.blue, 
                        (int(self.userPos[idx][0]), 
                        int(self.userPos[idx][1])), self.robRadLarge)


    #this function randomly generate new targets(it also makes sure that the 
    #new position should have some distance from the user's hand)
    def isInBox(self, x, y):
        if x < 400 and y < 200 :
            return False
        return True
    
    #randomly generate fruit position
    def randomGenerate(self):
        margin = 20
        height = 200

        ranPosX = random.randint(margin * 10, self.screenWidth - margin)
        ranPosY = random.randint(margin, 200)
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
                           
    
    #a helper function, it detects whether two position intersects
    def isCollide(self, x1, y1, x2, y2):
        allowError = 70
        dis = self.calculateDis(x1, x2, y1, y2)
        if dis < allowError:
            return True
        return False
        
    #draw the information: current score and time remaining
    def drawInfo(self, thisTime):
        pygame.font.init()
        font1 = pygame.font.SysFont('mono', 39, bold=True)
        text = font1.render("Score:" + str(self.score), 1, (0, 0, 0))
        text2 = font1.render("Time:" + str(round(60 - thisTime, 1)), \
        1, (0, 0, 0))
        self.frameSurface.blit(text, (130,370))
        self.frameSurface.blit(text2, (130,420))
    
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
        font1 = pygame.font.SysFont('mono', 39, bold=True)
        text = font1.render(":5", 1, (0, 0, 0))
        text2 = font1.render(":2", 1, (0, 0, 0))
        self.frameSurface.blit(text, (230, 500))
        self.frameSurface.blit(text2, (230, 590))
        
        
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
            font1 = pygame.font.SysFont('mono', fontSize, bold=True)
            text = font1.render("Paused" , 1, \
            (fontColR, fontColG, fontColB))
            self.frameSurface.blit(text, (textMargin, textMargin))
            
            text2MarX, text2MarY = 650, 550
            fontSize = 130
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
            font1 = pygame.font.SysFont('mono', fontSize, bold=True)
            text = font1.render("Dance  With  Robot!" , 1, \
            (fontColR, fontColG, fontColB))
            self.frameSurface.blit(text, (textMargin, textMargin))
            
            text2MarX, text2MarY = 650, 550
            fontSize = 130
            font1 = pygame.font.SysFont('mono', fontSize, bold=True)
            text2 = font1.render("Start" , 1, \
            (fontColR, fontColG, fontColB))
            self.frameSurface.blit(text2, (text2MarX, text2MarY))
            
            mouse = pygame.mouse.get_pos()
            xMin = 195
            xMax = 660
            yMin = 246
            yMax = 349
            if xMin < mouse[0] < xMax and yMin < mouse[1] < yMax:
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

        while not self.done:
            self.new.fill((255, 120, 234))

            thisTime = pygame.time.get_ticks() / 1000

            self.timeRemain = int(60 - thisTime)
            if thisTime > 60:
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
                        #CITATION: the syntax of the next eight lines is from:
                        #https://github.com/Te12944265
                        #-AMAHA/ESCAPE/blob/master/StartGame.py
                        if body.hand_left_state == 3:
                            self.leftGrabbing = True
                        else:
                            self.leftGrabbing = False
                        if body.hand_right_state == 3:
                            self.rightGrabbing = True
                        else:
                            self.rightGrabbing = False

                        
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
            
            for idx in range(0, len(self.userPos)):
                userX, userY = self.userPos[idx]
                if self.isInBasket(userX, userY):
                    if idx == 0 and self.leftGrabbingFruit != None:
                        if self.leftGrabbingFruit == self.strawberry:
                            self.score += 2
                            self.isLeftPicking = False
                            self.leftGrabbingFruit = None
                        elif self.leftGrabbingFruit == self.pineapple:
                            self.isLeftPicking = False
                            self.score += 5
                            self.leftGrabbingFruit = None
                    if idx == 1 and self.rightGrabbingFruit != None:
                        if self.rightGrabbingFruit == self.strawberry:
                            self.isRightPicking = False
                            self.score += 2
                            self.rightGrabbingFruit = None
                        elif self.rightGrabbingFruit == self.pineapple:
                            self.isRightPicking = False
                            self.score += 5
                            self.rightGrabbingFruit = None
                        

            #detect whether the user touch the target
            #if so, move the target to [-20, -20], where the user cannot see
            for idxOut in range(0, len(self.userPos)):
                userX, userY = self.userPos[idxOut]
                userY = self.screenHeight - userY
                
                if self.robPos != []:
                    
                    for idx in range(0, len(self.robPos)):
                        if self.robPos[idx] != []:
                            fruitX, fruitY, fruit = self.robPos[idx]
                            res = self.isCollide(userX, fruitX,\
                            self.screenHeight - userY, fruitY)
                            
                            if res == True:
                                if idxOut == 0:
                                    ifGrabbing = self.leftGrabbing
                                    hand = "left"
                                else:
                                    ifGrabbing = self.rightGrabbing
                                    hand = "right"
                                
                                
                                if ifGrabbing == False:
                                    continue
                                else:
                                    if hand == "left":
                                        if self.leftGrabbingFruit == None:
                                            self.isLeftPicking = True
                                            self.leftGrabbingFruit = fruit
                                            self.robPos[idx] = [-20, -20, None]                 
                                    else:
                                        if self.rightGrabbingFruit == None:
                                            self.isRightPicking = True
                                            self.rightGrabbingFruit = fruit
                                            self.robPos[idx] = [-20, -20, None]                       

            #user helper functions to draw background, info
            self.drawInfoBackGround()
            self.drawInfo(thisTime)
            self.drawSample()

            
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
#the program will not run until the runPickFruit function is called in the 
#main file
def runPickFruit(mask):
    game = GameRuntime(mask);
    game.startPage()
    #CITATION: the syntax of the next two lines is from:
    #https://stackoverflow.com/questions/7746263/
    #how-can-i-play-an-mp3-with-pygame
    pygame.mixer.music.load("BGM.MP3")
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play()
    game.run()
