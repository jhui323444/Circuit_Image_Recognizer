import numpy as np
import cv2 as cv
from ultralytics import YOLO
import sys

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

            results = model.predict(frame, conf=0.5, max_det=20, classes=[1]+list(range(3,52)))

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

def run_model(path):
    model = YOLO('yolov8n.pt')
    model = YOLO('./runs/detect/train8/weights/best.pt')

    frame = cv.imread(path)

    results = model.predict(frame, conf=0.5, max_det=20, classes=[1]+list(range(3,52)))

    annotated_frame = results[0].plot()

    grayscaleImage = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(grayscaleImage, (9,9),0)
    thresh = cv.adaptiveThreshold(blur, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 11, 2)

    cleared = thresh.copy()

    for r in results:
        #print(r.boxes)
        #print(r.boxes.xyxy)
        for x in r.boxes.xyxy:
            print(round(x[0].item()))
            print(x[1])
            coord = [[round(x[0].item()),round(x[1].item())]
                    ,[round(x[2].item()),round(x[3].item())]]
            print(coord)
            cv.rectangle(cleared, coord[0], coord[1], color=(0,0,0), thickness=-1)

    cv.imwrite('removed.jpg', cleared)
    cv.imwrite('gray.jpg', grayscaleImage)
    cv.imwrite('blur.jpg', blur)
    cv.imwrite('thresh_img.jpg', thresh)
    cv.imwrite('predicted.jpg', annotated_frame)
    print('Saved image to: predicted.jpg')



def main():
    if len(sys.argv) > 1:
        run_model(sys.argv[1])
    else:
        userin = int(input('do you want to use the camera(1), or analyze an image in the directory(2): '))
        if userin == 1:
            igen_frames()
        elif userin == 2:
            img_path = input('Please enter image path: ') 
            run_model(img_path)
        else:
            print('non valid option, exiting program...')

if __name__=='__main__':
    main()
