import pygame, sys, random, math
from pygame.locals import *
from enum import IntEnum
pygame.init()

''' DEFINE ENUMS '''
class tileTypes(IntEnum): Water, Grass, Stone, Sand, Dirt = range(5)
class buildingTypes(IntEnum): Road, CityHall, Residential, Commercial, Industrial, Health, Fire, Police, Water, Power = range(10)

class TilePrefabs:
	def __init__(self):
		self.tilePrefabs = []
	
	def AddTileType(self,tileType):
		self.tilePrefabs.append(tileType)
		
	def FindTilePrefabFromType(self,findTileType):
		for prefab in self.tilePrefabs:
			if (prefab.tileType == findTileType):
				return prefab
		return None

class TilePrefab:
	def __init__(self,tileType,colour):
		self.tileType = tileType
		self.colour = colour

class Buildings:
	def __init__(self):
		self.buildingPrefabs = []
		
	def AddBuilding(self,building):
		self.buildingPrefabs.append(building)
		
	def FindPrefabFromType(self,findBuildingType):
		for building in self.buildingPrefabs:
			if (building.buildingType == findBuildingType):
				return building
		return None

class BuildingPrefab:
	def __init__(self,buildingType,colour,cost,maintenanceBase,maintenanceModifier,maxPopulationModifer):
		self.buildingType = buildingType
		self.colour = colour
		self.cost = cost
		self.maintenanceBase = maintenanceBase
		self.maintenanceModifier = maintenanceModifier
		self.maxPopulation = maxPopulationModifer

class Building:
	def __init__(self,prefab,parentTile):
		self.prefab = prefab
		self.maintenance = 0
		self.population = 0
		self.density = 1
		self.parentTile = parentTile
		
	def Update(self):
		self.maintenance = round(self.prefab.maintenanceBase + (self.prefab.maintenanceModifier * (math.sqrt(self.population))))
		if (self.population <= self.prefab.maxPopulation):
			self.population += 1 * deltaTime
		else:
			self.population = self.prefab.maxPopulation

''' DEFINE TILE MAP '''

class Tile:
	def __init__(self,height):
		self.height = height
		self.tempHeight = 0
		self.prefab = None
		self.building = None
		self.surroundingTiles = []
		self.hasRegion = False
		
	def BuildBuilding(self,prefab):
		self.building = Building(prefab,self)
		city.buildings.append(self.building)
	
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
					tile.prefab = tilePrefabs.FindTilePrefabFromType(tileTypes.Water)
				elif (tile.height > 0.47 and tile.height <= 0.53):
					tile.prefab = tilePrefabs.FindTilePrefabFromType(tileTypes.Grass)
				else:
					tile.prefab = tilePrefabs.FindTilePrefabFromType(tileTypes.Stone)
							
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
							if (surroundingTile not in checkedTiles and surroundingTile.hasRegion == False and surroundingTile.prefab == currentTile.prefab):
								frontier.append(surroundingTile)
								checkedTiles.append(surroundingTile)
								
					self.regions.append(TileRegion(tile.prefab,regionTiles))
					
		# Remove regions which are too small
		for region in self.regions:
			if (len(region.tiles) < 100):
				for tile in region.tiles:
					tile.prefab = tilePrefabs.FindTilePrefabFromType(tileTypes.Grass)
				
		# Set sand and dirt
		for row in self.tileMap:
			for tile in row:
				if (tile.prefab.tileType == tileTypes.Grass):
					for surroundingTile in tile.surroundingTiles:
						if (surroundingTile.prefab.tileType == tileTypes.Water):
							tile.prefab = tilePrefabs.FindTilePrefabFromType(tileTypes.Sand)
						elif (surroundingTile.prefab.tileType == tileTypes.Stone):
							tile.prefab = tilePrefabs.FindTilePrefabFromType(tileTypes.Dirt)		
				
	def Update(self):
		ui.mouseOverTile = None
		pygame.draw.rect(backgroundSurface, (25,25,25), (0,0,displayInfo.current_w,displayInfo.current_h))
		for rowIndex in range(len(self.tileMap)):
			row = self.tileMap[rowIndex]
			for tileIndex in range(len(row)):
				tile = row[tileIndex]
				colour = tile.prefab.colour
				tileBounds = (tileIndex*self.tileSizePixels+cameraPos[0]*self.tileSizePixels,rowIndex*self.tileSizePixels+cameraPos[1]*self.tileSizePixels,self.tileSizePixels,self.tileSizePixels)
				if (ui.selectedBuilding != None and ui.MouseWithinBounds(tileBounds)):
					colour = (colour[0]/2,colour[1]/2,colour[2]/2)
					ui.mouseOverTile = tile
				pygame.draw.rect(displaySurface,colour,tileBounds)
				
				if (tile.building != None):
					pygame.draw.rect(displaySurface,buildings.FindPrefabFromType(buildingTypes.Road).colour,tileBounds)
					if (tile.building.prefab.buildingType != buildingTypes.Road):
						pygame.draw.rect(displaySurface,tile.building.prefab.colour,(tileBounds[0]+5,tileBounds[1]+5,tileBounds[2]-10,tileBounds[3]-10))

