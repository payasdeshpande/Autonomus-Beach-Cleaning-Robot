from RPi.robot_control import control_motor
from flask import Flask, render_template, Response
from robot_control import control_all_motors
import cv2

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/forward')
def forward():
    control_all_motors('forward')
    return "Moving forward"

@app.route('/backward')
def backward():
    control_all_motors('backward')
    return "Moving backward"

@app.route('/left')
def left():
    control_motor('left_front', 'backward')
    control_motor('left_middle', 'backward')
    control_motor('left_back', 'backward')
    control_motor('right_front', 'forward')
    control_motor('right_middle', 'forward')
    control_motor('right_back', 'forward')
    return "Turning left"

@app.route('/right')
def right():
    control_motor('left_front', 'forward')
    control_motor('left_middle', 'forward')
    control_motor('left_back', 'forward')
    control_motor('right_front', 'backward')
    control_motor('right_middle', 'backward')
    control_motor('right_back', 'backward')
    return "Turning right"

@app.route('/stop')
def stop():
    control_all_motors('stop')
    return "Stopping"

def gen_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
