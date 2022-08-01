from PyQt5.QtCore import (
    Qt,
    QLineF,
    QRectF,
    QPointF,
)
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QPen,
    QPixmap,
    QFont
)
from PyQt5.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsRectItem,
    QGraphicsProxyWidget,
    QLabel,
)
import json
import os


class FaceItem(QGraphicsRectItem):
    """
    Item for face bounding box
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.click_pos = None
        self.click_rect = None
        self.selected_point = None

        self.setFlags(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)

        # draw bounding box
        pen = QPen(Qt.black)
        pen.setWidth(5)
        self.setPen(pen)

    def mousePressEvent(self, e):
        # scaling bounding rect
        self.click_pos = e.pos()
        rect = self.rect()
        self.click_rect = rect
        for point in ["topLeft", "topRight", "bottomLeft", "bottomRight"]:
            point_pos = rect.__getattribute__(point)()
            if (point_pos - self.click_pos).manhattanLength() < 10:
                self.selected_point = point
                e.accept()

        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        pos = e.pos()
        if self.selected_point:
            set_point_command = "set" + self.selected_point[0].upper() + self.selected_point[1:]
            self.click_rect.__getattribute__(set_point_command)(e.pos())
            self.setRect(self.click_rect)
            e.accept()
        else:
            super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if self.selected_point:
            self.selected_point = None
        else:
            super().mouseReleaseEvent(e)
            # reset pos to (0, 0) after move event
            self.setRect(QRectF(self.rect().topLeft() + self.pos(), self.rect().bottomRight() + self.pos()))
            self.setPos(0.0, 0.0)

    def setRect(self, rect: QRectF = None) -> None:
        super().setRect(rect.normalized())

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        super().hoverEnterEvent(event)
        self.setBrush(QColor(255, 0, 0, 96))

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        super().hoverLeaveEvent(event)
        self.setBrush(QColor(255, 255, 255, 0))