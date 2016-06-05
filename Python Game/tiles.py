import math, pygame, random
from pygame.locals import *

''' TILE PREFABS '''

class TilePrefab:
	def __init__(self,tileType,colour):
		self.tileType = tileType
		self.colour = colour
		
class TilePrefabs:
	def __init__(self):
		self.prefabs = []
		self.CreatePrefabs()
		
	def CreatePrefabs(self):
		lineIndex = 0
		for line in open("data/tiles.txt",'r'):
			fixedLine = line.split('\n')[0]
			if (fixedLine != "END"):
				lineData = fixedLine.split("/")
				
				tileType = lineData[0]
				colour = (int(lineData[1].split(",")[0]),int(lineData[1].split(",")[1]),int(lineData[1].split(",")[2]))
				
				self.AddPrefab(TilePrefab(tileType,colour))
			lineIndex += 1
		
	def AddPrefab(self,prefab):
		self.prefabs.append(prefab)
		
	def FindPrefabFromType(self,tileType):
		for prefab in self.prefabs:
			if (prefab.tileType == tileType):
				return prefab
		return None
		
''' TILE MAP '''
		
class Tile:
	def __init__(self,height,indexPos):
		self.height = height
		self.tempHeight = 0
		
		self.indexPos = indexPos
		self.CalculateTilePosition()
		
		self.prefab = None
		
		self.building = None
		
		self.surroundingTiles = []
		self.region = None
		
		self.cameFrom = None
		
	def AddBuilding(self,building):
		self.building = building
		
	def CalculateTilePosition(self):
		self.position = (self.indexPos[0]*tm.tileSize+camera.position[0]*tm.tileSize,self.indexPos[1]*tm.tileSize+camera.position[1]*tm.tileSize,tm.tileSize,tm.tileSize)

