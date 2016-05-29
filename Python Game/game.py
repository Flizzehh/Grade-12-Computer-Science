import pygame, sys, random
from pygame.locals import *
from enum import IntEnum
pygame.init()

''' DEFINE ENUMS '''
class tileTypes(IntEnum): Water, Grass, Stone, Sand, Dirt = range(5)
class buildingTypes(IntEnum): LowDenRes, HighDenRes, Health, Fire, Police, LowDenCom, HighDenCom, LowDenInd, HighDenInd, Water, Power = range(11)
typeColours = { tileTypes.Water : (100,100,255), tileTypes.Grass : (150,255,150), tileTypes.Stone : (100,100,100), tileTypes.Sand : (194,178,128), tileTypes.Dirt : (155,118,83) }

''' DEFINE TILE MAP '''

class Tile:
	def __init__(self,height):
		self.height = height
		self.tempHeight = 0
		self.type = None
		self.building = None
		self.surroundingTiles = []
		self.hasRegion = False
	
class TileMap:
	def __init__(self,tileMapSize,tileSizePixels):
		self.tileSizePixels = tileSizePixels
		self.tileMapInit = []
		self.tileMap = []
		self.regions = []
		
		# Create the grid of tiles
		for x in range(tileMapSize):
			newRow = []
			for y in range(tileMapSize):
				newRow.append(Tile(random.randrange(0,100)/100))
			self.tileMap.append(newRow)
			
		# Set the surrounding tiles of each tile
		for x in range(tileMapSize):
			for y in range(tileMapSize):
				tile = self.tileMap[x][y]
				if (x + 1 < tileMapSize):
					tile.surroundingTiles.append(self.tileMap[x+1][y])
				if (x - 1 >= 0):
					tile.surroundingTiles.append(self.tileMap[x-1][y])
				if (y + 1 < tileMapSize):
					tile.surroundingTiles.append(self.tileMap[x][y+1])
				if (y - 1 >= 0):
					tile.surroundingTiles.append(self.tileMap[x][y-1])
					
				if (x + 1 < tileMapSize and y + 1 < tileMapSize):
					tile.surroundingTiles.append(self.tileMap[x+1][y+1])
				if (x - 1 >= 0  and y + 1 < tileMapSize):
					tile.surroundingTiles.append(self.tileMap[x-1][y+1])
				if (x + 1 < tileMapSize and y - 1 >= 0):
					tile.surroundingTiles.append(self.tileMap[x+1][y-1])
				if (x - 1 < tileMapSize and y - 1 >= 0):
					tile.surroundingTiles.append(self.tileMap[x-1][y-1])
					
		# Smooth terrain
		for i in range(7):
			for row in self.tileMap:
				for tile in row:
					averageSurroundingHeight = 0
					for surroundingTile in tile.surroundingTiles:
						averageSurroundingHeight += surroundingTile.height
					averageSurroundingHeight /= len(tile.surroundingTiles)
					tile.tempHeight = averageSurroundingHeight
			for row in self.tileMap:
				for tile in row:
					tile.height = tile.tempHeight
		
		# Set basic tile types			
		for row in self.tileMap:
			for tile in row:
				if (tile.height <= 0.47):
					tile.type = tileTypes.Water
				elif (tile.height > 0.47 and tile.height <= 0.53):
					tile.type = tileTypes.Grass
				else:
					tile.type = tileTypes.Stone
					
		# Set sand and dirt
		for row in self.tileMap:
			for tile in row:
				if (tile.type == tileTypes.Grass):
					for surroundingTile in tile.surroundingTiles:
						if (surroundingTile.type == tileTypes.Water):
							tile.type = tileTypes.Sand
						elif (surroundingTile.type == tileTypes.Stone):
							tile.type = tileTypes.Dirt
							
		# Get the groups of different tiles
		for row in self.tileMap:
			for tile in row:
				if (tile.hasRegion == False):
				
					currentTile = tile
					
					checkedTiles = [currentTile]
					frontier = [currentTile]
					
					regionTiles = []
					
					while (len(frontier) > 0):
						currentTile = frontier.pop(0)
						if (currentTile.hasRegion == False):
							regionTiles.append(currentTile)
							currentTile.hasRegion = True
						for surroundingTile in currentTile.surroundingTiles:
							if (surroundingTile not in checkedTiles and surroundingTile.hasRegion == False):
								frontier.append(surroundingTile)
								checkedTiles.append(surroundingTile)
								
					self.regions.append(TileRegion(tile.type,regionTiles))
					
		# Remove regions which are too small
		for region in self.regions:
			if (len(region.tiles) < 100):
				for tile in region:
					tile.tileType = tileTypes.Grass
						
				
	def Update(self):
		pygame.draw.rect(backgroundSurface, (25,25,25), (0,0,displayInfo.current_w,displayInfo.current_h))
		for rowIndex in range(len(self.tileMap)):
			row = self.tileMap[rowIndex]
			for tileIndex in range(len(row)):
				tile = row[tileIndex]
				colour = typeColours[tile.type]
				tileBounds = (tileIndex*self.tileSizePixels+cameraPos[0]*self.tileSizePixels,rowIndex*self.tileSizePixels+cameraPos[1]*self.tileSizePixels,self.tileSizePixels,self.tileSizePixels)
				if (ui.MouseWithinBounds(tileBounds)):
					colour = (colour[0]/2,colour[1]/2,colour[2]/2)
				pygame.draw.rect(displaySurface,colour,tileBounds)

