import os.path
import sys
from config.config import dataset_dir
from data_io import (
    prepare_annotation_file,
    save_annotations,
    load_annotations,
    check_annotation_file,
)
from models.openpose import load_openpose
from PyQt5.QtCore import Qt, QFile
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QGraphicsPixmapItem,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QLabel
)
import natsort
from graphics.labels.PoseItem import PoseItem
from graphics.labels.FaceItem import FaceItem
from graphics.Scene import Scene
from graphics.View import View
from utils import *
from toolbar import ToolBar

open_img_dir = os.path.join(dataset_dir, "1")


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.scene = Scene(0, 0, 800, 600, self)
        self.view = View(self.scene)

        # state variables
        self.to_add_face = False
        self.pixmap = None
        self.output_dir = None
        self.lastOpenDir = None
        self.filename = None
        self.imageList = []

        # actions
        delete_item = newAction(
            parent=self,
            text=self.tr("&Delete"),
            slot=self.deleteItem,
            shortcut=[QKeySequence.Delete, "R"],
            icon="DELETE"
        )

        delete_all_items = newAction(
            parent=self,
            text=self.tr("&Delete All"),
            slot=lambda: self.deleteItem(delete_all=True),
            shortcut=["Ctrl+R"],
            icon="DELETE"
        )

        open_next_img = newAction(
            parent=self,
            text=self.tr("&Next Image"),
            slot=lambda: self.switchImg(open_next=True),
            shortcut="D",
            icon="NEXT",
        )

        open_prev_img = newAction(
            parent=self,
            text=self.tr("&Prev Image"),
            slot=lambda: self.switchImg(open_next=False),
            shortcut="A",
            icon="PREVIOUS",
        )

        add_face = newAction(
            parent=self,
            text=self.tr("&Add Face"),
            slot=lambda: self.setAddFace(),
            shortcut="F",
            icon="FACE",
        )

        # toolbar
        toolbar = ToolBar("Tools", [open_prev_img, delete_item, delete_all_items, add_face, open_next_img])

        # right side buttons
        # point buttons
        self.button_add_pose = QPushButton("新建姿态")
        self.button_add_pose.setCheckable(True)
        self.button_delete = QPushButton("删除")
        self.button_delete.clicked.connect(delete_item.trigger)
        self.button_model = QPushButton("模型预测")
        self.button_model.clicked.connect(self.load_model)
        # import / export data
        self.button_open_img = QPushButton("打开文件")
        self.button_export = QPushButton("保存标注")
        self.button_open_dir = QPushButton("打开文件夹")
        self.button_open_img.clicked.connect(self.openImgDialog)
        self.button_export.clicked.connect(self.saveAnnotations)
        self.button_open_dir.clicked.connect(self.openDirDialog)

        self.progress_label = QLabel("0/0, 0%")
        self.progress_label.setMaximumHeight(10)

        # widgets
        self.fileListWidget = QListWidget()
        self.fileListWidget.setResizeMode(QListWidget.Adjust)

        vbox_right_widget = QWidget()
        vbox_right = QVBoxLayout(vbox_right_widget)
        vbox_right.addWidget(self.progress_label)
        vbox_right.addWidget(self.button_open_img)
        vbox_right.addWidget(self.button_open_dir)
        vbox_right.addWidget(self.button_add_pose)
        vbox_right.addWidget(self.button_delete)
        vbox_right.addWidget(self.button_export)
        vbox_right.addWidget(self.button_model)
        vbox_right.addWidget(self.fileListWidget)

        vbox_left_widget = QWidget()
        vbox_left = QVBoxLayout(vbox_left_widget)
        vbox_left.addWidget(toolbar)
        vbox_left.addWidget(self.view)

        hbox = QHBoxLayout()
        # hbox.addLayout(vbox_left)
        # add adjustable splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(3)
        splitter.addWidget(vbox_left_widget)
        splitter.addWidget(vbox_right_widget)
        splitter.setChildrenCollapsible(False)
        # hbox.addLayout(vbox_right)
        hbox.addWidget(splitter)

        self.setLayout(hbox)
        rect = QApplication.instance().desktop().availableGeometry(self)
        self.resize(int(rect.width() * 2 / 3), int(rect.height() * 2 / 3))

        self.importDirImages(dir=open_img_dir)

    def deleteItem(self, delete_all=False):
        for item in (self.scene.items() if delete_all else self.scene.selectedItems()):
            if isinstance(item, FaceItem) or isinstance(item, PoseItem):
                self.scene.removeItem(item)

    def openImgDialog(self):
        image_path, _ = QFileDialog.getOpenFileName()
        if len(image_path) == 0:
            return
        self.loadFile(image_path)

    def saveAnnotations(self):
        if self.filename is None:
            return
        pose_list = []
        face_list = []
        for item in self.scene.items():
            if type(item) is PoseItem:
                pose_list.append(item)
            elif type(item) is FaceItem and item.legal:
                face_list.append(item)
        save_annotations(self.filename, pose_list, face_list)

    def load_model(self):
        if self.filename is None:
            return
        pose_list = load_openpose(self.filename, remote=True)
        for pose in pose_list:
            self.scene.addItem(pose)

        for item in self.scene.items():
            if type(item) is PoseItem or type(item) is FaceItem:
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
        self.imageList = self.scanAllImages(dir)
        for filename in self.imageList:
            if pattern and pattern not in filename:
                continue
            label_file = os.path.splitext(filename)[0] + "_annotation.json"
            if self.output_dir:
                label_file_without_path = os.path.basename(label_file)
                label_file = os.path.join(self.output_dir, label_file_without_path)
            item = QListWidgetItem(os.path.basename(filename))
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            if QFile.exists(label_file):
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.fileListWidget.addItem(item)
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
        # save annotations
        self.saveAnnotations()
        if len(self.imageList) <= 0:
            return

        # refresh fileListWidget check state
        if self.filename and check_annotation_file(self.filename):
            self.fileListWidget.item(self.fileListWidget.currentRow()).setCheckState(
                Qt.Checked
            )
        elif self.fileListWidget.item(self.fileListWidget.currentRow()) is not None:
            self.fileListWidget.item(self.fileListWidget.currentRow()).setCheckState(
                Qt.Unchecked
            )

        filename = None
        # get next image info
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
            self.progress_label.setText(f"{next_index} / {len_list}, {next_index / len_list * 100:.2f}%")
        self.filename = filename

        # load image
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
        if self.pixmap:
            self.scene.removeItem(self.pixmap)
        self.pixmap = QtGui.QPixmap(filename)
        self.pixmap = self.scene.addPixmap(self.pixmap)
        self.pixmap.setZValue(-1)
        self.scene.setSceneRect(self.pixmap.boundingRect())
        self.view.fitInView(self.pixmap, Qt.KeepAspectRatio)

        # prepare json file
        # assumes same name, but json extension
        # load annotations
        for item in self.scene.items():
            if type(item) is not QGraphicsPixmapItem:
                self.scene.removeItem(item)
        for item in load_annotations(filename):
            self.scene.addItem(item)
        for item in self.scene.items():
            if type(item) is PoseItem \
                    or type(item) is FaceItem:
                item.setInit()
        return True

    def setAddFace(self):
        """Reverse state of to_add_face"""
        self.to_add_face = not self.to_add_face


app = QApplication(sys.argv)

w = Window()
w.show()

app.exec()
