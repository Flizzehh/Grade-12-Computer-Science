import pygame, math
from pygame.locals import *

class Screen:
	def __init__(self):
		displayInfo = pygame.display.Info()
		self.width = displayInfo.current_w
		self.height = displayInfo.current_h

class UI:
	def __init__(self):
	
		self.mousePos = pygame.mouse.get_pos()
	
		self.panels = []
		self.updatePanels = []
		self.buttons = []
		self.updateButtons = []
		self.texts = []
		self.updateTexts = []
		self.menus = []
		
		self.uiSurface = pygame.display.set_mode((screen.width,screen.height),pygame.FULLSCREEN)
		
		self.AddUI()
		
		self.mouseDown = False
		self.mouseOverUI = False
		
		self.selectedGroup = None
		self.selectedBuilding = None
		
		self.mouseOverTile = None
		
	def AddUI(self):
	
		global cityPanelSize
		cityPanelPosition = (10,10)
		cityPanelSize = (100,100)
		self.AddPanel(Panel(cityPanelPosition,cityPanelSize,(255,255,255),5,(200,200,200)))	
		global cityTextPosition
		cityTextPosition = (cityPanelPosition[0]+5,cityPanelPosition[1])
				
		self.AddText(Text(cityTextPosition,cityPanelSize,"Population","verdana",14,(50,50,50)))
		self.AddText(Text((cityTextPosition[0],cityTextPosition[1]+35),cityPanelSize,"Money","verdana",14,(50,50,50)))
		
		global buildingPanelPosition
		buildingPanelPosition = (cityPanelPosition[0]+cityPanelSize[0]+15,cityPanelPosition[1])
		global buildingTextPosition
		buildingTextPosition = (buildingPanelPosition[0]+5,buildingPanelPosition[1])
		
		global rciPanelPosition
		rciPanelPosition = (cityPanelPosition[0],cityPanelPosition[1]+cityPanelSize[1]+15)
		global rciTextPosition
		rciTextPosition = (rciPanelPosition[0]+5,rciPanelPosition[1])
		
		self.AddPanel(Panel(rciPanelPosition,(cityPanelSize[0],cityPanelSize[1]+10),(255,255,255),5,(200,200,200)))
		
		self.AddText(Text(rciTextPosition,cityPanelSize,"Demand","verdana",14,(50,50,50)))
		self.AddText(Text((rciTextPosition[0],rciTextPosition[1]+15),cityPanelSize,"Residential","verdana",12,(50,50,50)))
		self.AddText(Text((rciTextPosition[0],rciTextPosition[1]+45),cityPanelSize,"Commercial","verdana",12,(50,50,50)))
		self.AddText(Text((rciTextPosition[0],rciTextPosition[1]+75),cityPanelSize,"Industrial","verdana",12,(50,50,50)))
		
		global datePanelPosition
		datePanelPosition = (rciPanelPosition[0],rciPanelPosition[1]+cityPanelSize[1]+25)
		global dateTextPosition
		dateTextPosition = (datePanelPosition[0]+5,datePanelPosition[1])
		
		self.AddPanel(Panel(datePanelPosition,(cityPanelSize[0],cityPanelSize[1]-35),(255,255,255),5,(200,200,200)))
		
		self.AddText(Text(dateTextPosition,cityPanelSize,"Date","verdana",14,(50,50,50)))
		
		from buildings import buildingGroups
		print(len(buildingGroups.groups))
		
		buildingButtonNum = len(buildingGroups.groups)
		buildingButtonSize = (100,35)
		buildingPanelSize = (5+(buildingButtonSize[0]+5)*buildingButtonNum,buildingButtonSize[1]+10)
		
		buildingPanelRect = (screen.width/2-buildingPanelSize[0]/2,screen.height-buildingPanelSize[1]-10,buildingPanelSize[0],buildingPanelSize[1])
		self.AddPanel(Panel((buildingPanelRect[0],buildingPanelRect[1]),(buildingPanelRect[2],buildingPanelRect[3]),(255,255,255),5,(200,200,200)))
		
		for groupIndex in range(buildingButtonNum):
			group = buildingGroups.groups[groupIndex]
			
			buildingButtonPosition = (buildingPanelRect[0] + 5 + (groupIndex * (buildingButtonSize[0] + 5)),buildingPanelRect[1]+5)
			
			buildingButtonTextPosition = (buildingButtonPosition[0]+5,buildingButtonPosition[1])
			buttonText = Text(buildingButtonTextPosition,buildingButtonSize,group.groupName,"verdana",12,(200,200,200))
			
			button = Button(buildingButtonPosition,buildingButtonSize,buttonText,(50,50,50),(75,75,75),(100,100,100),group,None)
			
			self.AddButton(button)
			
			menuSize = (buildingButtonSize[0],len(group.buildings)*buildingButtonSize[1]+15)
			menuPanel = Panel((buildingButtonPosition[0],buildingButtonPosition[1]-menuSize[1]-5),(menuSize[0],menuSize[1]-15),(255,255,255),5,(200,200,200))
			menuButtons = []
			for buildingIndex in range(len(group.buildings)):
				building = group.buildings[buildingIndex]
				buttonPosition = (buildingButtonPosition[0],buildingButtonPosition[1]-(buildingButtonSize[1]*(buildingIndex+1))-(buildingButtonSize[1]-15))
				buttonText = Text(buttonPosition,buildingButtonSize,building.buildingType,"verdana",12,(200,200,200))
				menuButtons.append(Button(buttonPosition,buildingButtonSize,buttonText,(50,50,50),(75,75,75),(100,100,100),None,building))
			menu = Menu(group,menuPanel,menuButtons)
			self.menus.append(menu)
			button.menu = menu
		
	def AddUIUpdate(self):
		from city import city
		self.AddUpdateText(Text((cityTextPosition[0],cityTextPosition[1]+15),cityPanelSize,str(round(city.population)) + " Citizens","verdana",12,(50,50,200)))
		
		self.AddUpdateText(Text((cityTextPosition[0],cityTextPosition[1]+50),cityPanelSize,"$" + str(round(city.bank)),"verdana",12,(50,50,200)))
		self.AddUpdateText(Text((cityTextPosition[0],cityTextPosition[1]+65),cityPanelSize,"$" + str(round(city.income)) + " Income","verdana",12,(50,200,50)))
		self.AddUpdateText(Text((cityTextPosition[0],cityTextPosition[1]+80),cityPanelSize,"$" + str(round(city.expense)) + " Expense","verdana",12,(200,50,50)))	
		
		if (self.mouseOverTile != None and self.mouseOverTile.building != None and self.mouseOverTile.building.prefab.group.groupName != "Roads"):
			building = self.mouseOverTile.building
			self.AddUpdatePanel(Panel(buildingPanelPosition,(cityPanelSize[0]+25,cityPanelSize[1]),(255,255,255),5,(200,200,200)))
			self.AddUpdateText(Text(buildingTextPosition,cityPanelSize,building.prefab.buildingType,"verdana",14,(50,50,50)))
			if (building.prefab.group.groupName == "Residential"):
				self.AddUpdateText(Text((buildingTextPosition[0],buildingTextPosition[1]+45),cityPanelSize,"Information","verdana",14,(50,50,50)))
				self.AddUpdateText(Text((buildingTextPosition[0],buildingTextPosition[1]+15),cityPanelSize,str(len(building.population)) + "/" + str(int(building.prefab.maxPopulation)) + " Citizens","verdana",12,(50,50,200)))
				self.AddUpdateText(Text((buildingTextPosition[0],buildingTextPosition[1]+30),cityPanelSize,str(building.employed) + " Employed","verdana",12,(50,50,200)))
				self.AddUpdateText(Text((buildingTextPosition[0],buildingTextPosition[1]+60),cityPanelSize,"$" + str(round(building.income)) + " Income","verdana",12,(50,200,50)))
				self.AddUpdateText(Text((buildingTextPosition[0],buildingTextPosition[1]+75),cityPanelSize,"$" + str(round(building.expense)) + " Expense","verdana",12,(200,50,50)))
			elif (building.prefab.group.groupName != "Roads"):
				self.AddUpdateText(Text((buildingTextPosition[0],buildingTextPosition[1]+15),cityPanelSize,str(len(building.population)) + "/" + str(int(building.prefab.maxPopulation)) + " Employees","verdana",12,(50,50,200)))
				self.AddUpdateText(Text((buildingTextPosition[0],buildingTextPosition[1]+35),cityPanelSize,"Information","verdana",14,(50,50,50)))
				self.AddUpdateText(Text((buildingTextPosition[0],buildingTextPosition[1]+50),cityPanelSize,"$" + str(round(building.income)) + " Income","verdana",12,(50,200,50)))
				self.AddUpdateText(Text((buildingTextPosition[0],buildingTextPosition[1]+65),cityPanelSize,"$" + str(round(building.expense)) + " Expense","verdana",12,(200,50,50)))
		else:
			self.AddUpdateText(Text(buildingTextPosition,cityPanelSize,"Mouse over a building for more information.","verdana",10,(50,50,50)))
			
		self.AddUpdateText(Text((rciTextPosition[0],rciTextPosition[1]+30),cityPanelSize,str(round(city.resDemand * 100)) + "%","verdana",12,(0,150,0)))
		self.AddUpdateText(Text((rciTextPosition[0],rciTextPosition[1]+60),cityPanelSize,str(round(city.comDemand * 100)) + "%","verdana",12,(0,0,150)))
		self.AddUpdateText(Text((rciTextPosition[0],rciTextPosition[1]+90),cityPanelSize,str(round(city.indDemand * 100)) + "%","verdana",12,(255,127,0)))
		
		from times import time
		self.AddUpdateText(Text((screen.width-20,0),(0,0),str(round(time.clock.get_fps())),"verdana",12,(50,50,50)))
		
		self.AddUpdateText(Text((dateTextPosition[0],dateTextPosition[1]+15),cityPanelSize,str(time.day) + self.AddS(" Day",time.day),"verdana",12,(50,50,50)))
		self.AddUpdateText(Text((dateTextPosition[0],dateTextPosition[1]+30),cityPanelSize,str(time.month) + self.AddS(" Month",time.month),"verdana",12,(50,50,50)))
		self.AddUpdateText(Text((dateTextPosition[0],dateTextPosition[1]+45),cityPanelSize,str(time.year) + self.AddS(" Year",time.year),"verdana",12,(50,50,50)))
		
	def AddS(self,string,value):
		if (value != 1):
			return string + "s"
		else:
			return string
		
	def AddPanel(self,panel):
		self.panels.append(panel)
		
	def AddButton(self,button):
		self.buttons.append(button)
		
	def AddText(self,text):
		self.texts.append(text)
		
	def AddUpdateText(self,text):
		self.updateTexts.append(text)
		
	def AddUpdatePanel(self,panel):
		self.updatePanels.append(panel)
		
	def AddUpdateButton(self,button):
		self.updateButtons.append(button)
		
	def Update(self):
		
		self.updatePanels.clear()
		self.updateTexts.clear()
		self.updateButtons.clear()
		self.AddUIUpdate()
		
		self.mousePos = pygame.mouse.get_pos()
		
		self.mouseOverUI = False
	
		for panel in self.panels:
			self.DrawPanel(panel)
				
		for panel in self.updatePanels:
			self.DrawPanel(panel)
			
		for button in self.buttons:
			self.DrawButton(button)
				
		for button in self.updateButtons:
			self.DrawButton(button)	
		
		for text in self.texts:
			self.DrawText(text)
			
		for text in self.updateTexts:
			self.DrawText(text)
			
		for menu in self.menus:
			if (menu.enabled):
				self.DrawPanel(menu.panel)
				for button in menu.buttons:
					self.DrawButton(button)
			
	def MouseWithinBounds(self,bounds):
		if (self.mousePos[0] >= bounds[0] and self.mousePos[0] < bounds[2]+bounds[0] and self.mousePos[1] >= bounds[1] and self.mousePos[1] < bounds[3]+bounds[1]):
			return True
		return False
		
	def DrawPanel(self,panel):
		if (panel.borderThickness > 0):
				pygame.draw.rect(self.uiSurface,panel.borderColour,(panel.borderPosition)+(panel.borderSize))
			
		pygame.draw.rect(self.uiSurface,panel.colour,(panel.position)+(panel.size))
		
		if (self.MouseWithinBounds((panel.position)+(panel.size))):
			self.mouseOverUI = True
			
	def DrawText(self,text):
		self.uiSurface.blit(text.textObject,text.position)
		
	def DrawButton(self,button):
		
		if (button.menu != None and self.selectedGroup != button.group):
			button.menu.enabled = False
				
		from buildings import buildingGroups
			
		buttonColour = button.normalColour

		if (self.MouseWithinBounds((button.position)+(button.size)) and button.disabled == False):
			buttonColour = button.hoverColour
			
			if (button.menu != None):
				button.menu.enabled = True
			
			if (self.mouseDown):
				
				buttonColour = button.clickColour
				
				if (button.group != None):
					self.selectedGroup = button.group
					if (button.menu != None):
						button.menu.enabled = True
						self.DrawPanel(button.menu.panel)
						for button in button.menu.buttons:
							self.AddUpdateButton(button)
								
				elif (button.building != None):
					self.selectedBuilding = button.building
				
		from city import city
		if (city.cityHall == None and ((button.group != None and button.group.groupName != "City") or (button.building != None and button.building.buildingType != "City Hall"))):			
			button.disabled = True
		elif (city.cityHall != None):
			if ((button.group != None and button.group.groupName == "City") or (button.building != None and button.building.buildingType == "City Hall")):
				button.disabled = True
			else:
				button.disabled = False
				if (button.building != None and city.bank < button.building.cost):
					button.disabled = True
		
		if (button.disabled):
			buttonColour = (button.normalColour[0]/2,button.normalColour[1]/2,button.normalColour[2]/2)
			if ((ui.selectedGroup != None and ui.selectedGroup == button.group) or (ui.selectedBuilding != None and ui.selectedBuilding.buildingType == button.text.text)):
				ui.selectedBuilding = None
				ui.selectedGroup = None
				
		pygame.draw.rect(self.uiSurface,buttonColour,(button.position)+(button.size))
		if (button.text != None):
			self.uiSurface.blit(button.text.textObject,button.text.position)
			
		if (self.MouseWithinBounds((button.position)+(button.size))):
			self.mouseOverUI = True

