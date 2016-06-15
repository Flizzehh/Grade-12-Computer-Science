import times, pygame, random, math
from pygame.locals import *

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

		self.moveSpeed = 1
		self.waterAmount = 0
		self.powerAmount = 0
		if (self.group.groupName == "Roads"):
			self.moveSpeed = float(lineData[6])
		elif (self.group.groupName == "Water"):
			self.waterAmount = int(lineData[6])
		elif (self.group.groupName == "Power"):
			self.powerAmount = int(lineData[6])

		self.range = 0
		if (self.group.groupName == "Police" or self.group.groupName == "Fire" or self.group.groupName == "Health"):
			self.range = int(lineData[6])
		
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

class Buildings:
	def __init__(self):
		self.buildings = []
		self.buildingsDict = {}

	def AddBuilding(self,building):

		from city import city

		self.buildings.append(building)

		foundPrefab = False
		for key in self.buildingsDict:
			if (key == building.prefab):
				self.buildingsDict[key].append(building)
				foundPrefab = True
		if (foundPrefab == False):
			self.buildingsDict[building.prefab] = []
			self.buildingsDict[building.prefab].append(building)

	def FindBuildingsFromName(self,name):
		returnBuildings = []
		for key in self.buildingsDict:
			for building in self.buildingsDict[key]:
				if (building.prefab.buildingType == name):
					returnBuildings.append(building)
		return returnBuildings

	def RemoveBuilding(self,building):
		self.buildings.remove(building)
		for key in self.buildingsDict:
			if (key == building.prefab):
				self.buildingsDict[key].remove(building)
				if (len(self.buildingsDict[key]) == 0):
					del self.buildingsDict[key]
				return

class Building:
	def __init__(self,prefab,tile):
		self.prefab = prefab
		self.tile = tile
		
		self.population = []
		self.maintenance = 0
		
		self.employed = 0
		self.landValue = 1
		self.income = 0
		self.expense = 0

		self.hasWater = 0
		self.hasPower = 0

		self.efficiency = 0
		
		self.populationTimer = 0
		
		self.sprite = self.prefab.sprites[0]

		self.coveredBuildings = []

		self.effectiveWaterAmount = 0
		self.effectivePowerAmount = 0

		self.policeCover = False
		self.fireCover = False
		self.healthCover = False
		self.services = 0
		self.averageHappiness = 0
		
		if (self.prefab.buildingType == "City Hall"):
			from city import city
			city.cityHall = self
		
	def Update(self):

		from city import city

		if (self.prefab.group.groupName == "Residential"):

			self.income = (len(self.population) * self.employed + self.landValue) * 0.1

			if (len(self.population) < self.prefab.maxPopulation):
				if (self.populationTimer < 10 * (1-city.resDemand)):
					self.populationTimer += 1 * times.time.deltaTime
				else:
					self.populationTimer = 0
					if (random.randrange(0,100) < (city.resDemand * 100)):
						self.population.append(Citizen(self))	
						city.DistributeUtilities()
					city.CalculateRCI()
				
			self.services = 0
			if (self.policeCover):
				self.services += 1 
			if (self.fireCover):
				self.services += 1
			if (self.healthCover):
				self.services += 1

			self.employed = 0
			self.hasWater = 0
			self.hasPower = 0
			self.averageHappiness = 0
			for citizen in self.population:

				citizen.happiness = 0

				if (citizen.hasWater):
					self.hasWater += 1
					citizen.happiness += 1
				if (citizen.hasPower):
					self.hasPower += 1
					citizen.happiness += 1

				if (citizen.jobBuilding == None):
					citizen.FindJob()
				else:
					self.employed += 1
					citizen.happiness += 1

					if (citizen.positionTimer < 1):
						citizen.positionTimer += citizen.speed * times.time.deltaTime * citizen.originPathTile.building.prefab.moveSpeed
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
				
				citizen.happiness += citizen.services
				citizen.happiness /= 6
				self.averageHappiness += citizen.happiness
			if (len(self.population) > 0):
				self.averageHappiness /= len(self.population)

		elif (self.prefab.group.groupName == "Commercial"):
			self.income = len(self.population) * city.comDemand * 0.5

		elif (self.prefab.group.groupName == "Industrial"):
			self.income = len(self.population) * city.indDemand * 0.5

		self.expense = (len(self.population) * 0.1) + self.prefab.maintenanceBase

		if (self.prefab.maxPopulation > 0):
			self.efficiency = len(self.population) / self.prefab.maxPopulation
	
	def SelfBitmasking(self):
		self.Bitmasking()
		for tile in self.tile.surroundingTiles:
			if (tile != None and tile.building != None):
				tile.building.Bitmasking()

	def Bitmasking(self):
		if (len(self.prefab.sprites) > 1):
			value = 0
			for tileIndex in range(len(self.tile.surroundingTiles[:4])):
				surroundingTile = self.tile.surroundingTiles[tileIndex]
				if (surroundingTile != None):
					if (surroundingTile.building != None and (surroundingTile.building.prefab == self.prefab or surroundingTile.building.prefab.group == self.prefab.group)):
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
		
		self.size = random.randrange(8,10)
		self.speed = random.randrange(1,3) / 2

		self.hasWater = False
		self.hasPower = False

		self.happiness = 0
		self.services = 0
		
	def FindJob(self):
		from gm import CalculatePointDistance
		closestJobBuilding = None
		closestJobBuildingDistance = 0
		for building in buildings.buildings:
			if (building.prefab.group.groupName != "Residential" and building.prefab.group.groupName != "Roads" and len(building.population) < building.prefab.maxPopulation):
				distance = CalculatePointDistance(building.tile.position,self.homeBuilding.tile.position)
				if (closestJobBuilding == None or distance < closestJobBuildingDistance):
					closestJobBuilding = building
					closestJobBuildingDistance = distance
		if (closestJobBuilding != None):
			self.jobBuilding = closestJobBuilding
			self.jobBuilding.population.append(self)
			from city import city
			city.DistributeServices()
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
	global buildings
	buildings = Buildings()
	
def Update():
	for building in buildings.buildings:
		building.Update()