class TileRegion:
	def __init__(self,tileType,tiles):
		self.tileType = tileType
		self.tiles = tiles

''' DEFINE UI '''

class UI:
	def __init__(self):
		self.mousePos = pygame.mouse.get_pos()
		self.selectedBuilding = None
		self.selectedTile = None
		self.mouseOverTile = None
		
		self.panels = []
		self.buttons = []
		self.texts = []
		
		self.buildBarPanelOrigin = (displayInfo.current_w/2 - 400, displayInfo.current_h - 60)
		self.buildBarPanelSize = (800,50)
		
		self.infoBarPanelOrigin = (displayInfo.current_w/2 - 400, displayInfo.current_h - displayInfo.current_h + 10)
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
		buttonSize = ((self.buildBarPanelSize[0]-10) / numButtons,40)
		
		for value in list(map(int,buildingTypes)):
			buttonColour = (150,150,150)
			buttonBounds = (self.buildBarPanelOrigin[0] + 5 + (value * (buttonSize[0] + 5)),self.buildBarPanelOrigin[1]+5,buttonSize[0],buttonSize[1])	
			buttonText = Text(str(buildingTypes(value)).split(".")[1],"verdana",12,(255,255,255),buttonBounds)
			self.buttons.append(Button(buttonBounds,buttonColour,buttonText,buildings.buildingPrefabs[value]))
			
	def DrawText(self,text):
		displaySurface.blit(text.text,text.bounds)
		
	def Update(self):
		self.mousePos = pygame.mouse.get_pos()
		self.UpdateBuildBar()
		self.UpdateInfoBar()
		self.DrawText(Text(str(deltaTime*1000),"verdana",12,(0,0,0),(0,0)))
		
	def UpdateBuildBar(self):
		for panel in self.panels:
			pygame.draw.rect(displaySurface,panel.colour,panel.bounds)
		
		for button in self.buttons:
			button.colour = (50,50,50)
			previewColour = button.storedObject.colour
			if (self.MouseWithinBounds(button.bounds)):
				button.colour = (75,75,75)
			if (button.selected):
				button.colour = (100,100,100)
				if (button.selectedTimer <= 1):
					button.selectedTimer += 1 * deltaTime
				else:
					button.selectedTimer = 0
					button.selected = False
				
			pygame.draw.rect(displaySurface,button.colour,button.bounds)
			pygame.draw.rect(displaySurface,previewColour,(button.bounds[0],button.bounds[1]+20,button.bounds[2],button.bounds[3]-20))
			self.DrawText(button.text)
	
	def UpdateInfoBar(self):
		accountBounds = (self.infoBarPanelOrigin[0]+5,self.infoBarPanelOrigin[1])
		self.DrawText(Text("$" + str(round(city.account)),"verdana",14,(0,0,0),accountBounds))
		self.DrawText(Text("+$" + str(round(city.profit)),"verdana",14,(0,127,0),(accountBounds[0],accountBounds[1]+15)))
		self.DrawText(Text("-$" + str(round(city.expenses)),"verdana",14,(127,0,0),(accountBounds[0],accountBounds[1]+30)))
		
		dateTimeBounds = (self.infoBarPanelOrigin[0]+self.infoBarPanelSize[0]-70,self.infoBarPanelOrigin[1])
		self.DrawText(Text("Day " + str(dateTime.day),"verdana",14,(0,0,0),dateTimeBounds))
		self.DrawText(Text("Month " + str(dateTime.month),"verdana",14,(0,0,0),(dateTimeBounds[0],dateTimeBounds[1]+15)))
		self.DrawText(Text("Year " + str(dateTime.year),"verdana",14,(0,0,0),(dateTimeBounds[0],dateTimeBounds[1]+30)))
		
			
	def MouseWithinBounds(self,bounds):
		if (self.mousePos[0] >= bounds[0] and self.mousePos[0] < bounds[2]+bounds[0] and self.mousePos[1] >= bounds[1] and self.mousePos[1] < bounds[3]+bounds[1]):
			return True
		return False
		
	def MouseClickButton(self):
		for button in self.buttons:
			if (self.MouseWithinBounds(button.bounds)):
				self.selectedBuilding = button.storedObject
				button.selected = True
				return
		for panel in self.panels:
			if (self.MouseWithinBounds(panel.bounds)):
				return
		if (self.selectedBuilding != None):
			if (city.account >= self.selectedBuilding.cost):
				if (self.mouseOverTile != None and self.mouseOverTile.building == None and self.mouseOverTile.prefab.tileType == tileTypes.Grass):
					self.mouseOverTile.BuildBuilding(self.selectedBuilding)
		
