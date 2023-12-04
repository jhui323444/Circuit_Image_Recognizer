import numpy as np
import cv2 as cv
from ultralytics import YOLO


def igen_frames():
    cap = cv.VideoCapture(0, cv.CAP_V4L2)
    cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'))

    if not cap.isOpened():
        print('Cannot Open Camera')
        exit()

    delay = 0

    model = YOLO('yolov8n.pt')
    model = YOLO('./weights/best.pt')

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

            results = model(frame)
            annotated_frame_arr = 

            if results:
                for r in results:
                    if r.boxes.cls.all() != 1 and r.boxes.cls.all() != 2:
                        print(f'\n{r.boxes.cls}\n')
                        annotated_frame_arr = r.plot()
                        
                    
                #display
                if annotated_frame_arr.any():
                    cv.imshow('frame', annotated_frame_arr)
                else:
                    cv.imshow('frame', frame)
            else:
                cv.imshow('frame', frame)

            if cv.waitKey(1) == ord('q'):
                break

    cap.release()
    cv.destroyAllWindows()

igen_frames()
