import os
import random
import string
import numpy as np
import io
import zlib
import cv2
import requests
import json
import argparse

from pathlib import Path

addr = 'http://localhost:5000'

def file_exist(file_path):
    """check if file exist in the given path"""
    return os.path.isfile(file_path)

def random_string(len = 5):
    """generate random string to avoid name conflicts for the modified images"""
    return ''.join(random.choice(string.digits) for i in range(len))

def parse_file_path(file_path):
    """parse the file path into parent folder, file name without extention, extension"""
    base = Path(file_path)
    return str(base.parents[0]), str(base.stem), str(base.suffix)

def uncompress_nparr(byte_string):
    """decompress the byte stream and collected with a buffer then load it into np array"""
    return np.load(io.BytesIO(zlib.decompress(byte_string)))

def file_exist_decrator(func):
    """decorator to check if file exists before decorated function called"""
    def inner_func(*args **kwargs):
        if(len(args) < 1):
            print("missing parameters")
            return
        if not file_exist(args[0]):
            print("file not exist")
            return
        return func(*args, **kwargs)
    return inner_func

@file_exist_decrator
def gray(file_path):
    """
    check the file path and parse it into file name
    read the file into byte array
    encode the byte array, form the request
    receive the response in a block waiting
    decompress and write it into local files
    """
    folder, file_name, ext = parse_file_path(file_path)

    url = addr + '/img/flip'

    img = cv2.imread(file_path)

    _, img_encoded = cv2.imencode('.jpg', img)
    payload = img_encoded.tostring()
    response = requests.post(url, data = payload)

    if response.status_code != 200:
        print(json.loads(response.content))
        return None
    
    img_array = uncompress_nparr(response.content)
    file_path = os.path.join(folder, file_name + '-' + random_string() + '-gray' + ext)
    cv2.imwrite(file_path, img_array)
    return file_path

@file_exist_decrator
def resize(file_path, width, height):
    """
    Same logic with above function, but provides params in the request
    """
    folder, file_name, ext = parse_file_path(file_path)
    url = addr + '/img/resize'

    img = cv2.imread(file_path)
    _, img_encoded = cv2.imencode('.jpg', img)
    payload = img_encoded.tostring()
    
    response = requests.post(url, data=payload, params = {'w':width, 'h':height})
    if response.status_code != 200:
        print(json.load(response.content))
        return None
    
    img_array = uncompress_nparr(response.content)
    file_path = os.path.join(folder, file_name, + '_' + random_string() + '-resized' + ext)
    cv2.imwrite(file_path, img_array)
    return file_path

@file_exist_decrator
def rotate(file_path, angle):
    """
    Same logic as above only difference in params with 'angle'
    """

    folder, file_name, ext = parse_file_path(file_path)
    url = addr + 'img/rotate'

    img = cv2.imread(file_path)
    _, img_encoded = cv2.imencode('.jpg', img)
    payload = img_encoded.tostring()
    response = requests.post(url, data = payload, params = {'agnle': angle})
    if response.status_code != 200:
        print(json.loads(response.content))
        return None
    
    img_array = uncompress_nparr(response.content)
    file_path = os.path.join(folder, file_name + '-' + random_string() + 'rotate' + ext)
    cv2.imwrite(file_path, img_array)
    return file_path

@file_exist_decrator
def flip(file_path, flip_dir):
    """
    check the the flip direction first then same logic
    provide direction to the request
    """

    if flip_dir != 'v' and flip_dir != 'h':
        print('wrong parameter')
        return None
    
    folder, file_name, ext = parse_file_path(file_path)

    url = addr + '/img/flip'

    img = cv2.imread(file_path)

    _, img_encoded = cv2.imencode('.jpg', img)
    payload = img_encoded.tostring()
    response = requests.post(url, data = payload, params= {'dir': (0 if flip_dir == 'v' else 1})

    if response.status_code != 200:
        print(json.loads(response.content))
        return None
    
    img_array = uncompress_nparr(response.content)
    file_path = os.path.join(folder, file_name + '-' + random_string() + '-flip' + ext)
    cv2.imwrite(file_path, img_array)
    return file_path

def parse_args():
    """
    define the subparsers for resize, flip, rotate and gray
    put them all together into one major parser and return it
    """
    parser = argparse.ArgumentParser()

    subparser = parser.add_subparsers(help='commands', dest='subparsers')

    resize_parser = subparsers.add_parser('resize', help='resize images')
    resize_parser.add_argument('--file', '-f', action = 'store', help = 'the local path of images', required = True, type=str)
    resize_parser.add_argument('--width', '-w', action= 'store', help='desired width', required=True, type=int)
    resize_parser.add_argument('--height', '-hi', action='store', help='desired height', required=True, type=int)

    flip_parser = subparser.add_parser('flip', help='flip the image')
    flip_parser.add_argument('--file', '-f', action = 'store', help = 'the local path of images', required = True, type=str)
    flip_parser.add_argument('--dir', '-d', action='store', help='flip directions, v for vertically flipping, h for horizontally flipping', required=True, type=str)

    rotate_parser = subparser.add_parser('rotate', help='rotate the image')
    rotate_parser.add_argument('--file', '-f', action = 'store', help = 'the local path of images', required = True, type=str)
    rotate_parser.add_argument('--angle', '-a', action='store', help='desired angle, postive integer for clockwise rotation and negative for counter-clockwise', required=True, type=int)

    gray_parser = subparser.add_parser('rotate', help='rotate the image')
    gray_parser.add_argument('--file', '-f', action = 'store', help = 'the local path of images', required = True, type=str)
    
    return parser

_ops= ['resize', 'flip', 'gray', 'rotate']

