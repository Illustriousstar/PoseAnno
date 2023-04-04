from config.config import dataset_dir
import os
from glob import glob
import random
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
import json
from tqdm import tqdm


def createAnnotationPascalVocTree(img_name: str):
    """
    code copied from https://github.com/akofman/wider-face-pascal-voc-annotations/blob/master/convert.py
    :param img_name: full path of image
    :return: annotation tree
    """
    # folder, basename, path, width, height
    basename = os.path.basename(img_name)
    folder = os.path.basename(os.path.dirname(img_name))
    path = img_name
    annotation = ET.Element('annotation')
    ET.SubElement(annotation, 'folder').text = folder
    ET.SubElement(annotation, 'filename').text = basename
    # ET.SubElement(annotation, 'path').text = path

    # get width and height
    img = Image.open(path)
    width, height = img.size
    size = ET.SubElement(annotation, 'size')
    ET.SubElement(size, 'width').text = str(width)
    ET.SubElement(size, 'height').text = str(height)
    ET.SubElement(size, 'depth').text = '3'

    ET.SubElement(annotation, 'segmented').text = '0'

    return ET.ElementTree(annotation)


def createObjectPascalVocTree(xmin, ymin, xmax, ymax):
    """
    code copied from https://github.com/akofman/wider-face-pascal-voc-annotations/blob/master/convert.py
    """
    obj = ET.Element('object')
    ET.SubElement(obj, 'name').text = 'face'
    ET.SubElement(obj, 'pose').text = 'Unspecified'
    ET.SubElement(obj, 'truncated').text = '0'
    ET.SubElement(obj, 'difficult').text = '0'

    bndbox = ET.SubElement(obj, 'bndbox')
    ET.SubElement(bndbox, 'xmin').text = xmin
    ET.SubElement(bndbox, 'ymin').text = ymin
    ET.SubElement(bndbox, 'xmax').text = xmax
    ET.SubElement(bndbox, 'ymax').text = ymax

    return ET.ElementTree(obj)


def convertAnnotations(imgs_path: list, target_path: str):
    """
    convert annotations from coco&pyqt to pascal voc format
    :param imgs_path: path of images and annotations
    :param target_path: path of target annotations
    :return:
    """
    print("\n"+target_path.split("/")[-1])
    target_path_xml = target_path + "/Annotations"
    os.makedirs(target_path_xml, exist_ok=True)
    for img_path in tqdm(imgs_path):

        # basename = os.path.basename(img_path)
        # folder_name = os.path.basename(os.path.dirname(img_path))
        # # prepare head for one annotation file
        # annotation_xml = createAnnotationPascalVocTree(img_path)
        # # read bounding boxes and add to annotation file

        try:
            with open(img_path.replace("images", "annotations").replace(".jpg", "_annotation.json"), "r") as f:
                annotation_json = json.load(f)
        # catch all errors here
        except Exception as e:
            print(e)
            print(img_path)
            continue


        # for bbox in annotation_json["annotations"]:
        #     xmin, ymin, width, height = bbox["bbox"]
        #     xmax = xmin + width
        #     ymax = ymin + height
        #     obj = createObjectPascalVocTree(str(xmin), str(ymin), str(xmax), str(ymax))
        #     annotation_xml.getroot().append(obj.getroot())
        # # save annotation file
        # xml_name = os.path.join(target_path_xml, basename.replace(".jpg", ".xml"))
        # annotation_xml.write(xml_name)
        # # copy image to target path
        # os.makedirs(os.path.join(target_path, folder_name), exist_ok=True)
        # os.system(f"cp '{img_path}' '{os.path.join(target_path, folder_name, basename)}'")


        # draw bounding boxes on images
        # img = Image.open(img_path)
        # draw = ImageDraw.Draw(img)
        # for bbox in annotation_json["annotations"]:
        #     xmin, ymin, width, height = bbox["bbox"]
        #     xmax = xmin + width
        #     ymax = ymin + height
        #     draw.rectangle([xmin, ymin, xmax, ymax], outline="green", width=3)
        # img.save(os.path.join(target_path, os.path.basename(img_path)))

    # write names to a txt file
    with open(os.path.join(target_path, f"{os.path.basename(target_path).split('_')[1]}.txt"), "w") as f:
        for img_path in imgs_path:
            name = os.path.basename(img_path).split(".")[0]
            f.write(name + "\n")


# path
target_path = os.path.join(dataset_dir, "PASCAL")
images_path = os.path.join(dataset_dir, "审核中")

# read all images
images = glob(os.path.join(images_path, "*", "*_annotation.json"))
images = [x.replace("_annotation.json", ".jpg") for x in images]
# random shuffle
random.seed(0)
random.shuffle(images)

# train val test split
train_images = images[:int(len(images) * 0.8)]
val_images = images[int(len(images) * 0.8):int(len(images) * 0.9)]
test_images = images[int(len(images) * 0.9):]

print(f"train images: {len(train_images)}, val images: {len(val_images)}", f"test images: {len(test_images)}")

convertAnnotations(train_images, os.path.join(target_path, "WIDER_train"))
convertAnnotations(val_images, os.path.join(target_path, "WIDER_val"))
convertAnnotations(test_images, os.path.join(target_path, "WIDER_test"))
