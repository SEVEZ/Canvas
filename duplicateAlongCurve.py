import maya.cmds as cmds
import maya.mel as mel

def fRange(start, end, step):
    while start<=end:
        yield start
        start+=step

def duplicateAlongCurve(density):
    selection = cmds.ls(sl=True)
    if len(selection)!=2:
        print("Please select the object, then the curve")
        return
    obj=selection[0]
    myCurve=selection[1]
    #print selection[0]
    infoNode = cmds.pointOnCurve(myCurve, ch=True, pr=0.0)
    #pos = cmds.getAttr(infoNode + ".position")
    #cmds.move(pos[0][0], pos[0][1], pos[0][2], 'pPlane1', absolute=True)
    cmds.connectAttr( infoNode+'.position', 'pPlane1.translate')
    step = 0.1
    min = cmds.getAttr(myCurve+'.minValue')
    max = cmds.getAttr(myCurve+'.maxValue')
    for i in fRange(min+step, max, density):
        cmds.select(obj)
        infoNode = cmds.pointOnCurve(myCurve, ch=True, pr=i)
        dup = cmds.duplicate();
        cmds.connectAttr( infoNode+'.position', dup[0]+'.translate')
        
duplicateAlongCurve(0.1);