''' DEFINE UI OBJECTS '''
		
class Button:
	def __init__(self,bounds,colour,text,storedObject):
		self.storedObject = storedObject
		self.bounds = bounds
		self.colour = colour
		self.text = text
		self.selected = False
		self.selectedTimer = 0
		
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

''' DEFINE CITY '''

class City:
	def __init__(self):
		self.population = 0
		self.income = 0
		self.expenses = 0
		self.profit = 0
		self.account = 20000
		self.buildings = []
		
	def Update(self):
		self.income = 0
		self.expenses = 0
		for building in self.buildings:
			self.population += building.population
			self.income = building.population * building.density
			self.expenses += building.maintenance
		
	def UpdateAccount(self):
		self.account += (self.income - self.expenses)
		
class DateTime:
	def __init__(self):
		self.day = 0
		self.month = 0
		self.year = 0
		self.dayTimer = 0
		
	def Update(self):
		self.dayTimer += 1 * deltaTime
		if (self.dayTimer >= 1):
			self.day += 1
			self.dayTimer = 0
		if (self.day > 30):
			self.month += 1
			self.day = 0
			if (self.month % 3 == 0):
				city.UpdateAccount()
		if (self.month > 12):
			self.year += 1
			self.month = 0

''' GAME HANDLER METHODS '''

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
	
	lineIndex = 0
	for line in open("data/buildings.txt",'r'):
		fixedLine = line.split('\n')[0]
		if (fixedLine != "END"):
			lineData = fixedLine.split("/")
			
			buildingType = buildingTypes(lineIndex)
			colour = (int(lineData[1].split(",")[0]),int(lineData[1].split(",")[1]),int(lineData[1].split(",")[2]))
			
			buildings.AddBuilding(BuildingPrefab(buildingType,colour,float(lineData[2]),float(lineData[3]),float(lineData[4]),float(lineData[5])))
		lineIndex += 1
	
	lineIndex = 0
	for line in open("data/tiles.txt",'r'):
		fixedLine = line.split('\n')[0]
		if (fixedLine != "END"):
			lineData = fixedLine.split("/")
			
			tileType = tileTypes(lineIndex)
			colour = (int(lineData[1].split(",")[0]),int(lineData[1].split(",")[1]),int(lineData[1].split(",")[2]))
			
			tilePrefabs.AddTileType(TilePrefab(tileType,colour))
		lineIndex += 1

def EventHandler():
	for event in pygame.event.get():
		EventTypeChecker(event)

def EventTypeChecker(event):
	if event.type == QUIT:
		Quit()
	global cameraPos
	if event.type == pygame.KEYDOWN:
		cameraMoveAmount = tileSizePixels / 10
		if (event.key == pygame.K_w):
			cameraPos = (cameraPos[0],cameraPos[1]+cameraMoveAmount)
		if (event.key == pygame.K_a):
			cameraPos = (cameraPos[0]+cameraMoveAmount,cameraPos[1])
		if (event.key == pygame.K_s):
			cameraPos = (cameraPos[0],cameraPos[1]-cameraMoveAmount)
		if (event.key == pygame.K_d):
			cameraPos = (cameraPos[0]-cameraMoveAmount,cameraPos[1])
		
		if (event.key == pygame.K_c):
			cameraW = ((-(tileMapSize*tileSizePixels)/2) + (displayInfo.current_w/2)) / tileSizePixels
			cameraH = ((-(tileMapSize*tileSizePixels)/2) + (displayInfo.current_h/2)) / tileSizePixels
			cameraPos = (cameraW,cameraH)
		
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
		
	if (pygame.mouse.get_pressed()[0]):
		ui.MouseClickButton()
	if (pygame.mouse.get_pressed()[2]):
		ui.selectedBuilding = None
			
def Quit():
	pygame.quit()
	sys.exit()

def Update():
	global deltaTime
	deltaTime = clock.tick() / 1000
	
	tm.Update()
	ui.Update()
	pygame.display.update()
	
	for building in city.buildings:
		building.Update()
	city.Update()
	
	dateTime.Update()

tileMapSize = 50
tileSizePixels = 20

dateTime = DateTime()
buildings = Buildings()
tilePrefabs = TilePrefabs()

Awake()

city = City()
ui = UI()
tm = TileMap(tileMapSize,tileSizePixels)

while True:
	EventHandler()
	Update()
