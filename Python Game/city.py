class City:
	def __init__(self):
		self.population = 0
		
		self.income = 0
		self.expense = 0
		self.bank = 500
		
		self.cityHall = None
		
		self.resDemand = 1
		self.comDemand = 1
		self.indDemand = 1

		self.averageHappiness = 0
	
	def Update(self):
	
		self.population = 0
		self.income = 0
		self.expense = 0
	
		from buildings import buildings
		for building in buildings.buildings:
			if (building.prefab.group.groupName == "Residential"):
				self.population += len(building.population)
				self.averageHappiness += building.averageHappiness
			self.averageHappiness /= len(buildings.buildings)

			self.income += building.income
			self.expense += building.expense
				
		self.expense += (0.001 * self.population)
	
	def CalculateBank(self):
		self.bank += (self.income - self.expense)
	
	def CalculateRCI(self):

		totalEmployed = 0
		numCommercial = 0
		numIndustrial = 0

		from buildings import buildings
		for building in buildings.buildings:
			if (building.prefab.group.groupName == "Residential"):
				totalEmployed += building.employed
			if (building.prefab.group.groupName == "Commercial"):
				numCommercial += 1
			if (building.prefab.group.groupName == "Industrial"):
				numIndustrial += 1
		
		employmentRate = 1
		commercialBuildingPopulationRatio = 1
		
		if (self.population > 0):
			employmentRate = totalEmployed / self.population

			commercialBuildingPopulationRatio = 1 - (numCommercial / self.population)
		
		demandHappiness = self.averageHappiness
		if (demandHappiness <= 0.5):
			demandHappiness = 0.5
		self.resDemand = employmentRate * demandHappiness

		self.comDemand = commercialBuildingPopulationRatio
		
		self.indDemand = 1

		if (numIndustrial > 0):
			indEmploymentRate = employmentRate
			if (employmentRate < 0.5):
				indEmploymentRate = 1 - employmentRate
			if (numCommercial > 0):
				self.indDemand = indEmploymentRate * (numIndustrial / numCommercial)

	def DistributeUtilities(self):
		from buildings import buildings
		for building in buildings.buildings:
			if (building.prefab.group.groupName == "Residential"):
				for citizen in building.population:
					citizen.hasWater = False
					citizen.hasPower = False
		for building in buildings.buildings:
			if (building.prefab.group.groupName == "Water"):
				building.coveredBuildings.clear()
				self.DistributeWater(building)
			elif (building.prefab.group.groupName == "Power"):
				building.coveredBuildings.clear()
				self.DistributePower(building)


	def DistributeWater(self,building):

		currentTile = building.tile	
		checkedTiles = [currentTile]
		frontier = [currentTile]

		waterAmount = building.prefab.waterAmount * building.efficiency
		building.effectiveWaterAmount = waterAmount

		while (len(frontier) > 0 and waterAmount > 0):
			currentTile = frontier.pop(0)
			if (currentTile.building != None and currentTile.building.prefab.group.groupName == "Residential"):
				building.coveredBuildings.append(currentTile.building)
				for citizen in currentTile.building.population:
					if (citizen.hasWater == False):
						citizen.hasWater = True
						waterAmount -= 1
						if (waterAmount <= 0):
							return
			for surroundingTile in currentTile.surroundingTiles:
				if (surroundingTile != None):
					if (surroundingTile not in checkedTiles and surroundingTile.building != None and (surroundingTile.building.prefab.group.groupName == "Roads" or surroundingTile.building.prefab.group.groupName == "Residential")):
						frontier.append(surroundingTile)
						checkedTiles.append(surroundingTile)

	def DistributePower(self,building):
		currentTile = building.tile	
		checkedTiles = [currentTile]
		frontier = [currentTile]

		powerAmount = building.prefab.powerAmount * building.efficiency
		building.effectivePowerAmount = powerAmount

		while (len(frontier) > 0 and powerAmount > 0):
			currentTile = frontier.pop(0)
			if (currentTile.building != None and currentTile.building.prefab.group.groupName == "Residential"):
				building.coveredBuildings.append(currentTile.building)
				for citizen in currentTile.building.population:
					if (citizen.hasPower == False):
						citizen.hasPower = True
						powerAmount -= 1
						if (powerAmount <= 0):
							return
			for surroundingTile in currentTile.surroundingTiles:
				if (surroundingTile != None):
					if (surroundingTile not in checkedTiles and surroundingTile.building != None and (surroundingTile.building.prefab.group.groupName == "Roads" or surroundingTile.building.prefab.group.groupName == "Residential")):
						frontier.append(surroundingTile)
						checkedTiles.append(surroundingTile)

	def DistributeServices(self):
		policeBuildings = []
		fireBuildings = []
		healthBuildings = []
		from buildings import buildings
		for building in buildings.buildings:
			if (building.prefab.group.groupName == "Police"):
				building.coveredBuildings.clear()
				policeBuildings.append(building)
			elif (building.prefab.group.groupName == "Fire"):
				building.coveredBuildings.clear()
				fireBuildings.append(building)
			elif (building.prefab.group.groupName == "Health"):
				building.coveredBuildings.clear()
				healthBuildings.append(building)

		from gm import CalculatePointDistance
		from tiles import tm
		for building in buildings.buildings:
			if (building.prefab.group.groupName == "Residential"):
				for policeBuilding in policeBuildings:
					buildingRange = policeBuilding.prefab.range * policeBuilding.efficiency
					if (CalculatePointDistance(building.tile.position,policeBuilding.tile.position) <= buildingRange * tm.tileSize):
						building.policeCover = True
						policeBuilding.coveredBuildings.append(building)
						break
				for fireBuilding in fireBuildings:
					buildingRange = fireBuilding.prefab.range * fireBuilding.efficiency
					if (CalculatePointDistance(building.tile.position,fireBuilding.tile.position) <= buildingRange * tm.tileSize):
						building.fireCover = True
						fireBuilding.coveredBuildings.append(building)
						break
				for healthBuilding in healthBuildings:
					buildingRange = healthBuilding.prefab.range * healthBuilding.efficiency
					if (CalculatePointDistance(building.tile.position,healthBuilding.tile.position) <= buildingRange * tm.tileSize):
						building.healthCover = True
						healthBuilding.coveredBuildings.append(building)
						break

def Awake():
	global city
	city = City()
	
def Update():
	city.Update()