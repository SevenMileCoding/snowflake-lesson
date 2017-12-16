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


def rotatePedal(l, angle=15, pivot=(0,0)):
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
		#self.parent = parent
		#self.angle = angle
		self.coords = coords
		#self.children = []
		self.numChildren = numChildren
		self.depth = depth

	# def addChild(self, child):
	# 	if len(self.children) >= self.numChildren:
	# 		return {'Error': 'Cannot add another child'}
	# 	self.children.append(child)

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

	def maxmin(self, fn, i):
		return self._funky(fn, self.coords, i)

	def _funky(self, fn, listy, i):
		return fn(listy, key=lambda item:item[i])

	def getDepth(self):
		return self.depth

	def slopeIntercept(self):
		""" 
		returns slope and intercept for the top (greatest y) line of shape
		"""
		coords = copy.deepcopy(self.coords)
		max1 = self._funky(max, coords, 1)
		coords.remove(max1)	
		max2 = self._funky(max, coords, 1)
		m = max1[1]
		if max1[0] - max2[0] != 0:
			m = (max1[1] - max2[1]) / deltaX
		b = max1[1]-m*max1[0]
		return (m,b)



def transformCoords(coords, newOrigin, scalar, angle):

	# translate to 0,0 for easy scaling and rotation
	translated = [(x - newOrigin[0], y - newOrigin[1]) for x,y in coords]	
	scaledCoords = [(x * scalar, y * scalar) for x,y in translated]

	# shift coordinates back (to above the parent node)
	scaledNode = Node(scaledCoords, 0, 0)
	height = scaledNode.getHeight()
	translated = [(x + newOrigin[0], y + newOrigin[1] + height) for x,y in scaledCoords]

	n = Node(translated, 0, 0)
	yPiv = n.minY()
	width = n.getWidth()
	xPiv = n.minX() + width / 2

	# in order to fit children near to the parent, we need to shift them down
	# new y position is calculated based on the two max's that form the top line of the parent
	parent = Node(coords, 0, 0)
	m, b = parent.slopeIntercept()
	fOfX = m*xPiv + b
	offset = parent.maxY() - fOfX
	translated = [(x, y - offset) for x,y in translated]

	n = Node(translated, 0, 0)
	yPiv = n.minY() # TODO: THIS IS NOT DA RIGHT VALUE we need
	rotated = rotateList(translated, (xPiv, yPiv), -1*angle)

	return rotated


def growFlake(startCoords, maxDepth=1, numChildren=2, angleBetweenSiblings=15, scalar=0.5):
	"""
	Grows a set of coordinates to have children like it

	startCoords: list of list of tuples [[(x1,y1), (x2,y2), ...], [(x1,y1), (x2,y2), ...] ...]
	- Optional:
	maxDepth: How many generations i.e. 2 = grandma, mom, daughter. Default=1
	numChildren: number of children each generation will have. Default=2
	angleBetweenSiblings: separation between siblings, in degrees. Default=15
	scalar: How much smaller the child will be from its parent. Default=0.5
	"""
	stack = []
	finalCoords = [startCoords]
	root = Node(startCoords, numChildren, 1)
	stack.append(root)

	if angleBetweenSiblings == 0:
		angleBetweenSiblings = 1
		# so maxDegree isn't -1

	while len(stack) > 0:
		p = stack.pop()

		numChildren = p.getNumChildren()

		if numChildren <= 0:
			continue
		
		maxDegree = numChildren * angleBetweenSiblings - 1
		shift = maxDegree /numChildren

		for i in range(0, numChildren):
			
			xOrig = p.maxX() + (p.getWidth() / (numChildren-1)) * i - p.getWidth()
			yOrig = p.maxY()
			newOrigin = (xOrig, yOrig)
			angle = i * angleBetweenSiblings - shift
			childCoords = transformCoords(p.getCoords(), newOrigin, scalar, angle)

			numChilds = 0
			if p.getDepth() < maxDepth:
				numChilds = p.getNumChildren()
			newChild = Node(childCoords, numChilds, p.getDepth() + 1)

			stack.append(newChild)

			finalCoords.append(childCoords)

	return finalCoords



