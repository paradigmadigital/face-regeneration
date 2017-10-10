from PIL import Image
from os import listdir
from os.path import isfile, isdir, join
import argparse


parser = argparse.ArgumentParser(description='Provide images directory.')
parser.add_argument('input_dir', metavar='INPUT_DIR', type=str, help='Input directory where get original images')

args = parser.parse_args()

INPUT_DIR = args.input_dir

SIZE = (1000, 1000)


def resize_image(path):
    img = Image.open(path)

    if img.size[0] > SIZE[0] and img.size[1] > SIZE[1]:
        print('resizing {}'.format(path))
        img.thumbnail(SIZE, Image.ANTIALIAS)
        img.save(path, quality=95)


def analyze_dir(dir):
    print('analyzing {}'.format(dir))
    for i in listdir(dir):
        path = join(dir, i)
        if isfile(path):
            resize_image(path)
        elif isdir(path):
            analyze_dir(path)


analyze_dir(INPUT_DIR)
