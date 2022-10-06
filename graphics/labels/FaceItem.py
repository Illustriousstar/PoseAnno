from PyQt5.QtCore import (
    Qt,
    QRectF,
)
from PyQt5.QtGui import (
    QColor,
    QPen
)
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsRectItem,
)


class FaceItem(QGraphicsRectItem):
    """
    Item for face bounding box
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.click_pos = None
        self.click_rect = None
        self.selected_point = None
        self.bbox_width = 3
        self.legal = True

        self.setFlags(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)

        self.scaleBbox()

    def setRect(self, rect: QRectF = None) -> None:
        super().setRect(rect.normalized())

    def setInit(self):
        """
        operations after face item is created added to scene,
        set points movable and set point radius
        :return:
        """
        rect = self.scene().sceneRect()
        self.check()

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        super().hoverEnterEvent(event)
        self.setBrush(QColor(255, 0, 0, 96))

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        super().hoverLeaveEvent(event)
        self.setBrush(QColor(255, 255, 255, 0))

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
            self.check()
        else:
            super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if self.selected_point:
            self.selected_point = None
            self.check()
        else:
            super().mouseReleaseEvent(e)
            # reset pos to (0, 0) after move event
            self.setRect(QRectF(self.rect().topLeft() + self.pos(), self.rect().bottomRight() + self.pos()))
            self.setPos(0.0, 0.0)

    def scaleBbox(self, factor=1.0):
        """
        scale width of bounding box using given factor
        :param factor: factor to scale
        :return:
        """
        self.bbox_width *= factor
        pen = QPen(Qt.green)
        pen.setWidth(self.bbox_width)
        self.setPen(pen)

    def check(self):
        """
        check whether face is legal
        :return:
        """
        # 1. bbox should be no less than 24x24
        if self.rect().width() < 24 or self.rect().height() < 24:
            self.legal = False
        # space for future restrictions
        else:
            self.legal = True

        # set pen to black if legal, red if not
        if self.legal:
            pen = QPen(Qt.green)
            pen.setWidth(self.bbox_width)
            self.setPen(pen)
        else:
            pen = QPen(Qt.red)
            pen.setWidth(self.bbox_width)
            self.setPen(pen)

    def getBboxCords(self):
        """
        get bounding box cordinates in [x1, y1, w, h] format
        :return:
        """
        return [self.rect().x(), self.rect().y(), self.rect().width(), self.rect().height()]
