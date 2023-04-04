# convert json file to wider face format
import json
import os
from glob import glob
from config.config import dataset_dir
import random

annotations = glob(os.path.join(dataset_dir, "*", "*_annotation.json"))

# random shuffle annotations
random.shuffle(annotations)

# split train and val, 0.8 for train, 0.2 for val
train_num = int(len(annotations) * 0.8)
val_num = len(annotations) - train_num

train_annotations = annotations[:train_num]
val_annotations = annotations[train_num:]

train_dir = os.path.join(dataset_dir, "total", "train")
val_dir = os.path.join(dataset_dir, "total", "val")


# write images and annotations
def write(image_dir, annotation_dir, annotations: list):
    os.makedirs(image_dir, exist_ok=True)
    with open(annotation_dir, "w") as f:
        for annotation in annotations:
            img = annotation[:-16] + ".jpg"
            # copy image to folder
            os.system(f"cp '{img}' '{image_dir}'")
            with open(annotation, "r") as f_anno:
                data = json.load(f_anno)
                bbox_list = [anno["bbox"] for anno in data["annotations"]]
            lines = [
                os.path.basename(img),
                str(len(bbox_list)),
            ]
            for bbox in bbox_list:
                x, y, w = bbox
                h = w
                # convert to int
                x, y, w, h = int(x), int(y), int(w), int(h)
                lines.append(f"{x} {y} {w} {h}")
            f.writelines([line + "\n" for line in lines])


if __name__ == "__main__":
    write(train_dir, os.path.join(dataset_dir, "total", "train.txt"), train_annotations)
    write(val_dir, os.path.join(dataset_dir, "total", "val.txt"), val_annotations)
