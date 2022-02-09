from common_libs import *
import pygame as pyg
from time import sleep
from threading import Timer

threadManager = coroutines_threads.threadManager()
Xy = Xy.Xy
pygameManager = pygame_interface.pygameManager
gameManager = game_manager.gameManager
settingsManager = settings_manager.settingsManager()

yellow = (255,255,0)
cyan = (0,255,255)
magenta = (255,0,255)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
black = (0,0,0)
white = (255,255,255)
grey = (230,230,230)

RIGHTMOUSEBUTTON = 2
MIDDLEMOUSEBUTTON = 1
LEFTMOUSEBUTTON = 0

class mainSceneManager(base_classes.baseManager):

    def onInit(self):
        gameManager.Current.registerObj(self)
        gridSceneManager()
        menuSceneManager()

    def onEarlyUpdate(self):
        gameManager.Current.scenes["Main"].fill(yellow)
        gameManager.Current.scenes["Main"].blit(gameManager.Current.scenes["Grid"],Xy(0,50))
        gameManager.Current.scenes["Main"].blit(gameManager.Current.scenes["Menu"],Xy(0))

    def onDestroy(self):
        gameManager.Current.unRegisterObj(self)   

class menuSceneManager(menu_objs.menuManager):
    
    Scene = "Menu"
    
    def buildGUI(self):
        toolManager()
        gameManager(None,None,None,{"Main":self.menuInputHandler})
        displayMenuObject("Place:",Xy(25,10))
        callBackMenuObject("Start",Xy(125,10),toolManager.Current.toggleTool,placeStartTool)
        callBackMenuObject("End",Xy(220,10),toolManager.Current.toggleTool,placeEndTool)
        callBackMenuObject("Wall",Xy(300,10),toolManager.Current.toggleTool,placeWallTool)
        callBackMenuObject("Clear",Xy(400,10),toolManager.Current.toggleTool,removeTool)
        callBackMenuObject("Go",Xy(500,10),gridManager.Current.go)

class displayMenuObject(menu_objs.displayMenuObject):

    Manager = menuSceneManager

class callBackMenuObject(menu_objs.callBackMenuObject):

    Manager = menuSceneManager

    def onClick(self):
        sleep(0.2)
        self.call_back(*self.args)

class gridSceneManager(base_classes.baseManager):
    
    def onInit(self):
        gameManager.Current.registerObj(self)
        gridManager()
        self.font = pygameManager.Current.font
        self.error = False
        self.text = "None"
        self.surface = self.font.render(self.text,False,blue)

    def displayError(self,level,text):
        if self.error:
            return
        self.error = True
        self.text = text
        self.surface = self.font.render(self.text,False,blue)
        Timer(1.75,self.closeError).start()

    def closeError(self):
        self.error = False

    def onEarlyUpdate(self):
        gameManager.Current.scenes["Grid"].fill(green)

    def onLateUpdate(self):
        if self.error:
            gameManager.Current.scenes["Grid"].blit(self.surface,Xy(50,200))
    
    def onDestroy(self):
        gameManager.Current.unRegisterObj(self)

#-----------------------------------------------------------------------------------------------
#       grid & pathfinding
#-----------------------------------------------------------------------------------------------

