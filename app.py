from flask import Flask
import json
import io
import zlib
import numpy as np
import cv2


app = Flask(__name__)

def compress_nparr(nparr):
    bytestream = io.BytesIO()
    np.save(bytestream,nparr)
    uncompressed = bytestream.getvalue()
    compressed = zlib.compress(uncompressed)
    return compressed, len(uncompressed), len(compressed)

@app.route('/img/resize', method= ['POST'])
def resize():
    img = request.data
    img_arr = np.fromstring(img, np.uint8)

    width = request.args.get('w')
    height = request.args.get('h')

    if width is None or height is None:
        return Response(response=json.dumps({'msg': 'missing parameter'}), status=400, mimetype="application/json")
    
    width = int(width)
    height = int(height)

    my_img = cv2.imdecode(img_arr,cv2.IMREAD_COLOR)

    my_img = cv2.resize(img, (width, height))
    resp,_,_=compress_nparr(img)
    return Response(response = resp, status = 200, mimetype = "application/octet_stream")



@app.route('/img/rotate', methods = ['POST'])
def rotate():
    
    img = request.data
    img_arr = np.fromstring(img, unit8)

    angle = request.args.get('angle')
    if angle is None:
        return Response(response = json.dumps({'msg': 'missing parameters'}), status=400, mimetype="application/json")

    angle = (int)angle

    img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)

    img_center = tuple(np.array(img.shape[1::-1])/2)
    rotate_matrix = cv2.getRotationMatrix2D(img_center, angle, 1)
    img = cv2.warpAffine(img, rotate_matrix, img.shape[1::-1], flags=cv2.INTER_LINEAR)
    resp,_,_ = compress_nparr(img)
    return Response(response=resp, status=200, mimetype="application/octet_stream")

@app.route('/img/flip', methods = ['POST'])
def flip():

    recv_img = request.data
    img_arr = np.fromstring(recv_img, uint8)

    flip_direction = request.args.get('flipDir')
    if flip_direction is None:
        return Response(response = json.dumps({'msg':'missing parameters'}), status=400), mimetype="application/json"
    
    flip_direction = (int)flip_direction

    img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)

    img = cv2.flip(img, flip_direction)

    resp,_,_ = compress_nparr(img)

    return Response(response = resp, status = 200, mimetype = "application/octet_stream")

@app.route('/img/gray', mthods = ['POST'])
def gray():
    recv_img = request.data
    img_arr = np.fromstring(recv_img, uint8)

    img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)

    img = cv2.cvtColor(img, cv2.COLOR_BAYER_BG2GRAY)

    resp, _, _ = compress_nparr(img)

    return Response(response= resp, status = 200, mimetype = "application/octet_stream")

if __name__ == '__main__':
    app.run()


def main():
    app.run(host="0.0.0.0", port=5000)

if __name__ == '__main__':
    main()
