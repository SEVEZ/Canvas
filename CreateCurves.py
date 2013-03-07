import sys
import random
import math

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds
import maya.mel as mel

def MAKE_INPUT(attr):
	attr.setKeyable(True)
	attr.setStorable(True)
	attr.setReadable(True)
	attr.setWritable(True)
def MAKE_OUTPUT(attr):
	attr.setKeyable(False)
	attr.setStorable(False)
	attr.setReadable(True)
	attr.setWritable(False)

pluginCmdName = "createCurves"

class createCurvesCmd(OpenMayaMPx.MPxCommand):
	def __init__(self):
		OpenMayaMPx.MPxCommand.__init__(self)

	def doIt(self, argList):
		selList = OpenMaya.MSelectionList()
		OpenMaya.MGlobal.getActiveSelectionList(selList)
		selListIter = OpenMaya.MItSelectionList(selList)
		
		curvesCreated = False

		while not selListIter.isDone():
			dagPath = OpenMaya.MDagPath()
			component = OpenMaya.MObject()
			selListIter.getDagPath(dagPath, component)
			mesh = OpenMaya.MFnMesh(dagPath)
			
			if component.apiType() == OpenMaya.MFn.kMeshPolygonComponent: #selected component is a face
				faceIter = OpenMaya.MItMeshPolygon(dagPath, component)
				while not faceIter.isDone():
					normal = OpenMaya.MVector()
					faceIter.getNormal(0, normal, OpenMaya.MSpace.kWorld)
					tangents = OpenMaya.MFloatVectorArray()
					mesh.getFaceVertexTangents(faceIter.index(), tangents, OpenMaya.MSpace.kWorld)
					tangent = OpenMaya.MVector(tangents[0])

					vertexArray = OpenMaya.MPointArray()
					mesh.getPoints(vertexArray, OpenMaya.MSpace.kWorld)
					vertexIndices = OpenMaya.MIntArray()
					mesh.getPolygonVertices(faceIter.index(), vertexIndices)
					if (vertexIndices.length() != 3):
						print ("A selected face is not a triangle")
					else:
						a = OpenMaya.MVector(vertexArray[vertexIndices[0]])
						b = OpenMaya.MVector(vertexArray[vertexIndices[1]])
						c = OpenMaya.MVector(vertexArray[vertexIndices[2]])

						n1 = normal * 0.5 + tangent * 0.5
						n2 = normal * 0.3 + tangent * 0.7
						n3 = normal * 0.1 + tangent * 0.9

						n1.normalize()
						n2.normalize()
						n3.normalize()

						u = 0.2
						w = 0.9

						cross = (b - a) ^ (c - a)
						area = 0.5 * cross.length()
						curveCount = int(area * 10)

						for i in xrange(0, curveCount):
							for j in xrange(0, curveCount - i):
								k = curveCount - i - j
								wa = float(i) / float(curveCount)
								wb = float(j) / float(curveCount)
								wc = float(k) / float(curveCount)
								s = a * wa + b * wb + c * wc

								r1x = random.random()
								r1y = random.random()
								r1z = random.random()
								r1 = OpenMaya.MVector(r1x, r1y, r1z)
								r1.normalize()

								p = s + (n1 * w + r1 * (1 - w)) * u

								r2x = random.random()
								r2y = random.random()
								r2z = random.random()
								r2 = OpenMaya.MVector(r2x, r2y, r2z)
								r2.normalize()

								q = p + (n2 * w + r2 * (1 - w)) * u

								r3x = random.random()
								r3y = random.random()
								r3z = random.random()
								r3 = OpenMaya.MVector(r3x, r3y, r3z)
								r3.normalize()

								e = q + (n3 * w + r3 * (1 - w)) * u

								cmd = "curve -p " + str(s[0]) + " " + str(s[1]) + " " + str(s[2]) + " -p " + str(p[0]) + " " + str(p[1]) + " " + str(p[2]) + " -p " + str(q[0]) + " " + str(q[1]) + " " + str(q[2]) + " -p " + str(e[0]) + " " + str(e[1]) + " " + str(e[2])
								mel.eval(cmd)

								curvesCreated = True

					faceIter.next()
			selListIter.next()

		if not curvesCreated:
			print ("No triangle faces are selected")

		self.setResult("Executed command")

