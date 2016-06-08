import times, pygame, random, math
from pygame.locals import *

''' BUILDING PREFABS '''

class BuildingGroups:
	def __init__(self):
		self.groups = []
		
	def AddGroup(self,group):
		self.groups.append(group)
		
	def FindGroupFromName(self,name):
		for group in self.groups:
			if (group.groupName == name):
				return group
		return None
		
	def FindPrefabFromName(self,name):
		for group in self.groups:
			for prefab in group.buildings:
				if (prefab.buildingType == name):
					return prefab
		return None

class BuildingGroup:
	def __init__(self,groupName):
		self.groupName = groupName
		self.buildings = []
		
	def AddPrefab(self,prefab):
		self.buildings.append(prefab)
		
	def FindPrefabFromType(self,buildingType):
		for building in self.buildings:
			if (building.buildingType == buildingType):
				return building
		return None

class BuildingPrefab:
	def __init__(self,lineData,group):
		if ('\t' in lineData[0]):
			self.buildingType = lineData[0].split('\t')[1]
		else:
			self.buildingType = lineData[0]
		self.cost = cost = float(lineData[1])
		self.maintenanceBase = float(lineData[2])
		self.maintenanceModifier = float(lineData[3])
		self.maxPopulation = float(lineData[4])
		self.landValueModifier = float(lineData[5])
		self.group = group
		try:
			self.spriteSheet = pygame.image.load("data/images/"+group.groupName+"/"+self.buildingType+".png")
		except pygame.error:
			self.spriteSheet = pygame.image.load("data/images/temp.png")
		self.sprites = []
		self.SplitSprites()
		
	def SplitSprites(self):
		spriteSheetSize = self.spriteSheet.get_rect().size
		numSprites = (round(spriteSheetSize[0]/32),round(spriteSheetSize[1]/32))
		for y in range(numSprites[1]):
			for x in range(numSprites[0]):
				sprite = pygame.Surface((32,32))
				sprite.blit(self.spriteSheet,(0,0),(x*32,y*32,32,32))
				self.sprites.append(sprite)
				
class BuildingPrefabs:
	def __init__(self):
		self.prefabs = []
		self.CreatePrefabs()
		
	def CreatePrefabs(self):		
		file = open("data/buildings.txt",'r')
		group = None
		for initialLine in file:
			line = initialLine.split('\n')[0]
			if ('\t' in list(line)):
				prefab = BuildingPrefab(line.split('/'),group)
				group.AddPrefab(prefab)
			else:
				if (group != None):
					buildingGroups.AddGroup(group)
				group = BuildingGroup(line)
		buildingGroups.AddGroup(group)
		
	def AddPrefab(self,prefab):
		self.prefabs.append(prefab)
		
	def FindPrefabFromType(self,buildingType):
		for prefab in self.prefabs:
			if (prefab.buildingType == buildingType):
				return prefab
		return None

''' BUILDINGS '''
	
