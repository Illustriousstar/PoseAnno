from PyQt5.QtWidgets import (
    QAction,
    QWidget,
    QWidgetAction,
    QSizePolicy,
    QToolBar,
    QToolButton
)
from PyQt5.QtCore import Qt


class ToolBar(QToolBar):
    """
    toolbar with buttons, copied from:
    https://github.com/wkentaro/labelme/blob/819a93cbbc8a7ae3009e9f380111d742e6c06615/labelme/widgets/tool_bar.py#L5
    """

    def __init__(self, title: str, actions: list):
        super(ToolBar, self).__init__(title)
        layout = self.layout()
        m = (0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setContentsMargins(*m)
        layout.setAlignment(Qt.AlignCenter)
        self.setContentsMargins(*m)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        self.addActions(actions)

    def addAction(self, action: QAction):
        """convert action into buttons"""
        if isinstance(action, QWidgetAction):
            return super(ToolBar, self).addAction(action)
        btn = QToolButton()
        btn.setDefaultAction(action)
        btn.setToolButtonStyle(self.toolButtonStyle())
        self.addWidget(btn)

        # center align
        for i in range(self.layout().count()):
            if isinstance(
                    self.layout().itemAt(i).widget(), QToolButton
            ):
                self.layout().itemAt(i).setAlignment(Qt.AlignCenter)

    def addActions(self, actions: list):
        left_spacer = QWidget()
        left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_spacer = QWidget()
        right_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.addWidget(left_spacer)
        for action in actions:
            self.addAction(action)
        self.addWidget(right_spacer)
