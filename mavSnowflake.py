from snowflake import plotPoints as draw, rotatePetal, growFlake, create3dPrintFile


points = []

points.append( (0,0) )
points.append( (1,1) )
points.append( (2,2) )
points.append( (2,4) )
points.append( (0,8) )
points.append( (5,6) )
points.append( (3,3) )
points.append( (4,0) )
points.append( (0,0) )

draw(points)

snowflakepetal = growFlake(points, maxDepth=2, numChildren=3, angleBetweenSiblings=30, scalar=0.35)

draw(snowflakepetal)

# generate
fullSnowflake = []
for i in range(0, 5):
	fullSnowflake +=  rotatePetal(snowflakepetal, pivot=(0,0), angle=(360/5) * i)

draw(fullSnowflake)

create3dPrintFile(fullSnowflake, 'mav')