class Panel:
	def __init__(self,position,size,colour,borderThickness,borderColour):
		self.position = position
		self.size = size
		
		self.colour = colour
		
		self.borderThickness = borderThickness
		self.borderPosition = (self.position[0]-self.borderThickness,self.position[1]-self.borderThickness)
		self.borderSize = (self.size[0]+(self.borderThickness*2),self.size[1]+(self.borderThickness*2))
		self.borderColour = borderColour

class Button:
	def __init__(self,position,size,text,normalColour,hoverColour,clickColour,group,building):
		self.position = position
		self.size = size
		
		self.text = text
		
		self.normalColour = normalColour
		self.hoverColour = hoverColour
		self.clickColour = clickColour
		
		self.disabled = False
		
		self.group = group
		self.building = building	
		self.menu = None

class Text:
	def __init__(self,position,size,text,font,fontSize,colour):
		self.position = position
		self.size = size
		
		self.text = text
		self.font = font
		self.fontSize = fontSize
		self.colour = colour
		
		self.textObject = pygame.font.SysFont(self.font,self.fontSize).render(self.text,1,self.colour)

class Menu:
	def __init__(self,id,panel,buttons):
		self.enabled = False
		self.id = id
		self.panel = panel
		self.buttons = buttons

def Awake():
	global screen
	screen = Screen()
	global ui
	ui = UI()
	
def Update():
	ui.Update()