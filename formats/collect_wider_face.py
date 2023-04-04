# collect wider face dataset train/val/test into one folder
from config.config import dataset_dir, wider_face_dir
import os
from glob import glob

folder_names = [str(61 + x) for x in range(1)]


def collect_one_folder(folder_name: str):
    print(f"processing {folder_name}")
    images = []
    for split_set in ["train", "val", "test"]:
        images += glob(os.path.join(
            wider_face_dir, "WIDER_" + split_set, "images", f"{61 - int(folder_name)}--*", "*.jpg"
        ))
    print(f"{len(images)} images found")

    output_dir = os.path.join(dataset_dir, "待标注", folder_name)
    os.makedirs(output_dir, exist_ok=True)
    for id, image in enumerate(images):
        if id % 100 == 0:
            print(f"processing {id}/{len(images)}")
        # copy image using python command
        filename = os.path.basename(image)
        os.system(f"cp '{image}' '{output_dir}'")


if __name__ == "__main__":
    for name in folder_names:
        collect_one_folder(name)
