import maya.OpenMaya as om
import maya.cmds as cmds
import math
from operator import itemgetter, attrgetter, methodcaller

def printMatrix(matrix):
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

def printMMatrix(matrix):
	endStr = '\n'
	outStr = ''
	outStr += endStr

	for r in range(0,4):
		for c in range(0,4):
			outStr += str(matrix(r,c)) + str(' ')
		outStr += endStr

	print 'transformation: ',  outStr


meshTransform = 'flygtest1:default1'
meshShape = cmds.listRelatives(meshTransform, c=True)[0]

#transformations matris, skala och translatering
meshMatrix = cmds.xform(meshTransform, q=True, ws=True, matrix=True)
#plockar ut andra kolumnen med 3 componenter, kommer motsvara en vektor som pekar i Y-riktning eftersom vi drar nytta av skalningen som 'alltid' är positiv
#vi kunde lika gärna gjort en egen vektor (0,1,0) istället för (0,y-skalning,0) 

printMatrix(meshMatrix)

primaryUp = om.MVector(*meshMatrix[4:7])
#polockar ut andra raden
# have a secondary up vector for faces that are facing the same way as the original up
# pekar i z-riktning
secondaryUp = om.MVector(*meshMatrix[8:11])

#lägger till det aktiva objektet i en lista
sel = om.MSelectionList()
sel.add(meshShape)

#hämtar meshen
meshObj = om.MObject()
sel.getDependNode(0, meshObj)

# skapar en iterator till alla polygon i meshen
meshPolyIt = om.MItMeshPolygon(meshObj)
faceNeighbors = []
faceCoordinates = []
normals = []
polyPosition = []
selectedFacesList = []
lastIndex = -1


# while not meshPolyIt.isDone():

# 	normal = om.MVector()
# 	meshPolyIt.getNormal(normal)

# 	position = om.MPointArray()
# 	vtxPointZero = meshPolyIt.center() 

# 	polyPosition.append(vtxPointZero)
# 	normals.append(normal)

# 	# use the seconary up if the normal is facing the same direction as the object Y
# 	# typ andra raden från transformationsmatrisen
# 	up = primaryUp if (1 - abs(primaryUp * normal)) > 0.001 else secondaryUp

# 	# Return the position of the center of the current polygon i förhållande till pivot.
# 	center = meshPolyIt.center()

# 	#hittar de tre anslutande polygonen
# 	faceArray = om.MIntArray()
# 	meshPolyIt.getConnectedFaces(faceArray)

# 	meshPolyIt.next()

# 	#lägger till de tre anslutande polygonen i faceNeighbors listan
# 	faceNeighbors.append([faceArray[i] for i in range(faceArray.length())])

# 	xAxis = up ^ normal
# 	yAxis = normal ^ xAxis


# 	matrixList = [xAxis.x, xAxis.y, xAxis.z, 0,
# 				  yAxis.x, yAxis.y, yAxis.z, 0,
# 				  normal.x, normal.y, normal.z, 0,
# 				  center.x, center.y, center.z, 1]

# 	# skapar matrisen och lägger till den i faceCoordinates
# 	faceMatrix = om.MMatrix()
# 	om.MScriptUtil.createMatrixFromList(matrixList, faceMatrix)

# 	# varje polygon får en matris
# 	faceCoordinates.append(faceMatrix)




