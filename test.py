from pycocotools.coco import COCO
import json
import numpy as np
from skimage import io
import matplotlib.pyplot as plt

val_info = r"/Users/maotianwei/Desktop/coco/annotations/person_keypoints_val2017.json"
val_image = r"/Users/maotianwei/Desktop/coco/val2017"

coco = COCO(val_info)
all_ids = coco.imgs.keys()

# person_id = coco.getCatIds(catNms=['person'])
# person_img_id = coco.getImgIds(catIds=person_id)
# id = person_img_id[np.random.randint(0, len(person_img_id))]
# img = coco.loadImgs(id)[0]
# print(id)
# print(img)

# read json part
person_img_id = 785
img = coco.loadImgs(person_img_id)
catIds = coco.getCatIds(catNms=["person"])
annIds = coco.getAnnIds(imgIds=img[0]['id'], catIds=catIds, iscrowd=None)
anno = coco.loadAnns(annIds)
cat = coco.loadCats(catIds)
del anno[0]["segmentation"]
print(img)
print(anno)
print(cat)
I = io.imread("/Users/maotianwei/Desktop/coco/val2017/%s" % (img[0]['file_name']))
plt.figure()
plt.axis('off')
plt.imshow(I)

coco.showAnns(anno)
plt.show()

with open(val_info, "r") as f:
    data = json.load(f)
    license = data["licenses"][3]
    print(data["licenses"][3])

# write json part
info = {
    "description": "test dataset for human key points",
    "url": "no",
    "version": "0.0",
    "contributor": "dust",
    "date_created": "2022/04/19"
}
with open("test_anno.json", "w") as f:
    json.dump({
        "info": info,
        "images": img,
        "annotations": anno,
        "categories": cat,
        "licenses": [license]
    }, f)
