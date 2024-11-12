# import math
# def distance_bearing(homeLattitude, homeLongitude, destinationLattitude, destinationLongitude):
#     R = 6371e3 #Radius of earth in metres
#     rlat1 = homeLattitude * (math.pi/180)
#     rlat2 = destinationLattitude * (math.pi/180) 
#     rlon1 = homeLongitude * (math.pi/180) 
#     rlon2 = destinationLongitude * (math.pi/180) 
#     dlat = (destinationLattitude - homeLattitude) * (math.pi/180)
#     dlon = (destinationLongitude - homeLongitude) * (math.pi/180)
#     #haversine formula to find distance
#     a = (math.sin(dlat/2) * math.sin(dlat/2)) + (math.cos(rlat1) * math.cos(rlat2) * (math.sin(dlon/2) * math.sin(dlon/2)))
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
#     distance = R * c #distance in metres
#     #formula for bearing
#     y = math.sin(rlon2 - rlon1) * math.cos(rlat2)
#     x = math.cos(rlat1) * math.sin(rlat2) - math.sin(rlat1) * math.cos(rlat2) * math.cos(rlon2 - rlon1)
#     bearing = math.atan2(y, x) #bearing in radians
#     bearingDegrees = bearing * (180/math.pi)
#     out = [distance, bearingDegrees]
#     return out

# if __name__ == '__main__':
#     distance = distance_bearing(13.38969,80.23008,13.38901,80.23022)
#     print(distance)

import cv2

def draw_focus_corners(frame, x, y, w, h, color=(0, 255, 0), thickness=2, corner_length=50):
    """
    Draws rectangular corners for object focus.
    :param frame: The image/frame on which to draw.
    :param x, y: Top-left corner coordinates of the bounding box.
    :param w, h: Width and height of the bounding box.
    :param color: Color of the corner lines.
    :param thickness: Thickness of the lines.
    :param corner_length: Length of the corner lines.
    """
    
    # Top-left corner
    cv2.line(frame, (x, y), (x + corner_length, y), color, thickness)
    cv2.line(frame, (x, y), (x, y + corner_length), color, thickness)

    # Top-right corner
    cv2.line(frame, (x + w, y), (x + w - corner_length, y), color, thickness)
    cv2.line(frame, (x + w, y), (x + w, y + corner_length), color, thickness)

    # Bottom-left corner
    cv2.line(frame, (x, y + h), (x, y + h - corner_length), color, thickness)
    cv2.line(frame, (x, y + h), (x + corner_length, y + h), color, thickness)

    # Bottom-right corner
    cv2.line(frame, (x + w, y + h), (x + w - corner_length, y + h), color, thickness)
    cv2.line(frame, (x + w, y + h), (x + w, y + h - corner_length), color, thickness)

# Capture video from webcam (or use your video source)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    
    # Assuming object detection returns this bounding box (replace with actual detection)
    x, y, w, h = 100, 100, 200, 200  # Example bounding box coordinates
    
    # Draw focus corners on the object
    draw_focus_corners(frame, x, y, w, h)
    
    # Display the frame
    cv2.imshow('Frame with Focus Corners', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
