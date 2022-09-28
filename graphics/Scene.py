from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import (
    Qt,
    QRectF,
    QPointF,
)
from PyQt5.QtWidgets import QGraphicsScene
from graphics.labels.PoseItem import PoseItem
from graphics.labels.FaceItem import FaceItem
from graphics.labels.SquareFaceItem import SquareFaceItem


class Scene(QGraphicsScene):
    current_rect = None
    start = QPointF()
    zoom_signal = QtCore.pyqtSignal(float)

    def __init__(self, *args):
        super().__init__(*args)
        self.zoom_signal.connect(self.setPointZoom)

    def mousePressEvent(self, e):
        if self.parent().button_add_pose.isChecked()\
                or self.parent().to_add_face:
            if e.button() == Qt.LeftButton:
                self.start = e.scenePos()
                self.current_rect = PoseItem(QRectF(self.start, self.start)) \
                    if self.parent().button_add_pose.isChecked() \
                    else SquareFaceItem(QRectF(self.start, self.start))
                self.addItem(self.current_rect)
            # elif e.button() == Qt.RightButton:
            if self.parent().button_add_pose.isChecked():
                self.parent().button_add_pose.setChecked(False)
            else:
                self.parent().setAddFace()
            e.accept()
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self.current_rect is not None:
            self.current_rect.setRect(QRectF(self.start, e.scenePos()))
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if self.current_rect is not None:
            self.current_rect.setInit()
            self.current_rect = None
        super().mouseReleaseEvent(e)

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        painter.setPen(Qt.transparent)
        painter.setBrush(Qt.lightGray)
        painter.drawRect(self.sceneRect())

    # set zoom of key points to ensure scale invariance
    def setPointZoom(self, factor=1.0):
        """
        scale key points of all pose items
        :param factor: factor to scale
        :return:
        """
        for item in self.items():
            if type(item) is PoseItem:
                item.scalePoint(factor)
            elif type(item) is FaceItem or type(item) is SquareFaceItem:
                item.scaleBbox(factor)

