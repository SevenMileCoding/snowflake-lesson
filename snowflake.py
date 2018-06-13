from dxfwrite import DXFEngine as dxf
import math
import random
import copy

import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches


def create3dPrintFile(points, filename):
	"""
	Generates a starter file for creating a 3d print
	"""

	drawing = dxf.drawing(filename + '.dxf')

	for x in points:
		polyline= dxf.polyline()
		polyline.add_vertices(x)
		polyline.close()
		
		drawing.add(polyline)
	drawing.save()


def plotPoints(points):
	"""
	Plots coordinates on a graph and connects them

	takes in a list of points (tuples), or a list of lists of tuples
	- ex: [(x1,y1), (x2,y2), ...]
	- ex: [ [(x1,y1), (x2,y2), ...], [(x1,y1), (x2,y2), ...] ...]
	"""
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.grid(linestyle='-', linewidth=1)
	ax.set_axisbelow(True)
	

	if type(points[0]) is not list:
		path = Path(points)
		patch = patches.PathPatch(path, facecolor='orange', lw=2)
		patch.set_alpha(0.4)
		ax.add_patch(patch)
		# TODO: remove code dupe
	else:
		for x in points:
			path = Path(x)
			randomColor = [random.random() for x in range(0, 3)]
			patch = patches.PathPatch(path, facecolor=randomColor, lw=2)
			patch.set_alpha(0.4)
			ax.add_patch(patch)
	
	plt.axis('equal')
	plt.xlabel('x coordinate')
	plt.ylabel('y coordinate')
	ax.autoscale_view()
	plt.show()


def rotate(origin, point, angle):
	"""
	Rotate a point counterclockwise by a given angle around a given origin.

	The angle should be given in degrees.
	"""

	angle = math.radians(angle)
	ox, oy = origin
	px, py = point
	cosA = math.cos(angle)
	sinA = math.sin(angle)

	qx = ox + cosA * (px - ox) - sinA * (py - oy)
	qy = oy + sinA * (px - ox) + cosA * (py - oy)
	return (qx, qy)


def rotateList(l, pivot, angle):
	return [rotate(pivot, x, angle) for x in l]


def rotatePetal(l, angle=15, pivot=(0,0)):
	"""
	Rotates a set of coordinates around a pivot point, for a given angle
	- Optional:
		angle: angle in degrees, default=15
		pivot: a tuple that represents (x,y) pivot point, default=(0,0)
	"""
	total = []
	for x in l:
		total.append(rotateList(x, pivot, angle))
	return total


class Node:
	"""
	Not really a node tho
	"""
	def __init__(self, coords, numChildren, depth):
		self.coords = coords
		self.numChildren = numChildren
		self.depth = depth

		# store what coordinates define the original top (y) line of the shape
		coordsCopy = copy.deepcopy(self.coords)
		max1 = self._funky(max, coordsCopy, 1)
		coordsCopy.remove(max1)
		max2 = self._funky(max, coordsCopy, 1)

		self.topline = { 
			'c1': {
				'index': self.coords.index(max1),
				'value': max1
			},
			'c2': {
				'index': self.coords.index(max2),
				'value': max2
			}
		}

		min1 = self._funky(min, coordsCopy, 1)
		coordsCopy.remove(min1)
		min2 = self._funky(min, coordsCopy, 1)

		self.bottomline = {
			'c1': {
				'index': self.coords.index(min1),
				'value': min1
			},
			'c2': {
				'index': self.coords.index(min2),
				'value': min2
			}
		}

		
	def getCoords(self):
		return self.coords

	def getNumChildren(self):
		return self.numChildren

	def getWidth(self):
		return self.maxmin(max, 0)[0] - self.maxmin(min, 0)[0]

	def getHeight(self):
		return self.maxmin(max, 1)[1] - self.maxmin(min, 1)[1]

	def minX(self):
		return self.maxmin(min,0)[0]
	def minY(self):
		return self.maxmin(min, 1)[1]

	def maxX(self):
		return self.maxmin(max, 0)[0]
	def maxY(self):
		return self.maxmin(max, 1)[1]

	def minXY(self):
		return self.maxmin(min, 1)

	def maxmin(self, fn, i):
		return self._funky(fn, self.coords, i)

	def _funky(self, fn, listy, i):
		return fn(listy, key=lambda item:item[i])

	def getDepth(self):
		return self.depth

	
	def getLineInfo(self, c1_index, c2_index, useCoords=False):

		c1 = None
		c2 = None

		if useCoords == True:
			c1 = c1_index
			c2 = c2_index
		else:
			c1 = self.coords[c1_index]
			c2 = self.coords[c2_index]

		m = 0
		if c1[0] - c2[0] != 0:
			m = (c1[1] - c2[1]) / (c1[0] - c2[0])
		b = c1[1]-m*c1[0]
		mid = ((c1[0]+c2[0]) / 2, (c1[1] + c2[1]) / 2)
		return {'m': m, 'b': b, 'midpoint': mid, 'c1': c1, 'c2': c2}


	def getAbsoluteTop(self):
		return self.topline

	def getAbsoluteLineInfo(self, side):
		line = self.bottomline
		if side == 'top':
			line = self.topline
		return self.getLineInfo(line['c1']['index'], line['c2']['index'])

	def getTopLineInfo(self):
		""" 
		Returns information about the top (greatest y) line of shape
		"""
		coords = copy.deepcopy(self.coords)
		max1 = self._funky(max, coords, 1)
		coords.remove(max1)	
		max2 = self._funky(max, coords, 1)
		return self.getLineInfo(max1,max2, useCoords=True)



