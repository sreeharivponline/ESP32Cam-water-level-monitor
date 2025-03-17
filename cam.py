import cv2
import numpy as np

# Global variables for ROI
roi = None
drawing = False
ix, iy = -1, -1

# Mouse callback function for drawing ROI
def draw_roi(event, x, y, flags, param):
    global ix, iy, roi, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = param.copy()
            cv2.rectangle(img_copy, (ix, iy), (x, y), (255, 0, 0), 2)
            cv2.imshow("Draw ROI", img_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        roi = (ix, iy, x - ix, y - iy)  # ROI as (x, y, width, height)
        cv2.rectangle(param, (ix, iy), (x, y), (255, 0, 0), 2)
        cv2.imshow("Draw ROI", param)
        print(f"ROI selected: {roi}")

# Function to detect water level
def detect_water_level(frame, roi, water_level_threshold):
    # Crop the frame to the ROI
    x, y, w, h = roi
    roi_frame = frame[y:y + h, x:x + w]

    # Convert to grayscale
    gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Thresholding to segment water area
    _, thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY_INV)

    # Detect contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    water_level = 0
    if contours:
        # Find the largest contour, assumed to be water
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        water_level = h  # Height of the bounding rectangle indicates water level

        # Draw bounding box and water level line
        cv2.rectangle(roi_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.line(roi_frame, (x, y + h), (x + w, y + h), (0, 0, 255), 2)

    # Display water level on frame
    cv2.putText(frame, f"Water Level: {water_level}px", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Flood alert if water level exceeds threshold
    if water_level > water_level_threshold:
        cv2.putText(frame, "FLOOD ALERT!", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    # Display the ROI frame for debugging
    cv2.imshow("ROI", roi_frame)
    return water_level

# Main function
def main():
    global roi

    # Video capture (use 0 for webcam or replace with video file path)
    cap = cv2.VideoCapture(r"C:\Users\sreeh\OneDrive\Desktop\river cam\river_crop.mp4")

    if not cap.isOpened():
        print("Error: Unable to open video file.")
        return

    # Read the first frame for ROI selection
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to read video frame.")
        return

    # Resize the frame to 640 pixels width
    fixed_width = 640
    height = int(frame.shape[0] * (fixed_width / frame.shape[1]))
    frame = cv2.resize(frame, (fixed_width, height))

    # Clone the frame for ROI selection
    clone = frame.copy()
    cv2.imshow("Draw ROI", clone)
    cv2.setMouseCallback("Draw ROI", draw_roi, clone)

    # Wait until the user selects ROI and presses a key
    print("Draw the ROI and press any key to continue.")
    cv2.waitKey(0)

    if roi is None:
        print("No ROI selected. Exiting...")
        return

    # Threshold for flood alert
    water_level_threshold = 150

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("End of video stream or unable to read frame.")
            break

        # Resize the frame to 640 pixels width
        height = int(frame.shape[0] * (fixed_width / frame.shape[1]))
        frame = cv2.resize(frame, (fixed_width, height))

        # Detect water level within the selected ROI
        water_level = detect_water_level(frame, roi, water_level_threshold)

        # Show the main frame
        cv2.imshow("Water Flow Monitoring", frame)

        # Exit on pressing 'q'
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
