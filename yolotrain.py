from ultralytics import YOLO

model = YOLO('yolov8n.yaml')
model = YOLO('yolov8n.pt')
model = YOLO('yolov8n.yaml').load('yolov8n.pt')

results = model.train(data='config.yaml', batch=9, epochs=100)

