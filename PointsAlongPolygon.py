# http://www.arcgis.com/home/item.html?id=e19b53170e004e46827b8129d6ef9bfe
def PerimeterPnts(coordLst, numPnts):

	perimPntLst_allRings = []

	totalPerim = 0    

	ringPerimLst = []

	for ringLst in coordLst:

		# perimeter length...
		perim = 0

		# for each perimeter segment, add lengths...
		for pos in range(len(ringLst)-1):
			x1,y1 = ringLst[pos][0], ringLst[pos][1]
			x2,y2 = ringLst[pos+1][0], ringLst[pos+1][1]
			d = ((x1-x2)**2 + (y1-y2)**2)**.5
			perim += d

		ringPerimLst.append(perim)
		totalPerim += perim

	spacingLst = []

	for perim in ringPerimLst:
		rNumPnts = int((perim / totalPerim) * numPnts)
		if rNumPnts == 0: 
			d = rNumPnts = 0
		else:
			d = perim / rNumPnts
			if d < .5: d = .5
		spacingLst.append([d, rNumPnts])

	
	# for each ring in polygon...
	for ringNo in range(len(coordLst)):

		ringLst = coordLst[ringNo]
		d = spacingLst[ringNo][0]
		numPnts = spacingLst[ringNo][1]
		
		if numPnts == 0: continue
		
		#---------------------------------
		# GENERATE POINTS ALONG PERIMETER OF CURRENT RING...

		# list of selected points... { (x,y): start point, end point]}
		perimPntDic = {}
		# ^ when a point is found, it is added to dictionary with its coordinates as the key, and the line segnment is falls on as the value

		# position in vertex list...
		pos = done = 0

		# endpoint coordinates of first perimeter segment...
		X1,Y1 = ringLst[pos][0], ringLst[pos][1]
		X2,Y2 = ringLst[pos+1][0], ringLst[pos+1][1]

		lastAdded = None
		# for each point desired...
		#for pntNum in xrange(numPnts+15):
		while True:
			   
			# determine the min and max X values for the segment...
			xLst = [X1,X2]
			xLst.sort()
			xMin = xLst[0]
			xMax = xLst[-1]

			# determine the min and max Y values for the segment...
			yLst = [Y1,Y2]
			yLst.sort()
			yMin = yLst[0]
			yMax = yLst[-1]

			# 1 = valid point found; 0 = no valid point found...
			pnt1 = pnt2 = 0
			
			# if segment slope is nearly vertical...
			if abs(X1 - X2) < abs(Y1-Y2)/100:
				x1 = x2 = X1    
				y1 = Y1 - d      
				y2 = Y1 + d
				
			# if segment slope is horizontal...
			elif Y2-Y1 == 0:
				y1 = y2 = Y1
				x1 = X1 - d
				x2 = X1 + d

			# if segment is not nearly vertical, calculate slope and y-intercept
			else:
			
				m = (Y2-Y1) / (X2-X1)    # slope
				b = Y1-(m*X1)            # y-intercept

			   
				#---------------------------
				# find point on line that is distance d from (X1,Y1)...

				# coefficients in the quadratic equation...
				A = 1+m**2
				B = 2*m*b - 2*X1 - 2*Y1*m
				C = X1**2 - d**2 + Y1**2 - 2*Y1*b + b**2

				# calculate x intercepts using quadratic equation...
				x1 = (-B + (B**2-4*A*C)**.5) / (2*A)
				y1 = m*x1+b

				x2 = (-B - (B**2-4*A*C)**.5) / (2*A)
				y2 = m*x2+b

			# check if 1st point is on the segment...
			if xMin <= x1 <= xMax:
				if yMin <= y1 <= yMax:
					# check if point is a vertex...
					if ((x1-X2)**2 + (y1-Y2)**2)**.5 < .00001:
						pos += 1
						# if position is last vertex, analysis is finished...
						if pos >= len(ringLst)-1:
							break
						X2,Y2 = ringLst[pos+1][0], ringLst[pos+1][1]
					pnt1 = 1

			# check if 2nd point is on the segment...
			if xMin <= x2 <= xMax:
				if yMin <= y2 <= yMax:
					# check if point is a vertex...
					if ((x2-X2)**2 + (y2-Y2)**2)**.5 < .00001:
						pos += 1
						# if position is last vertex, analysis is finished...
						if pos >= len(ringLst)-1:
							break
						X2,Y2 = ringLst[pos+1][0], ringLst[pos+1][1] 
					pnt2 = 1

			
					
			#---------------------------
			
			dNext = d  # additional distance needed (set to full separation distance initially)...

			# if neither point is on line segment, move along successive segments...        
			while pnt1 == pnt2 == 0:

				# calculate additional distance needed to meet spacing requirement...   
				dNext = dNext-((X1-X2)**2 + (Y1-Y2)**2)**.5

				# move position to next vertex (to get next segment)...
				pos += 1

				# if position is last vertex, analysis is finished...
				if pos >= len(ringLst)-1:
					break

				# if close to vertex, take vertex as the point...
				if dNext < .0001:
					x1,y1 = X2,Y2
					X2,Y2 = ringLst[pos+1][0], ringLst[pos+1][1]
					pnt1 = 1
					break
			
				# coordinates of next perimeter segment...
				X1,Y1 = ringLst[pos][0], ringLst[pos][1]
				X2,Y2 = ringLst[pos+1][0], ringLst[pos+1][1]

				# determine the min and max X values for the segment...
				xLst = [X1,X2]
				xLst.sort()
				xMin = xLst[0]
				xMax = xLst[-1]

				# determine the min and max Y values for the segment...
				yLst = [Y1,Y2]
				yLst.sort()
				yMin = yLst[0]
				yMax = yLst[-1]

				# 1 = valid point found; 0 = no valid point found...
				pnt1 = pnt2 = 0

				# if segment slope is nearly vertical...
				if abs(X1 - X2) < abs(Y1-Y2)/100:
					x1 = x2 = X1
					y1 = Y1 - dNext
					y2 = Y1 + dNext

				# if segment is not nearly vertical, calculate slope and y-intercept
				else:                
			   
					m = (Y2-Y1) / (X2-X1)
					b = Y1-(m*X1)

					#---------------------------
					# find point on line that is distance d from (X1,Y1)...

					# coefficients in the quadratic equation...
					A = 1+m**2
					B = 2*m*b - 2*X1 - 2*Y1*m
					C = X1**2 - dNext**2 + Y1**2 - 2*Y1*b + b**2
				  
					# calculate x intercepts using quadratic equation...
					x1 = (-B + (B**2-4*A*C)**.5) / (2*A)
					y1 = m*x1+b

					x2 = (-B - (B**2-4*A*C)**.5) / (2*A)
					y2 = m*x2+b

				# check if 1st point is on the segment...
				if xMin <= x1 <= xMax:
					if yMin <= y1 <= yMax:
						pnt1 = 1      

				# check if 2nd point is on the segment...
				if xMin <= x2 <= xMax:
					if yMin <= y2 <= yMax:
						pnt2 = 1
						
			# if position is last vertex, analysis is finished...
			if pos >= len(ringLst)-1:
				break

			# if point 1 is valid, and not already in list, add to list
			if pnt1 == 1:
				if (x1,y1) not in perimPntDic:
					perimPntDic[(x1,y1)] = [(X1, Y1), (X2, Y2)]
					lastAdded = (x1,y1)

			# if point 2 is valid, and not already in list, add to list
			elif pnt2 == 1:
				if (x2,y2) not in perimPntDic:
					perimPntDic[(x2,y2)] = [(X1, Y1), (X2, Y2)]
					lastAdded = (x2,y2)

			# set 1st endpoint to last perimeter point...
			X1,Y1 = lastAdded


		#perimPntLst_allRings.append(perimPntLst)

	return perimPntDic #perimPntLst_allRings


