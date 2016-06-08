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
					
				groupName = tile.building.prefab.group.groupName
				if (groupName == "Residential"):
					self.income += len(tile.building.population) * tile.building.employed + (tile.building.landValue * 0.05)
				elif (groupName == "Commercial"):
					self.income += tile.building.employed
				elif (groupName == "Industrial"):
					self.income += tile.building.employed
				
				self.expense += tile.building.prefab.maintenanceBase
				
		from times import time
		if (self.bankTimer < 10):
			self.bankTimer += 1 * time.deltaTime
		else:
			self.CalculateBank()
			self.bankTimer = 0
	
	def CalculateBank(self):
		self.bank += (self.income - self.expense)
		
	def CalculateRCI(self):
	
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