class TileMap:
	def __init__(self,size,tileSize):
		self.size = size
		self.tileSize = tileSize
	
		self.sortedTiles = []
		self.tiles = []
		
		self.regions = []
		
		from ui import screen
		self.screen = screen
		self.tileSurface = pygame.display.set_mode((self.screen.width,self.screen.height),pygame.FULLSCREEN)
		
		self.validRoadTiles = []
		self.validBuildTiles = []
		
	def GenerateTileMap(self):
		self.CreateTiles(self.size,self.tileSize)
		self.SetSurroundingTiles()
		self.SmoothTileHeight(7)
		self.SetBasicTileTypes(0.46,0.54)
		self.CreateTileRegions()
		self.RemoveSmallRegions(100)
		self.SetSpecialTileTypes()
		
	def CreateTiles(self,size,tileSize):
		for x in range(self.size):
			newRow = []
			for y in range(self.size):
				tile = Tile(random.randrange(0,100)/100,(x,y))
				newRow.append(tile)
				self.tiles.append(tile)
			self.sortedTiles.append(newRow)
		
	def SetSurroundingTiles(self):	
		for x in range(self.size):
			for y in range(self.size):
				tile = self.sortedTiles[x][y]
				if (y + 1 < self.size):
					tile.surroundingTiles.append(self.sortedTiles[x][y+1])
				if (x + 1 < self.size):
					tile.surroundingTiles.append(self.sortedTiles[x+1][y])
				if (y - 1 >= 0):
					tile.surroundingTiles.append(self.sortedTiles[x][y-1])
				if (x - 1 >= 0):
					tile.surroundingTiles.append(self.sortedTiles[x-1][y])		
					
				if (x - 1 >= 0  and y + 1 < self.size):
					tile.surroundingTiles.append(self.sortedTiles[x-1][y+1])
				if (x + 1 < self.size and y + 1 < self.size):
					tile.surroundingTiles.append(self.sortedTiles[x+1][y+1])				
				if (x + 1 < self.size and y - 1 >= 0):
					tile.surroundingTiles.append(self.sortedTiles[x+1][y-1])
				if (x - 1 < self.size and y - 1 >= 0):
					tile.surroundingTiles.append(self.sortedTiles[x-1][y-1])
					
	def SmoothTileHeight(self,iterations):
		for i in range(iterations):
			for tile in self.tiles:
				averageSurroundingHeight = 0
				for surroundingTile in tile.surroundingTiles:
					averageSurroundingHeight += surroundingTile.height
				averageSurroundingHeight /= len(tile.surroundingTiles)
				tile.tempHeight = averageSurroundingHeight
				
			for tile in self.tiles:
				tile.height = tile.tempHeight
					
	def SetBasicTileTypes(self,waterTop,stoneBottom):			
		for tile in self.tiles:
			if (tile.height <= waterTop):
				tile.prefab = tilePrefabs.FindPrefabFromType("Water")
			elif (tile.height > waterTop and tile.height <= stoneBottom):
				tile.prefab = tilePrefabs.FindPrefabFromType("Grass")
			else:
				tile.prefab = tilePrefabs.FindPrefabFromType("Stone")
					
	def CreateTileRegions(self):
		for tile in self.tiles:
			if (tile.region == None):
			
				currentTile = tile
				
				checkedTiles = [currentTile]
				frontier = [currentTile]
				
				regionTiles = []
				region = TileRegion(tile.prefab)
				
				while (len(frontier) > 0):
					currentTile = frontier.pop(0)
					if (currentTile.region == None):
						regionTiles.append(currentTile)
						currentTile.region = region
					for surroundingTile in currentTile.surroundingTiles:
						if (surroundingTile not in checkedTiles and surroundingTile.region == None and surroundingTile.prefab == currentTile.prefab):
							frontier.append(surroundingTile)
							checkedTiles.append(surroundingTile)
						
				region.AddTiles(regionTiles)
				self.regions.append(region)
					
	def RemoveSmallRegions(self,threshold):
		for region in self.regions:
			if (len(region.tiles) < threshold):
				for tile in region.tiles:
					tile.prefab = tilePrefabs.FindPrefabFromType("Grass")
				
	def SetSpecialTileTypes(self):
		for tile in self.tiles:
			if (tile.prefab.tileType == "Grass"):
				for surroundingTile in tile.surroundingTiles:
					if (surroundingTile.prefab.tileType == "Water"):
						tile.prefab = tilePrefabs.FindPrefabFromType("Sand")
					elif (surroundingTile.prefab.tileType == "Stone"):
						tile.prefab = tilePrefabs.FindPrefabFromType("Dirt")
						
	def Update(self):
	
		from ui import ui
		from buildings import Building
		from buildings import buildingPrefabs
		from city import city
		
		visibleTiles = 0
		
		lines = []
		
		ui.mouseOverTile = None
		for tile in self.tiles:
			if (self.TileWithinCamera(tile)):
				visibleTiles += 1
				tileColour = tile.prefab.colour
							
				if (ui.MouseWithinBounds((tile.position)+(self.tileSize,self.tileSize))):
					ui.mouseOverTile = tile
				
				if (ui.selectedBuilding != None and ui.MouseWithinBounds((tile.position)+(self.tileSize,self.tileSize))):
					if ((tile in self.validRoadTiles or tile in self.validBuildTiles) or ui.selectedBuilding.buildingType == "City Hall"):
						tileColour = (round(tileColour[0]/2),round(tileColour[1]),round(tileColour[2]/2))
					else:
						tileColour = (round(tileColour[0]),round(tileColour[1]/2),round(tileColour[2]/2))
					if (tile.prefab.tileType == "Grass" and ui.mouseDown and ui.mouseOverUI == False and tile.building == None):
						if (ui.selectedBuilding.buildingType == "City Hall" or ((ui.selectedBuilding.buildingType == "Road" and tile in self.validRoadTiles) or tile in self.validBuildTiles)):
							newBuilding = Building(ui.selectedBuilding,tile)
							tile.AddBuilding(newBuilding)
							self.CalculateLandValue()
							self.FindValidRoadTiles()
							self.FindValidBuildingSpots()
							city.bank -= newBuilding.prefab.cost
								
				if  (tile in tm.validRoadTiles and ui.selectedBuilding != None and ui.selectedBuilding.buildingType == "Road"):
					tileColour = (tileColour[0]/2,tileColour[1],tileColour[2]/2)
				elif (tile in tm.validBuildTiles and ui.selectedBuilding != None and ui.selectedBuilding.buildingType != "Road" and ui.selectedBuilding.buildingType != "City Hall"):
					tileColour = (tileColour[0]/2,tileColour[1],tileColour[2]/2)
					
				pygame.draw.rect(self.tileSurface,tileColour,tile.position)
				
				if (tile.building != None):
					buildingRect = tile.position
					if (tile.building.prefab.buildingType != "Road"):
						buildingRect = (tile.position[0]+(self.tileSize*0.1),tile.position[1]+(self.tileSize*0.1),self.tileSize-(self.tileSize*0.2),self.tileSize-(self.tileSize*0.2))				
					
					for value in range(len(tile.surroundingTiles[:4])):
						surroundingTile = tile.surroundingTiles[value]
						if (surroundingTile.building != None and surroundingTile.building.prefab.buildingType == "Road"):
							connectingRoadRect = None
							if (value == 0):
								connectingRoadRect = (tile.position[0]+self.tileSize/4,tile.position[1]+self.tileSize/2,self.tileSize/2,self.tileSize/2)
							if (value == 1):
								connectingRoadRect = (tile.position[0]+self.tileSize/2,tile.position[1]+self.tileSize/4,self.tileSize/2,self.tileSize/2)
							if (value == 2):
								connectingRoadRect = (tile.position[0]+self.tileSize/4,tile.position[1],self.tileSize/2,self.tileSize/2)
							if (value == 3):
								connectingRoadRect = (tile.position[0],tile.position[1]+self.tileSize/4,self.tileSize/2,self.tileSize/2)
							pygame.draw.rect(self.tileSurface,buildingPrefabs.FindPrefabFromType("Road").colour,connectingRoadRect)
							
					pygame.draw.rect(self.tileSurface,tile.building.prefab.colour,buildingRect)
					
					if (ui.mouseOverTile == tile and tile.building.prefab.buildingType == "Residential"):
						for citizen in tile.building.population:
							if (citizen.jobBuilding != None):
								lines.append(Line((255,255,255),(tile.position[0]+self.tileSize/2,tile.position[1]+self.tileSize/2),(citizen.jobBuilding.tile.position[0]+self.tileSize/2,citizen.jobBuilding.tile.position[1]+self.tileSize/2),round(self.tileSize * 0.05)))
		for line in lines:
			pygame.draw.line(self.tileSurface,line.colour,line.startPosition,line.endPosition,line.thickness)
			
	def UpdateTilePosition(self):
		for tile in self.tiles:
			tile.CalculateTilePosition()
			
	def CalculateLandValue(self):
		from gm import CalculatePointDistance
		from buildings import buildingPrefabs
		largestDistance = math.sqrt(math.pow(self.size,2) + (math.pow(self.size,2))) * 2
		for tile in self.tiles:
			if (tile.building != None and tile.building.prefab.buildingType == "Residential"):
				closestBuildings = dict()
				for nTile in self.tiles:
					if (tile != nTile and nTile.building != None):
						buildingType = nTile.building.prefab.buildingType
						if (buildingType != "Road" and buildingType != "Residential"):
							distance = CalculatePointDistance(nTile.indexPos,tile.indexPos)/largestDistance
							if (buildingType in closestBuildings):
								if (closestBuildings[buildingType] > distance):
									closestBuildings[buildingType] = distance
							else:
								closestBuildings[buildingType] = distance
					
				for key in closestBuildings:
					distanceMultiplier = (1 - closestBuildings[key])
					#print(key + " " + str(distanceMultiplier * buildingPrefabs.FindPrefabFromType(key).landValueModifier))
					tile.building.landValue += distanceMultiplier * buildingPrefabs.FindPrefabFromType(key).landValueModifier
				'''
				if (tile.building.landValue < 1 and tile.building.landValue >= 0):
					tile.building.landValue = 1
				if (tile.building.landValue < 0 and tile.building.landValue > -1):
					tile.building.landValue = -1
				'''
		
	def FindValidRoadTiles(self):
	
		self.validRoadTiles.clear()
	
		from city import city
		cityHall = city.cityHall
			
		currentTile = cityHall.tile
			
		checkedTiles = [currentTile]
		frontier = [currentTile]
		
		while (len(frontier) > 0):
			currentTile = frontier.pop(0)
			if (currentTile.prefab.tileType == "Grass" and currentTile.building == None):
				self.validRoadTiles.append(currentTile)
			for surroundingTile in currentTile.surroundingTiles[:4]:
				if (surroundingTile not in checkedTiles and currentTile.building != None and (currentTile.building.prefab.buildingType == "Road" or currentTile.building.prefab.buildingType == "City Hall")):
					frontier.append(surroundingTile)
					checkedTiles.append(surroundingTile)
	
	def FindValidBuildingSpots(self):
		self.validBuildTiles.clear()
		for tile in self.tiles:
			foundRoad = False
			for surroundingTile in tile.surroundingTiles[:4]:
				if (surroundingTile.building != None and surroundingTile.building.prefab.buildingType == "Road"):
					foundRoad = True
					break
			if (foundRoad and tile.building == None and tile.prefab.tileType == "Grass"):
				self.validBuildTiles.append(tile)
				
	def TileWithinCamera(self,tile):
		
		if (tile.indexPos[0]+1 >= -camera.position[0] and tile.indexPos[1]+1 >= -camera.position[1]):
			if (tile.indexPos[0]-1 <= -camera.position[0]+(self.screen.width/self.tileSize) and tile.indexPos[1]-1 <= -camera.position[1]+(self.screen.height/self.tileSize)):
				
				return True
		return False
			
