from flask import Flask, render_template, Response
from my_functions import *
import cv2

app = Flask(__name__)
video_source = "mb1.mp4"  # Path to your video file or camera address


def generate_frames():
    cap = cv2.VideoCapture(video_source)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame, _ = object_detection(frame)
        frame = cv2.resize(frame, frame_size)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route("/")
def index():
    return render_template("index.html")  # Assuming you have an HTML file for video display


@app.route("/video_feed")
def video_feed():

    return Response(generate_frames(), mimetype="video/mp4")


if __name__ == "__main__":
    app.run(debug=True)
