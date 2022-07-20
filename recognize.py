import numpy as np
import cv2
import pickle

import pyodbc

conn = pyodbc.connect(
    "Driver={SQL Server Native Client 11.0};"
    "Server=DESKTOP-N4JRA7K\SQLEXPRESS;"
    "Database=AttendanceModuleTest;"
    "Trusted_Connection=yes;"
)

from clock import get_time, get_date

# Haar Cascade Variables
face_cascade = cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_alt2.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer.yml")

labels = {"person_name": 1}
with open("labels.pickle", 'rb') as f:
    og_labels = pickle.load(f)
    labels = {v: k for k, v in og_labels.items()}

cap = cv2.VideoCapture(0)

# Loop makes capturing continuous
while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Draw rectangle on the detected face
    cv2.rectangle(frame, (0, 900), (2100, 400), (0, 0, 0), thickness=cv2.FILLED)

    # Write Text
    cv2.putText(frame, 'Date: ' + get_date(), (7, 415), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(frame, 'Time: ' + get_time(), (7, 435), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(frame, 'Press I to Time-In', (200, 415), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 255, 0), 1)
    cv2.putText(frame, 'Press O to Time-out', (200, 435), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 255, 0), 1)

    # Resize the frames
    width = int(frame.shape[1] * 1.5)
    height = int(frame.shape[0] * 1.5)
    dimensions = (width, height)
    resize_frame = cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)
    resize_gray = cv2.resize(gray, dimensions, interpolation=cv2.INTER_AREA)

    # Detect Face
    faces = face_cascade.detectMultiScale(resize_gray, scaleFactor=1.5, minNeighbors=2)

    # For every detected face identify the person
    for (x, y, w, h) in faces:
        roi_gray = resize_gray[y:y + h, x:x + w]
        roi_color = resize_frame[y:y + h, x:x + w]

        # Draw Rectangle on the detected face
        color = (255, 0, 0)
        stroke = 2
        end_cord_x = x + w
        end_cord_y = y + h
        cv2.rectangle(resize_frame, (x, y), (end_cord_x, end_cord_y), color, stroke)

        # Recognize Face
        id_, conf = recognizer.predict(roi_gray)
        # 40 <= conf <= 90
        if 30 <= conf <= 90:
            font = cv2.FONT_HERSHEY_SIMPLEX
            name = labels[id_]
            color = (255, 255, 255)
            stroke = 2
            cv2.putText(resize_frame, name, (x, y), font, 1, color, stroke, cv2.LINE_AA)

            detected_face = labels[id_]
            # print('Name: ' + labels[id_])
            # print('Machine Confidence Level: ' + str(conf))

        else:
            font = cv2.FONT_HERSHEY_SIMPLEX
            name = 'Unknown'
            color = (255, 255, 255)
            stroke = 2
            cv2.putText(resize_frame, name, (x, y), font, 1, color, stroke, cv2.LINE_AA)
            # print('Unknown Face Detected')

    cv2.imshow('frame', resize_frame)

    if cv2.waitKey(1) == ord('d'):
        break

    elif cv2.waitKey(1) == ord('i'):
        print('Timed in')
        cursor = conn.cursor()
        cursor.execute(
            "IF NOT EXISTS (SELECT EmployeeName, Date FROM AttendanceSheet WHERE EmployeeName='" + labels[id_] + "'" + " AND Date='" + get_date() + "')"
            "BEGIN "
            "INSERT INTO AttendanceSheet(EmployeeID ,EmployeeName, TimeIn, Date) values(?, ?, ?, ?)"
            "END",
            (1, labels[id_], get_time(), get_date())
        )
        conn.commit()

    elif cv2.waitKey(1) == ord('o'):
        print('Timed out')
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE AttendanceSheet SET TimeOut='" + get_time() + "' "
            "WHERE EmployeeName='" + labels[id_] + "' AND Date='" + get_date() + "' AND TimeOut IS NULL"
        )
        conn.commit()


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