class TileRegion:
	def __init__(self,tileType,tiles):
		self.tileType = tileType
		self.tiles = tiles

class UI:
	def __init__(self):
		self.mousePos = pygame.mouse.get_pos()
		self.selectedBuildingType = None
		self.selectedTile = None
		self.mouseOverTile = None
		self.panels = []
		self.buttons = []
		
		self.buildBarPanelOrigin = (displayInfo.current_w/2 - 400, displayInfo.current_h - 60)
		self.buildBarPanelSize = (800,50)
		
		self.infoBarPanelOrigin = (displayInfo.current_w/2 - 400, displayInfo.current_h - 60)
		self.infoBarPanelSize = (800,50)
		
		self.CreatePanels()
		self.CreateButtons()
	
	def CreatePanels(self):
		
		# Build bar panels
		self.panels.append(Panel((self.buildBarPanelOrigin[0]-5, self.buildBarPanelOrigin[1]-5, self.buildBarPanelSize[0] + 10,self.buildBarPanelSize[1] + 10),(50,50,50)))
		self.panels.append(Panel((self.buildBarPanelOrigin[0], self.buildBarPanelOrigin[1], self.buildBarPanelSize[0], self.buildBarPanelSize[1]),(200,200,200)))
		
		# Info bar panels
		self.panels.append(Panel((self.infoBarPanelOrigin[0]-5, self.infoBarPanelOrigin[1]-5, self.infoBarPanelSize[0] + 10,self.infoBarPanelSize[1] + 10),(50,50,50)))
		self.panels.append(Panel((self.infoBarPanelOrigin[0], self.infoBarPanelOrigin[1], self.infoBarPanelSize[0], self.infoBarPanelSize[1]),(200,200,200)))
		
	def CreateButtons(self):
		
		# Build bar buttons
		numButtons = len(list(map(int,buildingTypes)))
		buttonSize = (self.buildBarPanelSize[0]/(numButtons+(1-(1/numButtons))),40)
		
		for value in list(map(int,buildingTypes)):
			buttonColour = (150,150,150)
			buttonBounds = (self.buildBarPanelOrigin[0] + (buttonSize[0]+10) * value + 5 - 5*value,self.buildBarPanelOrigin[1]+5, buttonSize[0],buttonSize[1])			
			buttonText = Text(str(buildingTypes(value)).split(".")[1],"monospace",12,(255,255,255),buttonBounds)
			self.buttons.append(Button(buttonBounds,buttonColour,buttonText,buildingTypes,value))
			
	def DrawText(self,text):
		displaySurface.blit(text.text,text.bounds)
		
	def Update(self):
		self.mousePos = pygame.mouse.get_pos()
		self.UpdateBuildBar()
		self.DrawText(Text(str(deltaTime*1000),"monospace",12,(0,0,0),(0,0)))
		
	def UpdateBuildBar(self):
		for panel in self.panels:
			pygame.draw.rect(displaySurface,panel.colour,panel.bounds)
		
		for button in self.buttons:
			button.colour = (150,150,150)
			if (self.MouseWithinBounds(button.bounds)):
				button.colour = (125,125,125)
				
			pygame.draw.rect(displaySurface,button.colour,button.bounds)
			self.DrawText(button.text)
			
	def MouseWithinBounds(self,bounds):
		if (self.mousePos[0] >= bounds[0] and self.mousePos[0] < bounds[2]+bounds[0] and self.mousePos[1] >= bounds[1] and self.mousePos[1] < bounds[3]+bounds[1]):
			return True
		return False
		
