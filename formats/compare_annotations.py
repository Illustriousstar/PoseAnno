# compare new json annotation with old wider face annotation
from config.config import dataset_dir, wider_face_dir
import random
import os
import cv2
import json
import numpy as np
from glob import glob
from tqdm import tqdm

save_dir = "/Users/maotianwei/Desktop/compare_annotations"
random.seed(0)

# randomly select 100 images from training set of wider face
old_annotation_dir = wider_face_dir + "wider_face_split/wider_face_train_bbx_gt.txt"
# read the file and get all annotations
img_list = []
bbox_list = []
with open(old_annotation_dir, "r") as f:
    lines = f.readlines()
    idx = 0
    while idx < len(lines):
        img_name = lines[idx].strip()
        img_list.append(img_name)
        bbox_num = int(lines[idx + 1].strip())
        bbox = []
        for i in range(bbox_num):
            bbox.append(lines[idx + 2 + i].strip().split(" "))
        bbox_list.append(bbox)
        bbox_num = max(bbox_num, 1)
        idx += bbox_num + 2

# randomly select 100 of them
sample_idx = random.sample(range(len(img_list)), 100)
sample_img_list = [img_list[idx] for idx in sample_idx]
sample_bbox_list = [bbox_list[idx] for idx in sample_idx]

# save original images without annotations
save_dir_ori = os.path.join(save_dir, "ori")
os.makedirs(save_dir_ori, exist_ok=True)
for img_name in tqdm(sample_img_list):
    img = cv2.imread(os.path.join(wider_face_dir, "WIDER_train/images/", img_name))
    cv2.imwrite(os.path.join(save_dir_ori, img_name.split("/")[-1]), img)

save_dir_old = os.path.join(save_dir, "old")
os.makedirs(save_dir_old, exist_ok=True)
# # draw the bounding box in red on the image and save it
# for img_dir, bboxes in zip(sample_img_list, sample_bbox_list):
#     img_dir = os.path.join(wider_face_dir, "WIDER_train/images", img_dir)
#     img = cv2.imread(img_dir)
#     for bbox in bboxes:
#         x, y, w, h = bbox[:4]
#         x, y, w, h = int(x), int(y), int(w), int(h)
#         cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
#     cv2.imwrite(os.path.join(save_dir_old, img_dir.split("/")[-1]), img)

save_dir_new = os.path.join(save_dir, "new")
# # new annotation part
# os.makedirs(save_dir_new, exist_ok=True)
# new_annotation_dir = os.path.join(dataset_dir, "审核中")
# for img_dir in sample_img_list:
#     folder_idx = int(img_dir.split("--")[0])
#     folder_idx = (61 - folder_idx) if folder_idx < 61 else 1
#     img_dir_new = os.path.join(new_annotation_dir, str(folder_idx), img_dir.split("/")[-1])
#     img = cv2.imread(img_dir_new)
#     annotation_dir = img_dir_new.replace(".jpg", "_annotation.json")
#     if not os.path.exists(annotation_dir):
#         continue
#     bboxes = []
#     with open(annotation_dir, "r") as f:
#         data = json.load(f)
#         annotations = data["annotations"]
#         bboxes = [x["bbox"] for x in annotations]
#     for bbox in bboxes:
#         x, y, w, h = bbox[:4]
#         x, y, w, h = int(x), int(y), int(w), int(h)
#         cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
#     cv2.imwrite(os.path.join(save_dir_new, img_dir.split("/")[-1]), img)

#
# concat images of 2 parts
# img_list = glob(save_dir_new + "/*.jpg")
# save_dir_concat = os.path.join(save_dir, "concat")
# os.makedirs(save_dir_concat, exist_ok=True)
# for img_dir_new in img_list:
#     img_name = img_dir_new.split("/")[-1]
#     img_dir_old = os.path.join(save_dir_old, img_name)
#     img_old, img_new = cv2.imread(img_dir_old), cv2.imread(img_dir_new)
#     img_concat = np.concatenate((img_old, img_new), axis=1)
#     cv2.imwrite(os.path.join(save_dir_concat, img_name), img_concat)

images = glob(os.path.join(dataset_dir, "审核中", "*", "*.jpg"))
annotations = glob(os.path.join(dataset_dir, "审核中", "*", "*_annotation.json"))
print(len(annotations), len(images))

