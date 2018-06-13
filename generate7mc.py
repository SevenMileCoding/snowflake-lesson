from snowflake import plotPoints as draw, rotatePetal, growFlake, create3dPrintFile


points = []

points.append( (2,-1) )
points.append( (3,0) )
points.append( (3,5) )
points.append( (7,4) )
points.append( (7,5.5) )
points.append( (3,5.5) )
points.append( (3,7) )
points.append( (5,8) )
points.append( (3,9) )
points.append( (3,10.5) )
points.append( (7,10.5) )
points.append( (7,12) )
points.append( (4,12) )
points.append( (3,13) )
points.append( (3,15.5) )
points.append( (5,15.5) )
points.append( (5,13.5) )
points.append( (6,13.5) )
points.append( (7,14) )
points.append( (7,15.5) )
points.append( (8,15.5) )
points.append( (8,9) )
points.append( (6,9) )
points.append( (7,8) )
points.append( (6,7) )
points.append( (8,7) )
points.append( (8,2) )
points.append( (5,3) )
points.append( (5,0) )
points.append( (6,-1) )
points.append( (2,-1) )

draw(points)

snowflakePetal = growFlake(points, maxDepth=3, numChildren=4, angleBetweenSiblings=40, scalar=0.5)

draw(snowflakePetal)
# generate
fullSnowflake = []
for i in range(0, 6):
	fullSnowflake +=  rotatePetal(snowflakePetal, pivot=(0,0), angle=(360/6) * i)

draw(fullSnowflake)

create3dPrintFile(fullSnowflake, 'testy')



























