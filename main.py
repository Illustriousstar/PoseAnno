import sys
from data_io import (
    img_to_annotation,
    annotation_to_pose,
    pose_to_annotation,
    load_openpose
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PoseItem import PoseItem
from Scene import Scene
from View import View


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.scene = Scene(0, 0, 800, 600, self)
        self.view = View(self.scene)

        # state variables
        self.to_add_point = False
        self.cur_img_path = None
        self.pixmap = None

        # right side buttons
        # point buttons
        self.button_add_pose = QPushButton("Add Pose")
        self.button_add_pose.setCheckable(True)
        self.button_delete = QPushButton("Delete")
        self.button_delete.clicked.connect(self.deletePoint)
        self.button_model = QPushButton("model")
        self.button_model.clicked.connect(self.load_model)

        # import / export data
        self.button_import = QPushButton("import")
        self.button_export = QPushButton("export")
        self.button_import.clicked.connect(self.openImage)
        self.button_export.clicked.connect(self.export_data)

        vbox = QVBoxLayout()
        vbox.addWidget(self.button_add_pose)
        vbox.addWidget(self.button_delete)
        vbox.addWidget(self.button_import)
        vbox.addWidget(self.button_export)
        vbox.addWidget(self.button_model)

        hbox = QHBoxLayout()
        hbox.addWidget(self.view)
        hbox.addLayout(vbox)

        self.setLayout(hbox)
        rect = QApplication.instance().desktop().availableGeometry(self)
        self.resize(int(rect.width() * 2 / 3), int(rect.height() * 2 / 3))

    def deletePoint(self):
        for item in self.scene.selectedItems():
            self.scene.removeItem(item)

    def openImage(self):
        image_path, _ = QFileDialog.getOpenFileName()
        if len(image_path) == 0:
            return

        if self.cur_img_path:
            self.cur_img_path = None
            self.pixmap = None
        for item in self.scene.items():
            self.scene.removeItem(item)
        self.cur_img_path = image_path
        self.pixmap = QPixmap(image_path)
        self.pixmap = self.scene.addPixmap(self.pixmap)
        self.pixmap.setZValue(-1)
        self.view.fitInView(self.pixmap, Qt.KeepAspectRatio)
        self.scene.setSceneRect(self.pixmap.boundingRect())

        # load annotations
        annotations = img_to_annotation(image_path)

        for pose in annotation_to_pose(annotations):
            self.scene.addItem(pose)

        for item in self.scene.items():
            if type(item) is PoseItem:
                item.setInit(False)

    def export_data(self):
        pose_list = []
        for item in self.scene.items():
            if type(item) is PoseItem:
                pose_list.append(item)
        pose_to_annotation(self.cur_img_path, pose_list)

    def load_model(self):
        if self.cur_img_path is None:
            return
        pose_list = load_openpose(self.cur_img_path, remote=True)
        for pose in pose_list:
            self.scene.addItem(pose)

        for item in self.scene.items():
            if type(item) is PoseItem:
                item.setInit(False)


app = QApplication(sys.argv)

w = Window()
w.show()

app.exec()