class Button:
	def __init__(self,bounds,colour,text,buttonEnum,enumValue):
		self.buttonEnum = buttonEnum
		self.enumValue = enumValue
		self.bounds = bounds
		self.colour = colour
		self.text = text
		
class Panel:
	def __init__(self,bounds,colour):
		self.bounds = bounds;
		self.colour = colour;
		
class Text:
	def __init__(self,text,font,size,colour,bounds):
		self.textString = text
		self.text = pygame.font.SysFont(font,size).render(text,1,colour)
		self.font = font
		self.size = size
		self.colour = colour
		self.bounds = bounds
		
def Awake():
	global clock
	clock = pygame.time.Clock()
	global displayInfo
	displayInfo = pygame.display.Info()
	global backgroundSurface
	backgroundSurface = pygame.display.set_mode((displayInfo.current_w,displayInfo.current_h),pygame.FULLSCREEN)
	global displaySurface
	displaySurface = pygame.display.set_mode((displayInfo.current_w,displayInfo.current_h),pygame.FULLSCREEN)
	pygame.display.set_caption("Game")
	
	global cameraPos
	cameraW = ((-(tileMapSize*tileSizePixels)/2) + (displayInfo.current_w/2)) / tileSizePixels
	cameraH = ((-(tileMapSize*tileSizePixels)/2) + (displayInfo.current_h/2)) / tileSizePixels
	cameraPos = (cameraW,cameraH)

def EventHandler():
	for event in pygame.event.get():
		EventTypeChecker(event)

def EventTypeChecker(event):
	if event.type == QUIT:
		Quit()
	global cameraPos
	if event.type == pygame.KEYDOWN:
		cameraMoveAmount = 1 * tileSizePixels
		if (event.key == pygame.K_w):
			cameraPos = (cameraPos[0],cameraPos[1]+cameraMoveAmount)
		if (event.key == pygame.K_a):
			cameraPos = (cameraPos[0]+cameraMoveAmount,cameraPos[1])
		if (event.key == pygame.K_s):
			cameraPos = (cameraPos[0],cameraPos[1]-cameraMoveAmount)
		if (event.key == pygame.K_d):
			cameraPos = (cameraPos[0]-cameraMoveAmount,cameraPos[1])
		
		'''
		if (cameraPos[0] < -(tileMapSize)/2-tileSizePixels/(tileSizePixels/2)):
			cameraPos = (-(tileMapSize)/2-tileSizePixels/(tileSizePixels/2),cameraPos[1])
		if (cameraPos[0] > (tileMapSize/2)-tileSizePixels/(tileSizePixels/2)):
			cameraPos = (tileMapSize/2-tileSizePixels/(tileSizePixels/2),cameraPos[1])
		if (cameraPos[1] < -(tileMapSize)/2):
			cameraPos = (cameraPos[0],-(tileMapSize)/2)
		'''
		
		'''
		if (event.key == pygame.K_q):
			tm.tileSizePixels += 10
		if (event.key == pygame.K_e):
			tm.tileSizePixels -= 10
			if (tm.tileSizePixels < 10):
				tm.tileSizePixels = 10
		'''
		
		if (event.key == pygame.K_ESCAPE):
			Quit()
		
	if (event.type == pygame.MOUSEBUTTONDOWN):
		pass
			
def Quit():
	pygame.quit()
	sys.exit()

def Update():
	global deltaTime
	deltaTime = clock.tick() / 1000
	
	tm.Update()
	ui.Update()
	pygame.display.update()

tileMapSize = 100
tileSizePixels = 10

Awake()

ui = UI()
tm = TileMap(tileMapSize,tileSizePixels)


while True:
	EventHandler()
	Update()
