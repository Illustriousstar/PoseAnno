from PyQt5 import QtWidgets, QtGui
import os

here = os.path.dirname(os.path.abspath(__file__))


def newIcon(icon):
    """convert icon name to png filename"""
    icons_dir = os.path.join(here, "./icons")
    return QtGui.QIcon(os.path.join(icons_dir, "%s.svg" % icon))


def newAction(
        parent,
        text,
        slot=None,
        shortcut=None,
        icon=None,
        tip=None,
        checkable=False,
        enabled=True,
        checked=False,
):
    """convenient new Action type, copied from
    https://github.com/wkentaro/labelme/blob/819a93cbbc8a7ae3009e9f380111d742e6c06615/labelme/utils/qt.py#L28"""
    a = QtWidgets.QAction(text, parent)
    if icon is not None:
        a.setIconText(text.replace(" ", "\n"))
        a.setIcon(newIcon(icon))
    if shortcut is not None:
        if isinstance(shortcut, (list, tuple)):
            a.setShortcuts(shortcut)
        else:
            a.setShortcut(shortcut)
    if tip is not None:
        a.setToolTip(tip)
        a.setStatusTip(tip)
    if slot is not None:
        a.triggered.connect(slot)
    if checkable:
        a.setCheckable(True)
    a.setEnabled(enabled)
    a.setChecked(checked)
    return a
