import glob, os, random, math, sys, PIL, types
from PIL import Image, ImageFilter, ImageEnhance

# Defines enumerators used to easily identify different changable properties
class Filter: GaussianBlur, Color, Contrast, Rotate, NegateColor, Vignette, Banding, Grid, BlackAndWhite, Flip, Checkered, Pixellate = range(12)
class Negate: R, G, B, RG, RB, GB, RGB = range(7)	
class Orientation: Horizontal, Vertical = range(2)
class FittingType: Fill, Fit = range(2)
class BandType: Rectangular, Circular = range(2)
class FlipType: Horizontal, Vertical, Both = range(3)

# Stores the collage image and methods for adding images to itself
class Collage:
	
	def __init__(self,images,shuffle,maintainAspectRatio,fittingType):
	
		self.background = Image.new('RGB',(1000,1000),(255,255,255))
		
		if (shuffle):
			random.shuffle(images)
		
		# Defines the different regions of the collage, the indices of regions and sizes correspond
		self.regions = 	[(0,0),		(650,0),	(0,650),	(650,650)]
		self.sizes = 	[(650,650),	(350,650),	(650,350),	(350,350)]
		
		self.cimages = []
		for cimage in images:
			self.cimages.append(cimage)
			
			# Gets the new position and size of the image.
			imagePosition = self.regions.pop(0)
			imageSize = self.sizes.pop(0)
			
			cimage.position = imagePosition
			
			# Resizes the image
			cimage.Resize(imageSize[0],imageSize[1],maintainAspectRatio,fittingType)
			
			# Centers the image inside of it's new space and crops it to it's new size
			width,height = cimage.image.size
			
			left = ((width - imageSize[0])/2)
			top = ((height - imageSize[1])/2)
			right = ((width + imageSize[0])/2)
			bottom = ((height + imageSize[1])/2)
			
			imageCrop = (left,top,right,bottom)
			cimage.image = cimage.image.crop(imageCrop)

	def AddImages(self,images):
		
		for image in images:
			self.AddImage(image)
		
	def AddImage(self,cimage):
		
		# Add image to background (main collage image)
		self.background.paste(cimage.image,cimage.position)
	
	def Show(self):
		self.background.show()
	
