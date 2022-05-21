import math
from PyQt5.QtCore import (
    Qt,
    QRectF,
)
from PyQt5.QtGui import (
    QPainter,
    QPixmap,
)
from PyQt5.QtWidgets import QGraphicsView


class View(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDragMode(self.RubberBandDrag)
        self.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing |
                            QPainter.SmoothPixmapTransform)
        # self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setResizeAnchor(self.AnchorUnderMouse)
        self.setTransformationAnchor(self.AnchorUnderMouse)

    def scaleView(self, scaleFactor):
        factor = self.transform().scale(
            scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            return
        self.scale(scaleFactor, scaleFactor)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            self.scaleView(math.pow(2.0, -event.angleDelta().y() / 240.0))
            return event.accept()
        super().wheelEvent(event)
