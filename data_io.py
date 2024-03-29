import os
import glob
from graphics.labels.PoseItem import PoseItem
from graphics.labels.FaceItem import FaceItem
from pycocotools.coco import COCO
from PyQt5.QtCore import QRectF
import json
from PIL import Image

base_dir = os.path.dirname(__file__)


def load_annotations(img_name: str):
    """
    read corresponding json file of a image
    :param img_name: name of the image file
    :return: a list, each is an item of annotation
    """
    path, name = os.path.split(img_name)
    name, ext = os.path.splitext(name)
    anno_files = glob.glob(os.path.join(path, name + "_annotation" + ".json"))
    annotations = []
    # load annotations from json file
    if len(anno_files) == 0:
        return annotations
    else:
        try:
            coco = COCO(anno_files[0])
            img = coco.loadImgs(ids=[0])
            annotation_ids = coco.getAnnIds(imgIds=img[0]['id'], iscrowd=None)
            annotations = coco.loadAnns(annotation_ids)
        except json.decoder.JSONDecodeError:
            prepare_annotation_file(img_name)
            annotations = []

    # convert to PoseItem and FaceItem
    pose_list = []
    face_list = []
    for annotation in annotations:
        if annotation["category_id"] == 1:
            pose = PoseItem()
            # set bounding box
            rect = QRectF(*annotation["bbox"])
            pose.setRect(rect)
            # set points
            for anno_id in range(0, len(annotation["keypoints"]), 3):
                point_id = anno_id // 3
                x, y, v = annotation["keypoints"][anno_id:anno_id + 3]
                pose.point_list[point_id].setPos(x, y)
                pose.point_list[point_id].setStatus(v)
            pose.updatePointRatio()
            pose_list.append(pose)
        elif annotation["category_id"] == 2:
            face = FaceItem()
            # set bounding box
            x, y, w, h = annotation["bbox"]
            rect = QRectF(x, y, w, h)
            face.setRect(rect)
            face_list.append(face)
    item_list = pose_list + face_list
    return item_list


def save_annotations(img_name, pose_list=None, face_list=None):
    """
    export annotation to json file in coco format
    :param img_name: name of the image
    :param pose_list: list of PoseItems
    :param face_list: list of FaceItems or bbox cords
    :return:
    """
    if face_list is None:
        face_list = []
    if pose_list is None:
        pose_list = []
    path, name = os.path.split(img_name)
    name, ext = os.path.splitext(name)
    annotation_filename = os.path.join(path, name + "_annotation" + ".json")
    if len(pose_list) == 0 and len(face_list) == 0:
        # no need to save
        # delete annotation file if it exists
        if os.path.exists(annotation_filename):
            os.remove(annotation_filename)
        return
    if len(glob.glob(annotation_filename)) == 0:
        prepare_annotation_file(img_name)
    annotations = []
    # add pose annotations
    for idx, pose in enumerate(pose_list):
        annotation = {
            "num_keypoints": 17,
            "iscrowd": 0,
            "keypoints": [],
            "image_id": 0,
            "bbox": [
                pose.rect().x(),
                pose.rect().y(),
                pose.rect().width(),
                pose.rect().height()
            ],
            "category_id": 1,
            "id": idx
        }
        for point in pose.point_list:
            annotation["keypoints"].append(point.x())
            annotation["keypoints"].append(point.y())
            annotation["keypoints"].append(point.status)
        annotations.append(annotation)
    # add legal face annotations
    for idx, face in enumerate(face_list):
        if type(face) is FaceItem:
            face = face.getBboxCords()
        annotation = {
            "iscrowd": 0,
            "image_id": 0,
            "bbox": face,
            "category_id": 2,
            "id": idx
        }
        annotations.append(annotation)

    # write to file
    if os.path.exists(annotation_filename):
        os.remove(annotation_filename)
    prepare_annotation_file(img_name)
    with open(annotation_filename, 'r+') as f:
        data = json.load(f)
        data["annotations"] = annotations
        f.seek(0)
        json.dump(data, f)


def prepare_annotation_file(img_name: str):
    """
    prepare annotation file from template if it doesn't exist
    :param img_name: name of the designated image
    """
    path, name = os.path.split(img_name)
    name, ext = os.path.splitext(name)
    annotation_filename = os.path.join(path, name + "_annotation" + ".json")
    img = Image.open(img_name)
    width, height = img.size
    template_filename = os.path.join(base_dir, "config", "annotation_template.json")
    with open(template_filename) as f:
        json_dict = json.load(f)
    json_dict["images"] = [{
        "file_name": name + ext,
        "height": width,
        "width": height,
        "id": 0
    }
    ]
    with open(annotation_filename, "w") as f:
        json.dump(json_dict, f)


def check_annotation_file(img_name: str):
    """
    check if annotation file exists
    :param img_name: name of the image
    :return: True if exists
    """
    path, name = os.path.split(img_name)
    name, ext = os.path.splitext(name)
    annotation_filename = os.path.join(path, name + "_annotation" + ".json")
    if not os.path.exists(annotation_filename):
        return False
    with open(annotation_filename) as f:
        try:
            data = json.load(f)
            if len(data["annotations"]) == 0:
                return False
        except json.decoder.JSONDecodeError:
            return False
    return True