class gridManager(base_classes.baseManager):

    def onInit(self):
        gameManager.Current.registerObj(self)
        self.grid = {}
        self.placed = []
        self.buildGrid()

    def buildGrid(self):
        i = 0
        for y in range(0,11):
            for x in range(0,12):
                self.grid[Xy(x,y)] = gridSquare(Xy(x,y)*50,grey if i%2==0 else white)
                i+=1
            i+=1
            
    def go(self):
        if "Start" in self.placed and "End" in self.placed and (not gridSceneManager.Current.error):
            self.start = Xy(-1)
            self.end = Xy(-1)
            for key in self.grid.keys():
                if self.grid[key].type == "Start":
                    self.start = key
                elif self.grid[key].type == "End":
                    self.end = key
                elif self.grid[key].type == "Path":
                    self.grid[key].type == None
                    self.grid[key].reset()
                    if "Path" in self.placed:
                        self.placed.pop(self.placed.index("Path"))
                self.grid[key].shortestPath = 9999
                self.grid[key].shortestPathRoute = []
            self.distances = {self.start:0}
            self.unVisitedDistances = {self.start:0}
            self.position = Xy(self.start)
            self.visited = []
        #   for x in range(0,10):
          #      print(" ")
         #   print(self.start,self.end)
            while True:
     #           print(self.position,self.distances)
                for vector in [Xy(0,1),Xy(0,-1),Xy(1,0),Xy(-1,0)]:
                    magnitude = 1
                    if not ((vector + self.position) <= (Xy(12,11)-Xy(1)) and (vector + self.position) >= Xy(0)):
                        continue
                    elif self.grid[Xy(vector+self.position)].type == "Wall" or Xy(vector+self.position) in self.visited:
                        continue
                    else:
                        if Xy(vector+self.position) not in self.distances:
                            self.distances.update({Xy(vector+self.position):self.distances[self.position]+magnitude})
                        else:
                            if self.distances[Xy(vector+self.position)] > self.distances[self.position]+magnitude:
                                self.distances[Xy(vector+self.position)] = self.distances[self.position]+magnitude

                        if Xy(vector+self.position) not in self.visited:
                            self.unVisitedDistances[Xy(vector+self.position)] = self.distances[self.position]+magnitude
                        
                        if self.grid[Xy(vector+self.position)].shortestPath > self.distances[self.position]+magnitude:
                            self.grid[Xy(vector+self.position)].shortestPath = self.distances[self.position]+magnitude
                            self.grid[Xy(vector+self.position)].shortestPathRoute = self.grid[self.position].shortestPathRoute.copy()
                            self.grid[Xy(vector+self.position)].shortestPathRoute.append(self.position+vector)

                #this bit does diagonals
                '''
                for vector in [Xy(1,1),Xy(1,-1),Xy(1,-1),Xy(-1,-1)]:
                    magnitude = 2.5
                    if not ((vector + self.position) <= (Xy(12,11)-Xy(1)) and (vector + self.position) >= Xy(0)):
                        continue
                    elif self.grid[Xy(vector+self.position)].type == "Wall" or Xy(vector+self.position) in self.visited:
                        continue
                    else:
                        if Xy(vector+self.position) not in self.distances:
                            self.distances.update({Xy(vector+self.position):self.distances[self.position]+magnitude})
                        else:
                            if self.distances[Xy(vector+self.position)] > self.distances[self.position]+magnitude:
                                self.distances[Xy(vector+self.position)] = self.distances[self.position]+magnitude

                        if Xy(vector+self.position) not in self.visited:
                            self.unVisitedDistances[Xy(vector+self.position)] = self.distances[self.position]+magnitude
                        
                        if self.grid[Xy(vector+self.position)].shortestPath > self.distances[self.position]+magnitude:
                            self.grid[Xy(vector+self.position)].shortestPath = self.distances[self.position]+magnitude
                            self.grid[Xy(vector+self.position)].shortestPathRoute = self.grid[self.position].shortestPathRoute.copy()
                            self.grid[Xy(vector+self.position)].shortestPathRoute.append(self.position+vector)
                '''  
               
                self.visited.append(self.position)
                self.unVisitedDistances.pop(self.position)
                minimumDistance = 9999
                for xy in self.unVisitedDistances:
                    if self.unVisitedDistances[xy] < minimumDistance:
                        self.position = xy
                        minimumDistance = self.unVisitedDistances[xy]
                if self.end in self.distances.keys():
                    if self.distances[self.position] >= self.distances[self.end]:
                        gridSceneManager.Current.displayError(2,"shortest distance: "+str(self.distances[self.end]))
                        #print(self.grid[self.end].shortestPathRoute)
                        for xy in self.grid[self.end].shortestPathRoute:
                            if self.grid[xy].type in ["Wall","Start","End"]:
                                continue
                            else:
                                self.grid[xy].type = "Path"
                                self.placed.append("Path")
                                surface = pyg.Surface(Xy(40))
                                surface.fill(yellow)
                                self.grid[xy].surface.blit(surface,Xy(5))                               
                        break
                if self.position in self.visited:
                    gridSceneManager.Current.displayError(2,"No Path")
                    break
            
            #print(self.position,self.distances)    
                
        else:
            gridSceneManager.Current.displayError(2,"Missing start and end points")
        
    def onUpdate(self):
        pass

    def onDestroy(self):
        gameManager.Current.unRegisterObj(self)

class gridSquare(base_classes.baseObject):

    Manager = gridManager

    def onInit(self,pos,color):
        self.surface = pyg.Surface(Xy(50))
        self.surface.fill(color)
        self.pos = pos
        self.type = None
        self.originalSurface = self.surface.copy()
        self.shortestPath = 9999
        self.shortestPathRoute = list()

    def reset(self):
        self.surface = self.originalSurface.copy()
        if self.type != None and self.type in gridManager.Current.placed:
            gridManager.Current.placed.pop(gridManager.Current.placed.index(self.type))
        self.type = None

    def onUpdate(self):
        gameManager.Current.scenes["Grid"].blit(self.surface,self.pos)