# ORIGINAL #########################
# def PerimeterPnts(coordLst, numPnts):

# 	perimPntLst_allRings = []

# 	totalPerim = 0    

# 	ringPerimLst = []

# 	for ringLst in coordLst:

# 		# perimeter length...
# 		perim = 0

# 		# for each perimeter segment, add lengths...
# 		for pos in range(len(ringLst)-1):
# 			x1,y1 = ringLst[pos][0], ringLst[pos][1]
# 			x2,y2 = ringLst[pos+1][0], ringLst[pos+1][1]
# 			d = ((x1-x2)**2 + (y1-y2)**2)**.5
# 			perim += d

# 		ringPerimLst.append(perim)
# 		totalPerim += perim

# 	spacingLst = []

# 	for perim in ringPerimLst:
# 		rNumPnts = int((perim / totalPerim) * numPnts)
# 		if rNumPnts == 0: 
# 			d = rNumPnts = 0
# 		else:
# 			d = perim / rNumPnts
# 			if d < .5: d = .5
# 		spacingLst.append([d, rNumPnts])

	
# 	# for each ring in polygon...
# 	for ringNo in range(len(coordLst)):

# 		ringLst = coordLst[ringNo]
# 		d = spacingLst[ringNo][0]
# 		numPnts = spacingLst[ringNo][1]
		
