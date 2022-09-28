from .FaceItem import FaceItem
from PyQt5.QtCore import (
    QRectF,
)
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsRectItem,
)


class SquareFaceItem(FaceItem):
    """ item for square face bounding box """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_state = True
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

    def setInit(self):
        """
        operations after face item is created added to scene,
        set points movable and set point radius
        :return:
        """
        super().setInit()
        self.init_state = False

    def setRect(self, rect: QRectF = None) -> None:

        if rect is None:
            rect = self.rect()
        if self.init_state:
            # rectify bounding box to square
            width, height = rect.width(), rect.height()
            # use the min edge length to scale the bounding box
            if width > height:
                rect.setRight(rect.left() + height)
            else:
                rect.setBottom(rect.top() + width)
        super().setRect(rect.normalized())

    def rectifyBbox(self, rect: QRectF = None):
        """
        scale bounding box
        :return:
        """
        if rect is None:
            rect = self.rect()
        width = rect.width()
        height = rect.height()
        # center should not change
        center = rect.center()
        if width > height:
            rect.setTop(rect.top() - (width - height) / 2)
            rect.setBottom(rect.bottom() + (width - height) / 2)
        else:
            rect.setLeft(rect.left() - (height - width) / 2)
            rect.setRight(rect.right() + (height - width) / 2)
        self.setRect(rect)

    def mouseMoveEvent(self, e):
        pos = e.pos()
        if not self.selected_point:
            super().mouseMoveEvent(e)
            return
        if self.selected_point == "topLeft":
            width, height = self.click_rect.bottomRight().x() - pos.x(), self.click_rect.bottomRight().y() - pos.y()
            if width > height:
                self.click_rect.setTop(pos.y())
                self.click_rect.setLeft(pos.x() + (width - height))
            else:
                self.click_rect.setTop(pos.y() + (height - width))
                self.click_rect.setLeft(pos.x())
        elif self.selected_point == "topRight":
            width, height = pos.x() - self.click_rect.bottomLeft().x(), self.click_rect.bottomLeft().y() - pos.y()
            if width > height:
                self.click_rect.setTop(pos.y())
                self.click_rect.setRight(pos.x() - (width - height))
            else:
                self.click_rect.setTop(pos.y() + (height - width))
                self.click_rect.setRight(pos.x())
        elif self.selected_point == "bottomLeft":
            width, height = self.click_rect.topRight().x() - pos.x(), pos.y() - self.click_rect.topRight().y()
            if width > height:
                self.click_rect.setBottom(pos.y())
                self.click_rect.setLeft(pos.x() + (width - height))
            else:
                self.click_rect.setBottom(pos.y() - (height - width))
                self.click_rect.setLeft(pos.x())
        elif self.selected_point == "bottomRight":
            width, height = pos.x() - self.click_rect.topLeft().x(), pos.y() - self.click_rect.topLeft().y()
            if width > height:
                self.click_rect.setBottom(pos.y())
                self.click_rect.setRight(pos.x() - (width - height))
            else:
                self.click_rect.setBottom(pos.y() - (height - width))
                self.click_rect.setRight(pos.x())
        self.setRect(self.click_rect)
        self.check()

    def getBboxCords(self):
        """
        get bounding box coordinates in [x1, y1, w] format
        :return:
        """
        rect = self.rect()
        return rect.x(), rect.y(), rect.width()
