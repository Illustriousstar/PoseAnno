import os
from bs4 import BeautifulSoup
from glob import glob
from data_io import save_annotations, prepare_annotation_file
from config.config import dataset_dir

batch_dir = os.path.join(dataset_dir, "batch2")


def extract_face_from_xml(xml_dir: str):
    """ read xml file and return face detection results"""
    with open(xml_dir, "r") as f:
        data = f.read()
    data = BeautifulSoup(data, "xml")
    face_list = data.find_all("face")
    result_list = []
    for face in face_list:
        cords = face.find("circle").attrs.values()
        cords = [float(x) for x in cords]
        result_list.append(cords)
    return result_list


def save_face_in_json(xml_name: str, face_list: list):
    img_name = xml_name[:-4]
    prepare_annotation_file(img_name)
    face_list = [
        [x[0] - x[2], x[1] - x[2], 2 * x[2]] for x in face_list
    ]
    save_annotations(img_name, [], face_list)


if __name__ == "__main__":
    dirs = glob(os.path.join(batch_dir, "*.xml"))
    for dir in dirs:
        face_list = extract_face_from_xml(dir)
        save_face_in_json(dir, face_list)
