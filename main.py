from snowflake import plotPoints as draw, rotatePetal, growFlake, create3dPrintFile

points = [
	(24,4),
	(16,4),
	(16,6),
	(20,6),
	(19,7),
	(20,8),
	(16,8),
	(16,10),
	(24,10),
	(24,8),
	(23,7),
	(24,6),
	(24,4)
]



snowflakePetal = growFlake(points, maxDepth=3, numChildren=3, 
	angleBetweenSiblings=15, scalar=0.5)


snowflake = []
numBranches = 6
for i in range(numBranches):
	snowflake = snowflake + rotatePetal(snowflakePetal, angle=(360/numBranches)*i, pivot=(24,4))
	
	

draw(snowflake)














