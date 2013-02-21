import sys
import random
import math

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds
import maya.mel as mel

pluginCmdName = "createCurves"

class createCurvesCmd(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)

    def doIt(self, argList):
    	n1x = 0.717
    	n1y = 0.717
    	n1z = 0

    	n2x = 0.866
    	n2y = 0.5
    	n2z = 0

    	u = 0.2
    	w = 0.9

        for i in xrange(0, 10):
        	for j in xrange(0, 10):
        		sx = 0.1 * i
        		sy = 0
        		sz = 0.1 * j

        		r1x = random.random()
        		r1y = random.random()
        		r1z = random.random()
        		r1l = math.sqrt(r1x * r1x + r1y * r1y + r1z * r1z)
        		r1x = r1x / r1l
        		r1y = r1y / r1l
        		r1z = r1z / r1l

        		px = sx + u * (w * n1x + (1 - w) * r1x)
        		py = sy + u * (w * n1y + (1 - w) * r1y)
        		pz = sz + u * (w * n1z + (1 - w) * r1z)

        		r2x = random.random()
        		r2y = random.random()
        		r2z = random.random()
        		r2l = math.sqrt(r2x * r2x + r2y * r2y + r2z * r2z)
        		r2x = r2x / r2l
        		r2y = r2y / r2l
        		r2z = r2z / r2l

        		ex = px + u * (w * n2x + (1 - w) * r2x)
        		ey = py + u * (w * n2y + (1 - w) * r2y)
        		ez = pz + u * (w * n2z + (1 - w) * r2z)

        		cmd = "curve -p " + str(sx) + " " + str(sy) + " " + str(sz) + " -p " + str(px) + " " + str(py) + " " + str(pz) + " -p " + str(ex) + " " + str(ey) + " " + str(ez)
        		mel.eval(cmd)
        self.setResult("Executed command")

# Create an instance of the command.
def cmdCreator():
    return OpenMayaMPx.asMPxPtr(createCurvesCmd())

# Initialize the plugin
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "CIS660", "1.0", "2013")
    try:
        mplugin.registerCommand(pluginCmdName, cmdCreator)
    except:
        sys.stderr.write("Failed to register command: %s\n" % pluginCmdName)
        raise

# Uninitialize the plugin
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(pluginCmdName)
    except:
        sys.stderr.write("Failed to unregister command: %s\n" % pluginCmdName)
        raise