import math
from PyQt5.QtCore import (
    Qt,
    QRectF,
)
from PyQt5.QtGui import (
    QNativeGestureEvent,
    QPainter,
    QPixmap,
)
from PyQt5.QtWidgets import QGraphicsView


class View(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setDragMode(self.RubberBandDrag)
        self.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing |
                            QPainter.SmoothPixmapTransform)
        # self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setResizeAnchor(self.AnchorUnderMouse)
        self.setTransformationAnchor(self.AnchorUnderMouse)

    def scaleView(self, scaleFactor):
        factor = self.transform().scale(
            scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()
        # restrict total scale factor
        if factor < 0.5 or factor > 20:
            return
        self.setResizeAnchor(self.AnchorUnderMouse)
        self.scale(scaleFactor, scaleFactor)
        self.scene().zoom_signal.emit(1 / scaleFactor)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            delta = -event.angleDelta().y()
            factor = 1.1 if 0 < delta else 1 / 1.1
            self.scaleView(factor)
            return event.accept()
        super().wheelEvent(event)

    def event(self, e):
        if isinstance(e, QNativeGestureEvent):
            gesture_type = e.gestureType()
            self.nativeGestureEvent(e)
        return super().event(e)

    def nativeGestureEvent(self, e: QNativeGestureEvent):
        gesture_type = e.gestureType()
        if gesture_type == Qt.ZoomNativeGesture:
            factor = 1.025 if 0 < e.value() else 1 / 1.025
            self.scaleView(factor)
