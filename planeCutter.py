

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