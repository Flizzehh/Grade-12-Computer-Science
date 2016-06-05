import pygame
from pygame.locals import *

class TimeManager:
	def __init__(self):
		self.deltaTime = 0
		self.clock = pygame.time.Clock()
	
	def Update(self):
	
		self.deltaTime = self.clock.tick() / 1000

def Awake():
	global time
	time = TimeManager()
	
def Update():
	time.Update()