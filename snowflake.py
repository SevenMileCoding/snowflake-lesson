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


import PointsAlongPolygon as pp
def getChildrenCoordinates(coords, numChildren, yCutoff):
	"""
	Figures out points along the polygon (defined by coords) that children can be put at
	"""

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



def min(coords):
	# returns min y coordniate pair, or midpoint of min line

	# sort list by y value
	sortedCoords = sorted(coords, key=lambda x: x[1])

	p1, p2 = sortedCoords[:2]
	if p1[1] == p2[1]:
		return ((p2[0] + p1[0]) / 2, p2[1])
	else:
		return p1 




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
	"""
	Returns all of the transformations for the first iteration of children for coords
	aka makes numChildren kids of coords, that are scaled and evenly spaced around coords

	coords: [(x1,y1), (x2,y2)....]
	yCutoff: The y value that children will appear above
	origin: pivot point for coords
	scalar: size of child relative to coords
	"""

	finalCoords = [ ]
	if yCutoff is None:
		yCutoff = length(coords, 1) / 2
	

	if origin is None:
		origin = min(coords)

	scaledCoords = transformey(coords, [scalar, scalar], [0,0], localScale=True, origin=origin) # siblings are the same scale
	childTranslations = getChildrenCoordinates(coords, numChildren, yCutoff)

	for i in range(numChildren):
		
		translateX, translateY = childTranslations[i]['coords']
		translateX -= origin[0]
		translateY -= origin[1]

		angle = getRotation(childTranslations[i]['lineSegment'])
		rotatedCoords = rotateList(scaledCoords, origin, angle)

		translatedCoords = transformey(rotatedCoords, [1,1], [translateX,translateY], localScale=False)
		
		info = {
			'coords': translatedCoords, 
			'translation': (translateX, translateY), 
			'rotation': angle, 
			'origin': (translateX + origin[0], translateY + origin[1]),
			'depth': 1
		}
		finalCoords.append(info)


	return finalCoords
	# then for one child, we take all the children in finalCoords, scale it, rotate and translate it by the amount that that child was


def genChild(template, parent, scalar):
	"""
	parent is the shape that the child will be placed along. the template is the one of the originally generated versions of the shape (1 of numChildren original children)
	"""
	#scalar = scalar ** parent['depth']

	coords = template['coords']
	x, y = parent['translation']
	parentOrign = (parent['origin'][0] - x, parent['origin'][1] - y)

	for i in range(parent['depth']):
		coords = transformey(coords, [scalar, scalar], [0,0], origin=parentOrign)
		coords = transformey(coords, [1,1], parent['translation'] )
		coords = rotateList(coords, parent['origin'], parent['rotation'])

	kid = {
		'coords': coords, 'translation': (x,y), 
		'rotation': parent['rotation'], 
		'origin': (x + parentOrign[0], y + parentOrign[1]),
		'depth': parent['depth'] + 1
	}

	return kid


def growFlake(startCoords, depth=3, numChildren=3, scalar=0.4):

	final = []
	totalNumShapes = depth**numChildren + numChildren + 1
	base = grow(startCoords, numChildren=numChildren, yCutoff=1, scalar=scalar) # minus startCoords
	baseCopy = [x for x in base]

	if depth == 1:
		return [startCoords] + [x['coords'] for x in base]

	grandKidCoords = []
	while len(baseCopy) > 0:
		# if len(baseCopy) > totalNumShapes:
		# 	break

		parent = baseCopy.pop()
		if parent['depth'] >= depth:
			continue

		more = []
		for template in base: # this makes all the necessary children for a given polygon
			grandKid = genChild(template, parent, scalar)
			grandKidCoords.append(grandKid['coords'])
			baseCopy.append(grandKid)

	final = [startCoords] + [x['coords'] for x in base] + grandKidCoords

	return final