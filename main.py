from snowflake import plotPoints as draw, rotatePedal, growFlake, create3dPrintFile

points = [
	(2,0),
	(4,2),
	(0,2),
	(2,0)
]

snowflakePetal = growFlake(points, maxDepth=1, numChildren=2, 
	angleBetweenSiblings=45, scalar=0.5)

draw(snowflakePetal) # see if you added the points correctly

# Turn your snowflake petal (branch) into a full snowflake
fullSnowflake = []
for i in range(0, 6):
	fullSnowflake +=  rotatePedal(snowflakePetal, angle=(360/6) * i, pivot=(0,0))

#draw(fullSnowflake)

create3dPrintFile(fullSnowflake, 'mysnowflake')
