# Stores an image and methods for modifying how the image looks
class CollageImage:
	
	# Takes in an image filename and opens the image from the directory
	def __init__(self,imageName):
		self.image = Image.open(imageName)
		self.position = None
		
	# Resizes an image into a given width and height.
	def Resize(self,width,height,maintainAspectRatio,fittingType):
		if (maintainAspectRatio):
			self.ResizeMaintainAspectRatio(width,height,fittingType)
		else:
			self.image = self.image.resize((width,height),PIL.Image.ANTIALIAS)
			
	# Resizes an image to fit in a given width and height while maintaining it's original aspect ratio
	def ResizeMaintainAspectRatio(self,width,height,fittingType):
		# Fills the image within the space (no blank borders)
		targetSize = min(self.image.size[0],self.image.size[1])
		targetNewSize = max(width,height)
		
		if (fittingType == FittingType.Fit): # Fits the image within the space (with borders)
			targetSize = max(self.image.size[0],self.image.size[1])
			targetNewSize = min(width,height)
			
		ratio = targetSize / targetNewSize

		newWidth = self.image.size[0] / ratio
		newHeight = self.image.size[1] / ratio
		
		self.Resize(math.ceil(newWidth),math.ceil(newHeight),False,fittingType)
		
	# Resize a region rather than the image
	def ResizeRegion(self,region,width,height,maintainAspectRatio,fittingType):
		tempImage = self.image
		self.image = region
		self.Resize(width,height,maintainAspectRatio,fittingType)
		region = self.image
		self.image = tempImage
		return region
		
	# Calculates the distance between two points on a 2D grid
	def CalculateDistanceFromPoints(self,pointx,pointy,centerx,centery):
		yd = (centery - pointy)
		xd = (centerx - pointx)
		return math.sqrt(math.pow(xd,2) + math.pow(yd,2))
		
	# Calculates the distance from an index location to the center of the image
	def CalculateDistanceFromIndex(self,index,width,height):
		yd = (height/2 - (math.floor(index/(width))))
		xd = (width/2 - (index%(width)))
		return math.sqrt(math.pow(xd,2) + math.pow(yd,2))
		
	# Calculate the amount that a pixel should change from the vignette
	# Function you can paste in desmos: f\left(x\right)=\frac{a}{\left(\left(b\cdot 100\right)\cdot \left(x-c\right)^4\right)+1}
	def CalculateVignettePercentage(self,distancePercentage,brightnessPercentage,strengthScale,startDistancePercentage):
		return brightnessPercentage/((strengthScale * 100) * math.pow(distancePercentage - startDistancePercentage,4) + 1)
	
	# Apply the vignette to the image
	def Vignette(self,brightnessPercentage,strengthScale,startDistancePercentage):
		
		# Get the list of pixels (tuples)
		pixelsRaw = self.image.getdata()
		outputPixels = []
		
		if  (startDistancePercentage > 1):
			startDistancePercentage = 1
		elif (startDistancePercentage < 0):
			startDistancePercentage = 0

		#startDistancePercentage = 1 - startDistancePercentage
		
		# Get the maximum distance for a pixel on the image
		maxDistance = self.CalculateDistanceFromPoints(self.image.size[0],self.image.size[1],(self.image.size[0]/2),(self.image.size[1]/2))
			
		index = 0
		for pixel in pixelsRaw:
			# Calculate the distance of the pixel from the center of the image as a percentage of the maximum distance a pixel can be from the center
			distancePercentage = self.CalculateDistanceFromIndex(index,self.image.size[0],self.image.size[1]) / maxDistance
			
			# Calculate the amount by which the pixel should be darkened based on the distance percentage
			if (distancePercentage <= startDistancePercentage):
				vignettePercentage = 1
			else:
				vignettePercentage = self.CalculateVignettePercentage(distancePercentage,brightnessPercentage,strengthScale,startDistancePercentage)
		
			# Apply the darkness amount to each component of the pixel
			outputPixel = round(pixel[0] * vignettePercentage),round(pixel[1] * vignettePercentage),round(pixel[2] * vignettePercentage)
			
			# Add the pixel to the new image
			outputPixels.append(outputPixel)
			index += 1
			
		# Overwrite the old image with the new image with the vignette applied
		self.image.putdata(outputPixels)
	
	# Inverts the components of a pixel depending on the negate setting selected
	def NegateColor(self,region,negate):
		pixelsRaw = region.getdata()
		outputPixels = []
		for pixel in pixelsRaw:
			newPixel = pixel
			if (negate == Negate.R):
				newPixel = (255-pixel[0],pixel[1],pixel[2])
			elif (negate == Negate.G):
				newPixel = (pixel[0],255-pixel[1],pixel[2])
			elif (negate == Negate.B):
				newPixel = (pixel[0],pixel[1],255-pixel[2])
			elif (negate == Negate.RG):
				newPixel = (255-pixel[0],255-pixel[1],pixel[2])
			elif (negate == Negate.RB):
				newPixel = (255-pixel[0],pixel[1],255-pixel[2])
			elif (negate == Negate.GB):
				newPixel = (pixel[0],255-pixel[1],255-pixel[2])
			elif (negate == Negate.RGB):
				newPixel = (255-pixel[0],255-pixel[1],255-pixel[2])
			else:
				return region
			outputPixels.append(newPixel)
		region.putdata(outputPixels)
		return region
		
	# Creates a progressive banding effect on the image
	def Banding(self,bandType,bandSize,filter,filterMulti,multipleSkip,orientation,reverse):
		newImage = Image.new('RGB',self.image.size,(255,255,255))
		
		# Clamps values to be 1 or greater (to prevent division by 0)
		if (bandSize < 1):
			bandSize = 1
		
		# Set the value to 1 when the banding is being reversed which affects the equation
		reverseMod = 0
		if (reverse):
			reverseMod = 1
		
		# Changes the algorithm depending on the banding type chosen
		if (bandType == BandType.Rectangular):
			# Reverses many of the function inputs depending on the orientation chosen
			if (orientation == Orientation.Vertical): # Vertical
				numBands = math.ceil(newImage.size[0]/bandSize)+1
				for bandIndex in range(numBands):
					# Remove a region of the image to be a single band
					region = self.image.crop((bandSize*(bandIndex-1),0,bandSize*bandIndex,self.image.size[1]))
					# Only applies banding to bands which are divisible by the multipleSkip value
					if (bandIndex % multipleSkip == 0):
						region = self.ApplyFilterToRegion(region,filter,(bandIndex-(2*bandIndex-(numBands+1))*reverseMod)*filterMulti)
					# Paste the filtered band back into the image
					newImage.paste(region,(bandSize*(bandIndex-1),0))
					
			elif (orientation == Orientation.Horizontal): # Horizontal
				numBands = math.ceil(newImage.size[1]/bandSize)+1
				for bandIndex in range(numBands):
					region = self.image.crop((0,bandSize*(bandIndex-1),self.image.size[0],bandSize*bandIndex))
					if (bandIndex % multipleSkip == 0):
						region = self.ApplyFilterToRegion(region,filter,(bandIndex-(2*bandIndex-(numBands+1))*reverseMod)*filterMulti)
					newImage.paste(region,(0,bandSize*(bandIndex-1)))
			self.image = newImage
			
		elif (bandType == BandType.Circular):
			pixelsRaw = self.image.getdata()
			outputPixels = []
			index = 0
			for pixel in pixelsRaw:
				pixelDistance = self.CalculateDistanceFromIndex(index,self.image.size[0],self.image.size[1])
				# Rounds the band to the nearest multiple of the bandSize value
				bandIndex = round(pixelDistance / bandSize + 1)
				newPixel = pixel
				if (bandIndex % multipleSkip == 0):
					newPixel = self.ApplyFilterToPixel(pixel,filter,(bandIndex * filterMulti))
				outputPixels.append(newPixel)
				index += 1
			self.image.putdata(outputPixels)
		
	
	
	# Create a grid of the same image and applies a progressive filter to each
	def Grid(self,horizontalSize,verticalSize,filter,filterMulti,reverse,maintainAspectRatio):
		newImage = Image.new('RGB',self.image.size,(255,255,255))
		
		# Clamps values to be 1 or greater (to prevent division by 0)
		if (horizontalSize < 1):
			horizontalSize = 1
		if (verticalSize < 1):
			verticalSize = 1
			
		# Gets the dimensions of the images in the grid
		horizontalImageSize = math.ceil(newImage.size[0]/horizontalSize)
		verticalImageSize = math.ceil(newImage.size[1]/verticalSize)
		
		# Reverses the filter equation if it is reversed
		reverseMod = ((horizontalSize-1)+(verticalSize-1))*filterMulti
		if (reverse):
			reverseMod = ((horizontalSize-1)+(verticalSize-1))*filterMulti
		
		# Loop through the grid values
		for y in range(verticalSize):
			for x in range(horizontalSize):
				region = self.image
				# Resize the image to the dimensions created above
				region = self.ResizeRegion(region,horizontalImageSize,verticalImageSize,maintainAspectRatio,0)
				# Apply the selected filter to the new image
				region = self.ApplyFilterToRegion(region,filter,reverseMod-((x+y)*filterMulti))
				# Paste the new smaller image into the bigger image
				newImage.paste(region,(x*horizontalImageSize,y*verticalImageSize))
		self.image = newImage
	
	# Makes an image black and white
	def BlackAndWhite(self,region):
		pixelsRaw = region.getdata()
		outputPixels = []
		for pixel in pixelsRaw:
			# Rounds the component to either 0 or 255
			newComponent = round(sum(pixel)/3/255)*255
			# Creates the pixel tuple with the same value for RGB
			newPixel = (newComponent,)*3
			outputPixels.append(newPixel)
		region.putdata(outputPixels)
		
	# Flips an image horizontal, vertical, or both
	def Flip(self,flipType):
		if (flipType == FlipType.Horizontal or flipType == FlipType.Both):
			self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
		if (flipType == FlipType.Vertical or flipType == FlipType.Both):
			self.image = self.image.transpose(Image.FLIP_TOP_BOTTOM)
			
	def Checkered(self,size,filter,filterMulti):
		# Determines the number of boxes which will fit into the image
		horizontalBoxes = math.ceil(self.image.size[0]/size)
		verticalBoxes = math.ceil(self.image.size[1]/size)
		
		# Iterates through each box index with a grid
		for y in range(verticalBoxes):
			for x in range(horizontalBoxes):
				# Determines whether the index of the box is filtered or not
				if ((x % 2 == 0 and y % 2 != 0) or (y % 2 == 0 and x % 2 != 0)):
					# Take the region out of the image to be filtered
					region = self.image.crop((size*x,size*y,size*x+size,size*y+size))
					
					# Apply a filter to the region
					region = self.ApplyFilterToRegion(region,filter,(x+y)*filterMulti)
					
					# Paste the region back into the image
					self.image.paste(region,(size*x,size*y,size*x+size,size*y+size))
	
	def Pixellate(self,pixelSize):
		# Determines the number of boxes which will fit into the image
		horizontalBoxes = math.ceil(self.image.size[0]/pixelSize)
		verticalBoxes = math.ceil(self.image.size[1]/pixelSize)
		
		# Loops through the coordinates for each new, larger, pixel
		for y in range(verticalBoxes):
			for x in range(horizontalBoxes):
				# Gets the data from the region
				region = self.image.crop((pixelSize*x,pixelSize*y,pixelSize*x+pixelSize,pixelSize*y+pixelSize))
				
				regionPixels = region.getdata()
				regionAverage = (0,0,0)
				numPixels = len(regionPixels)
				averagedPixels = 0
				
				# Calculate the average colour of the region
				pixelIndex = 0
				for pixel in regionPixels:
				
					# Calculates the coordinates of the pixel in the image
					xPixel = (x * pixelSize) + (pixelIndex % pixelSize)
					yPixel = (y * pixelSize) + (math.floor(pixelIndex / pixelSize))
					
					# Adds the pixel components to the average if they are within the image bounds
					if (xPixel < self.image.size[0] and yPixel < self.image.size[1]):
						regionAverage = (regionAverage[0] + pixel[0],regionAverage[1] + pixel[1],regionAverage[2] + pixel[2])
						averagedPixels += 1
						
					pixelIndex += 1
					
				# Calculates the average colour of the region by averaging all components
				regionAverage = (round(regionAverage[0]/averagedPixels),round(regionAverage[1]/averagedPixels),round(regionAverage[2]/averagedPixels))
				
				# Set the entire region to be the average colour
				newPixels = []
				for i in range(numPixels):
					newPixels.append(regionAverage)
				region.putdata(newPixels)
				
				# Paste the region back into the image
				self.image.paste(region,(pixelSize*x,pixelSize*y,pixelSize*x+pixelSize,pixelSize*y+pixelSize))
	
	# Applies different filters to an image or region using a filterIndex to choose which filter to use
	def ChooseFilter(self,filter,region,filterData):
		# If the filterData is not a tuple (as required) it will make it into a tuple
		if (isinstance(filterData,tuple) == False):
			filterData = tuple([filterData,None])
			
		if (filter == Filter.GaussianBlur):
			self.image = region.filter(ImageFilter.GaussianBlur(filterData[0]))
		elif (filter == Filter.Color):
			enhancer = ImageEnhance.Color(region)
			self.image = enhancer.enhance(filterData[0])
		elif (filter == Filter.Contrast):
			enhancer = ImageEnhance.Contrast(region)
			self.image = enhancer.enhance(filterData[0])
		elif (filter == Filter.Rotate):
			self.image = region.rotate(filterData[0])
		elif (filter == Filter.NegateColor):
			self.NegateColor(region,filterData[0])
		elif (filter == Filter.Vignette):
			self.Vignette(filterData[0],filterData[1],filterData[2])
		elif (filter == Filter.Banding):
			self.Banding(filterData[0],filterData[1],filterData[2],filterData[3],filterData[4],filterData[5],filterData[6])
		elif (filter == Filter.Grid):
			self.Grid(filterData[0],filterData[1],filterData[2],filterData[3],filterData[4],filterData[5])
		elif (filter == Filter.BlackAndWhite):
			self.BlackAndWhite(region)
		elif (filter == Filter.Flip):
			self.Flip(filterData[0])
		elif (filter == Filter.Checkered):
			self.Checkered(filterData[0],filterData[1],filterData[2])
		elif (filter == Filter.Pixellate):
			self.Pixellate(filterData[0])
			
	# Applies a filter to this image
	def ApplyFilter(self,filter,filterData):
		self.ChooseFilter(filter,self.image,filterData)
		
	# Applies a filter to a region rather than the image
	def ApplyFilterToRegion(self,region,filter,filterData):
		tempImage = self.image
		self.image = region
		self.ApplyFilter(filter,filterData)
		region = self.image
		self.image = tempImage
		return region
		
	# Applies a filter to a single pixel rather than the image
	def ApplyFilterToPixel(self,pixel,filter,filterData):
		region = Image.new('RGB',(1,1),(255,255,255))
		region.putdata([pixel])
		region = self.ApplyFilterToRegion(region,filter,filterData)
		return region.getdata()[0]
		
