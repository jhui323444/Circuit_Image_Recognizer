import numpy as np
import cv2 as cv
from ultralytics import YOLO
import sys
import os
import time
from processing.endpoint import resize_image, threshold_image, get_contours
from processing.line_detection import generate_lines, draw_lines
from processing.schematic import identify_component, generate_schematic

def igen_frames():
    cap = cv.VideoCapture(0, cv.CAP_V4L2)
    cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'))

    if not cap.isOpened():
        print('Cannot Open Camera')
        exit()

    model = YOLO('train/yolov8n.pt')
    model = YOLO('./runs/detect/train8/weights/best.pt')

    while cap.isOpened():
        #capture frame
        ret, frame = cap.read()
        cur_path = os.getcwd()
        
        #resizing image
        resized, width, height = resize_image(image=frame, path=cur_path, scale_percent=50)
        
        #scale_percent = 25
        #width = int(resized.shape[1] * scale_percent / 100)
        #height = int(resized.shape[0] * scale_percent / 100) 

        #if frame not read correctly
        if not ret:
            print('Cant receive frame (Stream end?). Exiting...')
            break

        else:

            #do operations here
            #detections = coco_model(frame)[0]

            results = model.predict(resized, conf=0.5, \
                                    iou=0.8, \
                                    max_det=20, \
                                    vid_stride=5,\
                                    classes=[1,4,5,6,7,8,9,10,11,13,15,17,25,26,28,31])

            #annotated_frame_arr = frame 

            if results:
                #plot prediction boxes
                annotated_frame = results[0].plot()

                #threshold image
                thresh = threshold_image(resized, cur_path)

                #removing components
                cleared = thresh.copy()

                for r in results:
                    for x in r.boxes.xyxy:
                        coord = [[round(x[0].item()),round(x[1].item())]
                                ,[round(x[2].item()),round(x[3].item())]]
                        #print(coord)
                        cv.rectangle(cleared, coord[0], coord[1], \
                                     color=(0,0,0), thickness=-1)

                #getting contours
                out, contours = get_contours(cleared, cur_path)
                
                #lines
                horizontal, vertical = generate_lines(cleared, contours)
                
                #creating components
                c_h, c_v, h, v, other, fixes = identify_component(results, horizontal, vertical)
                #print(c_h)
                #print(c_v)
                image = draw_lines(resized, h, v, cur_path)

                for line in fixes.values():
                    cv.line(image, (line[0], line[1]), \
                            (line[2], line[3]), (255, 0, 0), 6)

                #generating txt file schematic
                generate_schematic(height, width, c_h, c_v, other, fixes, results)
                
                #image concatenation for single windows
                cleared_3 = cv.cvtColor(cleared, cv.COLOR_GRAY2BGR)
                thresh_3  = cv.cvtColor(thresh, cv.COLOR_GRAY2BGR)

                Hori1 = np.concatenate((cleared_3, thresh_3), axis=1)
                Hori2 = np.concatenate((image, annotated_frame), axis=1)
                Verti = np.concatenate((Hori1, Hori2), axis=0)
                
                #display predictions
                cv.imshow('frame1', Verti)
                #cv.imshow('thresh',thresh)
                #cv.imshow('cleaned', cleared)
                #cv.imshow('contours',contours)
                #cv.imshow('image', image)
            else:
                cv.imshow('frame', resized)
            
            if cv.waitKey(1) == ord('q'):
                break


    cap.release()
    cv.destroyAllWindows()

def run_model(path):
    model = YOLO('train/yolov8n.pt')
    model = YOLO('./runs/detect/train8/weights/best.pt')

    frame = cv.imread(path)
    cur_path = os.getcwd()
    
    resized, width, height = resize_image(frame, cur_path)
    
    results = model.predict(resized, conf=0.5, \
                            max_det=20, classes=[1]+list(range(3,52)))

    annotated_frame = results[0].plot()
    
    thresh = threshold_image(resized, cur_path)
    print('thresh done')

    cleared = thresh.copy()

    for r in results:
        for x in r.boxes.xyxy:
            coord = [[round(x[0].item()),round(x[1].item())]
                    ,[round(x[2].item()),round(x[3].item())]]
            #print(coord)
            cv.rectangle(cleared, coord[0], coord[1], \
                         color=(0,0,0), thickness=-1)

    out, contours = get_contours(cleared, cur_path)

    horizontal, vertical = generate_lines(cleared, contours)

    c_h, c_v, h, v, other, fixes = identify_component(results, horizontal, vertical)
    print(c_h)
    print(c_v)
    image = draw_lines(resized, h, v, cur_path)

    for line in fixes.values():
        cv.line(image, (line[0], line[1]), \
                (line[2], line[3]), (255, 0, 0), 6)

    generate_schematic(height, width, c_h, c_v, other, fixes, results)
    
    #cv.imwrite('fixed.jpg', image)
    
    cv.imwrite('images/removed.jpg', cleared)
    print('Saved image to: removed.jpg')
   
    cv.imwrite('images/line.jpg', image)
    print('Saved image to: line.jpg')


    cv.imwrite('images/thresh.jpg', thresh)
    print('Saved image to: thresh.jpg')

    cv.imwrite('images/predicted.jpg', annotated_frame)
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
