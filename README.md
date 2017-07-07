# Selection Tools
Select hidden or hard to reach objects in FreeCAD.

<p align="center">
<img src="/screen.png" />
</p>

## Install
The repository must be cloned into the Mod folder of FreeCAD (usually
~/.FreeCAD/Mod). Use the following command to install the add-on:

    git clone https://github.com/drhooves/SelectionTools.git \
    $HOME/.FreeCAD/Mod/SelectionTools

## Usage
Press S,E while hovering above a object in the 3D view to invoke the selection
process. Choose the sub object from the context menu that you want to select.
The context menu shows only the sub objects intersecting a imaginary ray from
the camera through the cursor. The shortcut can be customized in preferences
window under Preferences-\>Display-\>Selection Tools.
