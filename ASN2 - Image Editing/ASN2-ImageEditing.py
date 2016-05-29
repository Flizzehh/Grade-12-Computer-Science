imageFile = open('lol.txt')
imageFileLines = imageFile.split('\n')
imageSize = [imageFileLines[1].split(' ')[0],imageFileLines[1].split(' ')[0]]

for i in range(3,len(imageFileLines)):
	print(imageFileLines[i])