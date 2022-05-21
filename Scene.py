import sys
import math
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import (
    Qt,
    QRectF,
    QPointF,
)
from PyQt5.QtWidgets import QGraphicsScene
from PoseItem import PoseItem


class Scene(QGraphicsScene):
    def __init__(self, *args):
        super().__init__(*args)
        self.current_rect = None
        self.start = QPointF()

    def mousePressEvent(self, e):
        if self.parent().button_add_pose.isChecked():
            if e.button() == Qt.LeftButton:
                self.start = e.scenePos()
                self.current_rect = PoseItem(QRectF(self.start, self.start))
                self.addItem(self.current_rect)
                self.parent().button_add_pose.setChecked(False)
                e.accept()
            elif e.button() == Qt.RightButton:
                self.parent().button_add_pose.setChecked(False)
                e.accept()
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self.current_rect is not None:
            self.current_rect.setRect(QRectF(self.start, e.scenePos()))
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if self.current_rect is not None:
            self.current_rect.setInit(init=False)
            self.current_rect = None
        super().mouseReleaseEvent(e)

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        painter.setPen(Qt.transparent)
        painter.setBrush(Qt.lightGray)
        painter.drawRect(self.sceneRect())
