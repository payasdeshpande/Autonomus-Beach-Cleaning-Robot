import cv2
import torch
from PIL import Image

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='"C:/Users/HP/OneDrive/Desktop/Project/yolov5/yolov5s.pt"', force_reload=True)
model.conf = 0.25  # Set confidence threshold
model.iou = 0.45   # Set IoU threshold for NMS
model.classes = [0, 1, 2]  # Define the classes you want to detect (based on your training)

# Preprocess the input image
def preprocess_image(image):
    img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    img = img.resize((model.stride.max() * img.shape[1] // model.stride.max(), model.stride.max() * img.shape[0] // model.stride.max()))
    img = torch.from_numpy(img).to(model.device).float() / 255.0
    img = img.permute(2, 0, 1).unsqueeze(0)
    return img

# Perform inference using the YOLOv5 model
def detect_garbage(image):
    preprocessed_img = preprocess_image(image)
    results = model(preprocessed_img)
    return results.xyxy[0].tolist()  # Returns [x1, y1, x2, y2, confidence, class] for each detected object

# Process the detections and return only detected garbage objects
def filter_garbage_detections(detections):
    garbage_detections = []
    for detection in detections:
        if detection[4] >= model.conf:
            garbage_detections.append(detection)
    return garbage_detections
