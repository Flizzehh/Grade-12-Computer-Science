import math

# Ryan White
# 19-Feb-2016

# Words in variables start lower-case, each following word starts upper-case. eg: "ingredientsToAdd"
# Words in methods always start upper-case. eg: "ReadList"

# Stores a list of all stored ingredients
# Provides methods to modify/analyze the list
class IngredientsList:

	# Master list of ingredients
	ingredients = []
	
	# When the list is initializes, takes in a list of initial ingredients to add
	def __init__(self, addIngredients):
		self.ReadList(addIngredients)
	
	# Takes in an Ingredient object.
	# Adds the object to the list of ingredients.
	def Add(self, ingredient):
		self.ingredients.append(ingredient)
		
	# Takes in the name of an Ingredient. Returns the calorie count per 100g of the ingredient.
	# Return a None type if it does not find it.
	def Find(self, findIngredientName):
	
		for ingredient in self.ingredients:
			if (ingredient.name == findIngredientName):
				return ingredient.calorieCount
		return None
		
	# Takes in a list of ingredients in the format: "ingredientName caloriesPer100g"
	# Creates the Ingredient object and adds it to the list of ingredients.
	def ReadList(self, ingredientsToAdd):
		for newIngredient in ingredientsToAdd:
			self.Add(Ingredient(newIngredient.split(' ')[0],newIngredient.split(' ')[1]))
	
	# Takes in a list of ingredients (recipe) in the format: "ingredientName ingredientGrams"
	# Returns the amount of calories in the recipe
	def Count(self, recipe):
		totalCalories = 0
		for ingredient in recipe:
			ingredientCalories = self.Find(ingredient.split(' ')[0])
			if (ingredientCalories != None):
				totalCalories += ingredientCalories * (int(ingredient.split(' ')[1]) / 100)
		return round(totalCalories,2)

# Stores the properties of each ingredient
class Ingredient:
	name = ""
	calorieCount = 0
	def __init__(self, name, calorieCount):
		self.name = name
		self.calorieCount = float(calorieCount)
		
# Initializes the variable which stores the master ingredient list object
ingredientList = None

# Initializes the master ingredient list object using the master ingredients file
def Main():
	# Open master ingredients file
	lineList = open("table.dat",'r')

	# Create ingredients list andn add ingredients to the list
	ingredientList = IngredientsList(lineList)

	# Close master ingredients file
	lineList.close()
	
	
Main()