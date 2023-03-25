import maya.OpenMaya as om
import maya.cmds as cmds
import math
import os

class polySelector:

	def __init__(self):
		self.targetIds = 0
		self.geometryData = GeometryData()
		self.geometryData.setPolyData()

	def select(self):
		selectedEdges = []
		selectedVertices = []

		selectedEdges, centerPolygon = self.getSelectedComponents()

		#selectedEdges = self.geometryData.slice(selectedVertices)

		poly_ids2 = self.geometryData.selectPolygonsBorder(selectedEdges, centerPolygon)

		sel = om.MSelectionList()
		om.MGlobal.getActiveSelectionList(sel)

		mdag = om.MDagPath()
		sel.getDagPath(0, mdag)

		# Create an MIntArray and populate it with component ids to add to our component object
		# MIntArray takes an array of ints. That has to be passed using an MScriptUtil pointer
		# This is where you would use your list of polyIds that you had gotten

		to_sel = om.MSelectionList()

		# Only for selecting sliced edges
		#********************

		# util = om.MScriptUtil()
		# util.createFromList(selectedEdges, len(selectedEdges))
		# ids_ptr = util.asIntPtr()
		# edgeIds = om.MIntArray(ids_ptr, len(selectedEdges))

		# # Create a singleIndexedComponent of type polygon
		# mfn_components = om.MFnSingleIndexedComponent()
		# components = mfn_components.create(om.MFn.kMeshEdgeComponent)
		# # Add our MIntArray of ids to the component
		# mfn_components.addElements(edgeIds)

		# # The object the selection refers to, and the components on that object to select
		# to_sel.add(mdag, components)
		# om.MGlobal.setActiveSelectionList(to_sel)

		# ********************

		util = om.MScriptUtil()
		util.createFromList(poly_ids2, len(poly_ids2))
		ids_ptr = util.asIntPtr()
		polyids = om.MIntArray(ids_ptr, len(poly_ids2))

		# Create a singleIndexedComponent of type polygon
		mfn_components = om.MFnSingleIndexedComponent()
		components = mfn_components.create(om.MFn.kMeshPolygonComponent)
		# Add our MIntArray of ids to the component
		mfn_components.addElements(polyids)

		# The object the selection refers to, and the components on that object to select
		to_sel.add(mdag, components)
		om.MGlobal.setActiveSelectionList(to_sel)

	def getSelectedComponents(self):

		selList = om.MSelectionList()
		# Add selected meshes from maya to selList
		om.MGlobal.getActiveSelectionList(selList)

		if selList.isEmpty():
			print("Select four polygons")
			return

		targetVertexIds = []
		targetEdgeIds = []
		targetPolyIds = []

		# Iterate through the nodes in the objects hypergraph
		selListIter = om.MItSelectionList(selList)
		while not selListIter.isDone():
			print("Get selected component ids")

			components = om.MObject()
			dagPath = om.MDagPath()
			selListIter.getDagPath(dagPath, components)

			if components.isNull():
				selListIter.next()
				continue

			compListFn = om.MFnComponent(components)
			compType = compListFn.componentType()

			if compType == om.MFn.kMeshVertComponent:
				# allows compListFn to query single indexed components
				compListFn = om.MFnSingleIndexedComponent(components)
				targetVertexIds = om.MIntArray()
				# Now the id's from the selected vertices are added to targetVertexIds
				compListFn.getElements(targetVertexIds)

			if compType == om.MFn.kMeshEdgeComponent:
				compListFn = om.MFnSingleIndexedComponent(components)
				targetEdgeIds = om.MIntArray()
				compListFn.getElements(targetEdgeIds)

			if compType == om.MFn.kMeshPolygonComponent:
				compListFn = om.MFnSingleIndexedComponent(components)
				targetPolyIds = om.MIntArray()
				compListFn.getElements(targetPolyIds)

			selListIter.next()

		if len(targetVertexIds) > 10:
			print("too many vertices selected")
			return

		if len(targetVertexIds) == 0:
			print("no vertices selected")

		if len(targetEdgeIds) == 0:
			print("no edges are selected")

		if targetPolyIds is None:
			print("select one polygon")
			return

		print("targetEdgeIds: ", targetEdgeIds)
		print("targetPolyIds: ", targetPolyIds)

		return targetEdgeIds, targetPolyIds

