import os
import glob
import json
import sys
import cv2
from PoseItem import PoseItem
from pycocotools.coco import COCO
from PyQt5.QtCore import QRectF
import numpy as np
from sys import platform
import requests
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
    # print(len(pose_list))
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


def load_openpose(img_path, remote=False):
    """
    load openpose model to predict pose
    :param img_path: path of image
    :return: pose item
    """
    if not remote:
        from openpose.build.python.openpose import pyopenpose as op
        params = dict()
        params["model_folder"] = "openpose/models/"

        # Starting OpenPose
        opWrapper = op.WrapperPython()
        opWrapper.configure(params)
        opWrapper.start()

        # Process Image
        datum = op.Datum()
        imageToProcess = cv2.imread(img_path)
        datum.cvInputData = imageToProcess
        opWrapper.emplaceAndPop(op.VectorDatum([datum]))

        print("Body keypoints: \n" + str(datum.poseKeypoints))
        key_points = np.array(datum.poseKeypoints)
        return process_openpose(key_points)
    else:
        url = "http://166.111.139.99:5000/openpose"
        files = {
            "file": open(img_path, "rb")
        }
        result = requests.post(url, files=files)
        result = np.array(result.json())
        return process_openpose(result)


def process_openpose(key_points: np.array) -> list:
    keypoint_map = [
        0, 16, 15, 18, 17, 5, 2, 6, 3, 7, 4, 12, 9, 13, 10, 14, 11
    ]
    key_points = key_points[:, keypoint_map, :]
    pose_list = []
    for keypoint in key_points:
        pose = PoseItem()
        # set bounding box
        # rect in (x, y, w, h)
        valid_points = keypoint[keypoint[:, 0] + keypoint[:, 1] > 5][:, :2]
        x_y = np.min(valid_points, axis=0)
        w_h = np.max(valid_points, axis=0) - x_y
        x_y = x_y - w_h * 0.1
        w_h = w_h * 1.2
        print(np.concatenate((x_y, w_h)))
        rect = QRectF(*np.concatenate((x_y, w_h)))
        pose.setRect(rect)
        # set points
        for id in range(17):
            if np.sum(keypoint[id, :2]) > 1.0:  # valid point
                pose.point_list[id].setPos(*keypoint[id, :2])
            else:  # point not detected
                pose.point_list[id].setStatus(0)
        pose.updatePointRatio()
        pose_list.append(pose)
    return pose_list
