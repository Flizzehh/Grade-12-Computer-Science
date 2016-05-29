import random

def ShowIntroduction():
	print("> Choose one of the two caves. Careful not to choose the one with the hungry dragon inside!")
	state = ChooseCave()
	if (state != None):
		RestartGame(state)
	else:
		ChooseCave()
	
def ChooseCave():
	dragonRoom = (random.randint(0,1))
	caveChosen = input("Choose the 'left' or 'right' cave").lower()
	if (caveChosen == "left" or caveChosen == "right"):
		if (caveChosen == "left" and dragonRoom == 0):
			return False
		elif (caveChosen == "right" and dragonRoom == 1):
			return False
		else:
			return False
	else:
		return None

def RestartGame(alive):
	if (alive):
		print("> You found the friendly dragon!")
		playAgain = input("Continue? 'yes' or 'no'").lower()
		if (playAgain == "yes"):
			ChooseCave()
		else:
			print("> Game Over!")
	else:
		print("> The hungry dragon ate you!")
		tryAgain = input("Try again? 'yes' or 'no'").lower()
		if (tryAgain == "yes"):
			ShowIntroduction()
		else:
			print("> Game Over!")
			
ShowIntroduction()