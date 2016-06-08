class City:
	def __init__(self):
		self.population = 0
		
		self.income = 0
		self.expense = 0
		self.bank = 10000
		
		self.cityHall = None
		
		self.bankTimer = 0
		
		self.resDemand = 1
		self.comDemand = 1
		self.indDemand = 1
	
	def Update(self):
	
		self.population = 0
		self.income = 0
		self.expense = 0
	
		from tiles import tm
		for tile in tm.tiles:
			if (tile.building != None):
				self.population += len(tile.building.population)

				self.income += tile.building.income
				self.expense += tile.building.prefab.maintenanceBase
				
		self.expense += (0.001 * self.population)

		from times import time
		if (self.bankTimer < 10):
			self.bankTimer += 1 * time.deltaTime
		else:
			self.CalculateBank()
			self.bankTimer = 0
	
	def CalculateBank(self):
		self.bank += (self.income - self.expense)
		
	def CalculateRCI(self):

		averageComEmployedRatio = 0
		numComBuildings = 0
		comWorkers = 0

		from tiles import tm
		for tile in tm.tiles:
			if (tile.building != None):
				if (tile.building.prefab.group.groupName == "Residential"):
					pass
				elif (tile.building.prefab.group.groupName == "Commercial"):
					numComBuildings += 1
					averageComEmployedRatio += (len(tile.building.population)/tile.building.prefab.maxPopulation)
					comWorkers += len(tile.building.population)
		
		self.comDemand = 1
		if (numComBuildings > 0 and comWorkers > 0):
			averageComEmployedRatio /= numComBuildings
			self.comDemand = ((self.population / (numComBuildings * (comWorkers * 3))) + averageComEmployedRatio) / 2

		# self.comDemand = 1
		# if (numComBuildings > 0):
		# 	averageComEmployedRatio /= numComBuildings
		# 	if (comWorkers > 0):
		# 		self.comDemand = (averageComEmployedRatio + (self.population/(numComBuildings*comWorkers)))/2

		self.resDemand = 1
		self.indDemand = 1

	def OLD_CalculateRCI(self):
	
		from tiles import tm
	
		employedCitizens = 0
		unemploymentRate = 0
		
		averageLandValue = 0
		
		numBuildings = 0
		numRes = 0
		numCom = 0
		numInd = 0
		
		for tile in tm.tiles:
			if (tile.building != None):
				employedCitizens += tile.building.employed
				numBuildings += 1
				if (tile.building.prefab.group.groupName == "Residential"):
					averageLandValue += tile.building.landValue
					numRes += 1
				elif (tile.building.prefab.group.groupName == "Commercial"):
					numCom += 1
				elif (tile.building.prefab.group.groupName == "Industrial"):
					numInd += 1
		if (numBuildings != 0 and self.population != 0):
			averageLandValue /= numBuildings
			unemploymentRate = 1 - (employedCitizens / self.population)
			self.resDemand = (unemploymentRate + averageLandValue) / 2
			
		if (numRes != 0):
			inverseResComRatio = 1 - (numCom / numRes)
			self.comDemand = (unemploymentRate + inverseResComRatio) / 2
			
		comIndRatio = 0
		if (numCom != 0):
			comIndRatio = numInd / numCom
			if (comIndRatio != 0):
				self.indDemand = unemploymentRate / comIndRatio
		

def Awake():
	global city
	city = City()
	
def Update():
	city.Update()