# 		if numPnts == 0: continue
		
# 		#---------------------------------
# 		# GENERATE POINTS ALONG PERIMETER OF CURRENT RING...

# 		# list of selected points...
# 		perimPntLst = []

# 		# position in vertex list...
# 		pos = done = 0

# 		# endpoint coordinates of first perimeter segment...
# 		X1,Y1 = ringLst[pos][0], ringLst[pos][1]
# 		X2,Y2 = ringLst[pos+1][0], ringLst[pos+1][1]


# 		# for each point desired...
# 		#for pntNum in xrange(numPnts+15):
# 		while True:
			   
# 			# determine the min and max X values for the segment...
# 			xLst = [X1,X2]
# 			xLst.sort()
# 			xMin = xLst[0]
# 			xMax = xLst[-1]

# 			# determine the min and max Y values for the segment...
# 			yLst = [Y1,Y2]
# 			yLst.sort()
# 			yMin = yLst[0]
# 			yMax = yLst[-1]

# 			# 1 = valid point found; 0 = no valid point found...
# 			pnt1 = pnt2 = 0
			
# 			# if segment slope is nearly vertical...
# 			if abs(X1 - X2) < abs(Y1-Y2)/100:
# 				x1 = x2 = X1    
# 				y1 = Y1 - d      
# 				y2 = Y1 + d
				
# 			# if segment slope is horizontal...
# 			elif Y2-Y1 == 0:
# 				y1 = y2 = Y1
# 				x1 = X1 - d
# 				x2 = X1 + d

# 			# if segment is not nearly vertical, calculate slope and y-intercept
# 			else:
			
# 				m = (Y2-Y1) / (X2-X1)    # slope
# 				b = Y1-(m*X1)            # y-intercept

			   
# 				#---------------------------
# 				# find point on line that is distance d from (X1,Y1)...

# 				# coefficients in the quadratic equation...
# 				A = 1+m**2
# 				B = 2*m*b - 2*X1 - 2*Y1*m
# 				C = X1**2 - d**2 + Y1**2 - 2*Y1*b + b**2

# 				# calculate x intercepts using quadratic equation...
# 				x1 = (-B + (B**2-4*A*C)**.5) / (2*A)
# 				y1 = m*x1+b

# 				x2 = (-B - (B**2-4*A*C)**.5) / (2*A)
# 				y2 = m*x2+b

# 			# check if 1st point is on the segment...
# 			if xMin <= x1 <= xMax:
# 				if yMin <= y1 <= yMax:
# 					# check if point is a vertex...
# 					if ((x1-X2)**2 + (y1-Y2)**2)**.5 < .00001:
# 						pos += 1
# 						# if position is last vertex, analysis is finished...
# 						if pos >= len(ringLst)-1:
# 							break
# 						X2,Y2 = ringLst[pos+1][0], ringLst[pos+1][1]
# 					pnt1 = 1

