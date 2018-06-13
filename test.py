from snowflake import plotPoints as draw, rotatePetal, grow, create3dPrintFile, growFlake

points = [
	(3,0),
	(6,3),
	(0,3),
	(3,0)    
]


# a = grow(points)
# draw(a)

a = growFlake(points)
draw(a)