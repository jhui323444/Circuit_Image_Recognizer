import numpy as np
import cv2 as cv
from ultralytics import YOLO


def igen_frames():
    cap = cv.VideoCapture(0, cv.CAP_V4L2)
    cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'))

    if not cap.isOpened():
        print('Cannot Open Camera')
        exit()

    model = YOLO('yolov8n.pt')
    model = YOLO('./runs/detect/train8/weights/best.pt')

    while cap.isOpened():
        #capture frame
        ret, frame = cap.read()

        #if frame not read correctly
        if not ret:
            print('Cant receive frame (Stream end?). Exiting...')
            break

        else:

            #do operations here
            #detections = coco_model(frame)[0]

            results = model.predict(frame, conf=0.5, max_det=20, classes=list(range(3,52)))

            #annotated_frame_arr = frame 

            if results:
                annotated_frame = results[0].plot()
                

                #display
                cv.imshow('frame', annotated_frame)

            else:
                cv.imshow('frame', frame)
            
            
            if cv.waitKey(1) == ord('q'):
                break

    cap.release()
    cv.destroyAllWindows()

igen_frames()
