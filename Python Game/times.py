import pygame
from pygame.locals import *

class TimeManager:
	def __init__(self):
		self.deltaTime = 0
		self.clock = pygame.time.Clock()
		
		self.dayTimer = 0
		self.day = 0
		self.month = 0
		self.year = 0
	
	def Update(self):
	
		self.deltaTime = self.clock.tick() / 1000
		
		if (self.dayTimer < 1):
			self.dayTimer += 1 * self.deltaTime
		else:
			self.day += 1
			self.dayTimer = 0
			if  (self.day > 30):
				self.month += 1
				self.day = 0

				from city import city
				city.CalculateBank()

				if (self.month > 12):
					self.year += 1
					self.month = 0

def Awake():
	global time
	time = TimeManager()
	
def Update():
	time.Update()