class Building:
	def __init__(self,prefab,tile):
		self.prefab = prefab
		self.tile = tile
		
		self.population = []
		self.maintenance = 0
		
		self.employed = 0
		self.landValue = 1
		
		self.populationTimer = 0
		
		self.sprite = self.prefab.sprites[0]
		
		if (self.prefab.buildingType == "City Hall"):
			from city import city
			city.cityHall = self
		
	def Update(self):
		if (self.prefab.group.groupName == "Residential"):
			if (len(self.population) < self.prefab.maxPopulation):
				if (self.populationTimer < 10 / self.landValue):
					self.populationTimer += 1 * times.time.deltaTime
				else:
					self.populationTimer = 0
					self.population.append(Citizen(self))
					from city import city
					city.CalculateRCI()
				
			self.employed = 0
			for citizen in self.population:
				if (citizen.jobBuilding == None):
					citizen.FindJob()
				else:
					self.employed += 1
					
					if (citizen.positionTimer < 1):
						citizen.positionTimer += citizen.speed * times.time.deltaTime
						citizen.position = ((citizen.targetPathTile.position[0]-citizen.originPathTile.position[0]) * citizen.positionTimer + citizen.originPathTile.position[0],(citizen.targetPathTile.position[1]-citizen.originPathTile.position[1]) * citizen.positionTimer + citizen.originPathTile.position[1])
					else:
						citizen.positionTimer = 0
						citizen.position = citizen.targetPathTile.position
						citizen.originPathTile = citizen.targetPathTile
						citizen.targetPathTile = citizen.pathToWork[citizen.indexNum]
						citizen.indexNum += 1
						if (citizen.indexNum == len(citizen.pathToWork)-1):
							citizen.indexNum = 0
							citizen.pathToWork.reverse()
						
					from tiles import tm
					pygame.draw.rect(tm.tileSurface, (255,255,255), (citizen.position[0]+tm.tileSize/2-tm.tileSize/citizen.size + citizen.size/2,citizen.position[1]+tm.tileSize/2-tm.tileSize/citizen.size + citizen.size/2,round(tm.tileSize/citizen.size),round(tm.tileSize/citizen.size)))
	
	def SelfBitmasking(self):
		self.Bitmasking()
		for tile in self.tile.surroundingTiles:
			if (tile != None):
				if (tile.building != None):
					tile.building.Bitmasking()

	def Bitmasking(self):
		if (len(self.prefab.sprites) > 1):
			value = 0
			for tileIndex in range(len(self.tile.surroundingTiles[:4])):
				surroundingTile = self.tile.surroundingTiles[tileIndex]
				if (surroundingTile != None):
					if (surroundingTile.building != None and surroundingTile.building.prefab == self.prefab):
						value += math.pow(2,tileIndex)
			self.sprite = self.prefab.sprites[int(value)]
		else:
			self.sprite = self.prefab.sprites[0]
		
class Citizen:
	def __init__(self,building):
		self.jobBuilding = None
		self.homeBuilding = building
		
		self.pathToWork = []
		
		self.positionTimer = 0
		self.position = (self.homeBuilding.tile.position)
		self.originPathTile = self.homeBuilding.tile
		self.targetPathTile = self.homeBuilding.tile
		self.indexNum = 0
		
		self.size = random.randrange(4,10)
		self.speed = random.randrange(1,3) / 2
		
	def FindJob(self):
		from gm import CalculatePointDistance
		closestJobBuilding = None
		closestJobBuildingDistance = 0
		for tile in tm.tiles:
			if (tile.building != None and tile.building.prefab.group.groupName != "Residential" and tile.building.prefab.group.groupName != "Roads" and len(tile.building.population) < tile.building.prefab.maxPopulation):
				distance = CalculatePointDistance(tile.position,self.homeBuilding.tile.position)
				if (closestJobBuilding == None or distance < closestJobBuildingDistance):
					closestJobBuilding = tile.building
					closestJobBuildingDistance = distance
		if (closestJobBuilding != None):
			self.jobBuilding = closestJobBuilding
			self.jobBuilding.population.append(self)
			self.FindPathToWork()
			
	def FindPathToWork(self):
		currentTile = self.homeBuilding.tile
			
		checkedTiles = [currentTile]
		frontier = [currentTile]
		
		while (len(frontier) > 0):
			currentTile = frontier.pop(0)
			if (currentTile == self.jobBuilding.tile):
				while (currentTile != self.homeBuilding.tile):
					self.pathToWork.append(currentTile)
					currentTile = currentTile.cameFrom
				
			for surroundingTile in currentTile.surroundingTiles[:4]:
				if (surroundingTile != None):
					if (surroundingTile not in checkedTiles and surroundingTile.building != None and (surroundingTile.building.prefab.group.groupName == "Roads" or surroundingTile.building == self.jobBuilding)):
						frontier.append(surroundingTile)
						checkedTiles.append(surroundingTile)
						surroundingTile.cameFrom = currentTile
					
		self.pathToWork.append(self.homeBuilding.tile)
		self.pathToWork.reverse()

''' INIT METHODS '''
	
def Awake():
	global buildingGroups
	buildingGroups = BuildingGroups()
	global buildingPrefabs
	buildingPrefabs = BuildingPrefabs()
	
def Update():
	global tm
	from tiles import tm
	for tile in tm.tiles:
		if (tile.building != None):
			tile.building.Update()
	
''' USER METHODS '''