#-----------------------------------------------------------------------------------------------
#       tool managers
#-----------------------------------------------------------------------------------------------

class toolManager(base_classes.baseManager):

    def onInit(self):
        gameManager.Current.registerObj(self)
        self.tools = {}

    def toggleTool(self,tool):
        if str(tool.__name__) in self.tools.keys():
            self.tools[str(tool.__name__)].exitOnlySelf()
            self.tools.pop(str(tool.__name__))
        else:
            for key in list(self.tools.keys()):
                self.tools[key].exitOnlySelf()
                self.tools.pop(key)
            newTool = tool()
            self.tools.update({type(newTool).__name__:newTool})

    def closeTool(self,tool):
        if str(tool.__name__) in self.tools.keys():
            self.tools[str(tool.__name__)].exitOnlySelf()
            self.tools.pop(str(tool.__name__))

    def onDestroy(self):
        gameManager.Current.unRegisterObj(self)

class placeTool(base_classes.baseObject):

    Manager = toolManager
    Type = None

    def onInit(self):
        self.surface = pyg.Surface(Xy(25))
        gameManager(None,None,None,{"Main":self.inputHandler})
        self.buildSurface()

    def buildSurface(self):
        pass

    def inputHandler(self,events):
        for event in events:
            if event.type == pyg.MOUSEBUTTONDOWN:
                if event.button-1 == LEFTMOUSEBUTTON and ((Xy(pyg.mouse.get_pos())-pygameManager.Current.offset-Xy(0,50))//50).y>=0:
                    self.place()

    def place(self):
        pos = (Xy(pyg.mouse.get_pos())-pygameManager.Current.offset-Xy(0,50))//50
        gridManager.Current.grid[pos].reset()
        gridManager.Current.grid[pos].type = self.Type
        gridManager.Current.placed.append(self.Type)
        gridManager.Current.grid[pos].surface.blit(self.surface,Xy(12.5))
        toolManager.Current.toggleTool(type(self))

    def onLateUpdate(self):
        if self.Type in gridManager.Current.placed:
            toolManager.Current.closeTool(type(self))
        gameManager.Current.scenes["Grid"].blit(self.surface,Xy(pyg.mouse.get_pos())-Xy(0,50)-pygameManager.Current.offset-Xy(self.surface.get_size())//2)

    def onExit(self):
        gameManager.Current.removeInputHandler("Main",self.inputHandler)

class placeStartTool(placeTool):

    Type = "Start"

    def buildSurface(self):
        self.surface.fill(blue)

class placeEndTool(placeTool):

    Type = "End"

    def buildSurface(self):
        self.surface.fill(black)

class placeWallTool(placeTool):

    Type = "Wall"

    def buildSurface(self):
        self.surface.fill(magenta)

    def onLateUpdate(self):
        gameManager.Current.scenes["Grid"].blit(self.surface,Xy(pyg.mouse.get_pos())-Xy(0,50)-pygameManager.Current.offset-Xy(self.surface.get_size())//2)

    def place(self):
        pos = (Xy(pyg.mouse.get_pos())-pygameManager.Current.offset-Xy(0,50))//50
        gridManager.Current.grid[pos].reset()
        gridManager.Current.grid[pos].type = self.Type
        gridManager.Current.placed.append(self.Type)
        gridManager.Current.grid[pos].surface.blit(self.surface,Xy(12.5))
        
class removeTool(placeTool):

    Type = None

    def buildSurface(self):
        self.surface.fill(red)

    def onLateUpdate(self):
        gameManager.Current.scenes["Grid"].blit(self.surface,Xy(pyg.mouse.get_pos())-Xy(0,50)-pygameManager.Current.offset-Xy(self.surface.get_size())//2)

    def place(self):
        gridManager.Current.placed.append(None)
        pos = (Xy(pyg.mouse.get_pos())-pygameManager.Current.offset-Xy(0,50))//50
        gridManager.Current.grid[pos].reset()
        
##########################

def start():    
    gameManager(
        60,
        {"Main": pyg.Surface(Xy(600,600)),"Grid":pyg.Surface(Xy(600,550)),"Menu":pyg.Surface(Xy(600,50))}
        )
    threadManager.Current.startTasks([pygameManager,Xy(600,600),"Dikstras algothim",gameManager.Current.userInput])
    gameManager(
        None,
        None,
        None,
        None,
        {"Main":[mainSceneManager]}
        )
    sleep(0.4)
    gameManager.Current.changeScene("Main")
    
if __name__ == '__main__':
    start()
    
