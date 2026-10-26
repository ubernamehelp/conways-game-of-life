import pygame
import time
from dataclasses import dataclass
import collections
import math
import sys

CELLWIDTH = 25
CELLHEIGHT = 25

def round_to_bound(value, lb=-sys.maxsize - 1, ub=sys.maxsize): # basically just checks if a certain value is between the lb and ub if not then it returns closest bound
    if lb <= value <= ub: # check value between lb and ub
        return value
    else:
        return (lb if value < lb else ub) # low bound if value lower than it otherwise return upperbound

def get_neighbors(cells, row, column):
    neighbours = []
    for celldata in cells:
        if celldata.get('column') == column and celldata.get('row') == row: continue # not current cell
        if celldata.get('row') < row-1 or celldata.get('row') > row+1: continue  # if not row neighbour
        if celldata.get('column') < column-1 or celldata.get('column') > column+1: continue # if not column neighbour
        neighbours.append([celldata.get('row'), celldata.get('column')])

    return neighbours

@dataclass
class Camera: # dc for the camera
    position: pygame.Vector2
    zoom_level: float
    move_speed:int

class Text: # for displaying text
    def __init__(self, text:str, screen: pygame.surface.Surface):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 16)

        self.textSurface = self.font.render(text, True, 'green')

    def render(self, position):
        self.screen.blit(self.textSurface, position)
        

