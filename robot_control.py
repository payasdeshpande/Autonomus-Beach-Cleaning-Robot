import RPi.GPIO as GPIO
from picamera import PiCamera
from time import sleep
from garbage_detection import detect_garbage, filter_garbage_detections
import cv2
# Motor control setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define the pins connected to L293D motor drivers
motor_pins = {
    'left_front': (23, 24),
    'left_middle': (25, 8),
    'right_front': (7, 1),
    'right_middle': (20, 21),
    'left_behind': (5, 6),
    'right_behind': (27, 22),
    'sieve': (10, 9)
}

enable_pins = [12, 13, 18, 19, 26, 16, 17]

# Set the GPIO pins as output and initialize them to LOW
for pins in motor_pins.values():
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

for enable_pin in enable_pins:
    GPIO.setup(enable_pin, GPIO.OUT)
    GPIO.output(enable_pin, GPIO.HIGH)  # Enable all motors

# Function to control the motor direction
def control_motor(motor, direction):
    if direction == 'forward':
        GPIO.output(motor_pins[motor][0], GPIO.HIGH)
        GPIO.output(motor_pins[motor][1], GPIO.LOW)
    elif direction == 'backward':
        GPIO.output(motor_pins[motor][0], GPIO.LOW)
        GPIO.output(motor_pins[motor][1], GPIO.HIGH)
    else:  # stop
        GPIO.output(motor_pins[motor][0], GPIO.LOW)
        GPIO.output(motor_pins[motor][1], GPIO.LOW)

# Function to control all motors simultaneously
def control_all_motors(direction):
    for motor in motor_pins.keys():
        control_motor(motor, direction)



# Camera setup
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 24
raw_capture = PiRGBArray(camera, size=(640, 480))
sleep(2)  # Allow the camera to warm up

try:
    # Capture video and detect garbage
    for frame in camera.capture_continuous(raw_capture, format='bgr', use_video_port=True):
        img = frame.array
        detections = detect_garbage(img)
        garbage_detections = filter_garbage_detections(detections)

        # Draw bounding boxes on the live video feed
        for detection in garbage_detections:
            x1, y1, x2, y2, conf, cls = detection
            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

        # Display the live video feed
        cv2.imshow('Garbage Detection', img)
        key = cv2.waitKey(1) & 0xFF

        # Clear the stream for the next frame
        raw_capture.truncate(0)

        # Break the loop when the 'q' key is pressed
        if key == ord('q'):
            break

    # Clean up
    cv2.destroyAllWindows()

except KeyboardInterrupt:
    control_all_motors('stop')
    GPIO.cleanup()
    cv2.destroyAllWindows()
