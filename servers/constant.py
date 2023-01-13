import logging
import pickle
from os import path
from PIL import Image

MAP = {'dam': '1', 'editor': '2', 'thumb': '3'}
APP_TO_NAME = {MAP.get(K): K for K in MAP}


def gen_pic_id(app_no, img_id):
    app_no = str(app_no).zfill(2)
    img_id = str(img_id)
    return int(f'{img_id}{app_no}')


def gen_eb_id(app_no, img_id, eb_no):
    app_no = str(app_no).zfill(2)
    img_id = str(img_id)
    return int(f'{img_id}{eb_no}{app_no}')


def get_threshold(args):
    try:
        threshold = args.get('score', 0.9)
        if threshold is None:
            threshold = 0.9
        else:
            threshold = float(threshold)
        return threshold
    except:
        return 0.9


def get_topk(args):
    try:
        size = args.get('size', 12)
        if size is None:
            size = 12
        else:
            size = int(size)
        if size < 1:
            size = 12
        return size
    except:
        return 0.85


def to_time_message(time_second, task_name=None):
    minutes = time_second // 60
    secs = time_second % 60
    if task_name is None:
        print(
            "Finished in {:.2f} min {:.2f} sec.".format(minutes, secs))
    else:
        print("{} finished in {:.2f} min {:.2f} sec.".format(
            task_name, minutes, secs))


def dump_to_file(obj, filename):
    with open(filename, "wb") as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_from_file(filename):
    if path.isfile(filename):
        with open(filename, "rb") as f:
            return pickle.load(f)
    return None


def resize_img(img):
    width, height = img.size
    if width > 224:
        ratio = 224/width
        hsize = int(height * float(ratio))
        img = img.resize((128, hsize), Image.ANTIALIAS)
    return img
