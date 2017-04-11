import maya.OpenMaya as om
import maya.cmds as cmds
import math
import os
from operator import itemgetter, attrgetter, methodcaller

class polySelector:

#----------------------------------------------------------------------------------------------------------------------
	def __init__(self):
		self.targetIds = 0
		self.targetGeom = []
		self.geometryData = GeometryData()
		self.geometryData.setPolyData()



	def printMMatrix(matrix):
		endStr = '\n'
		outStr = ''
		outStr += endStr

		for r in range(0,4):
			for c in range(0,4):
				outStr += str(matrix(r,c)) + str(' ')
			outStr += endStr

		print 'transformation: ',  outStr


	def select(self):

		#set_polyData()
		
		poly_ids = []
		selectedEdges = []

		selectedVertices, centerPolygon = self.getCornerPolygonIds()
		selectedEdges = self.geometryData.slice(selectedVertices)
		#poly_ids, cornerVertex = self.geometryData.surroundBuilding(selectedVertices)
		# poly_ids2 = self.geometryData.selectPolygonsBorder(poly_ids,cornerVertex, centerPolygon)
		# #poly_ids2 = self.geometryData.selectPolygonsBorder2(selectedEdges, centerPolygon)

		sel = om.MSelectionList()
		om.MGlobal.getActiveSelectionList(sel)

		mdag = om.MDagPath()
		sel.getDagPath(0, mdag)


		# # Create an MIntArray and populate it with component ids to add to our component object
		# # MIntArray takes an array of ints. That has to be passed using an MScriptUtil pointer
		# # This is where you would use your list of polyIds that you had gotten

		# #********************

		util = om.MScriptUtil()
		util.createFromList(selectedEdges, len(selectedEdges))
		ids_ptr = util.asIntPtr()
		edgeIds = om.MIntArray(ids_ptr, len(selectedEdges))

		# Create a singleIndexedComponent of type polygon
		mfn_components = om.MFnSingleIndexedComponent()
		components = mfn_components.create(om.MFn.kMeshEdgeComponent)
		# Add our MIntArray of ids to the component
		mfn_components.addElements(edgeIds)

		to_sel = om.MSelectionList()
		# The object the selection refers to, and the components on that object to select
		to_sel.add(mdag, components)
		om.MGlobal.setActiveSelectionList(to_sel)

		# #********************

		# util = om.MScriptUtil()
		# util.createFromList(poly_ids2, len(poly_ids2))
		# ids_ptr = util.asIntPtr()
		# polyids = om.MIntArray(ids_ptr, len(poly_ids2))

		# # Create a singleIndexedComponent of type polygon
		# mfn_components = om.MFnSingleIndexedComponent()
		# components = mfn_components.create(om.MFn.kMeshPolygonComponent)
		# # Add our MIntArray of ids to the component
		# mfn_components.addElements(polyids)

		# # The object the selection refers to, and the components on that object to select
		# to_sel.add(mdag, components)
		# om.MGlobal.setActiveSelectionList(to_sel)

		#return getDirectionalFace(faceIndex, om.MVector(0,1,0))




	def getCornerPolygonIds(self):
		targetGeom = []

		selList = om.MSelectionList()
		#lägger till markerade meshar i listan selList
		om.MGlobal.getActiveSelectionList(selList)

		# om inget polygon är markerat
		if selList.isEmpty():
			print "Select four polygons"
			return

		targetVertexIds = []
		targetEdgeIds = []
		targetPolyIds = []

		# itererar igenom objektets noder, de noder som finns i hypergraphen
		selListIter = om.MItSelectionList(selList)
		while not selListIter.isDone():
			print "selListIter"

			components = om.MObject()
			dagPath = om.MDagPath()
			selListIter.getDagPath( dagPath, components)

			if components.isNull():   
				selListIter.next()
				continue

			compListFn = om.MFnComponent(components)
			compType = compListFn.componentType()

			if compType == om.MFn.kMeshVertComponent:
				# allows compListFn to query single indexed components
				compListFn = om.MFnSingleIndexedComponent(components)
				targetVertexIds = om.MIntArray()
				# äntligen får vi ut samtliga id för de markerade polygonen
				compListFn.getElements(targetVertexIds)

			if compType == om.MFn.kMeshEdgeComponent:
				# allows compListFn to query single indexed components
				compListFn = om.MFnSingleIndexedComponent(components)
				targetEdgeIds = om.MIntArray()
				# äntligen får vi ut samtliga id för de markerade polygonen
				compListFn.getElements(targetEdgeIds)


			# kontrollerar om det finns ett polygon i komponenterna 
			if compType == om.MFn.kMeshPolygonComponent:
				# allows compListFn to query single indexed components
				compListFn = om.MFnSingleIndexedComponent(components)
				targetPolyIds = om.MIntArray()
				# äntligen får vi ut samtliga id för de markerade polygonen
				compListFn.getElements(targetPolyIds)

			selListIter.next()

		if len(targetVertexIds) > 10:
			print "too many vertices selected"
			return
		if len(targetVertexIds) == 0:
			print "no vertices selected"
			return
		if len(targetEdgeIds) == 0:
			print "no edges are selected"

		if targetPolyIds is None:
			print "select one polygon"
			return


		print "targetIds length", targetVertexIds
		return targetVertexIds, targetPolyIds

	

