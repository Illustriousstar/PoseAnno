from config.config import dataset_dir
import cv2
import os
from glob import glob
import json

batch_names = ["batch" + str(index + 1) for index in range(3)]


def out(batch_name: str = "batch1", to_draw_demo: bool = False):
    print("Processing", batch_name)
    batch_dir = os.path.join(dataset_dir, batch_name)
    out_dir = batch_dir + "_out"
    draw_dir = batch_dir + "_draw"
    to_draw_demo = False

    annotations = sorted(glob(os.path.join(batch_dir, "*_annotation.json")))
    imgs = [anno[:-16] + ".jpg" for anno in annotations]

    # copy images and annotations to out_dir
    os.makedirs(out_dir, exist_ok=True)
    print(f"{len(annotations)} json files, {len(imgs)} images")
    for img, anno in zip(imgs, annotations):
        # check annotation file, if it is empty, skip
        with open(anno, "r") as f:
            data = json.load(f)
            if len(data["annotations"]) == 0:
                continue
        os.system(f"cp '{img}' '{out_dir}'")
        os.system(f"cp '{anno}' '{out_dir}'")

    # draw bounding boxed and save
    if to_draw_demo:
        os.makedirs(draw_dir, exist_ok=True)
        for img, anno in zip(imgs, annotations):
            with open(anno, "r") as f:
                data = json.load(f)
                bbox_list = [anno["bbox"] for anno in data["annotations"]]
            _img = cv2.imread(img)
            for bbox in bbox_list:
                x, y, w = bbox
                h = w
                # convert to int
                x, y, w, h = int(x), int(y), int(w), int(h)
                cv2.rectangle(_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.imwrite(os.path.join(draw_dir, os.path.basename(img)), _img)


if __name__ == "__main__":
    for batch in batch_names:
        out(batch)
