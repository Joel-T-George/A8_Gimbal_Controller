import cv2
import numpy as np

# Create a black image
image = np.zeros((512, 512, 3), dtype=np.uint8)

# Define points of the polygon
pts = np.array([[100, 100], [200, 50], [300, 100], [350, 200], [250, 250]], np.int32)

# Reshape the points array to the format required by polylines (a sequence of points)
pts = pts.reshape((-1, 1, 2))

# Draw the polyline on the image
cv2.polylines(image, [pts], isClosed=False, color=(0, 255, 0), thickness=3)

# Display the image with the polygon
cv2.imshow("Polygon with Polylines", image)

# Press any key to close the window
cv2.waitKey(0)
cv2.destroyAllWindows()
