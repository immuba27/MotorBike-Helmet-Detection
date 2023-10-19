from flask import Flask, render_template, Response, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from my_functions import *
import cv2
from extract_numberplate import my_job

app = Flask(__name__)
video_source = "mb1.mp4"  # Path to your video file or camera address


def generate_frames():
    cap = cv2.VideoCapture(video_source)
    print("AAAAAAAAAAAAAAAAAAAA")
    print(cap.isOpened())
    while cap.isOpened():
        ret, frame = cap.read()
        print(ret)
        if not ret:
            break
        print("Before")
        try:
            frame = cv2.resize(frame, frame_size)
            print("frame resize done")
            frame, resDetection = object_detection(frame)
            print("After")

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        except RuntimeError:
            print("frame error")
            break



@app.route("/")
def index():
    return render_template("index.html")  # Assuming you have an HTML file for video display


@app.route("/video_feed")
def video_feed():

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

print("Before")
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(my_job, 'interval', seconds=10)
scheduler.start()
print("After")

if __name__ == "__main__":
    app.run(debug=True)