# Calls the methods required to create the collage and allows for filter application
def CreateCollage():
	# Creates the image objects
	im1 = CollageImage("29.jpg")
	im2 = CollageImage("49.jpg")
	im3 = CollageImage("50.jpg")
	im4 = CollageImage("53.jpg")
	collageImages = [im1,im2,im3,im4]
	
	# Resizes the images to fit in their areas of the collage
	collage = Collage(collageImages,False,True,FittingType.Fill)
	
	# Apply filters to the images here:
	
	im1.ApplyFilter(Filter.Vignette,(0,100000000,0.1))
	
	for image in collageImages:
		# Apply filters to all images here:
		#image.ApplyFilter(Filter.Checkered,(40,Filter.Contrast,0.1))
		pass
	
	# Adds the images to the collage and shows the finished collage
	collage.AddImages(collageImages)
	collage.Show()

CreateCollage()

'''

Resize function includes properties which can be modified:

Resize(a,b,c,d):
	a: New Width - do not change
	b: New Height - do not change
	c: Maintain Aspect Ratio - maintain the aspect ratio when resizing
		True: Maintain aspect ratio
		False: Do not maintain aspect ratio
	d: Fitting Type - how the image should fit into the new space when maintaining the aspect ratio
		FittingType.Fill: fill the new space with the image, cutting off parts of the image
		FittingType.Fit: fit the whole image in the new space, creating borders around the image

There are various filters which can be applied to an image:

Filters:
	Filter.GaussianBlur - (a):
		a: Blur Radius (float) - the blurriness of the image
			0: original image
			>0: more blurred image
		
	Filter.Color - (a):
		a: Amount (float) - amount of colour in the image
			<0: inverse of original image
			0: greyscale
			1: original image
			>1: higher colour image
		
	Filter.Contrast - (a):
		a: Amount (float) - amount of difference between colours in the image
			<0: inverse of original image
			0: grey image
			1: original image
			>1: higher contrast image
		
	Filter.Rotate - (a):
		a: Angle (float) - degrees that the image should be rotated
		
	Filter.NegateColor - (a):
		a: Negate - which colours should be negated
			Negate.R: Red
			Negate.G: Green
			Negate.B: Blue
			Negate.RG: Red & Green
			Negate.RB: Red & Blue
			Negate.GB: Green & Blue
			Negate.RGB: Red, Green, & Blue (All)
		
	Filter.Vignette - (a,b):
		a: Brightness Percentage (float) - the overall brightness multiplier of the image
		b: Strength Scale (float) - the intensity of the vignette's change from light to dark
		c: Start Distance Percentage (float) - the percentage distance from the center of the image that the vignette will start
			0: the vignette will start at the center of the image
			1: the vignette will start at the edge of the image
		
	Filter.Banding - (a,b,c,d,e,f,g):
		a: Band Type - the type of banding to use
			BandType.Rectangular: bands are boxes
			BandType.Circular: bands are circles around the image center
		b: Band Size (int) - the pixel size of a single band
		c: Filter - filter to be applied to the bands
		d: Filter Multiplier (float) - multiplier for the intensity of the filter
		e: Multiple Skip - if the index of the band is not divisible by this, it remains the same
		f: Orientation - whether the bands should be horizontal or vertical
			Orientation.Horizontal: orient horizontally
			Orientation.Vertical: orient vertically
		g: Reverse - invert the direction the filter is applied to each band
		
	Filter.Grid - (a,b,c,d,e,f):
		a: Horizontal Boxes (int) - number of image instances horizontally
		b: Vertical Boxes (int) - number of image instance vertically
		c: Filter - filter to be applied to the image instances
		d: Filter Multiplier (float) - multiplier for the intensity of the filter
		e: Reverse - invert the direction the filter is applied to each image instance
			True: Invert from original direction
			False: Do not invert from original direction
		f: Maintain Aspect Ratio - maintain the aspect ratio of the image instances
			True: Maintain aspect ratio
			False: Do not maintain aspect ratio
		
Filters can be applied to an image using the ApplyFilter method:
	
	ApplyFilter(a,b):
		a: Filter - filter to be applied to the image
		b: Filter Data - tuple containing the data (variables) which the filter requires (as specified above)
		
'''