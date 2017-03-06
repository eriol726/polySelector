

import maya.OpenMaya as om
import maya.OpenMayaMPx as OpenMayaMPx
import functools
import maya.cmds as cmds

 
class HelloWorld(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)

        
 
    def doIt(self,  getWinName='helloWorldWin'):
        self.winTitle = "helloWorld"
        self.winName = getWinName
        
        self.createUI( applyCallback)
        #edgeCapSelector()

        print 'Hello World efkusf!'

    def createUI(self,pApplyCallback):
        windowID = 'myWindowID'

        if cmds.window(windowID, exists=True):
            cmds.deleteUI(windowID)

        # Start with the Window
        cmds.window(windowID,title=self.winTitle,sizeable=False,resizeToFitChildren=True)

        # Add a 3 column layout to add controls into
        cmds.rowColumnLayout(numberOfColumns=3,columnWidth=[(1,75),(2,60),(3,60)],columnOffset=[(1,'right',3)])

        cmds.text(label="Time Range:")

        stratTimeField = cmds.intField(value=cmds.playbackOptions(q=True,minTime=True))

        endTimeField = cmds.intField(value=cmds.playbackOptions(q=True,minTime=True))

        cmds.text(label="Attribute")

        targetAttributeFiled = cmds.textField(text='rotateY')

        cmds.separator(h=10,style='none')

        cmds.separator(h=10,style='none')
        cmds.separator(h=10,style='none')
        cmds.separator(h=10,style='none')

        cmds.separator(h=10,style='none')





        # cancel button
        cmds.button( label="Apply", command=functools.partial(pApplyCallback,
                                                    stratTimeField,
                                                    endTimeField,
                                                    targetAttributeFiled))

        def cancelCallback(*pArgs):
            if cmds.window(windowID, exists=True):
                cmds.deleteUI(windowID)

        cmds.button( label="Cancel", command=cancelCallback)
        # Display the window
        cmds.showWindow()

def applyCallback(pStartTimeField,pEndTimeField, pTargetAttributeField,*pArgs):
    print 'Apply button pressed.'

    startTime = cmds.intField(pStartTimeField,query=True,value=True)
    endTime = cmds.intField(pEndTimeField,query=True,value=True)
    targetAttribute = cmds.textField(pTargetAttributeField,query=True,text=True)

    print 'Start Time: %s' % (startTime)
    print 'End Time: %s' % (endTime)
    print 'Attribute: %s' % (targetAttribute)

def edgeCapSelector():
    # Check if vertices or faces were selected.
    # If true convert selection to edges  
    verts = cmds.filterExpand(sm = 31, ex = True, fullPath =True)
    faces = cmds.filterExpand(sm = 31, ex = True, fullPath =True)
    if verts is not None or Faces is not None:
        cmds.ConvertSelectionToEdges()
    # Create variable of special class MScriptUtil.
    # It's required to store pointer to integer variable.
    mutil = om.MScriptUtil()
    # Create variable "resultSelection" of type MSelectionList to store cap edge.
    resultSelection = om.MSelectionList()
    # Create variable "selection" with list of selected objects
    om.MGlobal.getActiveSelectionList()
    # Fill "Selection" with list of selected objects.
    om.MGlobal.getActiveSelectionList(selection)
    # Create iterator through list of selected objects
    selection_iter = om.MItSelectionList(selection)
    # Create variable to store DagPath to selected object
    selection_DagPath = om.MDagPath()
    # Create variable to store iterating edge as MObject
    component_edge = om.MObject
    # Create variable to store pointer to iterate value.
    # There is no other way to get Python value from Maya API function which return &int
    int_Ptr = mutil.asIntPtr()
    # Variable to store currently iterting object as MObject.
    selectedMObject = om.MObject()
    # Main loop of selection iterator
    while not selection_iter.isDone():
        # Get list of selected edges (if components are selected, but not object)
        selection_iter.getDagPath(selection_DagPath, component_edge)
        if selection_iter.hasComponents();
            # Create iterator through SELECTED edges, if edges are in selection.
            edge_iter = om.MItMeshEdge(selection_DagPath, component_edge)
        else:
            # Create iterator through ALL edges of currently iterating selected object, beacause object is selected, but not components
            selection_iter.getDependNode(selectedMObject)
            edge_iter = om.MItMeshEdge(selectedMObject)
        # Main loop of edges iterator
        while not edge_iter.isDone():
            # get pointer to int with number of edges connected to currently iterating
            edge_iter.numConnectedEdges(int_Ptr)
            # get value from int pointer
            numConEdges = mutil.getInt(int_Ptr)
            # check if it's really polystripe
            if numConEdges != 2 and numConEdges != 4 and numConEdges !=3:
                print edge_iter.index()
                cmds.error('Topology error, check mesh topology.')
            # if current edge is connected to two edges it's cap edge
            if numConEdges == 2
                # add cap edge to MSelectionList where we store results
                resultSelection.add(selection_DagPath, edge_iter.currentItem())
            # get next edge and go to loop begginning
            edge_iter.next()
        selection_iter.next()

        # if we found cap edges select and highlight them. We highlight them because
        # usually selection is also highlighted in maya, so it looks more natural
        # for user.
        if resultSelection.length()>0:
            om.MGlobal.setSelectionMode(om.MGlobal.kSelectionComponentMode)
            om.MGlobal.setHiliteList(selection)
            om.MGlobal.setActiveSelection(resultSelection)







 
def creator():
    return OpenMayaMPx.asMPxPtr( HelloWorld() )
 
def initializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj, 'Chad Vernon', '1.0', 'Any')
    try:
        plugin.registerCommand('helloWorld', creator)
    except:
        raise RuntimeError, 'Failed to register command'
 
def uninitializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj)
    try:
        plugin.deregisterCommand('helloWorld')
    except:
        raise RuntimeError, 'Failed to unregister command'