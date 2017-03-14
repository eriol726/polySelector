import maya.OpenMaya as om
import maya.cmds as cmds
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


meshTransform = 'icaOrigo:Object002'
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


while not meshPolyIt.isDone():

	normal = om.MVector()
	meshPolyIt.getNormal(normal)

	position = om.MPointArray()
	vtxPointZero = meshPolyIt.center()

	#print "normal: ",  position[0].x , " " , position(0) , " " , position(0) 
	# print "primaryUp: ",  primaryUp.x , " " , primaryUp.y , " " , primaryUp.z
	# print "secondaryUp: ",  secondaryUp.x , " " , secondaryUp.y , " " , secondaryUp.z  

	polyPosition.append(vtxPointZero)
	normals.append(normal)


	#printMatrix(meshMatrix)

	


	# use the seconary up if the normal is facing the same direction as the object Y
	# typ andra raden från transformationsmatrisen
	up = primaryUp if (1 - abs(primaryUp * normal)) > 0.001 else secondaryUp

	# if meshPolyIt.index() == 5:
	# 	print "primaryUp * normal: ", primaryUp * normal
	# 	print "up: ",  up.x , " " , up.y , " " , up.z 	

	# Return the position of the center of the current polygon i förhållande till pivot.
	center = meshPolyIt.center()

	#hittar de tre anslutande polygonen
	faceArray = om.MIntArray()
	meshPolyIt.getConnectedFaces(faceArray)

	meshPolyIt.next()

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

