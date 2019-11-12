import cv2
import time
import json
from datetime import datetime
import face_recognition
import argparse
import pickle
import imutils
from imutils.video import VideoStream


ap = argparse.ArgumentParser()
ap.add_argument("-e", "--encodings", required=True, help="path to serialized db of facial encodings")
args = vars(ap.parse_args())


def face_show():    
    print("開啟攝影機中...")
    vs = VideoStream(src=0).start()    
    time.sleep(2.0)

    while True:
        frame = vs.read()
        orig = frame.copy()
        frame = imutils.resize(frame, width=640)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
        data = pickle.loads(open(args["encodings"], "rb").read())      
        boxes = face_recognition.face_locations(rgb, model='hog') 
        encodings = face_recognition.face_encodings(rgb, boxes)    
        if len(boxes):
            names = []
            for encoding in encodings:
                matches = face_recognition.compare_faces(data["encodings"], encoding, tolerance=0.3)
                name = "Unknown"

                if True in matches:
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1
                    name = max(counts, key=counts.get)
                names.append(name)
            for i, (top, right, bottom, left) in enumerate(boxes):                
                cv2.rectangle(
                        frame, (left, top), (right, bottom),
                        (0, 0, 255), 2)
                cv2.putText(
                        frame, names[i],
                        (left + int((right - left) / 2), top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 2)
        cv2.imshow('Frame', frame)
        k = cv2.waitKey(1)
        if k == ord('q') or k == ord('Q'):
            cv2.destroyAllWindows()
            vs.stop()
            break


face_show()