def transformCoords(coords, newOrigin, scalar, angle):

	# translate to 0,0 for easy scaling and rotation
	translated = [(x - newOrigin[0], y - newOrigin[1]) for x,y in coords]	
	scaledCoords = [(x * scalar, y * scalar) for x,y in translated]

	# shift coordinates back (to above the parent node)
	scaledNode = Node(scaledCoords, 0, 0)
	height = scaledNode.getHeight()
	translated = [(x + newOrigin[0], y + newOrigin[1] + height) for x,y in scaledCoords]
	
	n = Node(translated, 0, 0)
	xPiv = n.getAbsoluteLineInfo('bottom')['midpoint'][0]

	# in order to fit children near to the parent, we need to shift them down
	# new y position is calculated based on the two max's that form the top line of the parent
	return translated
	rotated = rotateList(translated, newOrigin, -1*angle)
	return rotated
	rNode = Node(rotated, 0, 0)
	offsetX = rNode.getAbsoluteLineInfo('bottom')['c1'][0] - newOrigin[0]
	offsetY = rNode.getAbsoluteLineInfo('bottom')['c1'][1] - newOrigin[1]
	rotated = [(x+offsetX, y-offsetY) for x,y in rotated]
	return rotated


def getChildrenCoordinates(coords, numChildren, yCutoff):
	import PointsAlongPolygon as pp

	pointsAbovePerim = []
	numPointsOnPerim = 0

	# TODO: super innefficient, but it works
	# Because PointsAlongPolygon.PerimeterPnts calculates evenly across the total permin,
	# we want to get the number of children, but only above a certain cutoff on the y axis
	# So Keep increasing the points pp.PerimeterPnts calculates until there are numChildren points above the cutoff
	while len(pointsAbovePerim) < numChildren:
		numPointsOnPerim += 1
		pointsAbovePerim = []
		perimeterPoints = pp.PerimeterPnts([coords], numPointsOnPerim)

		for p in perimeterPoints:
			if p[1] >= yCutoff:
				tmp = {'coords': p, 'lineSegment': perimeterPoints[p]}
				pointsAbovePerim.append(tmp)

	return pointsAbovePerim


# TODO: optimize list so that a straight line isn't split into multiple segments (by user)

# def minMidpoint(coords):
# 	# returns a coordinate that is the midpoint of the minimum line, 
# 	# where min is determined by y value

# 	# sort list by y value
# 	sortedCoords = sorted(coords, key=lambda x: x[1])

# 	p1, p2 = sortedCoords[:2]
# 	return ((p2[0] + p1[0]) / 2, (p2[1] - p1[1]) / 2)

def min(coords):
	# returns min y coordniate pair, or midpoint of min line

	# sort list by y value
	sortedCoords = sorted(coords, key=lambda x: x[1])

	p1, p2 = sortedCoords[:2]
	if p1[1] == p2[1]:
		return ((p2[0] + p1[0]) / 2, p2[1])
	else:
		return p1 


def newFlake(coordinates, origin=None):
	
	if origin is None:
		origin = minMidpoint(coordinates)

def transformey(coords, scalars, offsets, localScale=True, origin=None):
	"""
	Applies a transformation to coordinate set

	coords: list of tuples [(x1,y1), (x2,y2), ...],
	scalars: tuple (x scalar, y scalar)
	offsets tuple (x offset, y offset)
	"""

	# NOTE: maybe break up in to translate and scaling functions

	newCoords = []
	for p in coords:
		x, y = p

		if localScale is True and origin:
			x = x - origin[0]
			y = y - origin[1]

		x = x * scalars[0] + offsets[0] # TODO: priority option
		y = y * scalars[1] + offsets[1]

		if localScale is True and origin:
			x = x + origin[0]
			y = y + origin[1]

		newCoords.append((x,y))

	return newCoords

def length(coords, axis):
	"""
	Returns the max distance between the points on the given axis
	axis=0 is x
	axis=1 is y, etc
	"""
	s = sorted(coords, key=lambda x: x[axis])

	minn = s[0]
	maxx = s[-1]
	return maxx[axis] - minn[axis]

def getRotation(endPoints):
	"""
	Figures out the angle of rotation wanted for a child. That is angle of the line segment the child falls on

	endPoints: two coordinates on linear line [(x1,y1), (x2,y2)] 
	"""

	p1, p2 = endPoints
	xDiff = p2[0] - p1[0]
	yDiff = p2[1] - p1[1]
	angleOfInclination = math.atan2(yDiff, xDiff)
	angleOfInclination = math.degrees(angleOfInclination)
	return angleOfInclination + 180
	


