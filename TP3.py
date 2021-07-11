#This file is a start page. After running this file, it draws a start page, and
#the player can click to choose masks and modes.

import basic
import pathTracking
import pickFruit
import pygame
import sudoku
import doubleGame

#CITATION: the framework is written by myself, but the framework of the 
#startPage function is revised from the run function in the following link
#https://github.com/fletcher-marsh/kinect_python
class mainPage(object):
    def __init__(self):
        pygame.init()
        self.mask = None
        #CITATION: the bgm is from:
        #https://www.bensound.com/royalty-free-music/corporate-pop
        #CITATION: the syntax of the next two lines is from:
        #https://stackoverflow.com/questions/7746263/
        #how-can-i-play-an-mp3-with-pygame
        pygame.mixer.music.load("BGM.MP3")
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play()
        #CITATION: the following background image is from :
        #https://depositphotos.com/104129026/stock-photo-watercolor
        #-fruits-background.html
        self.backGroundImg = pygame.image.load("mainPage.jpg")
        #CITATION: the following image is generated from:
        #http://www.akuziti.com/
        self.topicImg = pygame.image.load("Dancing Game.png")
        self.topicImg = pygame.transform.scale(self.topicImg, (1000, 400))
        
        #CITATION: the next line is from:
        #https://github.com/fletcher-marsh/kinect_python
        self.frameSurface =pygame.Surface((1920, 1080), 0, 32)
        
        #set the position of three buttons
        self.mode11x, self.mode11y = 560, 600
        self.mode12x, self.mode12y = 960, 600
        self.mode2x, self.mode2y = 1360, 600
        self.boxWid, self.boxHi = 200, 200      
        
        self.doubleX, self.doubleY = 560, 400
        self.sudokuX, self.sudokuY = 1210, 400
        self.bigBoxWid, self.bigBoxHi = 150, 350
        
        #set the font and text 
        self.font = pygame.font.SysFont('mono', 39, bold=True)
        self.text1 = self.font.render( "Basic", 1, (0,0,0))
        self.text2 = self.font.render("Monster", 1, (0,0,0))
        self.text3 = self.font.render("Fruit",1,(0,0,0))
        self.text4 = self.font.render("Double",1,(0,0,0))
        self.text5 = self.font.render("Sudoku",1,(0,0,0))
        
        self.screenWidth = 960
        self.screenHeight = 540 
        self.backGroundImg = pygame.transform.scale(self.backGroundImg, \
        (1920, 1080))
        
        #CITATION: the next line is from:
        #https://github.com/fletcher-marsh/kinect_python
        self.screen = pygame.display.set_mode((960, 540), \
        pygame.HWSURFACE|pygame.DOUBLEBUF, 32)
        
        #Define some colors by RGB
        self.yellow = (242, 200, 100)
        self.pink = (252, 161, 171)
        self.green = (205, 226, 149)
        self.purple = (202, 193, 232)
        
        #import mask
        #CITATION:all the images are from website
        #they are respectively from:
        #https://cdn1.iconfinder.com/data/icons/people
        #-avatars-23/24/people_avatar_head_comic_batman_bat_man-512.png

        #https://i.etsystatic.com/6608809/r/il/e826d3/1124748426/il_794xN.
        #1124748426_rpa3.jpg

        #https://images-na.ssl-images-amazon.com/images/I/41uddGjOiML
        #._SY355_.jpg

        #https://i.ebayimg.com/images/g/dP8AAOSwQjNW8gD~/s-l300.jpg

        #https://images-na.ssl-images-amazon.com/images/I/71zIf6eYL1L.
        #_SY355_.jpg

        #https://i.pinimg.com/originals/7f/f7/d9/7ff7d93eaa14a904e3e35
        #013fb7550fd.png

        self.bat = pygame.image.load("[Head]Batman.png")
        self.bat = pygame.transform.smoothscale(self.bat, (100, 100))
        self.cap = pygame.image.load("[Head]Captain.png") 
        self.cap = pygame.transform.smoothscale(self.cap, (100, 100))
        self.spider = pygame.image.load("[Head]Spiderman.png")  
        self.spider = pygame.transform.smoothscale(self.spider, (100, 100))
        self.mickey = pygame.image.load("[Head]Mickey.png")
        self.mickey = pygame.transform.smoothscale(self.mickey, (100, 100))
        self.minnie = pygame.image.load("[Head]Minnie.png")
        self.minnie = pygame.transform.smoothscale(self.minnie, (100, 100))
        self.pikachu = pygame.image.load("[Head]Pikachu.png")
        self.pikachu = pygame.transform.smoothscale(self.pikachu, (100, 100))
        self.mask = (self.bat, self.cap, self.spider,self.mickey, \
        self.minnie, self.pikachu)
        self.thisMask = None
        
    
    
    #draw the masks
    def drawMask(self):
        for idx in range(0, 6):
            x = 550 + idx * 160
            y = 850
            self.frameSurface.blit(self.mask[idx], (x, y))
        
    #the following three functions detect whether the mouse 
    #is within each button    
    def ifInBox1(self, x, y):
        if x > self.mode11x and x < self.mode11x + self.boxWid and \
        y > self.mode11y and y < self.mode11y + self.boxHi:
            return True
        return False
        
    def ifInBox2(self, x, y):
        if x > self.mode12x and x < self.mode12x + self.boxWid and \
        y > self.mode12y and y < self.mode12y + self.boxHi:
            return True
        return False
    
    def ifInBox3(self, x, y):
        if x > self.mode2x and x < self.mode2x + self.boxWid and \
        y > self.mode2y and y < self.mode2y + self.boxHi:
            return True
        return False
    
    def ifInBox4(self,x,y):
        if x > self.doubleX and x < self.doubleX + self.bigBoxHi and \
        y > self.doubleY and y < self.doubleY + self.bigBoxWid:
            print("4")
            return True
        return False
        
    def ifInBox5(self,x,y):
        if x > self.sudokuX and x < self.sudokuX + self.bigBoxHi and \
        y > self.sudokuY and y < self.sudokuY + self.bigBoxWid:
            print("5")
            return True
        return False
    
    def startMusic(self):
        pygame.mixer.music.pause()
        #CITATION: the bgm is revised from:
        #https://www.soundsnap.com/tags/horse_race
        pygame.mixer.music.load("startGame.MP3")
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play()

    #This function is similar to a run function, it draws a background
    #and have buttons on it. Users can choose the mode they want by touching
    #the button.
    def startPage(self):
        while True:
            pygame.font.init()
            
            #CITATION: the next four lines are from 
            #https://pythonprogramming.net/pygame-button-function-events/
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    
                    if 850 < mouse[1] * 2 < 950:
                        if 550 < mouse[0] * 2 < 650:
                            self.thisMask = self.bat
                        if 710 < mouse[0] * 2 < 810:
                            self.thisMask = self.cap                       
                        if 870 < mouse[0] * 2 < 970:
                            self.thisMask =  self.spider                 
                        if 1030 < mouse[0] * 2 < 1130:
                            self.thisMask = self.mickey
                        if 1190 < mouse[0] * 2 < 1290:
                            self.thisMask = self.minnie
                        if 1350 < mouse[0] * 2 < 1450:
                            self.thisMask = self.pikachu  
                            
                    resBasic = self.ifInBox1(mouse[0] * 2, mouse[1] * 2)
                    if resBasic == True:
                        self.startMusic()
                        basic.runBasic(self.thisMask)

                   
                    resMonster = self.ifInBox2(mouse[0] * 2, mouse[1] * 2)
                    if resMonster == True:
                        self.startMusic()
                        pathTracking.runPathTracking(self.thisMask)

                    resFruit = self.ifInBox3(mouse[0] * 2, mouse[1] * 2)
                    if resFruit == True:
                        self.startMusic()
                        pickFruit.runPickFruit(self.thisMask)

                    resDouble = self.ifInBox4(mouse[0] * 2, mouse[1] * 2)
                    if resDouble == True:
                        self.startMusic()
                        doubleGame.runDouble()
                        
                    resSudoku = self.ifInBox5(mouse[0] * 2, mouse[1] * 2)
                    if resSudoku == True:
                        self.startMusic()
                        sudoku.runSudoku(self.thisMask)
                                    
            pygame.display.flip()
            self.screen.blit(self.frameSurface, (0, 0))
            
            #draw the background
            self.frameSurface.blit(self.backGroundImg, (0,0))
            self.frameSurface.blit(self.topicImg, (500, 180))
            self.drawMask()
            
            textMargin = 22
            textMarginY = 80
            
            #draw the three buttons and draw text on them
            pygame.draw.rect(self.frameSurface, self.pink, \
        (self.mode11x, self.mode11y, self.boxHi, self.boxWid))
            self.frameSurface.blit(self.text1, (self.mode11x + textMargin,\
             self.mode11y + textMarginY))
            
            pygame.draw.rect(self.frameSurface, self.yellow, \
        (self.mode12x, self.mode12y,  self.boxHi, self.boxWid))
            self.frameSurface.blit(self.text2, (self.mode12x + textMargin,\
             self.mode12y+ textMarginY))
        
            pygame.draw.rect(self.frameSurface, self.green, \
        (self.mode2x, self.mode2y,  self.boxHi, self.boxWid))
            self.frameSurface.blit(self.text3, (self.mode2x + textMargin,\
             self.mode2y+ textMarginY))
            
            pygame.draw.rect(self.frameSurface, self.purple, \
        (self.doubleX, self.doubleY,  self.bigBoxHi, self.bigBoxWid))
            self.frameSurface.blit(self.text4, (self.doubleX + textMargin * 5, \
            self.doubleY+ textMarginY - 20))        
            
            pygame.draw.rect(self.frameSurface, self.purple, \
        (self.sudokuX, self.sudokuY,  self.bigBoxHi, self.bigBoxWid))
            self.frameSurface.blit(self.text5, (self.sudokuX + textMargin * 5,\
             self.sudokuY+ textMarginY - 20))                        
            
            
            #get mouse position and find out whether the mouse is on the button
            #if it is, then direct the user to that game mode
            mouse = pygame.mouse.get_pos()


            hToW = float(self.frameSurface.get_height()) / self.\
            frameSurface.get_width()
            targetHeight = int(hToW * self.screenWidth)
            surfaceToDraw = pygame.transform.scale(self.frameSurface\
            , (self.screenWidth, targetHeight));
            self.frameSurface.blit(surfaceToDraw, (0,0))
            surfaceToDraw = None # memory save
            pygame.display.update()

#start the game
game = mainPage()
game.startPage()
