from ultralytics import YOLO

model = YOLO('./runs/detect/train8/weights/last.pt')

results = model.train(data='config.yaml', batch=6, epochs=100, resume=True)
