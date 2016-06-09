class City:
	def __init__(self):
		self.population = 0
		
		self.income = 0
		self.expense = 0
		self.bank = 10000
		
		self.cityHall = None
		
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
				if (tile.building.prefab.group.groupName == "Residential"):
					self.population += len(tile.building.population)

				self.income += tile.building.income
				self.expense += tile.building.expense
				
		self.expense += (0.001 * self.population)
	
	def CalculateBank(self):
		self.bank += (self.income - self.expense)
	
	def CalculateRCI(self):

		totalEmployed = 0
		numCommercial = 0
		numIndustrial = 0

		from tiles import tm
		for tile in tm.tiles:
			if (tile.building != None):
				if (tile.building.prefab.group.groupName == "Residential"):
					totalEmployed += tile.building.employed
				if (tile.building.prefab.group.groupName == "Commercial"):
					numCommercial += 1
				if (tile.building.prefab.group.groupName == "Industrial"):
					numIndustrial += 1
		
		employmentRate = 1
		commercialBuildingPopulationRatio = 1
		
		if (self.population > 0):
			employmentRate = totalEmployed / self.population

			commercialBuildingPopulationRatio = 1 - (numCommercial / self.population)

		self.resDemand = employmentRate

		self.comDemand = commercialBuildingPopulationRatio
		
		self.indDemand = 1

		if (numIndustrial > 0):
			indEmploymentRate = employmentRate
			if (employmentRate < 0.5):
				indEmploymentRate = 1 - employmentRate
			self.indDemand = indEmploymentRate * (numIndustrial / numCommercial)

def Awake():
	global city
	city = City()
	
def Update():
	city.Update()