class App:
    def __init__(self):
        # inits
        pygame.init()
        pygame.font.init()

        # objects
        self.screen = pygame.display.set_mode((540,340), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.camera = Camera(pygame.Vector2(0,0), 1.0, 1)

        # states
        self.running = True
        self.paused = True
        self.can_step = False
        self.keybinds_shown = True

        # delta time
        self.dt = 0
        
        # display caption
        pygame.display.set_caption("Conway's Game Of Life")

        # cells to be displayed on the screen, includes the birth of it, its row and collum
        self.cells = []

        # generation number
        self.generation = 0

        # how long between each generation
        self.generationsPerSecond = 2

        # last generation time
        self.lastGenerationTime = time.time()

    def run(self):

        while self.running: # main loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    if event.key == pygame.K_r:
                        self.cells = {}
                        self.paused = True
                    if event.key == pygame.K_f:
                        self.can_step = True
                    if event.key == pygame.K_q:
                        self.generationsPerSecond = round_to_bound((self.generationsPerSecond-10 if pygame.key.get_pressed()[pygame.K_LSHIFT] else self.generationsPerSecond-1), 1) # if shift then -10 otherwise -1
                    if event.key == pygame.K_e:
                        self.generationsPerSecond = round_to_bound((self.generationsPerSecond+10 if pygame.key.get_pressed()[pygame.K_LSHIFT] else self.generationsPerSecond+1), 1) # if shift then +10 otherwise +1
                    if event.key == pygame.K_h:
                        self.keybinds_shown = not self.keybinds_shown

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 2: # middle mouse button
                        self.camera.zoom_level = 1.0
                        self.camera.move_speed = 1

                    if event.button == 1:
                        pos = pygame.Vector2(pygame.mouse.get_pos())
                        world_pos = pygame.Vector2(
                            math.floor((pos.x - self.screen.get_width() / 2 + self.camera.position.x) / (CELLWIDTH * self.camera.zoom_level)),
                            math.floor((pos.y - self.screen.get_height() / 2 - self.camera.position.y) / (CELLHEIGHT * self.camera.zoom_level)),
                            )
                        
                        self.cells.append({'birth':self.generation, 'row':int(world_pos.x), 'column':int(world_pos.y)})

                    if event.button == 3:
                        pos = pygame.Vector2(pygame.mouse.get_pos())
                        world_pos = pygame.Vector2(
                            math.floor((pos.x - self.screen.get_width() / 2 + self.camera.position.x) / (CELLWIDTH * self.camera.zoom_level)),
                            math.floor((pos.y - self.screen.get_height() / 2 - self.camera.position.y) / (CELLHEIGHT * self.camera.zoom_level)),
                            )
                        
                        for celldata in self.cells:
                            if celldata.get('row') == int(world_pos.x) and celldata.get('column') == int(world_pos.y):
                                self.cells.remove(celldata)


                if event.type == pygame.MOUSEWHEEL:
                    if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                        self.camera.zoom_level = round_to_bound(self.camera.zoom_level+event.y/100, 0.01, 2) # no value below 0.01, or higher than 2
                    else:
                        self.camera.move_speed = round_to_bound(self.camera.move_speed+event.y, 1, 20) # no value below 1, or above 100

            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.camera.position.y +=round(1*self.camera.move_speed*1+self.dt)
            if keys[pygame.K_s]:
                self.camera.position.y -=round(1*self.camera.move_speed*1+self.dt)
            if keys[pygame.K_a]:
                self.camera.position.x -=round(1*self.camera.move_speed*1+self.dt)
            if keys[pygame.K_d]:
                self.camera.position.x +=round(1*self.camera.move_speed*1+self.dt)

            self.screen.fill("black")

            for celldata in self.cells: # draw cells
                row = celldata.get('row')
                column = celldata.get('column')

                neighbours = get_neighbors(self.cells, row, column)

                if len(neighbours) < 2: # underpopulation
                    celldata.update({'deathmarked':True})
                elif len(neighbours) > 3: # overpopulation
                    celldata.update({'deathmarked':True})
                else:
                    celldata.update({'deathmarked':False})

                xlb = self.camera.position.x / CELLWIDTH * self.camera.zoom_level - (self.screen.get_width()/2+CELLWIDTH) / CELLWIDTH*self.camera.zoom_level
                xub = self.camera.position.x / CELLWIDTH * self.camera.zoom_level + self.screen.get_width()/2 / CELLWIDTH*self.camera.zoom_level

                ylb = self.camera.position.y / CELLHEIGHT * self.camera.zoom_level - self.screen.get_height()/2 / CELLHEIGHT*self.camera.zoom_level
                yub = self.camera.position.y / CELLHEIGHT * self.camera.zoom_level + (self.screen.get_height()/2+CELLHEIGHT) / CELLHEIGHT*self.camera.zoom_level                

                if xlb < row < xub and ylb < column < yub: # only render inside what cam can see

                    pygame.draw.rect(
                        self.screen, 
                        ('red' if celldata.get('deathmarked') else 'white'),
                        pygame.Rect(
                            row*CELLWIDTH*self.camera.zoom_level+self.screen.get_width()/2-self.camera.position.x,
                            column*CELLHEIGHT*self.camera.zoom_level+self.screen.get_height()/2+self.camera.position.y,
                            CELLWIDTH*self.camera.zoom_level,
                            CELLHEIGHT*self.camera.zoom_level
                            )
                        )
                
            # draw informational text:
            cameraText = Text(f"Camera Position: {self.camera.position}\nCamera speed: {self.camera.move_speed}\nCamera zoom: {format(self.camera.zoom_level, '.2f')}", self.screen)
            generationText = Text(f"Generation: {self.generation}\nAlive Cells: {len(self.cells)}\nGenerations Per Second: {self.generationsPerSecond}", self.screen)
            fpsText = Text(f"FPS:{round(self.clock.get_fps())}", self.screen)

            cameraText.render((0,0))
            generationText.render((0, self.screen.get_height()-generationText.textSurface.get_height()))
            fpsText.render((self.screen.get_width()-fpsText.textSurface.get_width(), 0))

            # check if can step
            if (self.paused and not self.can_step) or time.time() < self.lastGenerationTime + 1/self.generationsPerSecond:
                pygame.display.flip()
                self.dt = self.clock.tick(240)/100
                continue

            self.lastGenerationTime = time.time()

            self.generation+=1

            self.can_step = False


                    
            potentialCells = []

            for celldata in self.cells:
                row = celldata.get('row')
                column = celldata.get('column')

                neighbours = get_neighbors(self.cells, row, column)

                # reproduction

                surroundingCells = []
                for surroundingRow in range(row-1, row+2):
                    for surroundingColumn in range(column-1, column+2):
                        if surroundingColumn == column and surroundingRow == row: continue
                        surroundingCells.append([surroundingRow, surroundingColumn])

                for potentialCell in surroundingCells:
                    is_neighbour = False
                    for neighbour in neighbours:
                        if potentialCell == neighbour:
                            is_neighbour = True
                    if not is_neighbour:
                        potentialCells.append(tuple(potentialCell))
            
            
            potentialCellsCount = collections.Counter(potentialCells)
            print(potentialCellsCount)
            for potentialCell, count in potentialCellsCount.items():
                if count == 3:
                    self.cells.append({'birth':self.generation, 'row':potentialCell[0], 'column':potentialCell[1]})
                    print("newcell:", potentialCell)

            newCells = []
            for celldata in self.cells:
                if not celldata.get('deathmarked'):
                    newCells.append(celldata)
            self.cells = newCells

            if len(self.cells) == 0: # reset generation count if cells die out
                self.generation = 0

            print("-"*50)
            pygame.display.flip()
            self.dt = self.clock.tick(240)/100


        
        pygame.quit()

if __name__=="__main__":
    app = App()
    app.run()