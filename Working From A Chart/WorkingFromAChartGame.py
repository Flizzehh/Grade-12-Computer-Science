import random

class Weapon():
	def __init__(self, name, damage, durability):
		self.name = name
		self.damage = damage
		self.durability = durability
		
	def ChangeDurability(self, durabilityDelta):
		durability += durabilityDelta

class Player():
	def __init__(self, health):
		self.health = health
		self.inventory = [Weapon("Sword",10,100)]
		self.visitedRooms = []
		for i in range(len(roomList.roomList)):
			self.visitedRooms.append(0)
		self.ChangeRoom(0,False)
		self.forward = True
		self.validRooms = self.room.followingRooms
	
	def ChangeHealth(self, healthDelta):
		self.health += healthDelta
	
	def AddWeapon(self, weapon):
		self.inventory.append(weapon)
		
	def Attack(self, enemy, weapon):
		attackSuccess = random.randint(1,10)
		enemy.ChangeHealth((weapon.damage / 2) * (5/attackSuccess))
		weapon.ChangeDurability(10/attackSuccess)
		
	def ChangeRoom(self, roomValue, update = True):
		self.visitedRooms[roomValue] += 1
		self.room = roomList.FindRoomFromValue(roomValue)
		if (update):
			UpdateStatus()
	
class Enemy():
	def __init__(self, name, health):
		self.name = name
		self.health = health
		self.inventory = [Weapon("Fist",3,100)]
		
	def ChangeHealth(self, healthDelta):
		self.health += healthDelta

class Room():
	def __init__(self, value, numGlobalRooms):
		self.value = value	
		self.followingRooms = []
		self.precedingRooms = []		
		for i in range(1,random.randint(2,4)):
			if (value + i <= numGlobalRooms-1):
				self.followingRooms.append(value + i)
		for i in range(1,random.randint(2,4)):
			if (value - i >= 0):
				self.precedingRooms.append(value - i)	
		self.enemies = []
		if (value != 0):
			self.enemies.append(Enemy("Zombie",25))	
		self.look = ""
		if (random.randint(0,100) < 50):
			self.look += "wet atrium. There are vines growing down from a small hole in the ceiling where the light of the sun shines through in powerful rays to the ground. You hear the constant dripping of water echo from the large walls."
			if (len(self.enemies) > 0):
				self.look += " The low moans of some "+self.enemies[0].name+"s rumble in the darkness."
		else:
			self.look += "long twisting tunnel through the cavern. You hear the pitter-patter of spiders and centipedes crawling along the walls."
		
class RoomList():	
	def __init__(self):
		self.roomList = []
	
	# Takes in a room object and adds it to the list of rooms if it does not exist there yet
	def AddRoom(self, room):
		if (room not in self.roomList):
			self.roomList.append(room)
	
	def FindRoomFromValue(self, value):
		return self.roomList[value]

def UpdateStatus():
	status = player.room.look
	if (len(player.room.enemies) > 0):
		status += " There looks to be about "+str(len(player.room.enemies))+" of them."
	if (player.visitedRooms[player.room.value] == 2):
		status += " This place looks familiar."
	elif (player.visitedRooms[player.room.value] >= 3):
		status += " You feel like you're walking in circles."
	player.validRooms = []
	if (player.forward):
		player.validRooms = player.room.followingRooms
	else:
		player.validRooms = player.room.precedingRooms
	if (len(player.validRooms) > 0):
		status += " You can see a hallway "
		for i in range(len(player.validRooms)):
			if (i == 0):
				status += "straight ahead"
			elif (i == 1):
				if (len(player.validRooms) == 2):
					status += ", and"
				else:
					status += ","
				status += " to your left"
			elif (i == 2):
				status += ", and to your right"
	else:
		status += " There's nowhere to go."
	status += "."
	print("You find yourself in a "+status);
	GetPlayerInput()
		
def GetPlayerInput():
	playerInput = input("What do you do?")
	print("> "+playerInput)
	EvaluatePlayerInput(playerInput)
	
def EvaluatePlayerInput(playerInput):
	if (playerInput == "help"):
		print("You can 'go straight', 'go left', 'go right', 'check inventory', 'examine room', 'turn around'")
	elif (playerInput == "go straight"):
		if (len(player.validRooms) > 0):
			player.ChangeRoom(player.validRooms[0])
		else:
			print("You can't go straight")
	elif (playerInput == "go left"):
		if (len(player.validRooms) > 1):
			player.ChangeRoom(player.validRooms[1])
		else:
			print("You can't go left.")
	elif (playerInput == "go right"):
		if (len(player.validRooms) > 2):
			player.ChangeRoom(player.validRooms[2])
		else:
			print("You can't go right.")
	elif (playerInput == "check inventory"):
		inventoryItems = "In your bag you find "
		for i in range(len(player.inventory)):
			item = player.inventory[i]
			inventoryItems += "a "+item.name
			if (i == len(player.inventory)-1 and len(player.inventory) > 1):
				inventoryItems +", "
		print(inventoryItems+".")
	elif (playerInput == "turn around"):
		if (player.forward):
			player.forward = False
		else:
			player.forward = True
		orientation = "You turn around. You are now facing "
		if (player.forward):
			orientation += "forwards."
		else:
			orientation += "backwards."
		print(orientation)
		return UpdateStatus()
	else:
		print("The action "+playerInput+" is unknown.")
	GetPlayerInput()
		
roomList = RoomList()
lastRoomValue = -1
numGlobalRooms = random.randint(10,20)
while (len(roomList.roomList) < numGlobalRooms):
	roomList.AddRoom(Room(lastRoomValue + 1,numGlobalRooms))
	lastRoomValue += 1	
player = Player(100)
UpdateStatus()