import matplotlib.pyplot as plt, math, numpy as np, matplotlib.patches as patches

# Ryan White

# Stores the data for each individual person
class Person ():
	def __init__(self,line):
		# Check if the data can be transferred into a value, and do so if it can be
		lineData = []
		for item in line.split(" "):
			try:
				lineData.append(float(item))
			except:
				continue
		
		# Skeletal Measurements
		self.biacromialDiameter = float(lineData[0])
		self.biiliacDiameter = float(lineData[1])
		self.bitrochantericDiameter = float(lineData[2])
		self.chestDepth = float(lineData[3])
		self.chestDiameter = float(lineData[4])
		self.elbowDiameter = float(lineData[5])
		self.wristDiameter = float(lineData[6])
		self.kneeDiameter = float(lineData[7])
		self.ankleDiameter = float(lineData[8])
		
		# Girth Measurements
		self.shoulderGirth = float(lineData[9])
		self.chestGirth = float(lineData[10])
		self.waistGirth = float(lineData[11])
		self.navelGirth = float(lineData[12])
		self.hipGirth = float(lineData[13])
		self.thighGirth = float(lineData[14])
		self.bicepGirth = float(lineData[15])
		self.forearmGirth = float(lineData[16])
		self.kneeGirth = float(lineData[17])
		self.calfGirth = float(lineData[18])
		self.ankleGirth = float(lineData[19])
		self.wristGirth = float(lineData[20])
		
		# Other Measurements
		self.age = float(lineData[21])
		self.weight = float(lineData[22])
		self.height = float(lineData[23])
		self.gender = float(lineData[24])
		self.BMI = CalculateBMI(self.weight,self.height)
		self.newBMI = CalculateNewBMI(self.chestDiameter,self.chestDepth,self.bitrochantericDiameter,self.wristGirth,self.ankleGirth,self.height)


# Stores the list of people, and the temporary x and y lists of data
people, x, y = [], [], []

# Generate a list of people and graph their data
def GeneratePeople():
	# Parse the body data
	for line in open("body.dat",'r'):
		people.append(Person(line))
		
	# Generate graph between original BMI and age
	for i in range(len(people)):
		person = people[i]
		x.append(person.age)
		y.append(person.BMI)
	GenerateGraph("",x,"",y,'ro','r')

	# Generate graph between weight and combination of physical attributes (newBMI)
	for i in range(len(people)):
		person = people[i]
		x.append(person.weight)
		y.append(person.newBMI)
	GenerateGraph("",x,"",y,'bo','b')

	# Generate the legend
	CreateLegendItem("BMI","red","Age","BMI")
	CreateLegendItem("New BMI","blue","Weight","New BMI")

	# Show the graphs
	plt.show()

# Stores the list of legend items
legendHandles = []
# Create a single legend item and update the legend
def CreateLegendItem(name,colour,xAxis,yAxis):
	# Create the legend item and add it to the list of legend items
	legendHandles.append(patches.Patch(color=colour, label=name + " (" + xAxis + " vs. " + yAxis + ")"))
	
	# Update the legend
	plt.legend(handles=legendHandles)

# Create a graph of the data
def GenerateGraph(xName, x, yName, y, pointColour, lineColour):
	# Calculate the values for calculating slope, intercept, and correlation
	sumX = sum(x)
	sumY = sum(y)
	sumXY = SumXY(x,y)
	sumXSquared = SumSquared(x)
	sumYSquared = SumSquared(y)
	n = len(x)
	
	# Calculate the slope and intercept of the data for the least squares line
	slope = CalculateSlope(sumX,sumY,sumXY,sumXSquared,n)
	intercept = CalculateItercept(sumX,sumY,n,slope)
	
	# Calculate the correlation of the data
	correlation = CalculateCorrelation(sumX,sumY,sumXY,sumXSquared,sumYSquared,n)
	print(correlation)
	
	# Using the slope, intercept, and x-values, create a list of corresponding y-values of the least squares line
	lineValues = []
	for i in x:
		lineValues.append(slope * i + intercept)
	
	# Plot the points of the data
	plt.plot(x,y,pointColour)
	
	# Plot the least squares line of the data
	plt.plot(x,lineValues,lineColour)
	
	# Clear the data
	x.clear()
	y.clear()

# Calculate the sum of all the products of each corresponding x, y pair
def SumXY(x,y):
	values = []
	for i in range(len(x)):
		values.append(x[i] * y[i])
	return sum(values)
		
# Calculate the sum of the square of every value
def SumSquared(values):
	returnList = []
	for number in values:
		returnList.append(math.pow(number,2))
	return sum(returnList)
	
# Calculate the correlation of the data
def CalculateCorrelation(sumX, sumY, sumXY, sumXSquared, sumYSquared, n):
	return (n * sumXY - (sumX * sumY)) / math.sqrt((n * sumXSquared - math.pow(sumX,2)) * (n * sumYSquared - math.pow(sumY,2)))
	
# Calculate the slope of the line which best matches the data
def CalculateSlope(sumX,sumY,sumXY,sumXSquared,n):
	return (n * sumXY - (sumX * sumY)) / (n * sumXSquared - math.pow(sumX,2))
	
# Calculate the intercept of the line which best matches the data
def CalculateItercept(sumX,sumY,n,slope):
	return (sumY - (slope * sumX)) / n
	
# Calculate the BMI of a person
def CalculateBMI(weight,height):
	return weight / math.pow(height/100,2)

# Calculate the New BMI of a person
def CalculateNewBMI(chestDiameter,chestDepth,bitrochantericDiameter,wristGirth,ankleGirth,height):
	return -110 + (1.34 * chestDiameter) + (1.54 * chestDepth) + (1.20 * bitrochantericDiameter) + (1.11 * wristGirth) + (1.15 * ankleGirth) + (0.177 * height)

GeneratePeople()