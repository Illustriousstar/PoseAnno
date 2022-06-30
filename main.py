import sys
import os
from data_io import (
    img_to_annotation,
    annotation_to_pose,
    pose_to_annotation,
    load_openpose
)
from PyQt5.QtCore import Qt, QFile
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QGraphicsPixmapItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
import natsort
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
        self.pixmap = None
        self.output_dir = None
        self.lastOpenDir = None
        self.filename = None
        self.imageList = []

        # right side buttons
        # point buttons
        self.button_add_pose = QPushButton("Add Pose")
        self.button_add_pose.setCheckable(True)
        self.button_delete = QPushButton("Delete")
        self.button_delete.clicked.connect(self.deletePoint)
        self.button_model = QPushButton("Model")
        self.button_model.clicked.connect(self.load_model)
        # import / export data
        self.button_import = QPushButton("Open")
        self.button_export = QPushButton("Save")
        self.button_open_dir = QPushButton("Open Dir")
        self.button_open_prev_img = QPushButton("Prev")
        self.button_open_next_img = QPushButton("Next")
        self.button_import.clicked.connect(self.openImgDialog)
        self.button_export.clicked.connect(self.export_data)
        self.button_open_dir.clicked.connect(self.openDirDialog)
        self.button_open_prev_img.clicked.connect(lambda: self.switchImg(open_next=False))
        self.button_open_next_img.clicked.connect(lambda: self.switchImg(open_next=True))

        # widgets
        self.fileListWidget = QListWidget()

        vbox = QVBoxLayout()
        vbox.addWidget(self.button_add_pose)
        vbox.addWidget(self.button_delete)
        vbox.addWidget(self.button_import)
        vbox.addWidget(self.button_export)
        vbox.addWidget(self.button_model)
        vbox.addWidget(self.button_open_dir)
        vbox.addWidget(self.button_open_prev_img)
        vbox.addWidget(self.button_open_next_img)
        # vbox.addWidget(self.fileListWidget)

        hbox = QHBoxLayout()
        hbox.addWidget(self.view)
        hbox.addLayout(vbox)

        self.setLayout(hbox)
        rect = QApplication.instance().desktop().availableGeometry(self)
        self.resize(int(rect.width() * 2 / 3), int(rect.height() * 2 / 3))

    def deletePoint(self):
        for item in self.scene.selectedItems():
            self.scene.removeItem(item)

    def openImgDialog(self):
        image_path, _ = QFileDialog.getOpenFileName()
        if len(image_path) == 0:
            return
        self.loadFile(image_path)

    def export_data(self):
        pose_list = []
        for item in self.scene.items():
            if type(item) is PoseItem:
                pose_list.append(item)
        pose_to_annotation(self.filename, pose_list)

    def load_model(self):
        if self.filename is None:
            return
        pose_list = load_openpose(self.filename, remote=True)
        for pose in pose_list:
            self.scene.addItem(pose)

        for item in self.scene.items():
            if type(item) is PoseItem:
                item.setInit()

    def openDirDialog(self, _value=False, dirpath=None):
        defaultOpenDirPath = dirpath if dirpath else "."
        if self.lastOpenDir and os.path.exists(self.lastOpenDir):
            defaultOpenDirPath = self.lastOpenDir
        else:
            defaultOpenDirPath = (
                os.path.dirname(self.filename) if self.filename else "."
            )

        targetDirPath = str(
            QFileDialog.getExistingDirectory(
                self,
                "Open Directory",
                defaultOpenDirPath,
                QFileDialog.ShowDirsOnly
                | QFileDialog.DontResolveSymlinks,
            )
        )
        self.importDirImages(targetDirPath)

    def importDirImages(self, dir, pattern=None, load=True):
        """
        open dir function, copied from labelme
        https://github.com/wkentaro/labelme/blob/819a93cbbc8a7ae3009e9f380111d742e6c06615/labelme/app.py#L2027
        :param dir: directory to open
        :param pattern: specific pattern required of the filename
        :param load: whether load image file or nor
        :return:
        """
        if not dir:
            return
        self.lastOpenDir = dir
        self.filename = None
        self.fileListWidget.clear()
        for filename in self.scanAllImages(dir):
            if pattern and pattern not in filename:
                continue
            label_file = os.path.splitext(filename)[0] + ".json"
            if self.output_dir:
                label_file_without_path = os.path.basename(label_file)
                label_file = os.path.join(self.output_dir, label_file_without_path)
            item = QListWidgetItem(filename)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            if QFile.exists(label_file):
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.fileListWidget.addItem(item)
        self.imageList = []
        for i in range(self.fileListWidget.count()):
            item = self.fileListWidget.item(i)
            self.imageList.append(item.text())
        self.switchImg(open_next=True)

    def scanAllImages(self, folderPath):
        """
        scan all images in dir folder, copied from labelme
        https://github.com/wkentaro/labelme/blob/819a93cbbc8a7ae3009e9f380111d742e6c06615/labelme/app.py#L2055
        :param folderPath: folder to scan
        :return:
        """
        extensions = [
            ".%s" % fmt.data().decode().lower()
            for fmt in QtGui.QImageReader.supportedImageFormats()
        ]

        images = []
        for root, dirs, files in os.walk(folderPath):
            for file in files:
                if file.lower().endswith(tuple(extensions)):
                    relativePath = os.path.join(root, file)
                    images.append(relativePath)
        images = natsort.os_sorted(images)
        return images

    def switchImg(self, open_next=True):
        """
        switch to adjacent image
        :param open_next: whether to open the next or previous img
        :return:
        """
        if len(self.imageList) <= 0:
            return
        filename = None
        if self.filename is None:
            filename = self.imageList[0]
        else:
            cur_index = self.imageList.index(self.filename)
            len_list = len(self.imageList)
            if open_next:
                next_index = (cur_index + 1) % len_list
            else:
                next_index = (cur_index - 1 + len_list) % len_list
            filename = self.imageList[next_index]
        self.filename = filename
        if self.filename:
            self.loadFile(self.filename)

    def loadFile(self, filename=None):
        """
        Load the specified file, or the last opened file if None.
        :param filename: file to open
        :return: whether successful or not
        """
        """"""
        # file should exist
        if filename is None:
            return False
        filename = str(filename)
        if not QFile.exists(filename):
            return False

        # changing fileListWidget loads file
        if filename in self.imageList and (
                self.fileListWidget.currentRow() != self.imageList.index(filename)
        ):
            # TODO: error message
            self.fileListWidget.setCurrentRow(self.imageList.index(filename))
            self.fileListWidget.repaint()

        self.filename = filename
        # delete previous pixmap
        self.scene.removeItem(self.pixmap)
        self.pixmap = QtGui.QPixmap(filename)
        self.pixmap = self.scene.addPixmap(self.pixmap)
        self.pixmap.setZValue(-1)
        self.scene.setSceneRect(self.pixmap.boundingRect())
        self.view.fitInView(self.pixmap, Qt.KeepAspectRatio)

        # prepare json file
        # assumes same name, but json extension
        # load annotations
        # TODO: keep previous annotations ?
        for item in self.scene.items():
            if type(item) is not QGraphicsPixmapItem:
                self.scene.removeItem(item)
        annotations = img_to_annotation(filename)
        for pose in annotation_to_pose(annotations):
            self.scene.addItem(pose)
        for item in self.scene.items():
            if type(item) is PoseItem:
                item.setInit()
        return True


app = QApplication(sys.argv)

w = Window()
w.show()

app.exec()
