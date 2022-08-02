from PyQt5.QtCore import QRectF
from graphics.labels.PoseItem import PoseItem
import numpy as np
import requests
import cv2


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

        key_points = np.array(datum.poseKeypoints)
        return process_openpose(key_points)
    else:
        url = "http://lab_dust:5000/openpose"
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
