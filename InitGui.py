import FreeCAD as App
import FreeCADGui as Gui

import ListSelect
import SelectionTools_rc


TOOLS = [
        ("ListSelect", ListSelect.select, "S, E"),
]


def activateTool(name, callback, defaultShortcut):
    from PySide import QtGui
    pref = App.ParamGet(
        "User parameter:BaseApp/Preferences/Mod/SelectionTools/" + name)
    if not pref.GetBool("disabled"):
        action = QtGui.QAction(Gui.getMainWindow())
        Gui.getMainWindow().addAction(action)
        action.setText(name)
        action.setObjectName("Std_%s" % name)
        shortcut = pref.GetString("shortcut")
        if shortcut == "":
            shortcut = defaultShortcut
        action.setShortcut(QtGui.QKeySequence(shortcut))
        action.triggered.connect(callback)


################
# Main Routine #
################

Gui.addPreferencePage(
    ":/ui/SelectionToolsSettings.ui","Display")
for t in TOOLS:
    activateTool(*t)
