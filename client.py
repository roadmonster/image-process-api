import os
import random
import string
import numpy as np
import io
import zlib
import cv2
import requests
import json

from pathlib import Path

addr = 'http://localhost:5000'

def file_exist(file_path):
    return os.path.isfile(file_path)

def random_string(len = 5):
    return ''.join(random.choice(string.digits) for i in range(len))

def parse_file_path(file_path):
    base = Path(file_path)
    return str(base.parents[0]), str(base.stem), str(base.suffix)

def uncompress_nparr(byte_string):
    return np.load(io.BytesIO(zlib.decompress(byte_string)))

def file_exist_decrator(func):
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