def getUpFace(faceIndex):
	poly_ids = []
	poly_ids = ui_setTargetGeometry()

	sel = om.MSelectionList()
	om.MGlobal.getActiveSelectionList(sel)

	mdag = om.MDagPath()
	sel.getDagPath(0, mdag)

	print "poly_ids: ",  poly_ids[0]

	# Create an MIntArray and populate it with component ids to add to our component object
	# MIntArray takes an array of ints. That has to be passed using an MScriptUtil pointer
	# This is where you would use your list of polyIds that you had gotten
	#poly_ids = [faceIndex]
	util = om.MScriptUtil()
	util.createFromList(poly_ids, len(poly_ids))
	ids_ptr = util.asIntPtr()
	polyids = om.MIntArray(ids_ptr, len(poly_ids))

	# Create a singleIndexedComponent of type polygon
	mfn_components = om.MFnSingleIndexedComponent()
	components = mfn_components.create(om.MFn.kMeshPolygonComponent)
	# Add our MIntArray of ids to the component
	mfn_components.addElements(polyids)

	to_sel = om.MSelectionList()
	# The object the selection refers to, and the components on that object to select
	to_sel.add(mdag, components)
	om.MGlobal.setActiveSelectionList(to_sel)

	#return getDirectionalFace(faceIndex, om.MVector(0,1,0))

def getDownFace(faceIndex):
	return getDirectionalFace(faceIndex, om.MVector(0,-1,0))

def getRightFace(faceIndex):
	return getDirectionalFace(faceIndex, om.MVector(1,0,0))

def getLeftFace(faceIndex):
	return getDirectionalFace(faceIndex, om.MVector(-1,0,0))

# selectedFaces är en target face (som är markerad sen innan)
def getDirectionalFace(selectedFaces, axis, endIndex, lastIndex):
	startFaceMatrix = faceCoordinates[selectedFaces]
	endFaceMatrix = faceCoordinates[endIndex]

	nMatrix = faceCoordinates[endIndex] * startFaceMatrix.inverse()
	nVector = om.MVector(nMatrix(3,0), nMatrix(3,1), nMatrix(3,2))

	nextFace = -1
	selectedFacesList.append(selectedFaces)
	goalVtx= polyPosition[endIndex]

	selectedFaceNeighbors = faceNeighbors[selectedFaces]

	

	numberOfNeighbors = len(selectedFaceNeighbors)


	if numberOfNeighbors == 3:
		distance1_3D = math.sqrt(math.pow(goalVtx.x-polyPosition[selectedFaceNeighbors[0]].x,2)+math.pow(goalVtx.y-polyPosition[selectedFaceNeighbors[0]].y,2)+math.pow(goalVtx.z-polyPosition[selectedFaceNeighbors[0]].z,2))
		distance2_3D = math.sqrt(math.pow(goalVtx.x-polyPosition[selectedFaceNeighbors[1]].x,2)+math.pow(goalVtx.y-polyPosition[selectedFaceNeighbors[1]].y,2)+math.pow(goalVtx.z-polyPosition[selectedFaceNeighbors[1]].z,2))
		distance3_3D = math.sqrt(math.pow(goalVtx.x-polyPosition[selectedFaceNeighbors[2]].x,2)+math.pow(goalVtx.y-polyPosition[selectedFaceNeighbors[2]].y,2)+math.pow(goalVtx.z-polyPosition[selectedFaceNeighbors[2]].z,2))

		distance1_2D = math.sqrt(math.pow(goalVtx.x-polyPosition[selectedFaceNeighbors[0]].x,2)+math.pow(goalVtx.y-polyPosition[selectedFaceNeighbors[0]].y,2))
		distance2_2D = math.sqrt(math.pow(goalVtx.x-polyPosition[selectedFaceNeighbors[1]].x,2)+math.pow(goalVtx.y-polyPosition[selectedFaceNeighbors[1]].y,2))
		distance3_2D = math.sqrt(math.pow(goalVtx.x-polyPosition[selectedFaceNeighbors[2]].x,2)+math.pow(goalVtx.y-polyPosition[selectedFaceNeighbors[2]].y,2))
	elif numberOfNeighbors == 2:
		distance1_3D = abs(goalVtx-getattr(polyPosition[selectedFaceNeighbors[0]],str(axis)))
		distance2_3D = abs(goalVtx-getattr(polyPosition[selectedFaceNeighbors[1]],str(axis)))
		# något som är större än distance1 och distance2
		distance3_3D = distance1_3D+distance2_3D

	elif numberOfNeighbors == 1:
		distance1_3D = abs(goalVtx-getattr(polyPosition[selectedFaceNeighbors[0]],str(axis)))
		# något som är större än distance1
		distance2_3D = distance1+distance1_3D
		distance3_3D = distance1+distance1_3D



	if distance1_3D<distance2_3D and distance1_3D<distance3_3D:
		nextFace = selectedFaceNeighbors[0]
	elif distance3_3D<distance1_3D and distance3_3D<distance2_3D:
	 	nextFace = selectedFaceNeighbors[2]
	elif distance2_3D<distance3_3D and distance2_3D<distance1_3D:
		nextFace = selectedFaceNeighbors[1]

	#om nextFace redan redan är markerat, välj en annan granne
	for n in selectedFacesList:
		if(numberOfNeighbors == 2):
			if n == selectedFaceNeighbors[0]:
				nextFace = selectedFaceNeighbors[1]
			elif  n == selectedFaceNeighbors[1] and numberOfNeighbors == 2:
				nextFace = selectedFaceNeighbors[0]

		elif(numberOfNeighbors == 3):
			if n == selectedFaceNeighbors[0] and distance2_3D<distance3_3D:
				nextFace = selectedFaceNeighbors[1]
				#print "case1"
			elif n == selectedFaceNeighbors[0] and distance2_3D>distance3_3D:
				nextFace = selectedFaceNeighbors[2]
				#print "case2"
			elif n == selectedFaceNeighbors[1] and distance1_3D<distance3_3D:
				nextFace = selectedFaceNeighbors[0]
				#print "case3"
			elif n == selectedFaceNeighbors[1] and distance1_3D>distance3_3D:
				nextFace = selectedFaceNeighbors[2]
				#print "case4"
			elif n == selectedFaceNeighbors[2] and distance1_3D<distance2_3D:
				nextFace = selectedFaceNeighbors[0]
				#print "case5"
			elif n == selectedFaceNeighbors[2] and distance1_3D>distance2_3D:
				nextFace = selectedFaceNeighbors[1]
				#print "case6"

		 	
	#print "nextFace", nextFace
	return nextFace