def grow(coords, numChildren=4, yCutoff=None, origin=None, scalar=0.33):

	finalCoords = [ ]
	if yCutoff is None:
		yCutoff = length(coords, 1) / 2
	
	myOrigin = min(coords)
	if origin is not None:
		myOrigin = origin
	
	origScalar = scalar
	print('Origin is:', myOrigin)
	# 1st iteration
	# how many children? 3
	#for i in range(numChildren):

	scalar = origScalar #* depth # depth = family generation

	scaledCoords = transformey(coords, [scalar, scalar], [0,0], localScale=True, origin=myOrigin) # siblings are the same scale
	
	childTranslations = getChildrenCoordinates(coords, numChildren, yCutoff)


	for i in range(numChildren):
		
		translateX, translateY = childTranslations[i]['coords']
		translateX -= myOrigin[0]
		translateY -= myOrigin[1]

		angle = getRotation(childTranslations[i]['lineSegment'])
		rotatedCoords = rotateList(scaledCoords, myOrigin, angle)

		translatedCoords = transformey(rotatedCoords, [1,1], [translateX,translateY], localScale=False)
		
		info = {'coords': translatedCoords, 'translation': (translateX, translateY), 'rotation': angle}
		finalCoords.append(info)


	return finalCoords
	# then for one child, we take all the children in finalCoords, scale it, rotate and translate it by the amount that that child was


def growFlake(startCoords, depth=2, numChildren=3, scalar=0.4):

	final = []
	for i in range(1):#depth):

		generationStack = grow(startCoords, numChildren=numChildren, yCutoff=1, scalar=scalar)
		mhm = [x['coords'] for x in generationStack]
		
		# child 1
		grandKids = []
		child2 = generationStack[2]
		for x in generationStack:
			coords = x['coords']
			coords = transformey(coords, [scalar, scalar], [0,0], origin=min(startCoords))

			coords = transformey(coords, [1,1], child2['translation'])
			oldOrigin = min(startCoords)
			x, y = child2['translation']
			newOrigin = oldOrigin[0] + x, oldOrigin[1] + y
			print(newOrigin)
			coords = rotateList(coords, newOrigin, child2['rotation'])
			grandKids.append(coords)

		final = [startCoords] + mhm + grandKids
		# while len(generationStack) > 0:
		# 	sibling = generationStack.pop()
		# 	x = grow(sibling, numChildren=)
		# 	hmmm.append(x)

	return final
		



# def growFlake(startCoords, maxDepth=1, numChildren=2, angleBetweenSiblings=15, scalar=0.5):
# 	"""
# 	Grows a set of coordinates to have children like it

# 	startCoords: list of list of tuples [[(x1,y1), (x2,y2), ...], [(x1,y1), (x2,y2), ...] ...]
# 	- Optional:
# 	maxDepth: How many generations i.e. 2 = grandma, mom, daughter. Default=1
# 	numChildren: number of children each generation will have. Default=2
# 	angleBetweenSiblings: separation between siblings, in degrees. Default=15
# 	scalar: How much smaller the child will be from its parent. Default=0.5
# 	"""
# 	stack = []
# 	finalCoords = [startCoords]
# 	root = Node(startCoords, numChildren, 1)
# 	stack.append(root)

# 	if angleBetweenSiblings == 0:
# 		angleBetweenSiblings = 1
# 		# so maxDegree isn't -1

# 	while len(stack) > 0:
# 		p = stack.pop()

# 		numChildren = p.getNumChildren()

# 		if numChildren <= 0:
# 			continue
		
# 		maxDegree = numChildren * angleBetweenSiblings - 1
# 		shift = maxDegree /numChildren

# 		for i in range(0, numChildren):
			
# 			xOrig = p.getAbsoluteLineInfo('top')['midpoint'][0]
# 			if numChildren > 1:
# 				xOrig = p.getAbsoluteLineInfo('top')['c2'][0]  + (p.getWidth() / (numChildren-1)) * i# + p.getWidth()/(numChildren+1)
# 				#xOrig = p.maxX() + (p.getWidth() / (numChildren-1)) * i - p.getWidth()
# 			yOrig = p.getAbsoluteLineInfo('top')['midpoint'][1]
# 			#yOrig = p.getAbsoluteLineInfo('top')['c2'][1]  + (p.getHeight() / (numChildren-1)) - p.getHeight()
# 			newOrigin = (xOrig, yOrig)
# 			angle = i * angleBetweenSiblings - shift
# 			childCoords = transformCoords(p.getCoords(), newOrigin, scalar, angle)

# 			numChilds = 0
# 			if p.getDepth() < maxDepth:
# 				numChilds = p.getNumChildren()
# 			newChild = Node(childCoords, numChilds, p.getDepth() + 1)

# 			stack.append(newChild)

# 			finalCoords.append(childCoords)

# 	return finalCoords



