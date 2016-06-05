class City:
	def __init__(self):
		self.population = 0
		
		self.income = 0
		self.expense = 0
		self.bank = 10000
		
		self.cityHall = None
		
		self.bankTimer = 0
	
	def Update(self):
	
		self.population = 0
		self.income = 0
		self.expense = 0
	
		from tiles import tm
		for tile in tm.tiles:
			if (tile.building != None):
				self.population += len(tile.building.population)
					
				buildingType = tile.building.prefab.buildingType
				if (buildingType == "Residential"):
					self.income += len(tile.building.population) * tile.building.employed + (tile.building.landValue * 0.05)
				elif (buildingType == "Commercial"):
					self.income += tile.building.employed
				elif (buildingType == "Industrial"):
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

def Awake():
	global city
	city = City()
	
def Update():
	city.Update()