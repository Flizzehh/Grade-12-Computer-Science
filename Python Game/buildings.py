import times, pygame, random
from pygame.locals import *

''' BUILDING PREFABS '''

class BuildingGroup:
	def __init__(self,groupName):
		self.groupName = groupName
		self.buildings = []
		
	def AddPrefab(self,prefab):
		self.buildings.append(prefab)

class BuildingPrefab:
	def __init__(self,buildingType,colour,cost,maintenanceBase,maintenanceModifier,maxPopulationModifer,landValueModifier):
		self.buildingType = buildingType
		self.colour = colour
		self.cost = cost
		self.maintenanceBase = maintenanceBase
		self.maintenanceModifier = maintenanceModifier
		self.maxPopulation = maxPopulationModifer
		self.landValueModifier = landValueModifier
		
class BuildingPrefabs:
	def __init__(self):
		self.prefabs = []
		self.CreatePrefabs()
		
	def CreatePrefabs(self):
		lineIndex = 0
		for line in open("data/buildings.txt",'r'):
			fixedLine = line.split('\n')[0]
			if (fixedLine != "END"):
				lineData = fixedLine.split("/")
				
				buildingType = lineData[0]
				colour = (int(lineData[1].split(",")[0]),int(lineData[1].split(",")[1]),int(lineData[1].split(",")[2]))
				
				self.AddPrefab(BuildingPrefab(buildingType,colour,float(lineData[2]),float(lineData[3]),float(lineData[4]),float(lineData[5]),float(lineData[6])))
			lineIndex += 1
		
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
		
		if (self.prefab.buildingType == "City Hall"):
			from city import city
			city.cityHall = self
		
	def Update(self):
		if (self.prefab.buildingType == "Residential"):
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
					pygame.draw.rect(tm.tileSurface, citizen.jobBuilding.prefab.colour, (citizen.position[0]+tm.tileSize/2-tm.tileSize/citizen.size + citizen.size/2,citizen.position[1]+tm.tileSize/2-tm.tileSize/citizen.size + citizen.size/2,round(tm.tileSize/citizen.size),round(tm.tileSize/citizen.size)))
		
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
			if (tile.building != None and tile.building.prefab.buildingType != "Residential" and tile.building.prefab.buildingType != "Road" and len(tile.building.population) < tile.building.prefab.maxPopulation):
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
				if (surroundingTile not in checkedTiles and surroundingTile.building != None and (surroundingTile.building.prefab.buildingType == "Road" or surroundingTile.building == self.jobBuilding)):
					frontier.append(surroundingTile)
					checkedTiles.append(surroundingTile)
					surroundingTile.cameFrom = currentTile
					
		self.pathToWork.append(self.homeBuilding.tile)
		self.pathToWork.reverse()

''' INIT METHODS '''
	
def Awake():
	global buildingPrefabs
	buildingPrefabs = BuildingPrefabs()
	
def Update():
	global tm
	from tiles import tm
	for tile in tm.tiles:
		if (tile.building != None):
			tile.building.Update()
	
''' USER METHODS '''
