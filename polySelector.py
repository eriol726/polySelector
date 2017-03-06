import maya.OpenMaya as om
import maya.cmds as cmds
meshTransform = 'pSphere1'
meshShape = cmds.listRelatives(meshTransform, c=True)[0]

meshMatrix = cmds.xform(meshTransform, q=True, ws=True, matrix=True)
primaryUp = om.MVector(*meshMatrix[4:7])
# have a secondary up vector for faces that are facing the same way as the original up
secondaryUp = om.MVector(*meshMatrix[8:11])

sel = om.MSelectionList()
sel.add(meshShape)

meshObj = om.MObject()
sel.getDependNode(0, meshObj)

meshPolyIt = om.MItMeshPolygon(meshObj)
faceNeighbors = []
faceCoordinates = []

while not meshPolyIt.isDone():

    normal = om.MVector()
    meshPolyIt.getNormal(normal)

    # use the seconary up if the normal is facing the same direction as the object Y
    up = primaryUp if (1 - abs(primaryUp * normal)) > 0.001 else secondaryUp

    center = meshPolyIt.center()

    faceArray = om.MIntArray()
    meshPolyIt.getConnectedFaces(faceArray)

    meshPolyIt.next()

    faceNeighbors.append([faceArray[i] for i in range(faceArray.length())])

    xAxis = up ^ normal
    yAxis = normal ^ xAxis

    matrixList = [xAxis.x, xAxis.y, xAxis.z, 0,
                  yAxis.x, yAxis.y, yAxis.z, 0,
                  normal.x, normal.y, normal.z, 0,
                  center.x, center.y, center.z, 1]

    faceMatrix = om.MMatrix()
    om.MScriptUtil.createMatrixFromList(matrixList, faceMatrix)

    faceCoordinates.append(faceMatrix)



        

def getUpFace(faceIndex):
    poly_ids = []
    poly_ids = ui_setTargetGeometry()
    poly_ids[0] = poly_ids[0]+1 
    poly_ids[1] = poly_ids[1]+1 
    poly_ids[2] = poly_ids[2]+1 
    poly_ids[3] = poly_ids[3]+1 

    sel = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(sel)

    mdag = om.MDagPath()
    sel.getDagPath(0, mdag)

    print  poly_ids[0]

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

    return getDirectionalFace(faceIndex, om.MVector(0,1,0))

def getDownFace(faceIndex):
    return getDirectionalFace(faceIndex, om.MVector(0,-1,0))

def getRightFace(faceIndex):
    return getDirectionalFace(faceIndex, om.MVector(1,0,0))

def getLeftFace(faceIndex):
    return getDirectionalFace(faceIndex, om.MVector(-1,0,0))

def getDirectionalFace(faceIndex, axis):
    faceMatrix = faceCoordinates[faceIndex]

    closestDotProd = -1.0
    nextFace = -1

    for n in faceNeighbors[faceIndex]:
        nMatrix = faceCoordinates[n] * faceMatrix.inverse()
        nVector = om.MVector(nMatrix(3,0), nMatrix(3,1), nMatrix(3,2))

        dp = nVector * axis

        if dp > closestDotProd:
            closestDotProd = dp
            nextFace = n

    return nextFace

def ui_setTargetGeometry():
    targetGeom = []

    selList = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(selList)

    if selList.isEmpty():
        print "no targets"
        return

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

        if compType == om.MFn.kMeshPolygonComponent:
            compListFn = om.MFnSingleIndexedComponent(components)
            ids = om.MIntArray()
            compListFn.getElements(ids)
            selItem = SelectionItem(dagPath, ids)
            targetGeom.append(selItem)

        selListIter.next()
    if not targetGeom :
        print "somthing is wrong" 
        return

    print "targets: " + str(ids)
    return ids

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