def ui_setTargetGeometry():
	targetGeom = []

	selList = om.MSelectionList()
	#lägger till markerade faces i listan selList
	om.MGlobal.getActiveSelectionList(selList)

	if selList.isEmpty():
		print "no targets"
		return

	

	# itererar igenom listan med markerade faces
	selListIter = om.MItSelectionList(selList)
	while not selListIter.isDone():
		print "selListIter"

		components = om.MObject()
		dagPath = om.MDagPath()
		selListIter.getDagPath(dagPath, components)

		if components.isNull():   
			selListIter.next()
			continue

		compListFn = om.MFnComponent(components)
		compType = compListFn.componentType()


		# kontrollerar om det finns ett polygon i komponenterna
		if compType == om.MFn.kMeshPolygonComponent:
			# styckar ut en enstaka komponent från alla markerade komponenter
			compListFn = om.MFnSingleIndexedComponent(components)
			targetIds = om.MIntArray()
			# äntligen får vi ut face id:et
			compListFn.getElements(targetIds)
			print "selListIter: "+ str(targetIds)
			print "element: ", compListFn.element(1) 
			selItem = SelectionItem(dagPath, targetIds)
			pathName = dagPath.fullPathName()
			subName = pathName[(pathName.find("|")+1):len(pathName)]
			meshName = subName[0:(subName.find("|"))]
			print "dagPath" + str(meshName)
			# lägger till den markerade facet/componenten i en lista
			targetGeom.append(selItem)


		selListIter.next()

	if not targetGeom :
		print "somthing is wrong" 
		return


	#transformations matris, skala och translatering
	meshMatrix = cmds.xform(meshName, q=True, ws=True, matrix=True)
	#plockar ut andra kolumnen med 3 componenter, kommer motsvara en vektor som pekar i Y-riktning eftersom vi drar nytta av skalningen som 'alltid' är positiv
	#vi kunde lika gärna gjort en egen vektor (0,1,0) istället för (0,y-skalning,0) 

	printMatrix(meshMatrix)

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
	polyData = []
	 #MStatus status
	# targetGeom är den markerade meshen
	for obj in targetGeom :
		edgeIter = om.MItMeshEdge(obj.dagPath)
		faceIter = om.MItMeshPolygon(obj.dagPath)
		print "obj"

		# skapar ett nytt klassobjekt
		objPolyData = ObjectPolyData()
		# lägger till klassobjektet i listan
		polyData.append(objPolyData)
		# initierar dagPath
		objPolyData.dagPath = obj.dagPath
		#initierar faceIter.count() antal toma polygons till objektet
		objPolyData.polygons = [PolyData() for _ in xrange(faceIter.count())]

		#print "edgeIter: " + str(edgeIter.index())
		# här loopar vi igenom alla edges i meshen
		i=0
		while not faceIter.isDone():
			#print "index: ", faceIter.index()
			#cfLength = edgeIter.getConnectedFaces(connectedFaces)
			polyData = objPolyData.polygons[i]
			objPolyData.polygons[i].normalAngel = 5.0

			# itererar igenom alla edges
			faceIter.getEdges(polyEdgesIds)

			for edgeId in polyEdgesIds:

					edgeIter.setIndex(edgeId, dummyIntPtr)
					cfLength = edgeIter.getConnectedFaces(edgeFaces)

					if cfLength == 2 :
						# bestämmer vilket face utav två index som ska tilldelas med normalens vinkel
						otherFace = edgeFaces[1] if edgeFaces[0] == i else edgeFaces[0]
						polyData.connectedFaces[otherFace] = 1.0

			
			i += 1

			normal = om.MVector()
			faceIter.getNormal(normal)

			position = om.MPointArray()
			vtxPointZero = faceIter.center() 

			polyPosition.append(vtxPointZero)
			normals.append(normal)

			# use the seconary up if the normal is facing the same direction as the object Y
			# typ andra raden från transformationsmatrisen
			up = primaryUp if (1 - abs(primaryUp * normal)) > 0.001 else secondaryUp

			# Return the position of the center of the current polygon i förhållande till pivot.
			center = faceIter.center()

			#hittar de tre anslutande polygonen
			faceArray = om.MIntArray()
			faceIter.getConnectedFaces(faceArray)


			#lägger till de tre anslutande polygonen i faceNeighbors listan
			faceNeighbors.append([faceArray[i] for i in range(faceArray.length())])

			xAxis = up ^ normal
			yAxis = normal ^ xAxis


			matrixList = [xAxis.x, xAxis.y, xAxis.z, 0,
						  yAxis.x, yAxis.y, yAxis.z, 0,
						  normal.x, normal.y, normal.z, 0,
						  center.x, center.y, center.z, 1]

			# skapar matrisen och lägger till den i faceCoordinates
			faceMatrix = om.MMatrix()
			om.MScriptUtil.createMatrixFromList(matrixList, faceMatrix)

			# varje polygon får en matris
			faceCoordinates.append(faceMatrix)
					faceIter.next()
		


	neighborFaces = []
	selectedFaces = []




	poly_selectedList=[{'id':targetIds[0], 'x':polyPosition[targetIds[0]].x, 'z':polyPosition[targetIds[0]].y },
					   {'id':targetIds[1], 'x':polyPosition[targetIds[1]].x, 'z':polyPosition[targetIds[1]].y },
					   {'id':targetIds[2], 'x':polyPosition[targetIds[2]].x, 'z':polyPosition[targetIds[2]].y },
					   {'id':targetIds[3], 'x':polyPosition[targetIds[3]].x, 'z':polyPosition[targetIds[3]].y }]
	
	#sorted(poly_selectedList, key=lambda k: k['x'])

	poly_selectedList.sort(key=lambda x: (-x['x'],x['z']))

	startIndex = poly_selectedList[0]["id"]
	secondIndex = poly_selectedList[1]["id"]
	thirdIndex = poly_selectedList[3]["id"]
	fourthIndex = poly_selectedList[2]["id"]

	print "startIndex", startIndex
	print "secondIndex", secondIndex
	print "thirdIndex", thirdIndex
	print "fourthIndex", fourthIndex

	#lägger till det först markeade facet
	selectedFaces.append(startIndex)

	print "negativ z-sträcka"
	axis = 'z'
	index = 0

	currentIndex = getDirectionalFace(selectedFaces[index], axis, secondIndex, -1)
	while  currentIndex != secondIndex:
		if currentIndex == secondIndex:
			print "found"
		selectedFaces.append(currentIndex)
		index += 1
		currentIndex = getDirectionalFace(selectedFaces[index], axis, secondIndex, selectedFaces[-2])
		
		
	
	print "negativ x-sträcka"
	selectedFaces.append(secondIndex)
	axis = 'x'
	index += 1
	currentIndex = getDirectionalFace(selectedFaces[index], axis, thirdIndex, selectedFaces[-2])
	while  currentIndex != thirdIndex:
		if currentIndex == thirdIndex:
			print "found"
		selectedFaces.append(currentIndex)
		index += 1
		currentIndex = getDirectionalFace(selectedFaces[index], axis, thirdIndex, selectedFaces[-2])
		
		
		
		
	
	print "positiv z-sträcka"
	selectedFaces.append(thirdIndex)
	axis = 'z'
	index += 1
	currentIndex = getDirectionalFace(selectedFaces[index], axis, fourthIndex, selectedFaces[-2])
	while currentIndex != fourthIndex:
		if currentIndex == fourthIndex:
			print "hi" 
		selectedFaces.append(currentIndex)
		index += 1
		currentIndex = getDirectionalFace(selectedFaces[index], axis, fourthIndex, selectedFaces[-2])
		

	print "positiv x-sträcka"
	selectedFaces.append(fourthIndex)
	axis = 'x'
	index += 1
	currentIndex = getDirectionalFace(selectedFaces[index], axis, startIndex,selectedFaces[-2])
	while currentIndex != startIndex:
		if currentIndex == startIndex:
			print "found"
		selectedFaces.append(currentIndex)
		index += 1
		currentIndex = getDirectionalFace(selectedFaces[index], axis, startIndex,selectedFaces[-2])
		
		

	return selectedFaces