# faceIndex är en target face (som är markerad sen innan)
def getDirectionalFace(selectedFaces, axis, endIndex):
	startFaceMatrix = faceCoordinates[selectedFaces]
	endFaceMatrix = faceCoordinates[endIndex]
	#print "endIndex", endIndex
	nMatrix = faceCoordinates[endIndex] * startFaceMatrix.inverse()
	nVector = om.MVector(nMatrix(3,0), nMatrix(3,1), nMatrix(3,2))



	#printMMatrix(startFaceMatrix)
	#printMatrix(startFaceMatrix)
	#printMatrix(endFaceMatrix)

	#print "printMatrix: ", printMatrix(endFaceMatrix.inverse())

	#endDp = nVector * axis
	#print "endDp", endDp

	#print "nVector", nVector.x, " ", nVector.y ," ", nVector.z
	closestVtx = -1
	closestDotProd = -1.0
	nextFace = -1
	selectedFacesList.append(selectedFaces)
	goalVtx= getattr(polyPosition[endIndex], str(axis))

	selectedFaceNeighbors = faceNeighbors[selectedFaces]

	numberOfNeighbors = len(selectedFaceNeighbors)




	# multiplicerar granne-polygon-matriserna med det valda polygonet faceIndex
	i=0
	#for n in faceNeighbors[selectedFaces]:
		
		#print "normal: ",  normals[n].x, ' ', normals[n].y, ' ', normals[n].z 
	#	nMatrix = faceCoordinates[n] * startFaceMatrix.inverse()
	#	nVector = om.MVector(nMatrix(3,0), nMatrix(3,1), nMatrix(3,2))


	if numberOfNeighbors == 3:
		distance1 = abs(goalVtx-getattr(polyPosition[selectedFaceNeighbors[0]],str(axis)))
		distance2 = abs(goalVtx-getattr(polyPosition[selectedFaceNeighbors[1]],str(axis)))
		distance3 = abs(goalVtx-getattr(polyPosition[selectedFaceNeighbors[2]],str(axis)))

	elif numberOfNeighbors == 2:
		distance1 = abs(goalVtx-getattr(polyPosition[selectedFaceNeighbors[0]],str(axis)))
		distance2 = abs(goalVtx-getattr(polyPosition[selectedFaceNeighbors[1]],str(axis)))
		# något som är större än distance1 och distance2
		distance3 = distance1+distance2

	elif numberOfNeighbors == 1:
		distance1 = abs(goalVtx-getattr(polyPosition[selectedFaceNeighbors[0]],str(axis)))
		# något som är större än distance1
		distance2 = distance1+distance1
		distance3 = distance1+distance1

		#dp = nVector * axis

	

		#print "n: ", n
		#print "FaceId: ",faceIndex,  "dp: ", dp


	#if abs(normals[n].x) < 0.4 and abs(normals[n].z) < 0.4 and dp> closestDotProd:
	if distance1<distance2 and distance1<distance3:
		#closestDotProd = dp
		nextFace = selectedFaceNeighbors[0]
		# for n in selectedFacesList:
		# 	if n == nextFace and axis != 'x':
		# 		nextFace = selectedFaceNeighbors[2]
	elif distance3<distance1 and distance3<distance2:
	 	nextFace = selectedFaceNeighbors[2]
	elif distance2<distance3 and distance2<distance1:
		nextFace = selectedFaceNeighbors[1]
		# #print "lastIndex", lastIndex
		# for n in selectedFacesList:
		# 	if n == nextFace:
		# 		nextFace = selectedFaceNeighbors[0]

	for n in selectedFacesList:
		if(numberOfNeighbors == 2):
			if n == selectedFaceNeighbors[0]:
				nextFace = selectedFaceNeighbors[1]
			elif  n == selectedFaceNeighbors[1] and numberOfNeighbors == 2:
				nextFace = selectedFaceNeighbors[0]

		elif(numberOfNeighbors == 3):
			if n == selectedFaceNeighbors[0] and distance2<distance3:
				nextFace = selectedFaceNeighbors[1]
			elif n == selectedFaceNeighbors[0] and distance2>distance3:
				nextFace = selectedFaceNeighbors[2]

			elif n == selectedFaceNeighbors[1] and distance1<distance3:
				nextFace = selectedFaceNeighbors[0]
			elif n == selectedFaceNeighbors[1] and distance1>distance3:
				nextFace = selectedFaceNeighbors[2]

			elif n == selectedFaceNeighbors[2] and distance1<distance2:
				nextFace = selectedFaceNeighbors[0]
			elif n == selectedFaceNeighbors[2] and distance1>distance2:
				nextFace = selectedFaceNeighbors[1]
		 	
	lastIndex = nextFace
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
			# lägger till den markerade facet/componenten i en lista
			targetGeom.append(selItem)


		selListIter.next()

	if not targetGeom :
		print "somthing is wrong" 
		return


	#for obj in targetGeom :
	#print "obj: " + str(targetGeom[0].polyIds[0])

	#print "targets: " + str(targetIds)

	

	connectedFaces = om.MIntArray()
	faceIndecis = om.MIntArray()
	polyEdgesIds = om.MIntArray()
	dummy = om.MScriptUtil()
	edgeFaces = om.MIntArray()
	dummyIntPtr = dummy.asIntPtr()
	polyData = []
	 #MStatus status
	# objList är target polygon
	for obj in targetGeom :
		edgeIter = om.MItMeshEdge(obj.dagPath)
		faceIter = om.MItMeshPolygon(obj.dagPath)

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
			faceIter.next()
		


	neighborFaces = []
	selectedFaces = []



	


	#markerar nästa, med första facet som utgångspunkt

	#selectedFaces.append(getDirectionalFace(selectedFaces[0], om.MVector(1,0,0)))
	#selectedFaces.append(getDirectionalFace(selectedFaces[1], om.MVector(1,0,0)))
	# selectedFaces.append(getDirectionalFace(selectedFaces[2], om.MVector(1,0,0)))
	# selectedFaces.append(getDirectionalFace(selectedFaces[3], om.MVector(1,0,0)))
	# selectedFaces.append(getDirectionalFace(selectedFaces[4], om.MVector(1,0,0)))
	# selectedFaces.append(getDirectionalFace(selectedFaces[5], om.MVector(1,0,0)))
	# selectedFaces.append(getDirectionalFace(selectedFaces[6], om.MVector(1,0,0)))
	#printMMatrix(faceCoordinates[targetIds[0]])
	#printMMatrix(faceCoordinates[targetIds[1]])

	poly_selectedList=[{'id':targetIds[0], 'x':polyPosition[targetIds[0]].x, 'z':polyPosition[targetIds[0]].z },
					   {'id':targetIds[1], 'x':polyPosition[targetIds[1]].x, 'z':polyPosition[targetIds[1]].z },
					   {'id':targetIds[2], 'x':polyPosition[targetIds[2]].x, 'z':polyPosition[targetIds[2]].z },
					   {'id':targetIds[3], 'x':polyPosition[targetIds[3]].x, 'z':polyPosition[targetIds[3]].z }]


	

	
	#sorted(poly_selectedList, key=lambda k: k['x'])
	sortedPolygons_x = sorted(poly_selectedList, key=itemgetter('x')) 
	sortedPolygons_z = sorted(sortedPolygons_x, key=itemgetter('z'))

	print("selectedPolyList: ", sortedPolygons_z[0]["id"])
	print("selectedPolyList: ", sortedPolygons_z[1]["id"])
	print("selectedPolyList: ", sortedPolygons_z[2]["id"])
	print("selectedPolyList: ", sortedPolygons_z[3]["id"])

	sortedPolygons = []
	sortedPolygons.append(sortedPolygons_z[2]["id"])
	sortedPolygons.append(sortedPolygons_z[0]["id"])
	sortedPolygons.append(sortedPolygons_z[1]["id"])
	sortedPolygons.append(sortedPolygons_z[3]["id"])
	print("selectedPolyList: ", sortedPolygons[0])
	print("selectedPolyList: ", sortedPolygons[1])
	print("selectedPolyList: ", sortedPolygons[2])
	print("selectedPolyList: ", sortedPolygons[3])

	startIndex = sortedPolygons_z[2]["id"]
	secondIndex = sortedPolygons_z[0]["id"]
	thirdIndex = sortedPolygons_z[1]["id"]
	fourthIndex = sortedPolygons_z[3]["id"]

	#lägger till det först markeade facet
	selectedFaces.append(startIndex)

	print "negativ z-sträcka"
	axis = 'z'
	index = 0
	currentIndex = getDirectionalFace(selectedFaces[index], axis, secondIndex)
	while  currentIndex != secondIndex:
		selectedFaces.append(currentIndex)
		currentIndex = getDirectionalFace(selectedFaces[index], axis, secondIndex)
		index += 1
	
	print "negativ x-sträcka"
	selectedFaces.append(secondIndex)
	axis = 'x'

	index += 1
	currentIndex = getDirectionalFace(thirdIndex[index], axis, thirdIndex)
	while  currentIndex != secondIndex:
		selectedFaces.append(currentIndex)
		currentIndex = getDirectionalFace(thirdIndex[index], axis, thirdIndex)
		index += 1
	
	print "positiv z-sträcka"
	selectedFaces.append(thirdIndex)
	axis = 'z'
	index += 1
	while getDirectionalFace(selectedFaces[index], axis, fourthIndex) != fourthIndex:
		if getDirectionalFace(selectedFaces[index], axis, fourthIndex) == fourthIndex:
			print "hi"
			break
		else:
			selectedFaces.append(getDirectionalFace(selectedFaces[index],  axis, fourthIndex))
		index += 1

	print "positiv x-sträcka"
	selectedFaces.append(fourthIndex)

	axis = 'x'
	index += 1
	while getDirectionalFace(selectedFaces[index], axis, fourthIndex) != fourthIndex:
		if getDirectionalFace(selectedFaces[index], axis, startIndex) == startIndex:
			print "hi"
			break
		else:
			selectedFaces.append(getDirectionalFace(selectedFaces[index],  axis, startIndex))
		index += 1
		


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