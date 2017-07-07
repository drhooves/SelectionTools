import collections

from PySide import QtCore
from PySide import QtGui
from pivy import coin

import FreeCAD as App
import FreeCADGui as Gui


PRESEL_OFF = 2
PRESEL_ON = 0

SOLID_PREFIX = "Solid"
FACE_PREFIX = "Face"
EDGE_PREFIX = "Edge"
VERTEX_PREFIX = "Vertex"

prevTrans = None
prevPreMode = None

obj = None
picker = None


def select():
    global menu
    global obj
    global picker
    pos = Gui.activeView().getCursorPos()
    obj = getObjectBelow(pos)
    if pos[0] > 0 and pos[1] > 0:
        saveUserSettings()
        prepareGUI()
        picker = Picker()
        picker.pick(pos, obj)
        menu = createMenu()
        menu.exec_(QtGui.QCursor.pos())


class Picker(object):

    def __init__(self):
        self._pickedFaces = collections.OrderedDict()
        self._pickedEdges = collections.OrderedDict()
        self._pickedVertexes = collections.OrderedDict()
        self._facesNode = None
        self._edgesNode = None
        self._vertexesNode = None
        self.vp = None

    @property
    def solids(self):
        sSize = len(self.vp.Object.Shape.Solids)
        return ["%s%d" % (SOLID_PREFIX, i+1) for i in range(sSize)]

    @property
    def faces(self):
        return self._pickedFaces.keys()

    @property
    def edges(self):
        return self._pickedEdges.keys()

    @property
    def vertexes(self):
        return self._pickedVertexes.keys()

    def pick(self, cursorPos, obj):
        self.vp = obj.ViewObject

        pickAction = coin.SoRayPickAction(self._getViewport())
        pickAction.setPickAll(True)
        pickAction.setRadius(
                Gui.activeView().getViewer().getPickRadius())
        pickAction.setPoint(coin.SbVec2s(cursorPos))
        path = self._getPathForVP(self.vp)

        sa = coin.SoSearchAction()
        sa.setNode(self.vp.RootNode)
        sa.apply(self._getSceneGraph())
        pickAction.apply(sa.getPath())

        for pp in pickAction.getPickedPointList():
            node = pp.getPath().getTail()
            detail = self._castDetail(pp.getDetail())
            self._updatePicked(node, detail)
        self._clearPreselect()

    def highlight(self, name):
        node = None
        index = None
        if name in self._pickedFaces:
            node = self._facesNode
            index = self._pickedFaces[name]
        elif name in self._pickedEdges:
            node = self._edgesNode
            index = self._pickedEdges[name]
        elif name in self._pickedVertexes:
            node = self._vertexesNode
            index = self._pickedVertexes[name]
        self._clearPreselect()
        if node is not None:
            node.highlightIndex = index

    def select(self, name):
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(self.vp.Object, name)

    def _getPathForVP(self, vp):
        sa = coin.SoSearchAction()
        sa.setNode(vp.RootNode)
        sa.apply(self._getSceneGraph())
        return sa.getPath()

    def _clearPreselect(self):
        if self._facesNode is not None:
            self._facesNode.highlightIndex = -1
        if self._edgesNode is not None:
            self._edgesNode.highlightIndex = -1
        if self._vertexesNode is not None:
            self._vertexesNode.highlightIndex = -1

    def _updatePicked(self, node, detail):
        if detail.getTypeId() == coin.SoFaceDetail.getClassTypeId():
            index = detail.getPartIndex()
            name = FACE_PREFIX + str(index+1)
            self._pickedFaces[name] = index
            if self._facesNode is None:
                self._facesNode = node
        elif detail.getTypeId() == coin.SoLineDetail.getClassTypeId():
            index = detail.getLineIndex()
            name = EDGE_PREFIX + str(index+1)
            self._pickedEdges[name] = index
            if self._edgesNode is None:
                self._edgesNode = node
        elif detail.getTypeId() == coin.SoPointDetail.getClassTypeId():
            index = detail.getCoordinateIndex()
            name = VERTEX_PREFIX + str(index - node.startIndex.getValue() + 1)
            self._pickedVertexes[name] = index
            if self._vertexesNode is None:
                self._vertexesNode = node

    def _castDetail(self, detail):
	return coin.cast(detail, str(detail.getTypeId().getName()))

    def _getViewport(self):
        return self._getRenderManager().getViewportRegion()

    def _getRenderManager(self):
        return Gui.activeView().getViewer().getSoRenderManager()

    def _getSceneGraph(self):
        return self._getRenderManager().getSceneGraph()


def createMenu():
    menu = QtGui.QMenu()
    for s in picker.solids:
        menu.addAction(s)
    menu.addSeparator()
    for s in picker.faces:
        menu.addAction(s)
    menu.addSeparator()
    for s in picker.edges:
        menu.addAction(s)
    menu.addSeparator()
    for s in picker.vertexes:
        menu.addAction(s)

    menu.triggered.connect(menuReturn)
    menu.aboutToHide.connect(restoreUserSettings)
    menu.hovered.connect(showPreselect)

    return menu


def menuReturn(action):
    picker.select(action.text())


def showPreselect(action):
    picker.highlight(action.text())


def saveUserSettings():
    global prevPreMode
    global prevTrans
    prevPreMode = getPreselectMode()
    prevTrans = obj.ViewObject.Transparency


def restoreUserSettings():
    # Restore user settings.
    obj.ViewObject.Transparency = prevTrans
    setPreselectMode(prevPreMode)


def setPreselectMode(mode):
    sg = Gui.activeView().getSceneGraph()
    sg.highlightMode.setValue(mode)


def getPreselectMode():
    sg = Gui.activeView().getSceneGraph()
    return sg.highlightMode.getValue()


def prepareGUI():
    Gui.Selection.clearSelection()
    setPreselectMode(PRESEL_ON)
    pref = App.ParamGet(
        "User parameter:BaseApp/Preferences/Mod/SelectionTools/ListSelect")
    obj.ViewObject.Transparency = pref.GetInt("transparency")


def getObjectBelow(cursorPos):
    objInfo = Gui.activeView().getObjectInfo(cursorPos)
    if objInfo is None:
        return None
    return App.ActiveDocument.getObject(objInfo["Object"])