# 			# check if 2nd point is on the segment...
# 			if xMin <= x2 <= xMax:
# 				if yMin <= y2 <= yMax:
# 					# check if point is a vertex...
# 					if ((x2-X2)**2 + (y2-Y2)**2)**.5 < .00001:
# 						pos += 1
# 						# if position is last vertex, analysis is finished...
# 						if pos >= len(ringLst)-1:
# 							break
# 						X2,Y2 = ringLst[pos+1][0], ringLst[pos+1][1] 
# 					pnt2 = 1

			
					
# 			#---------------------------
			
# 			dNext = d  # additional distance needed (set to full separation distance initially)...

# 			# if neither point is on line segment, move along successive segments...        
# 			while pnt1 == pnt2 == 0:

# 				# calculate additional distance needed to meet spacing requirement...   
# 				dNext = dNext-((X1-X2)**2 + (Y1-Y2)**2)**.5

# 				# move position to next vertex (to get next segment)...
# 				pos += 1

# 				# if position is last vertex, analysis is finished...
# 				if pos >= len(ringLst)-1:
# 					break

# 				# if close to vertex, take vertex as the point...
# 				if dNext < .0001:
# 					x1,y1 = X2,Y2
# 					X2,Y2 = ringLst[pos+1][0], ringLst[pos+1][1]
# 					pnt1 = 1
# 					break
			
# 				# coordinates of next perimeter segment...
# 				X1,Y1 = ringLst[pos][0], ringLst[pos][1]
# 				X2,Y2 = ringLst[pos+1][0], ringLst[pos+1][1]

# 				# determine the min and max X values for the segment...
# 				xLst = [X1,X2]
# 				xLst.sort()
# 				xMin = xLst[0]
# 				xMax = xLst[-1]

# 				# determine the min and max Y values for the segment...
# 				yLst = [Y1,Y2]
# 				yLst.sort()
# 				yMin = yLst[0]
# 				yMax = yLst[-1]

# 				# 1 = valid point found; 0 = no valid point found...
# 				pnt1 = pnt2 = 0

# 				# if segment slope is nearly vertical...
# 				if abs(X1 - X2) < abs(Y1-Y2)/100:
# 					x1 = x2 = X1
# 					y1 = Y1 - dNext
# 					y2 = Y1 + dNext

# 				# if segment is not nearly vertical, calculate slope and y-intercept
# 				else:                
			   
# 					m = (Y2-Y1) / (X2-X1)
# 					b = Y1-(m*X1)

# 					#---------------------------
# 					# find point on line that is distance d from (X1,Y1)...

# 					# coefficients in the quadratic equation...
# 					A = 1+m**2
# 					B = 2*m*b - 2*X1 - 2*Y1*m
# 					C = X1**2 - dNext**2 + Y1**2 - 2*Y1*b + b**2
				  
# 					# calculate x intercepts using quadratic equation...
# 					x1 = (-B + (B**2-4*A*C)**.5) / (2*A)
# 					y1 = m*x1+b

# 					x2 = (-B - (B**2-4*A*C)**.5) / (2*A)
# 					y2 = m*x2+b

# 				# check if 1st point is on the segment...
# 				if xMin <= x1 <= xMax:
# 					if yMin <= y1 <= yMax:
# 						pnt1 = 1      

# 				# check if 2nd point is on the segment...
# 				if xMin <= x2 <= xMax:
# 					if yMin <= y2 <= yMax:
# 						pnt2 = 1
						
# 			# if position is last vertex, analysis is finished...
# 			if pos >= len(ringLst)-1:
# 				break

# 			# if point 1 is valid, and not already in list, add to list
# 			if pnt1 == 1:
# 				if [x1,y1] not in perimPntLst:
# 					perimPntLst.append([x1,y1])

# 			# if point 2 is valid, and not already in list, add to list
# 			elif pnt2 == 1:
# 				if [x2,y2] not in perimPntLst:
# 					perimPntLst.append([x2,y2])

# 			# set 1st endpoint to last perimeter point...
# 			X1,Y1 = perimPntLst[-1][0], perimPntLst[-1][1]

# 		# add last vertex point to perimeter point list...
# 		perimPntLst.append(ringLst[-1])

# 		perimPntLst_allRings.append(perimPntLst)

# 	return perimPntLst_allRings