# Create an instance of the command.
def cmdCreator():
	return OpenMayaMPx.asMPxPtr(createCurvesCmd())

curveNodeId = OpenMaya.MTypeId(0x8704)

class curveNode(OpenMayaMPx.MPxNode):
	density = OpenMaya.MObject()
	inCurve = OpenMaya.MObject()
	outPoints = OpenMaya.MObject()

	# constructor
	def __init__(self):
		OpenMayaMPx.MPxNode.__init__(self)

	# compute
	def compute(self,plug,data):
		densData = data.inputValue(curveNode.density)
		dens = densData.asFloat()
		curveData = data.inputValue(curveNode.inCurve)
		curveObject = OpenMaya.MObject(curveData.asNurbsCurve())
		curve = OpenMaya.MFnNurbsCurve(curveObject)

		pointsData = data.outputValue(curveNode.outPoints)
		pointsAAD = OpenMaya.MFnArrayAttrsData()
		pointsObject = pointsAAD.create()

		positionArray = pointsAAD.vectorArray("position")
		idArray = pointsAAD.doubleArray("id")

		max = curve.findParamFromLength(curve.length())
		for i in frange(0, max, dens):
			p = OpenMaya.MPoint()
			curve.getPointAtParam(i, p, OpenMaya.MSpace.kWorld)
			point = OpenMaya.MVector(p)
			positionArray.append(point)
			idArray.append(i)

		pointsData.setMObject(pointsObject)

		data.setClean(plug)

	def fRange(start, end, step):
		while start <= end:
			yield start
			start += step

# initializer
def curveNodeInitializer():
	tAttr = OpenMaya.MFnTypedAttribute()
	nAttr = OpenMaya.MFnNumericAttribute()

	curveNode.density = nAttr.create("density", "d", OpenMaya.MFnNumericData.kFloat, 0.1)
	MAKE_INPUT(nAttr)

	curveNode.inCurve = tAttr.create("inCurve", "ic", OpenMaya.MFnNurbsCurveData.kNurbsCurve)
	MAKE_INPUT(tAttr)

	curveNode.outPoints = tAttr.create("outPoints", "op", OpenMaya.MFnArrayAttrsData.kDynArrayAttrs)
	MAKE_OUTPUT(tAttr)

	try:
		curveNode.addAttribute(curveNode.density)
		curveNode.addAttribute(curveNode.inCurve)
		curveNode.addAttribute(curveNode.outPoints)

		curveNode.attributeAffects(curveNode.density, curveNode.outPoints)
		curveNode.attributeAffects(curveNode.inCurve, curveNode.outPoints)

		print "curveNode Initialization!\n"

	except:
		sys.stderr.write( "Failed to create attributes of curveNode node\n" )

def curveNodeCreator():
	return OpenMayaMPx.asMPxPtr(curveNode())

def createUI():
	OpenMaya.MGlobal.executeCommand("createUI")

def deleteUI():
	OpenMaya.MGlobal.executeCommand("deleteUI")

# Initialize the plugin
def initializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.registerCommand(pluginCmdName, cmdCreator)
	except:
		sys.stderr.write("Failed to register command: %s\n" % pluginCmdName)
		raise

	try:
		mplugin.registerNode( "curveNode", curveNodeId, curveNodeCreator, curveNodeInitializer )
	except:
		sys.stderr.write( "Failed to register curveNode" )

	OpenMaya.MGlobal.executeCommand("source \"" + mplugin.loadPath() + "/CanvasUI.mel\"");

	try:
		mplugin.registerUI(createUI, deleteUI)
	except:
		sys.stderr.write( "Failed to register UI" )
		raise

# Uninitialize the plugin
def uninitializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.deregisterCommand(pluginCmdName)
	except:
		sys.stderr.write("Failed to unregister command: %s\n" % pluginCmdName)
		raise