#######################################################################################################################

class GeometryData:

#----------------------------------------------------------------------------------------------------------------------
	def __init__(self):
		
		self.polygons = []
		self.edges = []
		self.vertex = []
		self.polygonBorder = []

	def printMatrix(self,matrix):
		endStr = '\n'
		outStr = ''
		outStr += endStr

		for i in range(0,16):
			if i == 0:
				outStr += '['

			if( i > 0 and i%4==0):
				outStr += endStr
			outStr += str(matrix[i]) + str(' ')
		outStr += ']'

		print 'transformation: ',  outStr

	def setPolyData(self):
		print "´selecting..."
		selList = om.MSelectionList()
		#lägger till markerade meshar i listan selList
		om.MGlobal.getActiveSelectionList(selList)

		print "selList length", selList
		if selList.isEmpty():
			print "No polygon is selected"
			return


		components = om.MObject()
		dagPath = om.MDagPath()
		selList.getDagPath(0, dagPath, components)

		# hämtar namnet på huvudnoden
		pathName = dagPath.fullPathName()

		meshName = pathName[(pathName.find("|")+1):len(pathName)]

		if meshName.find("|") != -1:
			print "found"
			meshName = meshName[0:(meshName.find("|"))]

		




		#transformations matris, skala, rotation och translatering
		meshMatrix = cmds.xform(meshName, q=True, ws=True, matrix=True)
		#plockar ut andra kolumnen med 3 componenter, kommer motsvara en vektor som pekar i Y-riktning eftersom vi drar nytta av skalningen som 'alltid' är positiv
		#vi kunde lika gärna gjort en egen vektor (0,1,0) istället för (0,y-skalning,0)

		self.printMatrix(meshMatrix)

		transMatrix = om.MMatrix()
		om.MScriptUtil.createMatrixFromList(meshMatrix, transMatrix) 

		#printMatrix(meshMatrix)

		primaryUp = om.MVector(*meshMatrix[4:7])
		#polockar ut andra raden
		# have a secondary up vector for faces that are facing the same way as the original up
		# pekar i z-riktning
		secondaryUp = om.MVector(*meshMatrix[8:11])


		connectedFaces = om.MIntArray()
		
		faceIndecis = om.MIntArray()
		polyEdgesIds = om.MIntArray()
		dummy = om.MScriptUtil()
		edgeFaces = om.MIntArray()
		dummyIntPtr = dummy.asIntPtr()

		 #MStatus status
		# targetGeom är den markerade meshen

		edgeIter = om.MItMeshEdge(dagPath)
		vertexIter = om.MItMeshVertex(dagPath)
		faceIter = om.MItMeshPolygon(dagPath)

		self.vertex = [VertexData() for _ in xrange(vertexIter.count())]

		print "vertexIter.count()", vertexIter.count()

		i=0
		while not vertexIter.isDone():

			connectedFaces = om.MIntArray()
			vertexIter.getConnectedFaces(connectedFaces)

			self.vertex[i].connectedFaces = connectedFaces

			connectedVertices = om.MIntArray()
			vertexIter.getConnectedVertices(connectedVertices)

			self.vertex[i].connectedVertices = connectedVertices

			connectedEdges = om.MIntArray()
			vertexIter.getConnectedEdges(connectedEdges)

			self.vertex[i].connectedEdges = connectedEdges

			self.vertex[i].position = vertexIter.position()
			self.vertex[i].numberOfNeighbors = len(connectedVertices)
			i+=1
			vertexIter.next()


		i=0
		self.edges = [EdgeData() for _ in xrange(edgeIter.count())]
		while not edgeIter.isDone():

			connectedEdges = om.MIntArray()
			edgeIter.getConnectedEdges(connectedEdges)
			
			self.edges[i].connectedEdges = connectedEdges

			connectedFaces = om.MIntArray()
			edgeIter.getConnectedFaces(connectedFaces)

			self.edges[i].connectedFaces = connectedFaces

			self.edges[i].vertices.append(edgeIter.index(0))
			self.edges[i].vertices.append(edgeIter.index(1))

			self.edges[i].position = edgeIter.center()
			#self.edges[i].numberOfNeighbors = edgeIter.numConnectedEdges()
			i+=1
			edgeIter.next()

		# #initierar faceIter.count() antal toma polygons till objektet
		self.polygons = [PolyData() for _ in xrange(faceIter.count())]


		#print "edgeIter: " + str(edgeIter.index())
		# här loopar vi igenom alla faces i meshen
		i=0
		while not faceIter.isDone():
			#print "index: ", faceIter.index()
			#cfLength = edgeIter.getConnectedFaces(connectedFaces)
			self.polygons[i].normalAngel = 5.0


			self.polygons[i].position = faceIter.center()

			normal = om.MVector()
			faceIter.getNormal(normal)
			self.polygons[i].normal = normal

			#hittar de tre anslutande polygonen
			faceArray = om.MIntArray()
			faceIter.getConnectedFaces(faceArray)

			vertexArray = om.MIntArray()
			faceIter.getVertices(vertexArray)

			self.polygons[i].vertices = vertexArray

			#lägger till de tre anslutande polygonen i faceNeighbors listan
			self.polygons[i].connectedFaces = faceArray


			i+=1
			faceIter.next()

	# http://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
	def lineIntersection(self, A, B, C, D): 
		Bx_Ax = B.x - A.x 
		By_Ay = B.z - A.z
		Dx_Cx = D.x - C.x 
		Dy_Cy = D.z - C.z 

		determinant = (-Dx_Cx * By_Ay + Bx_Ax * Dy_Cy) 

		if abs(determinant) < 1e-20: 
			return None 

		s = (-By_Ay * (A.x - C.x) + Bx_Ax * (A.z - C.z)) / determinant 
		t = ( Dx_Cx * (A.z - C.z) - Dy_Cy * (A.x - C.x)) / determinant 

		intersectionPoint = om.MFloatPoint()

		if s >= 0 and s <= 1 and t >= 0 and t <= 1: 
			intersectionPoint.x = A.x + (t * Bx_Ax)
			intersectionPoint.y = 0
			intersectionPoint.z = A.z + (t * By_Ay)
			return intersectionPoint

		return None

	def slice(self,targetIds):

		conectedStartVertecis = self.vertex[targetIds[0]].connectedVertices
		endPos = self.vertex[targetIds[1]].position

		vertexDict = dict()

		# lägger in alla sträckor från grann vertex till end vertex i en dict
		for index in conectedStartVertecis:
			startPos = self.vertex[index].position
			distanceToGoal = math.sqrt(math.pow(endPos.x-startPos.x,2)+math.pow(endPos.z-startPos.z,2))
			vertexDict[index] = distanceToGoal

		vertexDict= sorted(vertexDict.items(), key=lambda x: x[1])

		startEdges = self.vertex[vertexDict[0][0]].connectedEdges
		# hittar start edge genom att jämföra de närmsta vertex till end och hitta vilket edge de delar 
		for index in startEdges:
			if self.edges[index].vertices[0] == vertexDict[0][0] and self.edges[index].vertices[1] == vertexDict[1][0]:
				startEdge = index
			if self.edges[index].vertices[1] == vertexDict[0][0] and self.edges[index].vertices[0] == vertexDict[1][0]:
				startEdge = index

		conectedEndVertecis = self.vertex[targetIds[1]].connectedVertices
		startPos = self.vertex[targetIds[0]].position

		vertexDict = dict()
		# lägger in alla sträckor från end vertex till start vertex i en dict
		for index in conectedEndVertecis:
			endPos = self.vertex[index].position
			distanceToStart = math.sqrt(math.pow(startPos.x-endPos.x,2)+math.pow(startPos.z-endPos.z,2))
			vertexDict[index] = distanceToStart

		vertexDict= sorted(vertexDict.items(), key=lambda x: x[1])

		endEdges = self.vertex[vertexDict[0][0]].connectedEdges

		# hittar start edge genom att jämföra de närmsta vertex till end och hitta vilket edge de delar 
		for index in endEdges:
			if self.edges[index].vertices[0] == vertexDict[0][0] and self.edges[index].vertices[1] == vertexDict[1][0]:
				endEdge = index
			if self.edges[index].vertices[1] == vertexDict[0][0] and self.edges[index].vertices[0] == vertexDict[1][0]:
				endEdge = index


		selectedEdges = []
		# test, remove later
		selectedEdges.append(startEdge)

		print "negativ z-sträcka"
		axis = 'z'
		index = 0

		currentIndex = self.getDirectionalEdges(startEdge, endEdge)

		while currentIndex != endEdge:
			if os.path.exists("c:/break"): break

			print "i: ", index
			selectedEdges.append(currentIndex)
			index += 1
			currentIndex = self.getDirectionalEdges(selectedEdges[index],endEdge)

		selectedEdges.append(endEdge)
		print "edgesInDirection", selectedEdges
		# self.currentMesh = OpenMaya.MFnMeshData().create()
		# fnMesh = OpenMaya.MFnMesh(self.currentMesh)
		# inFnMeshData = inMeshDataHandle.asMesh()
                

		selList = om.MSelectionList()
		om.MGlobal.getActiveSelectionList(selList)
		components = om.MObject()
		MFnMesh = om.MFnMesh()
		fMesh = om.MObject()
		mesh = om.MObject()
		dagPath = om.MDagPath()
		print "hej"
		selList.getDagPath(0,dagPath)

		meshNode = om.MObject()

		meshNode = dagPath.node()

		fMesh = meshNode
		#MFnMesh meshFn(fMesh);

		fnMesh = om.MFnMesh(fMesh)

		

		edgeFactors = om.MFloatArray()
		



		# splitPlacements = om.MIntArray()
		# edgeList = om.MIntArray()
		# internalPoints = om.MFloatPointArray()

		# for index in edgesInDirection:



		# 	edgeVtx0= self.edges[index].vertices[0]
		# 	edgeVtx1= self.edges[index].vertices[1]
		# 	print "edgeVtx0", edgeVtx0
		# 	intersectionPoint = self.lineIntersection(self.vertex[edgeVtx0].position,self.vertex[edgeVtx1].position,self.vertex[targetIds[0]].position,self.vertex[targetIds[1]].position)
		# 	if intersectionPoint is not None:
		# 		edgeList.append(index)
		# 		splitPlacements.append(om.MFnMesh.kOnEdge)

			
		# 		edgeFactors.append(0.5)
		# 		print "intersectionPoint", intersectionPoint.x, " ", intersectionPoint.z
		# 		#internalPoints.append(intersectionPoint)
		# 	else:
		# 		# intersectionPoint = om.MFloatPoint(0.0,0.0,0.0)
		# 		# internalPoints.append(intersectionPoint)
		# 		print "no intersection"

			
			
		#fnMesh.split(splitPlacements, edgeList, edgeFactors, internalPoints)

		return selectedEdges

	def surroundBuilding(self,targetIds):

		selectedVertices = []

		

		print "passed"
		poly_selectedList=[{'id':targetIds[0], 'x':self.vertex[targetIds[0]].position.x, 'z':self.vertex[targetIds[0]].position.z },
						   {'id':targetIds[1], 'x':self.vertex[targetIds[1]].position.x, 'z':self.vertex[targetIds[1]].position.z },
						   {'id':targetIds[2], 'x':self.vertex[targetIds[2]].position.x, 'z':self.vertex[targetIds[2]].position.z },
						   {'id':targetIds[3], 'x':self.vertex[targetIds[3]].position.x, 'z':self.vertex[targetIds[3]].position.z }]
		
		#sorted(poly_selectedList, key=lambda k: k['x'])

		poly_selectedList.sort(key=lambda x: (-x['x'],x['z']))

		startIndex = poly_selectedList[0]["id"]
		secondIndex = poly_selectedList[1]["id"]
		thirdIndex = poly_selectedList[3]["id"]
		fourthIndex = poly_selectedList[2]["id"]

		cornerIds = []
		cornerIds.append(startIndex)
		cornerIds.append(secondIndex)
		cornerIds.append(thirdIndex)
		cornerIds.append(fourthIndex)
		cornerIds.append(startIndex)

		print "startIndex", startIndex
		print "secondIndex", secondIndex
		print "thirdIndex", thirdIndex
		print "fourthIndex", fourthIndex

		#lägger till det först markeade facet
		selectedVertices.append(startIndex)

		print "negativ z-sträcka"
		axis = 'z'
		index = 0

		currentIndex = self.getDirectionalFace(selectedVertices[index],secondIndex)
		while currentIndex != secondIndex:
			if os.path.exists("c:/break"): break
			if currentIndex == secondIndex:
				print "found"
			selectedVertices.append(currentIndex)
			index += 1
			currentIndex = self.getDirectionalFace(selectedVertices[index],secondIndex)
			
			
		
		# print "negativ x-sträcka"
		# selectedVertices.append(secondIndex)
		# axis = 'x'
		# index += 1
		# currentIndex = self.getDirectionalFace(selectedVertices[index],thirdIndex)
		# while currentIndex != thirdIndex:
		# 	if os.path.exists("c:/break"): break
		# 	if currentIndex == thirdIndex:
		# 		print "found"
		# 	selectedVertices.append(currentIndex)
		# 	index += 1
		# 	currentIndex = self.getDirectionalFace(selectedVertices[index],thirdIndex)
			
			
			
			
		
		# print "positiv z-sträcka"
		# selectedVertices.append(thirdIndex)
		# axis = 'z'
		# index += 1
		# currentIndex = self.getDirectionalFace(selectedVertices[index],fourthIndex)
		# while currentIndex != fourthIndex:
		# 	if os.path.exists("c:/break"): break
		# 	if currentIndex == fourthIndex:
		# 		print "found" 
		# 	selectedVertices.append(currentIndex)
		# 	index += 1
		# 	currentIndex = self.getDirectionalFace(selectedVertices[index],fourthIndex)
			

		# print "positiv x-sträcka"
		# selectedVertices.append(fourthIndex)

		# index += 1
		# currentIndex = self.getDirectionalFace(selectedVertices[index],startIndex)
		# while currentIndex != startIndex:
		# 	if os.path.exists("c:/break"): break
		# 	if currentIndex == startIndex:
		# 		print "found"
		# 	selectedVertices.append(currentIndex)
		# 	index += 1
		# 	currentIndex = self.getDirectionalFace(selectedVertices[index],startIndex)
			
		# selectedVertices.append(startIndex)
		# axis = 'x'
		# index += 1

		return selectedVertices, cornerIds

	def getDirectionalEdges(self, selectedEdge, endIndex):
		goalPos= self.edges[endIndex].position

		currentPos= self.edges[selectedEdge].position
		

		CG = goalPos - currentPos

		goalMagnitude = math.sqrt(math.pow(CG.x,2)+math.pow(CG.y,2)+math.pow(CG.z,2))

		goalPosProduct = self.dotProduct(CG,currentPos)

		if goalMagnitude == 0.0:
			print "goalMagnitude is zero"
			return endIndex

		selectedEdgeNeighbors = self.edges[selectedEdge].connectedEdges

		closestAngel = 100

		foundCandidate = False


		angleDict = dict()
		for i in selectedEdgeNeighbors:
			neighborPos = self.edges[i].position

			CN = neighborPos - currentPos

			neighborMagnitude = math.sqrt(math.pow(CN.x,2)+math.pow(CN.y,2)+math.pow(CN.z,2))

			if neighborMagnitude == 0:
				print "neighborMagnitude = 0"
				foundIndex = i
				break

			
			neighborPosProduct = self.dotProduct(CG,CN)
			neighborAngel = math.acos((neighborPosProduct/(goalMagnitude*neighborMagnitude+0.00001)))

			neighborAngel = neighborAngel*(180/3.1416)

			angleDict[i] = neighborAngel
			if neighborAngel < closestAngel and self.edges[i].selected != True:

				foundIndex = i
				foundCandidate = True
				closestAngel = neighborAngel

		if foundCandidate == False:
			foundIndex = selectedEdgeNeighbors[0]
			print "nextVertex could not be found "

		self.edges[foundIndex].selected = True

		print "angleDict", angleDict
		
		print "foundIndex, " , foundIndex
		return foundIndex

	def getDirectionalFace(self, selectedVertex, endIndex):


		nextFace = -1

		goalPos= self.vertex[endIndex].position
		currentPos= self.vertex[selectedVertex].position



		CG = goalPos - currentPos

		goalMagnitude = math.sqrt(math.pow(CG.x,2)+math.pow(CG.y,2)+math.pow(CG.z,2))


		goalPosProduct = self.dotProduct(CG,currentPos)

		if goalMagnitude == 0.0:
			return endIndex


		selectedVertexNeighbors = self.vertex[selectedVertex].connectedVertices

		closestAngel = 100

		foundCandidate = False

		
		for i in selectedVertexNeighbors:
			neighborPos = self.vertex[i].position

			CN = neighborPos - currentPos

			neighborMagnitude = math.sqrt(math.pow(CN.x,2)+math.pow(CN.y,2)+math.pow(CN.z,2))

			if neighborMagnitude == 0:
				print "neighborMagnitude = 0"
				foundIndex = i
				break

			
			neighborPosProduct = self.dotProduct(CG,CN)
			neighborAngel = math.acos((neighborPosProduct/(goalMagnitude*neighborMagnitude+0.00001)))

			neighborAngel = neighborAngel*(180/3.1416)

			if neighborAngel < closestAngel and self.vertex[i].selected != True:

				foundIndex = i
				foundCandidate = True
				closestAngel = neighborAngel



		#method 2
		closestDistance = math.sqrt(math.pow(goalPos.x-currentPos.x,2)+math.pow(goalPos.z-currentPos.z,2))
		if foundCandidate == False:
			print "method 2"
			for index in selectedVertexNeighbors:
				neighborPos = self.vertex[index].position
				neighborToGoal = math.sqrt(math.pow(goalPos.x-neighborPos.x,2)+math.pow(goalPos.z-neighborPos.z,2))

				print "distance", closestDistance , " " , neighborToGoal, "selcted: ", self.vertex[index].selected
				if neighborToGoal < closestDistance and self.vertex[index].selected == False:
					print "found"
					foundIndex = index
					foundCandidate = True
					closestDistance = neighborToGoal

		if foundCandidate == False:
			foundIndex = selectedVertexNeighbors[0]
			print "nextVertex could not be found "

		print "foundIndex", foundIndex

		self.vertex[foundIndex].selected = True
		

		return foundIndex

	def selectPolygonsBorder2(self, selectedEdges, centerPolygon):



		self.polygonBorder = []

		print "centerPolygon", centerPolygon[0]

		vertexBorder = []
		for index in selectedEdges:
			vertexBorder.append(self.edges[index].vertices[0])
			vertexBorder.append(self.edges[index].vertices[1])

		print "unsorted", vertexBorder

		sorted = False  # We haven't started sorting yet

		for i in range(0, len(vertexBorder) - 1):
			if os.path.exists("c:/break"): break
			for j in range(0, len(vertexBorder) - 1 - i):
				if os.path.exists("c:/break"): break
				if self.less(self.vertex[j].position,self.vertex[j+1].position,self.polygons[centerPolygon[0]].position):
					vertexBorder[j], vertexBorder[j+1] = vertexBorder[j+1], vertexBorder[j] 
					


			

		print "sorted", vertexBorder

		i = 0
		f0_v_pos_prev = 0
		for index_e in selectedEdges: 
			connectedFaces = self.edges[index_e].connectedFaces
			

			for index_f0_v in range(0,3):
				if self.polygons[connectedFaces[0]].vertices[index_f0_v] != self.edges[index_e].vertices[0] and self.polygons[connectedFaces[0]].vertices[index_f0_v] != self.edges[index_e].vertices[1]:
					z_dist_f0 = self.vertex[self.polygons[connectedFaces[0]].vertices[index_f0_v]].position.z-self.edges[index_e].position.z
					x_dist_f0 = self.vertex[self.polygons[connectedFaces[0]].vertices[index_f0_v]].position.x-self.edges[index_e].position.x
					f0_v_pos = self.vertex[self.polygons[connectedFaces[0]].vertices[index_f0_v]].position
					height_f0 = self.vertex[self.polygons[connectedFaces[0]].vertices[index_f0_v]].position.y
					notOnLineVtx_f0 = index_f0_v

			dist_f0 = math.sqrt(math.pow(x_dist_f0,2)+math.pow(z_dist_f0,2))

			prevVertexDist_f0 = math.sqrt(math.pow(f0_v_pos.x-f0_v_pos.x,2)+math.pow(f0_v_pos.y-f0_v_pos.y,2)+math.pow(f0_v_pos.z-f0_v_pos.z,2)) 


			if self.less(self.vertex[self.edges[index_e].vertices[0]].position,self.vertex[self.edges[index_e].vertices[1]].position,self.polygons[centerPolygon[0]].position):
				if self.isOutside( self.vertex[self.edges[index_e].vertices[0]].position, self.vertex[self.edges[index_e].vertices[1]].position, f0_v_pos, 1):
					isOutside_f0 = True
				else: 
					isOutside_f0 = False
			elif self.less(self.vertex[self.edges[index_e].vertices[1]].position,self.vertex[self.edges[index_e].vertices[0]].position,self.polygons[centerPolygon[0]].position):
				if self.isOutside( self.vertex[self.edges[index_e].vertices[1]].position, self.vertex[self.edges[index_e].vertices[0]].position, f0_v_pos, 1):
					isOutside_f0 = True
				else: 
					isOutside_f0 = False

			f0_v_pos_prev = f0_v_pos
			for index_f1_v in range(0,3):
				if self.polygons[connectedFaces[1]].vertices[index_f1_v] != self.edges[index_e].vertices[0] and self.polygons[connectedFaces[1]].vertices[index_f1_v] != self.edges[index_e].vertices[1]:
					z_dist_f1 = self.vertex[self.polygons[connectedFaces[1]].vertices[index_f1_v]].position.z-self.edges[index_e].position.z
					x_dist_f1 = self.vertex[self.polygons[connectedFaces[1]].vertices[index_f1_v]].position.x-self.edges[index_e].position.x
					f1_v_pos = self.vertex[self.polygons[connectedFaces[1]].vertices[index_f1_v]].position
					height_f1 = self.vertex[self.polygons[connectedFaces[1]].vertices[index_f0_v]].position.y

			if self.less(self.vertex[self.edges[index_e].vertices[0]].position,self.vertex[self.edges[index_e].vertices[1]].position,self.polygons[centerPolygon[0]].position):
				if self.isOutside( self.vertex[self.edges[index_e].vertices[0]].position, self.vertex[self.edges[index_e].vertices[1]].position, f1_v_pos, 1):
					isOutside_f1 = True
				else: 
					isOutside_f1 = False
			if self.less(self.vertex[self.edges[index_e].vertices[1]].position,self.vertex[self.edges[index_e].vertices[0]].position,self.polygons[centerPolygon[0]].position):
				if self.isOutside( self.vertex[self.edges[index_e].vertices[1]].position, self.vertex[self.edges[index_e].vertices[0]].position, f1_v_pos, 1):
					isOutside_f1 = True
				else: 
					isOutside_f1 = False

			dist_f1 = math.sqrt(math.pow(x_dist_f1,2)+math.pow(z_dist_f1,2))

			prevVertexDist_f0 = math.sqrt(math.pow(f0_v_pos.x-f0_v_pos.x,2)+math.pow(f0_v_pos.y-f0_v_pos.y,2)+math.pow(f0_v_pos.z-f0_v_pos.z,2)) 

			
			if isOutside_f0 == False:
				print "first"
				self.polygons[connectedFaces[0]].selected = True
				self.polygonBorder.append(connectedFaces[0])
			elif height_f0 > height_f1:
				print "height"
				self.polygons[connectedFaces[0]].selected = True
				self.polygonBorder.append(connectedFaces[0])
			elif dist_f0 < dist_f1 :
				print "dist"
				self.polygons[connectedFaces[0]].selected = True
				self.polygonBorder.append(connectedFaces[0])
			# elif dist_f0 > dist_f1:
			# 	print "dist"
			# 	self.polygonBorder.append(connectedFaces[1])
			# elif height_f0 > height_f1:
			# 	print "height"
			# 	self.polygonBorder.append(connectedFaces[0])
			# elif isOutside_f0 == False:
			# 	print "outside"
			# 	self.polygonBorder.append(connectedFaces[0])
			else:
				print "else"
				self.polygons[connectedFaces[1]].selected = True
				self.polygonBorder.append(connectedFaces[1])


			print self.polygonBorder[i]

			i=i+1

		connectedFaces = self.polygons[centerPolygon[0]].connectedFaces
		print "centerPolygon", centerPolygon[0]
		for i in range(0,100):
			if os.path.exists("c:/break"): break
			print i
			connectedFaces = self.growSelection(connectedFaces)

		for index in self.polygonBorder:
			self.polygons[index].selected=False

		return self.polygonBorder

	def	less(self,a, b,center):
	
		if (a.x - center.x >= 0 and b.x - center.x < 0):
			return True;
		if (a.x - center.x < 0 and b.x - center.x >= 0):
			return False
		if (a.x - center.x == 0 and b.x - center.x == 0): 
			if (a.z - center.z >= 0 or b.z - center.z >= 0):
				return a.z > b.z
			return b.z > a.z
		

		# compute the cross product of vectors (center -> a) x (center -> b)
		det = (a.x - center.x) * (b.z - center.z) - (b.x - center.x) * (a.z - center.z)
		if (det < 0):
			return True
		if (det > 0):
			return False

		# points a and b are on the same line from the center
		# check which point is closer to the center
		d1 = (a.x - center.x) * (a.x - center.x) + (a.z - center.z) * (a.z - center.z)
		d2 = (b.x - center.x) * (b.x - center.x) + (b.z - center.z) * (b.z - center.z)
		return d1 > d2
	


	def selectPolygonsBorder(self, selectedVertices, cornerIds, centerPolygon):

		self.polygonBorder = []
		cornerLength = 5
		i=0
		print "first", self.vertex[cornerIds[0]].position.x, " ", self.vertex[cornerIds[0]].position.z
		print "second", self.vertex[cornerIds[1]].position.x, " ", self.vertex[cornerIds[1]].position.z
		print "third", self.vertex[cornerIds[2]].position.x, " ", self.vertex[cornerIds[2]].position.z
		print "fourth", self.vertex[cornerIds[3]].position.x, " ", self.vertex[cornerIds[3]].position.z
		print "end", self.vertex[cornerIds[4]].position.x, " ", self.vertex[cornerIds[4]].position.z

		

		for cornerId in range(0,cornerLength-1):
			startCorner = cornerIds[cornerId]
			endCorner = cornerIds[cornerId+1]

			startCornerPos = self.vertex[startCorner].position
			endCornerPos = self.vertex[endCorner].position

			margin = 0.1

			if cornerId == 0:
				startCornerPos.x=startCornerPos.x+margin
				endCornerPos.x=endCornerPos.x+margin
				sign = 1
			if cornerId == 1:
				startCornerPos.z=startCornerPos.z-margin
				endCornerPos.z=endCornerPos.z-margin
				sign = 1
			if cornerId == 2:
				startCornerPos.x=startCornerPos.x-margin
				endCornerPos.x=endCornerPos.x-margin
				sign = 1
			if cornerId == 3:
				startCornerPos.z=startCornerPos.z+margin
				endCornerPos.z=endCornerPos.z+margin
				sign = 1

			print "cornerId",cornerId

			

			while selectedVertices[i] != endCorner:


				currentVertex = selectedVertices[i]
				connectedPolygons = self.vertex[currentVertex].connectedFaces

				for connectedPoly in connectedPolygons:
					if os.path.exists("c:/break"): break
					

					vtx1 = self.vertex[self.polygons[connectedPoly].vertices[0]].position
					vtx2 = self.vertex[self.polygons[connectedPoly].vertices[1]].position
					vtx3 = self.vertex[self.polygons[connectedPoly].vertices[2]].position


					isOutside1 = False
					isOutside2 = False
					isOutside3 = False
					# if self.isOutside(startCornerPos,endCornerPos, vtx1, sign):
					# 	isOutside1 = True
					# if self.isOutside(startCornerPos,endCornerPos, vtx2, sign):
					# 	isOutside2 = True
					# if self.isOutside(startCornerPos,endCornerPos, vtx3, sign):
					# 	isOutside3 = True


					tolerance = 40
					if isOutside1 == True or isOutside2 == True or isOutside3 == True:
						nej = 1
					else:
						if self.polygons[connectedPoly].selected == False: # and self.polygons[connectedPoly].position.y > self.vertex[currentVertex].position.y :
							self.polygons[connectedPoly].selected = True
							self.polygonBorder.append(connectedPoly)
				i = i+1
		allFaces = []
		connectedVertices = self.polygons[centerPolygon[0]].vertices

		self.polygonBorder.append(centerPolygon[0])

		connectedFaces = self.polygons[centerPolygon[0]].connectedFaces


		# for i in range(0,50):
		# 	if os.path.exists("c:/break"): break
		# 	print i
		# 	connectedFaces = self.growSelection(connectedFaces)

		for index in self.polygonBorder:
			self.polygons[index].selected=False

		return self.polygonBorder

	def growSelection(self, connectedFaces):
		connectedVertices3 = []


		for index in connectedFaces:
			

			if self.polygons[index].selected == False:
				connectedVertices3.append(self.polygons[index].connectedFaces[0])
				connectedVertices3.append(self.polygons[index].connectedFaces[1])
				connectedVertices3.append(self.polygons[index].connectedFaces[2])
				self.polygons[index].selected = True
				self.polygonBorder.append(index)

		return	connectedVertices3

	# if the sign/value is positive it returns true, the point is outside the building 
	def	isOutside(self,pointA, pointB, pointC, sign):
		if sign == 1:
			return ((pointB.x - pointA.x)*(pointC.z - pointA.z) - (pointB.z - pointA.z)*(pointC.x - pointA.x)) > 0
		elif sign == -1:
			return ((pointB.x - pointA.x)*(pointC.z - pointA.z) - (pointB.z - pointA.z)*(pointC.x - pointA.x)) < 0

	def dotProduct2D(self,poit1,point2):

		return poit1.x*point2.x+poit1.z*point2.z
	
	def dotProduct(self,poit1,point2):

		return poit1.x*point2.x+poit1.y*point2.y+poit1.z*point2.z



