import pygame
import numpy as np
import sys
import time
import copy
import random


SNAKE_BODY = 1
FOOD = 2
EMPTY = 0


class SnakeGraphics():
    BLACK = pygame.Color(0, 0, 0)
    WHITE = pygame.Color(255, 255, 255)
    RED = pygame.Color(255, 0, 0)
    ORANGE = pygame.Color(200, 0, 0)
    GREEN = pygame.Color(0, 255, 0)
    BLUE = pygame.Color(0, 0, 255)


    def __init__(self,window_size=(800,600),grid_size=(40,30),difficulty=10):
        self.rect_size = (window_size[0]/grid_size[0],window_size[1]/grid_size[1]) 
        pygame.init()
        self.FONT = pygame.font.SysFont('times new roman', 90)
        pygame.display.set_caption('Snake Game')
        self.lastKey = pygame.K_UP
        self.window_size = window_size
        self.game_window = pygame.display.set_mode(window_size)
        self.fps_controller = pygame.time.Clock()
        self.game = SnakeGame(gridSize=grid_size)
        self.difficulty = difficulty
        self.draw()

    def updateNoMove(self):
        events = pygame.event.get()
    
    #Update relative to snake position
    def update2(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # Whenever a key is pressed down
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == ord('w'):
                    self.lastKey = pygame.K_UP
                if event.key == pygame.K_DOWN or event.key == ord('s'):
                    self.lastKey = pygame.K_DOWN
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    self.lastKey = pygame.K_LEFT
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    self.lastKey = pygame.K_RIGHT

        if self.lastKey == pygame.K_UP:
            self.game.moveFront__()
        
        elif self.lastKey == pygame.K_LEFT:
            self.game.moveLeft__()
        
        elif self.lastKey == pygame.K_RIGHT:
            self.game.moveRight__()
        else:
            self.game.moveFront__()
        
        self.lastKey = None

        return

    #General Update
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # Whenever a key is pressed down
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == ord('w'):
                    self.lastKey = pygame.K_UP
                if event.key == pygame.K_DOWN or event.key == ord('s'):
                    self.lastKey = pygame.K_DOWN
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    self.lastKey = pygame.K_LEFT
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    self.lastKey = pygame.K_RIGHT

        if self.lastKey == pygame.K_UP:
            self.game.moveUp()
            #self.game.moveFront__()

        if self.lastKey == pygame.K_DOWN:
            self.game.moveDown()
            #self.game.moveFront()
        
        if self.lastKey == pygame.K_LEFT:
            self.game.moveLeft()
            #self.game.moveLeft__()
        
        if self.lastKey == pygame.K_RIGHT:
            self.game.moveRight()
            #self.game.moveRight__()

        return

    def draw(self):
        self.startDraw()
        if not self.game.isGameOver():
            self.drawBody(self.game.snakeBodyPos)
            self.drawScore(self.game.score)
            self.drawFood(self.game.foodPos)
            self.drawHead(self.game.snakeHead)
            self.endDraw()
        else:
            self.drawEnd(self.game.score)
            self.endDraw()
            time.sleep(3)
            pygame.quit()
            sys.exit()
        #self.fps_controller.tick(self.difficulty)


    def drawBody(self,listPos):
        for pos in listPos:
            pygame.draw.rect(self.game_window, self.GREEN, pygame.Rect(pos[0]*self.rect_size[0], pos[1]*self.rect_size[1], self.rect_size[0], self.rect_size[1]))

    def drawHead(self,pos):
        pygame.draw.rect(self.game_window, self.ORANGE, pygame.Rect(pos[0]*self.rect_size[0], pos[1]*self.rect_size[1], self.rect_size[0], self.rect_size[1]))

    def drawFood(self,pos):
        pygame.draw.rect(self.game_window, self.RED, pygame.Rect(pos[0]*self.rect_size[0], pos[1]*self.rect_size[1], self.rect_size[0], self.rect_size[1]))

    def drawScore(self,score,choice = 1):
        if choice == 1:
            font = pygame.font.SysFont('times new roman', 30)
            score_surface = font.render('Score : ' + str(score), True, self.WHITE)
            score_rect = score_surface.get_rect()
            score_rect.midtop = (self.window_size[0]/8, 15)
        else:
            score_surface = self.FONT.render('Score : ' + str(score), True, self.WHITE)
            score_rect = score_surface.get_rect()
            score_rect.midtop = (self.window_size[0]/2, self.window_size[1]/1.25)
        self.game_window.blit(score_surface, score_rect)
    
    def drawEnd(self,score):
        game_over_surface = self.FONT.render('YOU DIED', True, self.RED)
        game_over_rect = game_over_surface.get_rect()
        game_over_rect.midtop = (self.window_size[0]/2, self.window_size[1]/4)
        self.game_window.fill(self.BLACK)
        self.game_window.blit(game_over_surface, game_over_rect)
        self.drawScore(score,choice=0)

    def startDraw(self):
        self.game_window.fill(self.BLACK)

    def endDraw(self):
        pygame.display.update()



class SnakeGame():

    #Update speed in msec
    def __init__(self,initalLength= 6, gridSize=(50,50)):
        self.score = 0
        self.gridSize = gridSize
        self.foodPos = (0,0)
        self.isOver = False
        self.snakeBodyPos= []
        self.snakeHead = (int(gridSize[0]/2),int(gridSize[1]/2))

        #Stores the free places. Consumes more memory but uses less CPU power when computing the next food location
        self.freeGridPlaces = set()
        for x in range(gridSize[0]):
            for y in range(gridSize[1]):
                self.freeGridPlaces.add((x,y))

        self.freeGridPlaces.remove(self.snakeHead)

        for i in range(1,initalLength):
            x,y = self.snakeHead
            y+= i 
            self.snakeBodyPos.append((x,y))
            self.freeGridPlaces.remove((x,y))
        
        self.generateNewFood()
        
    def generateNewFood(self):
        self.foodPos = random.choice(list(self.freeGridPlaces))

    def gameOver(self):
        self.isOver = True

    def isGameOver(self):
        return self.isOver

    def getScore(self):
        return self.score
    
    def getLength(self):
        return len(self.snakeBodyPos)+1

    def getFrontPos(self):
        x,y = self.snakeHead
        _dir = self.getDirection()
        x+=_dir[0]
        y+=_dir[1]
        return (x,y)

    def posIsGameOver(self,pos):
        if(pos not in self.freeGridPlaces):
            return True
        else:
            return False


    def getLeftPos(self):
        x,y = self.snakeHead
        _dir = self.getDirection()
        x+=_dir[1]
        y-=_dir[0]
        return (x,y)

    def getRightPos(self):
        x,y = self.snakeHead
        _dir = self.getDirection()
        x-=_dir[1]
        y+=_dir[0]
        return (x,y)

    def getDistanceToFood(self,food_Pos = None,pos=None):
        if pos == None:
            pos = self.snakeHead
        if food_Pos == None:
            food_Pos = self.foodPos
        return abs(pos[0] -food_Pos[0]) + abs(pos[1]-food_Pos[1])

    def update(self,nextHeadPlace):
        #Check if is trying to walking back
        #And continue in opposite direction
        #print(self.posIsGameOver(nextHeadPlace))
        return_value = True
        if(nextHeadPlace == self.snakeBodyPos[0]):
            x1,y1 = self.snakeBodyPos[0]
            x2,y2 = self.snakeBodyPos[1]

            nextHeadPlace = (self.snakeHead[0] + x1-x2,self.snakeHead[1] + y1-y2)
            return_value = False


        #Check if is a free place
        if(nextHeadPlace not in self.freeGridPlaces):
            self.gameOver()

        #Valid position 
        else:
            #Check if food has been eaten
            if nextHeadPlace == self.foodPos:
                self.generateNewFood()
                self.score += 1

            #If food has not been eaten, remove the tail
            else:
                oldPos = self.snakeBodyPos.pop()
                self.freeGridPlaces.add(oldPos)

            #Extend head            
            self.snakeBodyPos.insert(0,(self.snakeHead))
            self.snakeHead = nextHeadPlace
            self.freeGridPlaces.remove(nextHeadPlace)
        
        return return_value


    def getDirection(self):
        _dir = (self.snakeHead[0]-self.snakeBodyPos[0][0],self.snakeHead[1]-self.snakeBodyPos[0][1]) 
        return _dir


    #Movement related to snake position
    def moveFront__(self):
        return self.update(self.getFrontPos())

    def moveRight__(self):
        return self.update(self.getRightPos())

    def moveLeft__(self):
        return self.update(self.getLeftPos())
        


    #Movement related to grid
    def moveUp(self):
        x,y = self.snakeHead
        return self.update((x,y-1))

    def moveDown(self):
        x,y = self.snakeHead
        return self.update((x,y+1))

    def moveRight(self):
        x,y = self.snakeHead
        return self.update((x+1,y))

    def moveLeft(self):
        x,y = self.snakeHead
        return self.update((x-1,y))



if __name__ == '__main__':
    snake = SnakeGraphics()
    #
    while(1):
        #print("Update")
        snake.update()
        snake.draw()
        time.sleep(0.1)