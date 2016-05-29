class Node:
	# Initialize a node
	def __init__(self,value):
		self.value = value
		self.parentNode = None
		self.greaterChild = None
		self.lesserChild = None
		self.depth = 1	
		
	def __str__(self):
		return str(self.value)	
		
class Tree:
	# Initialize the tree
	def __init__(self,nodeValues):
		# Add the first node of the tree with a depth of 0
		self.firstNode = Node(nodes.pop(0))
		self.firstNode.depth = 0
		
		# Add the rest of the nodes in the list of nodes
		for nodeValue in nodeValues:
			self.AddNode(nodeValue)
				
	# Add a new node to the tree given a value
	def AddNode(self,newValue):
		# Creates a new node object from the value given
		newNode = Node(newValue)
		
		# Selects the first node of the tree to be the starting point
		currentNode = self.firstNode
		
		# Loops through until the new node has found a place to go
		while (True):
			# If the new node is less than the current node, go to the left (lesser) position
			if (newNode.value < currentNode.value):
				# If a node exists in that position, select that node as the currently selected node
				if (currentNode.lesserChild != None):
					currentNode = currentNode.lesserChild
					newNode.depth += 1
				# If a node DOES NOT exist in that position, put the new node there
				else:			
					newNode.parentNode = currentNode
					currentNode.lesserChild = newNode
					return
			# If the new node is greater than or equal to the current node, go to the right (greater) position
			else:
				# If a node exists in that position, select that node as the currently selected node
				if (currentNode.greaterChild != None):
					currentNode = currentNode.greaterChild
					newNode.depth += 1
				# If a node DOES NOT exist in that position, put the new node there
				else:
					newNode.parentNode = currentNode
					currentNode.greaterChild = newNode
					return
	
	# Finds the node object in the tree from a given value using the Depth First Search
	def FindNodeFromValue(self,value):
		# Stores the nodes which have been checked already
		checkedNodes = []
		
		# Stores the first node in the tree initially and considers it checked
		currentNode = self.firstNode
		checkedNodes.append(currentNode)
		
		# Loops through until the node has been found or all nodes have been checked
		while (True):
		
			# Returns the currently selected node if it's value is the target value
			if (currentNode.value == value):
				return currentNode
				
			# If the smaller node exists and hasn't been checked, make it the currently selected node
			if (currentNode.lesserChild != None and currentNode.lesserChild not in checkedNodes):
				currentNode = currentNode.lesserChild
			else:
				# If the larger node exists and hasn't been checked, make it the currently selected node
				if (currentNode.greaterChild != None and currentNode.greaterChild not in checkedNodes):
					currentNode = currentNode.greaterChild
				# If both nodes don't exist or have been checked already, go back to the parent
				else:
					if (currentNode.parentNode != None):
						currentNode = currentNode.parentNode
						
			# Adds the currently selected node to the list of checked nodes if it hasn't already been checked
			if (currentNode not in checkedNodes):
				checkedNodes.append(currentNode)
				
			# If the search has gone through all nodes without finding the target value, return None
			if (currentNode == self.firstNode and currentNode.lesserChild in checkedNodes and currentNode.greaterChild in checkedNodes):
				return None
	
	# Calculates the distance between two nodes in the tree given the values of the nodes
	def DistanceBetweenNodes(self,firstValue,secondValue):
		# Find the tree nodes associated with each given value
		firstNode = self.FindNodeFromValue(firstValue)
		secondNode = self.FindNodeFromValue(secondValue)
		
		# Checks to ensure that both nodes do exist, return -1 if not
		if (firstNode == None or secondNode == None):
			return -1
		
		# Initialize the list of parents of the first node, automatically including the first node itself within it
		firstNodeParents = [firstNode]
		
		# Stores the deepest common parent of both nodes
		deepestCommonParent = None
		
		# Loops to create a list of the parent nodes of the first node
		currentNode = firstNode
		while(currentNode.parentNode != None):
			firstNodeParents.append(currentNode.parentNode)
			currentNode = currentNode.parentNode
			
		# Loops to find the deepest common parent of both nodes
		currentNode = secondNode
		while(True):
			continueSearch = True
			
			# Loops through all parents of the first node
			for node in firstNodeParents:
				# Checks if the currently selected second node parent is within the list of first node parents (the deepest common parent)
				if (node == currentNode):
					deepestCommonParent = node
					continueSearch = False
					break
					
			# Stops the search when the deepest common parent was found and calculates/returns the distance
			if (continueSearch == False):
				# Calculates the distance between the nodes by adding the depth of each node subtracted by the deepest common parent's depth
				distance = (firstNode.depth - deepestCommonParent.depth) + (secondNode.depth - deepestCommonParent.depth)	
				# Returns the final calculated distance
				return distance
				
			# Sets the currently selected node to be the parent of the currently selected node (working through the second node's parents)
			else:		
				if (currentNode.parentNode != None):
					currentNode = currentNode.parentNode
				else:
					break
					
	# Recursively prints a node and all of it's children in order from smallest to largest
	def PrintNodes(self,node):
		if (node != None):
			self.PrintNodes(node.lesserChild)
			print("V: " + str(node.value) + " - P: " + str(node.parentNode) + " - D: " + str(node.depth))
			self.PrintNodes(node.greaterChild)

# Setup
nodes = [0,1,2,3,4,5,6,1919,432,324,321,32,23,7,65,476,58,6755,-1,-532,-688,-123,-5]
tree = Tree(nodes)
tree.PrintNodes(tree.firstNode)
print(tree.DistanceBetweenNodes(-5,432))