class GeometryData:

	def __init__(self):

		self.polygons = []
		self.edges = []
		self.vertex = []
		self.polygonBorder = []

	def printMatrix(self, matrix):
		endStr = '\n'
		outStr = ''
		outStr += endStr

		for i in range(0, 16):
			if i == 0:
				outStr += '['

			if(i > 0 and i % 4 == 0):
				outStr += endStr
			outStr += str(matrix[i]) + str(' ')
		outStr += ']'

		print ('transformation: ',  outStr)

	def setPolyData(self):
		print("selecting...")
		
		selList = om.MSelectionList()
		# Add selected meshes from maya to selList
		om.MGlobal.getActiveSelectionList(selList)

		if selList.isEmpty():
			print("No polygon is selected")
			return

		components = om.MObject()
		dagPath = om.MDagPath()
		selList.getDagPath(0, dagPath, components)

		connectedFaces = om.MIntArray()

		edgeIter = om.MItMeshEdge(dagPath)
		vertexIter = om.MItMeshVertex(dagPath)
		faceIter = om.MItMeshPolygon(dagPath)

		self.vertex = [VertexData() for _ in range(vertexIter.count())]

		print("vertexIter.count()", vertexIter.count())

		i = 0
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
			i += 1
			vertexIter.next()

		i = 0
		self.edges = [EdgeData() for _ in range(edgeIter.count())]
		while not edgeIter.isDone():

			connectedEdges = om.MIntArray()
			edgeIter.getConnectedEdges(connectedEdges)

			self.edges[i].connectedEdges = connectedEdges

			connectedFaces = om.MIntArray()

			# Returns the indices of the faces connected to the current edge.
			# Normally a boundary edge will only have one face connected to it and
			# an internal edge will have two, but if the mesh has manifold geometry
			# then the edge may have three or more faces connected to it.
			edgeIter.getConnectedFaces(connectedFaces)

			# if connectedFaces is an array of just one face id the mesh is corrupt
			self.edges[i].connectedFaces = connectedFaces

			self.edges[i].vertices.append(edgeIter.index(0))
			self.edges[i].vertices.append(edgeIter.index(1))

			self.edges[i].position = edgeIter.center()
			#self.edges[i].numberOfNeighbors = edgeIter.numConnectedEdges()
			i += 1
			edgeIter.next()

		# Init size of array, as much faces the mesh has 
		self.polygons = [PolyData() for _ in range(faceIter.count())]

		# Loop through all faces in the mesh 
		i = 0
		while not faceIter.isDone():
			self.polygons[i].normalAngel = 5.0

			self.polygons[i].position = faceIter.center()

			normal = om.MVector()
			faceIter.getNormal(normal)
			self.polygons[i].normal = normal

			# Gets connected faces
			faceArray = om.MIntArray()
			faceIter.getConnectedFaces(faceArray)

			vertexArray = om.MIntArray()
			faceIter.getVertices(vertexArray)

			self.polygons[i].vertices = vertexArray

			# Add connected faces
			self.polygons[i].connectedFaces = faceArray

			i += 1
			faceIter.next()
	
	def onSegment(self, p,  q,  r):
		"""Given three colinear points p, q, r, the function checks if
			point q lies on line segment 'pr'
		"""

		if (q.x <= max(p.x, r.x) and q.x >= min(p.x, r.x) and q.z <= max(p.z, r.z) and q.z >= min(p.z, r.z)):
			return True

		return False

	def orientation(self, p, q, r):
		""" To find orientation of ordered triplet (p, q, r).
			The function returns following values
			0 --> p, q and r are colinear
			1 --> Clockwise
			2 --> Counterclockwise
		"""

		# See http://www.geeksforgeeks.org/orientation-3-ordered-points/
		# for details of below formula.
		val = (q.z - p.z) * (r.x - q.x) - (q.x - p.x) * (r.z - q.z)

		if (val == 0):
			return 0  # colinear

		return 1 if val > 0 else 2  # clock or counterclock wise

	def doIntersect(self, p1, q1, p2, q2):

		# Find the four orientations needed for general and
		# special cases
		o1 = self.orientation(p1, q1, p2)
		o2 = self.orientation(p1, q1, q2)
		o3 = self.orientation(p2, q2, p1)
		o4 = self.orientation(p2, q2, q1)

		# General case
		if (o1 != o2 and o3 != o4):
			return True

		# Special Cases
		# p1, q1 and p2 are colinear and p2 lies on segment p1q1
		if (o1 == 0 and self.onSegment(p1, p2, q1)):
			return True

		# p1, q1 and p2 are colinear and q2 lies on segment p1q1
		if (o2 == 0 and self.onSegment(p1, q2, q1)):
			return True

		# p2, q2 and p1 are colinear and p1 lies on segment p2q2
		if (o3 == 0 and self.onSegment(p2, p1, q2)):
			return True

		# p2, q2 and q1 are colinear and q1 lies on segment p2q2
		if (o4 == 0 and self.onSegment(p2, q1, q2)):
			return True

		return False  # Doesn't fall in any of the above cases

	def ccw(self, A, B, C):
		return (C.z-A.z) * (B.x-A.x) > (B.z-A.z) * (C.x-A.x)

	def intersect(self, A, B, C, D):
		""" Return true if line segments AB and CD intersect """

		return self.ccw(A, C, D) != self.ccw(B, C, D) and self.ccw(A, B, C) != self.ccw(A, B, D)

	def selectPolygonsBorder(self, selectedEdges, centerPolygon):

		self.polygonBorder = []

		vertexBorder = []
		for index in selectedEdges:
			vertexBorder.append(self.edges[index].vertices[0])
			vertexBorder.append(self.edges[index].vertices[1])

		for i in range(0, len(vertexBorder) - 1):
			if os.path.exists("c:/break"):
				break
			for j in range(0, len(vertexBorder) - 1 - i):
				if os.path.exists("c:/break"):
					break
				if self.less(self.vertex[j].position, self.vertex[j+1].position, self.polygons[centerPolygon[0]].position):
					vertexBorder[j], vertexBorder[j + 1] = vertexBorder[j+1], vertexBorder[j]

		i = 0
		for index_e in selectedEdges:
			if self.edges[index_e].connectedFaces and len(self.edges[index_e].connectedFaces) < 2:
				print("only one connected face, corrupt mesh or border face")
				continue 
			connectedFaces = self.edges[index_e].connectedFaces

			for index_f0_v in range(0, 3):
				if self.polygons[connectedFaces[0]].vertices[index_f0_v] != self.edges[index_e].vertices[0] and self.polygons[connectedFaces[0]].vertices[index_f0_v] != self.edges[index_e].vertices[1]:
					z_dist_f0 = self.vertex[self.polygons[connectedFaces[0]
														  ].vertices[index_f0_v]].position.z-self.edges[index_e].position.z
					x_dist_f0 = self.vertex[self.polygons[connectedFaces[0]
														  ].vertices[index_f0_v]].position.x-self.edges[index_e].position.x
					f0_v_pos = self.vertex[self.polygons[connectedFaces[0]
														 ].vertices[index_f0_v]].position
					height_f0 = self.vertex[self.polygons[connectedFaces[0]
														  ].vertices[index_f0_v]].position.y


			dist_f0 = math.sqrt(math.pow(x_dist_f0, 2)+math.pow(z_dist_f0, 2))

			if self.less(self.vertex[self.edges[index_e].vertices[0]].position, self.vertex[self.edges[index_e].vertices[1]].position, self.polygons[centerPolygon[0]].position):
				if self.isOutside(self.vertex[self.edges[index_e].vertices[0]].position, self.vertex[self.edges[index_e].vertices[1]].position, f0_v_pos, 1):
					isOutside_f0 = True
				else:
					isOutside_f0 = False
			elif self.less(self.vertex[self.edges[index_e].vertices[1]].position, self.vertex[self.edges[index_e].vertices[0]].position, self.polygons[centerPolygon[0]].position):
				if self.isOutside(self.vertex[self.edges[index_e].vertices[1]].position, self.vertex[self.edges[index_e].vertices[0]].position, f0_v_pos, 1):
					isOutside_f0 = True
				else:
					isOutside_f0 = False

			for index_f1_v in range(0, 3):
				if self.polygons[connectedFaces[1]].vertices[index_f1_v] != self.edges[index_e].vertices[0] and self.polygons[connectedFaces[1]].vertices[index_f1_v] != self.edges[index_e].vertices[1]:
					z_dist_f1 = self.vertex[self.polygons[connectedFaces[1]
														  ].vertices[index_f1_v]].position.z-self.edges[index_e].position.z
					x_dist_f1 = self.vertex[self.polygons[connectedFaces[1]
														  ].vertices[index_f1_v]].position.x-self.edges[index_e].position.x
					f1_v_pos = self.vertex[self.polygons[connectedFaces[1]
														 ].vertices[index_f1_v]].position
					height_f1 = self.vertex[self.polygons[connectedFaces[1]
														  ].vertices[index_f0_v]].position.y

			dist_f1 = math.sqrt(math.pow(x_dist_f1, 2)+math.pow(z_dist_f1, 2))

			if isOutside_f0 == False:
				self.polygons[connectedFaces[0]].selected = True
				self.polygonBorder.append(connectedFaces[0])
			elif height_f0 > height_f1:
				self.polygons[connectedFaces[0]].selected = True
				self.polygonBorder.append(connectedFaces[0])
			elif dist_f0 < dist_f1:
				self.polygons[connectedFaces[0]].selected = True
				self.polygonBorder.append(connectedFaces[0])
			else:
				self.polygons[connectedFaces[1]].selected = True
				self.polygonBorder.append(connectedFaces[1])

			i = i+1

		connectedFaces = self.polygons[centerPolygon[0]].connectedFaces
		print("centerPolygon", centerPolygon[0])

		for i in range(0, 170):
			# Stop the program with this script if the loop is infinity
			if os.path.exists("c:/break"):
				break
			if(len(connectedFaces)):
				connectedFaces = self.growSelection(connectedFaces)

		for index in self.polygonBorder:
			self.polygons[index].selected = False

		return self.polygonBorder

	def less(self, a, b, center):

		if (a.x - center.x >= 0 and b.x - center.x < 0):
			return True
		if (a.x - center.x < 0 and b.x - center.x >= 0):
			return False
		if (a.x - center.x == 0 and b.x - center.x == 0):
			if (a.z - center.z >= 0 or b.z - center.z >= 0):
				return a.z > b.z
			return b.z > a.z

		# compute the cross product of vectors (center -> a) x (center -> b)
		det = (a.x - center.x) * (b.z - center.z) - \
			(b.x - center.x) * (a.z - center.z)
		if (det < 0):
			return True
		if (det > 0):
			return False

		# points a and b are on the same line from the center
		# check which point is closer to the center
		d1 = (a.x - center.x) * (a.x - center.x) + \
			(a.z - center.z) * (a.z - center.z)
		d2 = (b.x - center.x) * (b.x - center.x) + \
			(b.z - center.z) * (b.z - center.z)
		return d1 > d2

	def growSelection(self, connectedFaces):
		connectedVertices3 = []

		for index in connectedFaces:
			# The end/border of the mesh does not feces with 3 connected faces
			if len(self.polygons[index].connectedFaces) > 2:
				if self.polygons[index].selected == False:
					connectedVertices3.append(
						self.polygons[index].connectedFaces[0])
					connectedVertices3.append(
						self.polygons[index].connectedFaces[1])
					connectedVertices3.append(
						self.polygons[index].connectedFaces[2])
					self.polygons[index].selected = True
					self.polygonBorder.append(index)

		return connectedVertices3

	# if the sign/value is positive it returns true, the point is outside the building
	def isOutside(self, pointA, pointB, pointC, sign):
		if sign == 1:
			return ((pointB.x - pointA.x)*(pointC.z - pointA.z) - (pointB.z - pointA.z)*(pointC.x - pointA.x)) > 0
		elif sign == -1:
			return ((pointB.x - pointA.x)*(pointC.z - pointA.z) - (pointB.z - pointA.z)*(pointC.x - pointA.x)) < 0

	def dotProduct2D(self, poit1, point2):

		return poit1.x*point2.x+poit1.z*point2.z

	def dotProduct(self, poit1, point2):

		return poit1.x*point2.x+poit1.y*point2.y+poit1.z*point2.z
	
	def transformMesh(dagPath):
		# Get the name of the main node for transformation
		pathName = dagPath.fullPathName()
		meshName = pathName[(pathName.find("|")+1):len(pathName)]

		if meshName.find("|") != -1:
			meshName = meshName[0:(meshName.find("|"))]

		# Transform the mesh here, if needed
		meshMatrix = cmds.xform(meshName, q=True, ws=True, matrix=True)
		transMatrix = om.MMatrix()
		om.MScriptUtil.createMatrixFromList(meshMatrix, transMatrix)
	
	def slice(self, targetIds):

		selectedEdges = []
		# test, remove later
		selectedEdges.append(targetIds[0])
		selectedEdges.append(targetIds[1])

		startPos = self.edges[targetIds[0]].position
		endPos = self.edges[targetIds[1]].position
		connectedEdges = self.edges[targetIds[0]].connectedEdges

		intersectionPointList = []
		currentIndex = 0
		i = 0

		# infinite loop :(
		while currentIndex != targetIds[1]:
			i = i+1
			if i > 20:
				break
			if os.path.exists("c:/break"):
				break
			foundIndex = []
			for index in connectedEdges:
				edgeVtex0 = self.vertex[self.edges[index].vertices[0]].position
				edgeVtex1 = self.vertex[self.edges[index].vertices[1]].position
				intersectionPoint = self.doIntersect(
					edgeVtex0, edgeVtex1, startPos, endPos)

				if intersectionPoint is not False and index not in selectedEdges:
					intersectionPointList.append(intersectionPoint)
					selectedEdges.append(index)
					currentIndex = index
					foundIndex.append(index)
					print("index", index)

				else:
					print("edge not found")

			connectedEdges = []

			for index in foundIndex:
				foundNeighbors = self.edges[index].connectedEdges
				for i in foundNeighbors:
					connectedEdges.append(i)

		print("edgesInDirection", selectedEdges)
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

		selList.getDagPath(0, dagPath)

		meshNode = om.MObject()

		meshNode = dagPath.node()

		fMesh = meshNode
		# MFnMesh meshFn(fMesh);

		fnMesh = om.MFnMesh(fMesh)

		edgeFactors = om.MFloatArray()

		# splitPlacements = om.MIntArray()
		# edgeList = om.MIntArray()
		# internalPoints = om.MFloatPointArray()

		# for index in edgesInDirection:

		# 	edgeVtx0= self.edges[index].vertices[0]
		# 	edgeVtx1= self.edges[index].vertices[1]
		# 	print("edgeVtx0", edgeVtx0)
		# 	intersectionPoint = self.lineIntersection(self.vertex[edgeVtx0].position,self.vertex[edgeVtx1].position,self.vertex[targetIds[0]].position,self.vertex[targetIds[1]].position)
		# 	if intersectionPoint is not None:
		# 		edgeList.append(index)
		# 		splitPlacements.append(om.MFnMesh.kOnEdge)

		# 		edgeFactors.append(0.5)
		# 		print("intersectionPoint", intersectionPoint.x,("(", intersectionPoint.z))
		# 		#internalPoints.append(intersectionPoint)
		# 	else:
		# 		# intersectionPoint = om.MFloatPoint(0.0,0.0,0.0)
		# 		# internalPoints.append(intersectionPoint)
		# 		print("no intersection")

		#fnMesh.split(splitPlacements, edgeList, edgeFactors, internalPoints)

		return selectedEdges

class VertexData:

	def __init__(self):
		self.selected = False
		self.connectedEdges = []
		self.connectedFaces = []
		self.connectedVertices = []
		self.position = om.MPoint(0, 0, 0)
		self.numberOfNeighbors = 0


class EdgeData:
	def __init__(self):
		self.selected = False
		self.normalAngel = 0.0
		self.vertices = []
		self.connectedEdges = []
		self.connectedFaces = []
		self.position = om.MPoint(0, 0, 0)
		self.numberOfNeighbors = 0

class PolyData:
	def __init__(self):
		self.selected = False
		self.normalAngel = 0.0
		self.connectedFaces = []
		self.vertices = []
		self.position = om.MPoint(0, 0, 0)
		self.normal = om.MVector(0, 0, 0)
		self.faceMatrix = om.MMatrix()

	def __str__(self):
		endStr = '\n'
		outStr = ''
		outStr += ', selected = ' + str(self.selected) + endStr
		for key in self.connectedFaces:
			outStr += '[' + str(key) + '] = ' + \
				str(self.connectedFaces[key]) + endStr
		return outStr

def run():
	classObj = polySelector()
	classObj.select()
	return classObj
