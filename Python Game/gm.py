import sys, pygame, math, times, controls, buildings, ui, tiles, city
from pygame.locals import *
pygame.init()

def Awake():	
	city.Awake()
	times.Awake()
	buildings.Awake()
	ui.Awake()
	tiles.Awake()
	controls.Awake()	
	
	global gameSurface	
	gameSurface = pygame.display.set_mode((ui.screen.width,ui.screen.height),pygame.FULLSCREEN)
	
def Update():
	DrawBackground()

	EventHandler()

	times.Update()
	tiles.Update()
	ui.Update()
	buildings.Update()
	city.Update()
	controls.Update()
	
	pygame.display.update()
	
def EventHandler():
	for event in pygame.event.get():
		EventTypeChecker(event)

def EventTypeChecker(event):
	if event.type == QUIT:
		Quit()
		
	controls.GetInput(event)
	
def Quit():
	pygame.quit()
	sys.exit()

def DrawBackground():
	pygame.draw.rect(gameSurface, (100,100,100), (0,0,ui.screen.width,ui.screen.height))
	
def CalculatePointDistance(pointA,pointB):
	point = (pointB[0]-pointA[0],pointB[1]-pointA[1])
	distance = math.sqrt(math.pow(point[0],2) + math.pow(point[1],2))
	return distance

if __name__ == "__main__":
	Awake()
	while (True):
		Update()