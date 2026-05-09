import cv2
import numpy as np

#IMAGE_PATH = "1.JPG"

IMAGE_PATH = 0 #TODO: зчитування з UI
image = cv2.imread(IMAGE_PATH)

if image is None:
    print("Image Not Found")
    exit(0)

#INPUT_STR = input("Enter Colors to use (e.g. red, blue): ")
#INPUT_COLORS = [c.strip().lower() for c in INPUT_STR.split(",")]

INPUT_COLORS = {} #TODO: зчитування з UI

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

COLOR_RANGES = {
    "red": [
        ((0, 120, 70), (10, 255, 255)),
        ((170, 120, 70), (180, 255, 255)),
    ],
    "orange": [
        ((11, 120, 70), (24, 255, 255)),
    ],
    "yellow": [
        ((25, 120, 70), (35, 255, 255)),
    ],
    "lime": [
        ((36, 120, 120), (50, 255, 255)),
    ],
    "green": [
        ((51, 60, 60), (85, 255, 255)),
    ],
    "turquoise": [
        ((86, 60, 60), (95, 255, 255)),
    ],
    "cyan": [
        ((96, 60, 60), (100, 255, 255)),
    ],
    "sky_blue": [
        ((101, 80, 80), (110, 255, 255)),
    ],
    "blue": [
        ((111, 80, 60), (130, 255, 255)),
    ],
    "navy": [
        ((131, 80, 40), (140, 255, 180)),
    ],
    "purple": [
        ((125, 60, 40), (155, 255, 255)),
    ],
    "magenta": [
        ((156, 80, 80), (165, 255, 255)),
    ],
    "pink": [
        ((166, 50, 70), (169, 255, 255)),
    ],
    "brown": [
        ((8, 80, 20), (25, 255, 200)),
    ],
    "beige": [
        ((15, 20, 150), (35, 80, 255)),
    ],
    "white": [
        ((0, 0, 200), (180, 40, 255)),
    ],
    "light_gray": [
        ((0, 0, 120), (180, 30, 199)),
    ],
    "gray": [
        ((0, 0, 60), (180, 40, 119)),
    ],
    "dark_gray": [
        ((0, 0, 30), (180, 50, 59)),
    ],
    "black": [
        ((0, 0, 0), (180, 255, 29)),
    ],
}

valid_colors = [c for c in INPUT_COLORS if c in COLOR_RANGES]

if not valid_colors:
    print("No valid colors found")
    exit(0)

mask = np.zeros(hsv.shape[:2], np.uint8)
count = 0

for current_color in valid_colors:

    COLOR_TO_PAINT = (0, 0, 0)
    bg_color = (255, 255, 255)

    color_mask = np.zeros(hsv.shape[:2], np.uint8)

    for lower, upper in COLOR_RANGES[current_color]:
        lower = np.array(lower, np.uint8)
        upper = np.array(upper, np.uint8)
        cur_mask = cv2.inRange(hsv, lower, upper)
        color_mask = cv2.bitwise_or(color_mask, cur_mask)

    kernel = np.ones((5, 5), np.uint8)
    color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel)
    color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel)

    mask = cv2.bitwise_or(mask, color_mask)

    contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 300:
            count += 1

            cv2.drawContours(image, [contour], -1, COLOR_TO_PAINT, 2)

            x, y, w, h = cv2.boundingRect(contour)

            M = cv2.moments(contour)
            if M["m00"] == 0:
                continue

            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            cv2.rectangle(image, (x, y), (x + w, y + h), COLOR_TO_PAINT, 2)
            cv2.circle(image, (cx, cy), 5, COLOR_TO_PAINT, -1)

            text = f'x={cx}, y={cy}'
            (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

            text_x = x
            text_y = y - 10

            if text_y - text_height < 0:
                text_y = y + h + text_height + 10

            if text_x + text_width > image.shape[1]:
                text_x = image.shape[1] - text_width - 5

            cv2.rectangle(image, (text_x - 2, text_y - text_height - 2), (text_x + text_width + 2, text_y + baseline),
                          bg_color, cv2.FILLED)
            cv2.putText(image, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_TO_PAINT, 1)

print(f'Detected {count} objects')
cv2.imwrite("output.jpg", image)
cv2.imshow("image", image)
cv2.imshow("mask", mask)
cv2.waitKey(0)
cv2.destroyAllWindows()