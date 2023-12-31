from flask import Flask, render_template, Response, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from my_functions import *
import cv2
from extract_numberplate import my_job
import os

app = Flask(__name__)
video_source = "with&without helmet.mp4"

save_video = True
show_video = True
save_img = False

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, frame_size)


def generate_frames():
    cap = cv2.VideoCapture(video_source)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, frame_size)
            orifinal_frame = frame.copy()
            frame, results = object_detection(frame)

            rider_list = []
            head_list = []
            number_list = []

            for result in results:
                x1, y1, x2, y2, cnf, clas = result
                if clas == 0:
                    rider_list.append(result)
                elif clas == 1:
                    head_list.append(result)
                elif clas == 2:
                    number_list.append(result)

            person_count = 0

            for rdr in rider_list:
                time_stamp = str(time.time())
                x1r, y1r, x2r, y2r, cnfr, clasr = rdr
                for hd in head_list:
                    x1h, y1h, x2h, y2h, cnfh, clash = hd
                    if inside_box([x1r, y1r, x2r, y2r], [x1h, y1h, x2h, y2h]):
                        try:
                            head_img = orifinal_frame[y1h:y2h, x1h:x2h]
                            helmet_present = img_classify(head_img)
                        except:
                            helmet_present[0] = None

                        if helmet_present[0] == True:  # if helmet present
                            frame = cv2.rectangle(frame, (x1h, y1h), (x2h, y2h), (0, 255, 0), 1)
                            frame = cv2.putText(frame, f'{round(helmet_present[1], 2)} Helmet Detected',(x1h, y1h + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

                            person_count += 1

                            if person_count > 1:
                                print(f"Total {person_count} person(s): Triples Detected")
                                try:
                                    cv2.imwrite(f'riders_pictures/triples_{time_stamp}.jpg', orifinal_frame[y1r:y2r, x1r:x2r])
                                except:
                                    print('could not save rider')

                                for num in number_list:
                                    x1_num, y1_num, x2_num, y2_num, conf_num, clas_num = num
                                    if inside_box([x1r, y1r, x2r, y2r], [x1_num, y1_num, x2_num, y2_num]):
                                        try:
                                            num_img = orifinal_frame[y1_num:y2_num, x1_num:x2_num]
                                            plate_img_path = f'temp_plates/lpr_temp_plate.jpg'
                                            cv2.imwrite(plate_img_path, num_img)  # Save the plate as an image file
                                            plate_text = image_to_text(plate_img_path)  # Pass the file path to the function
                                            frame = cv2.putText(frame,f'{round(helmet_present[1], 2)} Triples Detected {plate_text}',(x1h, y1h + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 1, cv2.LINE_AA)
                                            cv2.imwrite(f'number_plates/triples_{time_stamp}_{conf_num}.jpg', num_img)
                                            os.remove(plate_img_path)  # Remove the temporary plate image file
                                        except Exception as e:
                                            print(f'Error: {e}')

                        elif helmet_present[0] == None:
                            frame = cv2.rectangle(frame, (x1h, y1h), (x2h, y2h), (0, 255, 255), 1)
                            frame = cv2.putText(frame, f'{round(helmet_present[1], 1)} Predicting Helmet', (x1h, y1h),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                        elif helmet_present[0] == False:  # if helmet absent
                            frame = cv2.rectangle(frame, (x1h, y1h), (x2h, y2h), (255, 0, 255), 5)
                            frame = cv2.putText(frame, f'{round(helmet_present[1], 1)} No Helmet', (x1h, y1h + 40),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)

                            try:
                                cv2.imwrite(f'riders_pictures/nohelmet_{time_stamp}.jpg', orifinal_frame[y1r:y2r, x1r:x2r])
                            except:
                                print('could not save rider')

                            for num in number_list:
                                x1_num, y1_num, x2_num, y2_num, conf_num, clas_num = num
                                if inside_box([x1r, y1r, x2r, y2r], [x1_num, y1_num, x2_num, y2_num]):
                                    try:
                                        num_img = orifinal_frame[y1_num:y2_num, x1_num:x2_num]
                                        plate_img_path = f'temp_plates/temp_plate.jpg'
                                        cv2.imwrite(plate_img_path, num_img)  # Save the plate as an image file
                                        plate_text = image_to_text(plate_img_path)  # Pass the file path to the function
                                        # print(plate_text)
                                        frame = cv2.putText(frame,f'{round(helmet_present[1], 1)} No Helmet {plate_text}',(x1h, y1h + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255),1, cv2.LINE_AA)
                                        cv2.imwrite(f'number_plates/nohelmet_{time_stamp}_{conf_num}.jpg', num_img)
                                        os.remove(plate_img_path)  # Remove the temporary plate image file
                                    except Exception as e:
                                        print(f'Error: {e}')

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        # if save_video:  # save video
        #     out.write(frame)

        else:
            break

    cap.release()
    cv2.destroyAllWindows()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(my_job, 'interval', seconds=30)
scheduler.start()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
