import os
import glob
from graphics.labels.PoseItem import PoseItem
from pycocotools.coco import COCO
from PyQt5.QtCore import QRectF
import json

import PIL


def annotation_to_pose(annotations):
    """
    convert coco annotation of one person to poseItem
    :param annotations: list of annotations, each for a instance in coco format
    :return: list of PoseItem
    """
    pose_list = []
    for annotation in annotations:
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
    return pose_list


def img_to_annotation(img_name):
    """
    read corresponding json file of a image
    :param img_name: name of the image file
    :return: a list, each is an item of annotation
    """
    path, name = os.path.split(img_name)
    name, ext = os.path.splitext(name)
    anno_files = glob.glob(os.path.join(path, name + "_annotation" + ".json"))
    annotations = []
    if len(anno_files) == 0:
        prepare_annotation_file(img_name)
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
    return annotations


def pose_to_annotation(img_name, pose_list):
    """
    export pose items to annotation file in coco format
    :param img_name: name of the image
    :param pose_list: list of PoseItems
    :return:
    """
    path, name = os.path.split(img_name)
    name, ext = os.path.splitext(name)
    annotation_filename = os.path.join(path, name + "_annotation" + ".json")
    if len(glob.glob(annotation_filename)) == 0:
        prepare_annotation_file(img_name)
    annotations = []
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
    try:
        f = open(annotation_filename, "r+")
        data = json.load(f)
    except json.decoder.JSONDecodeError:
        prepare_annotation_file(img_name)
        f = open(annotation_filename, "r+")
        data = json.load(f)
    data["annotations"] = annotations
    f.seek(0)
    json.dump(data, f)
    f.close()


def prepare_annotation_file(img_name):
    """
    prepare annotation file from template if it doesn't exist
    :param img_name: name of the designated image
    """
    path, name = os.path.split(img_name)
    name, ext = os.path.splitext(name)
    annotation_filename = os.path.join(path, name + "_annotation" + ".json")
    img = PIL.Image.open(img_name)
    width, height = img.size
    with open("config/annotation_template.json") as f:
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


