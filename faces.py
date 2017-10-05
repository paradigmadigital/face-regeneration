import pprint
import boto3
import sys
from PIL import Image
from os import listdir, rename
from os.path import isfile, isdir, join, split
import argparse

rekognition = boto3.client('rekognition')

parser = argparse.ArgumentParser(description='Provide images directories.')
parser.add_argument('input_dir', metavar='INPUT_DIR', type=str, help='Input directory where get raw images')
parser.add_argument('output_dir', metavar='OUTPUT_DIR', type=str, help='Output directory where put face cropped')
parser.add_argument('done_dir', metavar='DONE_DIR', type=str, help='Done directory where move processed images')

args = parser.parse_args()

OUTPUT_DIR = args.output_dir
INPUT_DIR = args.input_dir
DONE_DIR = args.done_dir


def make_box(img, left, top, box_width, box_height):
    width, height = img.size
    box = [left * width,
           top * height,
           left * width + box_width * width,
           top * height + box_height * height]
    return box


def crop_faces(image_path, face, face_id):
    _, image_name = split(image_path)
    img = Image.open(image_path)

    face_box = make_box(img,
                        face['BoundingBox']['Left'],
                        face['BoundingBox']['Top'],
                        face['BoundingBox']['Width'],
                        face['BoundingBox']['Height'])
    if (face_box[2]-face_box[0]) < 64 or (face_box[3]-face_box[1]) < 64:
        print('skip face {} because is too small: {}'.format(face_id, face_box))
        return

    cropped_image = img.crop(face_box)
    # cropped_image.thumbnail((64, 64), Image.ANTIALIAS)
    filename = '{}_{}'.format(face_id, image_name)
    cropped_image.save(join(OUTPUT_DIR, filename))
    print('* generated {}'.format(filename))
    return filename


def analyze_image(image_path):
    _, image_name = split(image_path)

    with open(image_path, 'rb') as image:
        print('- analyzing image {}'.format(image_path))
        try:
            faces = rekognition.detect_faces(Image={'Bytes': image.read()})
        except Exception as e:
            print('Error processing image {}: {}'.format(image_path, e))
            return

        # pprint.pprint(faces)
        print('-> detected {} faces'.format(len(faces.get('FaceDetails'))))

        for face_id, face in enumerate(faces.get('FaceDetails'), start=1):
            crop_faces(image_path, face, face_id)

    rename(image_path, join(DONE_DIR, image_name))


def analyze_dir(dir):
    print('analyzing {}'.format(dir))
    for i in listdir(dir):
        path = join(dir, i)
        if isfile(path):
            analyze_image(path)
        elif isdir(path):
            analyze_dir(path)


analyze_dir(INPUT_DIR)


