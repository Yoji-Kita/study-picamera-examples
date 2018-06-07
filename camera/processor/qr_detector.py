from imutils.video.pivideostream import PiVideoStream
import time
from datetime import datetime
import numpy as np
import cv2

from flask import Flask, Response
from pyzbar import pyzbar
from picamera.array import PiRGBArray
from picamera import PiCamera

from pyzbar import pyzbar

class QRDetector(object):
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=(640, 480))
    time.sleep(0.5)

    app = Flask(__name__)

    @app.route('/stream')
    def stream():
        return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def gen():
        while True:
            frame = get_frame()
            yield (b'--frame\r\n'
	           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    def get_frame():
        camera.capture(rawCapture, format="bgr", use_video_port=True)
        frame = rawCapture.array
        decoded_objs = decode(frame)
        frame = display(frame, decoded_objs)
        ret, jpeg = cv2.imencode('.jpg', frame)
        rawCapture.truncate(0)

        return jpeg.tobytes()            

    def decode(frame):
        decoded_objs = pyzbar.decode(frame, scan_locations=True)
        for obj in decoded_objs:
            print(datetime.now().strftime('%H:%M:%S.%f'))
            print('Type: ', obj.type)
            print('Data: ', obj.data)
		
        return decoded_objs

    def display(frame, decoded_objs):
        for decoded_obj in decoded_objs:
            left, top, width, height = decoded_obj.rect
            frame = cv2.rectangle(frame,
    			      (left, top),
    			      (left + width, height + top),
    			      (0, 255, 0), 2)

        return frame

    if __name__ == '__main__':
        app.run(host="0.0.0.0", debug=False, threaded=True)

    
    def __init__(self, flip = False):
        self.vs = PiVideoStream(resolution=(800, 608)).start()
        self.flip = flip
        time.sleep(2.0)

    def __del__(self):
        self.vs.stop()

    def flip_if_needed(self, frame):
        if self.flip:
            return np.flip(frame, 0)
        return frame

    def get_frame(self):
        frame = self.flip_if_needed(self.vs.read())
        frame = self.process_image(frame)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
        
    def process_image(self, frame):
        decoded_objs = self.decode(frame)
        frame = self.draw(frame, decoded_objs)
        return frame

    def decode(self, frame):
        decoded_objs = pyzbar.decode(frame, scan_locations=True)
        for obj in decoded_objs:
            print(datetime.now().strftime('%H:%M:%S.%f'))
            print('Type: ', obj.type)
            print('Data: ', obj.data)
        return decoded_objs

    def draw(self, frame, decoded_objs):
        for obj in decoded_objs:
            left, top, width, height = obj.rect
            frame = cv2.rectangle(frame,
                                  (left, top),
                                  (left + width, height + top),
                                  (0, 0, 255), 2)
            data = obj.data.decode('utf-8')
            cv2.putText(frame,data,(left,top),cv2.FONT_HERSHEY_PLAIN, 2,(0, 0, 255))
        return frame
    

