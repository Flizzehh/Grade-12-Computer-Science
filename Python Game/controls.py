import pygame
from pygame.locals import *
from gm import Quit


def Awake():
	global camera
	from tiles import camera
	
def Update():
	SmoothCamera()
	ChangeTimeSpeed()

def GetInput(event):
	if event.type == pygame.KEYDOWN:
		if (event.key == pygame.K_ESCAPE):
			Quit()

		if (pygame.key.get_pressed()[K_LSHIFT]):
			if (event.key == pygame.K_w):
				camera.ChangePosition((0,1))
			if (event.key == pygame.K_s):
				camera.ChangePosition((0,-1))
			if (event.key == pygame.K_a):
				camera.ChangePosition((1,0))
			if (event.key == pygame.K_d):
				camera.ChangePosition((-1,0))
			
	from ui import ui
	if (pygame.mouse.get_pressed()[0]):
		ui.mouseDown = True
	else:
		ui.mouseDown = False
	if (pygame.mouse.get_pressed()[2]):
		if (ui.selectedBuilding == None):
			ui.selectedGroup = None
		ui.selectedBuilding = None
		
def SmoothCamera():
	cameraSpeed = 10
	from times import time
	pressedKeys = pygame.key.get_pressed()
	if (pressedKeys[pygame.K_w]):
		camera.ChangePosition((0,cameraSpeed * time.deltaTime))
	if (pressedKeys[pygame.K_s]):
		camera.ChangePosition((0,-cameraSpeed * time.deltaTime))
	if (pressedKeys[pygame.K_a]):
		camera.ChangePosition((cameraSpeed * time.deltaTime,0))
	if (pressedKeys[pygame.K_d]):
		camera.ChangePosition((-cameraSpeed * time.deltaTime,0))

def ChangeTimeSpeed():
	from times import time
	pressedKeys = pygame.key.get_pressed()
	if (pressedKeys[pygame.K_1]):
		time.timeMulti = 1
	if (pressedKeys[pygame.K_2]):
		time.timeMulti = 2
	if (pressedKeys[pygame.K_3]):
		time.timeMulti = 3