#######################################################################################################################


class VertexData:

#----------------------------------------------------------------------------------------------------------------------
	def __init__(self):
		self.selected = False
		self.connectedEdges = []
		self.connectedFaces = []
		self.connectedVertices= []
		self.position = om.MPoint(0,0,0)
		self.numberOfNeighbors = 0

class EdgeData:

#----------------------------------------------------------------------------------------------------------------------
	def __init__(self):
		self.selected = False
		self.normalAngel = 0.0
		self.vertices = []
		self.connectedEdges = []
		self.connectedFaces = []
		self.position = om.MPoint(0,0,0)
		self.numberOfNeighbors = 0



class PolyData:

#----------------------------------------------------------------------------------------------------------------------
	def __init__(self):
		self.selected = False
		self.normalAngel = 0.0
		self.connectedFaces = []
		self.vertices = []
		self.position = om.MPoint(0,0,0)
		self.normal = om.MVector(0,0,0)
		self.faceMatrix = om.MMatrix()

#----------------------------------------------------------------------------------------------------------------------
	def __str__(self):
		endStr = '\n'
		outStr = ''
		outStr += ', selected = ' + str(self.selected) + endStr
		for key in self.connectedFaces:
			outStr += '[' + str(key) + '] = ' + str(self.connectedFaces[key]) + endStr
		return outStr

#######################################################################################################################


def run():
	classObj = polySelector()
	return classObj



	