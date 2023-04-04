# convert txt format to json format

import os
from glob import glob
from data_io import save_annotations, prepare_annotation_file
from tqdm import tqdm
from config.config import dataset_dir


def convert_txt2json(txt_dir: str, imgs_dir: str):
    for txt_file in tqdm(glob(os.path.join(txt_dir, "*.txt"))):
        with open(txt_file, "r") as f:
            lines = f.readlines()
        lines = [line.strip() for line in lines]
        img_name = os.path.join(imgs_dir, lines[0] + ".jpg")
        face_num = int(lines[1])
        if face_num == 0:
            continue
        face_list = lines[2:]
        face_list = [face.split(" ") for face in face_list]
        face_list = [[float(x) for x in face[:4]] for face in face_list]
        face_list = [[x, y, w, h] for x, y, w, h in face_list]
        prepare_annotation_file(img_name)
        save_annotations(img_name, [], face_list)


if __name__ == "__main__":
    txt = "/Users/maotianwei/Desktop/results/%d"
    imgs = dataset_dir + "/待标注/%d"
    for id in range(51, 61 + 1):
        print("processing folder %d" % id)
        convert_txt2json(txt % id, imgs % id)
