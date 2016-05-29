import random

def GetInput(message):
	return input(message)

def CheckInput():
	chosenRoom = GetInput("Choose the left room or the right room. l/r ")
	dragonRoom = random.randint(0,1)
	if (chosenRoom == "l" and dragonRoom == 0):
		return False
	elif (chosenRoom == "r" and dragonRoom == 1):
		return False
	else:
		return True

def Checkpoints():
	playerAlive = CheckInput()
	print(playerAlive)
	if (playerAlive):
		print("You found the friendly dragon! He lets you pass unharmed. ")
		CheckInput()
	else:
		print("You found the hungry dragon! ")
		playerContinue = GetInput("Would you like to try again? y/n ")
		if (playerContinue == "y"):
			return True
		else:
			return False

while (True):
	Checkpoints()