class TileRegion:
	def __init__(self,prefab):
		self.prefab = prefab
		self.tiles = []
		
	def AddTiles(self,tiles):
		self.tiles = tiles
			
			
class Line:
	def __init__(self,colour,startPosition,endPosition,thickness):
		self.colour = colour
		self.startPosition = startPosition
		self.endPosition = endPosition
		self.thickness = thickness
		
''' FILE METHODS '''

class Camera:
	def __init__(self):
		self.position = (0,0)
		
	def ChangePosition(self,modifier):
		self.position = (self.position[0]+modifier[0],self.position[1]+modifier[1])
		tm.UpdateTilePosition()
		
	def CenterCamera(self):
		from ui import screen
		cameraW = ((-(tm.size*tm.tileSize)/2) + (screen.width/2)) / tm.tileSize
		cameraH = ((-(tm.size*tm.tileSize)/2) + (screen.height/2)) / tm.tileSize
		self.position = (cameraW,cameraH)
		tm.UpdateTilePosition()

def Awake():
	global tilePrefabs
	tilePrefabs = TilePrefabs()

	global camera
	camera = Camera()

	global tm
	tm = TileMap(50,100)
	tm.GenerateTileMap()
	
	camera.CenterCamera()

def Update():
	tm.Update()
	
''' USER METHODS '''

def GenerateTileMap(size,tileSize):
	pass
	
def GetSortedTiles():
	return tm.sortedTiles
	
def GetTiles():
	return tm.tiles