#######################################################################################################################

class PolyData:

#----------------------------------------------------------------------------------------------------------------------
	def __init__(self):
		self.selected = False
		self.normalAngel = 0.0
		self.connectedFaces = {}

#----------------------------------------------------------------------------------------------------------------------
	def __str__(self):
		endStr = '\n'
		outStr = ''
		outStr += ', selected = ' + str(self.selected) + endStr
		for key in self.connectedFaces:
			outStr += '[' + str(key) + '] = ' + str(self.connectedFaces[key]) + endStr
		return outStr

#######################################################################################################################

class ObjectPolyData:

#----------------------------------------------------------------------------------------------------------------------
	def __init__(self):
		self.dagPath = None
		self.polygons = []

#----------------------------------------------------------------------------------------------------------------------
	def __str__(self):
		endStr = '\n'
		outStr = ''
		outStr += 'DagPath = ' + self.dagPath.fullPathName() + endStr
		for i, poly in enumerate(self.polygons):
			outStr += 'polyId = ' + str(i) + endStr
			outStr += str(poly) + endStr
		return outStr  

class SelectionItem:

#----------------------------------------------------------------------------------------------------------------------
	def __init__(self, dagPath, polyIds):
		self.dagPath = dagPath
		self.polyIds = polyIds

#----------------------------------------------------------------------------------------------------------------------
	def __str__(self):
		endStr = '\n'
		outStr = ''
		outStr += 'DagPath = ' + self.dagPath.fullPathName() + endStr
		for i, elem in enumerate(self.polyIds):
			outStr += 'polyIds[' + str(i) + '] = ' + str(self.polyIds[i]) + endStr
		return outStr