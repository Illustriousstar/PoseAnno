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


class PoseItem(QGraphicsRectItem):
    """
    human pose item, contains 17 human key points and corresponding lines
    """
    point_list = None
    line_list = None
    point_colors = None
    line_colors = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlags(QGraphicsItem.ItemIsSelectable)
        self.click_pos = None
        self.click_rect = None
        self.selected_point = None
        self.setAcceptHoverEvents(True)

        if PoseItem.point_list is None:
            with open("config/Poseitem.json") as f:
                json_dict = json.load(f)
                PoseItem.point_list = json_dict["points"]
                PoseItem.line_list = json_dict["lines"]
                PoseItem.point_colors = json_dict["point_colors"]
                PoseItem.line_colors = json_dict["line_colors"]
        # human facing towards you
        self.point_list = []
        for x, y, name in PoseItem.point_list:
            self.point_list.append(KeyPointItem([x, y], parent=self, name=name))
        self.line_list = [QGraphicsLineItem(self) for _ in PoseItem.line_list]

        for idx, point in enumerate(self.point_list):
            point.setPos(self.rect().topLeft())
            point.setBrush(QBrush(QColor(*PoseItem.point_colors[idx])))
            pen = point.pen()
            pen.setWidth(1)
            point.setPen(pen)
            point.setZValue(1.0)
        for line, color in zip(self.line_list, PoseItem.line_colors):
            pen = QPen(QColor(*color))
            pen.setWidth(5)
            line.setPen(pen)

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
                return

        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        pos = e.pos()
        if self.selected_point:
            move = True
            if e.modifiers() & Qt.MetaModifier:
                move = False
            set_point_command = "set" + self.selected_point[0].upper() + self.selected_point[1:]
            self.click_rect.__getattribute__(set_point_command)(e.pos())
            self.setRect(self.click_rect, move)
            e.accept()
        else:
            super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if self.selected_point:
            self.selected_point = None
            self.updatePointRatio()
        else:
            super().mouseReleaseEvent(e)
            # reset pos to (0, 0) after move event
            self.setRect(QRectF(self.rect().topLeft() + self.pos(), self.rect().bottomRight() + self.pos()))
            self.setPos(0.0, 0.0)

    def setRect(self, rect: QRectF = None, move=True) -> None:
        if rect is None:
            rect = self.rect()
        super().setRect(rect)
        # move points
        if move:
            for point in self.point_list:
                shift = self.rect().bottomRight() - self.rect().topLeft()
                x, y = point.ratio
                shift.setX(x * shift.x()), shift.setY(y * shift.y())
                point.setPos(self.rect().topLeft() + shift)

            # move lines
            for (p1, p2), line in zip(PoseItem.line_list, self.line_list):
                line.setLine(QLineF(self.point_list[p1].pos(), self.point_list[p2].pos()))
        super().setRect(rect.normalized())

    def setInit(self, init=True):  # not init state, points are movable
        if not init:
            for point in self.point_list[:-1]:
                point.setFlag(QGraphicsItem.ItemIsMovable)
        # scaling radius
        rect = self.scene().sceneRect()
        radius = min(rect.width(), rect.height()) * 0.015
        for point in self.point_list:
            point.setRadius(radius)

    def updatePointRatio(self):
        # update point ratio
        rect = self.rect().normalized()
        for idx, point in enumerate(self.point_list):
            shift_rect = rect.bottomRight() - rect.topLeft()
            shift_point = point.pos() - rect.topLeft()
            x = shift_point.x() / shift_rect.x() if shift_rect.x() != 0 else point.ratio[0]
            y = shift_point.y() / shift_rect.y() if shift_rect.y() != 0 else point.ratio[1]
            point.ratio = [x, y]
        # set ratio of last point: mid point of left and right shoulder(5 and 6)
        self.point_list[-1].ratio[0] = (self.point_list[5].ratio[0] + self.point_list[6].ratio[0]) / 2
        self.point_list[-1].ratio[1] = (self.point_list[5].ratio[1] + self.point_list[6].ratio[1]) / 2
        self.setRect(rect)

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        super().hoverEnterEvent(event)
        self.setBrush(QColor(255, 0, 0, 96))
        self.setZValue(3)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        super().hoverLeaveEvent(event)
        self.setBrush(QColor(255, 255, 255, 0))
        self.setZValue(0)

    def setZValue(self, z: float) -> None:
        super().setZValue(z)
        for point in self.point_list:
            point.setZValue(z + 1)
        for line in self.line_list:
            line.setZValue(z + 1)


class KeyPointItem(QGraphicsEllipseItem):
    def __init__(self, ratio, radius=15, status=2, parent=None, name: str = ""):
        super().__init__(-radius, -radius, 2 * radius, 2 * radius, parent)
        self.ratio = ratio
        self.radius = radius
        self.status = status
        self.opacity_list = [0, 0.7, 1]

        # label and hover
        self.setAcceptHoverEvents(True)
        self.label = QGraphicsProxyWidget(self)
        self.name = name
        label = QLabel(name)
        label.setFont(QFont('Helvetica', 20))
        label.setStyleSheet("background-color: rgba(255, 255, 255, 30);")
        self.label.setWidget(label)
        self.label.setVisible(False)
        self.label.setPos(self.radius, -self.radius)
        self.label.setZValue(self.zValue() + 1)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.parentItem().updatePointRatio()
        if event.button() == Qt.RightButton:
            self.setStatus((self.status + 1) % 3)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.parentItem().updatePointRatio()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.parentItem().updatePointRatio()
        super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.label.setVisible(True)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.label.setVisible(False)

    def setRadius(self, radius):
        self.setRect(-radius, -radius, 2 * radius, 2 * radius)

    def setStatus(self, status):
        """
        set visible status of point
        :param status: 0 - not labeled, 1 - not visible, 2 - visible
        :return:
        """
        self.status = status
        opacity = self.opacity_list[status]
        brush = self.brush()
        color = brush.color()
        color.setAlphaF(opacity)
        brush.setColor(color)
        self.setBrush(brush)

    def setZValue(self, z):
        super().setZValue(z)
        self.label.setZValue(z + 1)
