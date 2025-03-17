import requests
import base64
import cv2
import numpy as np
import time

# Firebase URL to the image (ensure this matches the correct path)
firebase_url = ""

def fetch_and_show_image():
    response = requests.get(firebase_url)

    if response.status_code == 200:
        base64_image = response.json()
        if base64_image:
            # Remove the "blob,base64," prefix if it exists
            prefix = "blob,base64,"
            if base64_image.startswith(prefix):
                base64_image = base64_image[len(prefix):]

            # Decode the Base64 string to bytes
            img_data = base64.b64decode(base64_image)

            # Convert the bytes data to a numpy array
            np_arr = np.frombuffer(img_data, np.uint8)

            # Decode the numpy array to an OpenCV image
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            # Display the image
            cv2.imshow('Real-Time Camera Feed', img)

            # Exit if the user presses the 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return False

        else:
            print("No image data available at the specified URL.")
    else:
        print("Failed to fetch image from Firebase:", response.status_code)

    return True

# Streaming loop
while True:
    if not fetch_and_show_image():
        break
    time.sleep(0.2)  # Adjust the sleep duration for your desired FPS

# Clean up
cv2.destroyAllWindows()
