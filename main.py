from snowflake import plotPoints as draw, rotatePedal, growFlake, create3dPrintFile

points = []

points.append( (2,0) )
points.append( (4,2) )
points.append( (0,2) )
points.append( (2,0) )

snowflakePedal = growFlake(points, maxDepth=2, numChildren=3, 
	angleBetweenSiblings=15, scalar=0.25)

#draw(snowflakePedal) # see if you added the points correctly

# loop it good
fullSnowflake = []
for i in range(0, 6):
	fullSnowflake +=  rotatePedal(snowflakePedal, angle=(360/6) * i, pivot=(0,0))

draw(fullSnowflake)

create3dPrintFile(fullSnowflake, 'mysnowflake')






# points = []

# points.append( (0,0) )
# points.append( (1,1) )
# points.append( (3,2) )
# points.append( (2,3) )
# points.append( (0,0) )
























