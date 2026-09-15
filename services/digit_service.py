import cv2
import numpy as np
import tensorflow as tf


MODEL_PATH = "model/digit_model.keras"


# Load the trained CNN once
model = tf.keras.models.load_model(MODEL_PATH)


def preprocess_digit(image_path):
    """
    Real-world handwritten digit preprocessing.

    Assumption for the current development test:
    the handwritten digit is located roughly in
    the central region of the photograph.
    """

    # -----------------------------------
    # 1. Read image
    # -----------------------------------

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Could not read the image.")

    # -----------------------------------
    # 2. Resize
    # -----------------------------------

    max_dimension = 1200

    height, width = image.shape[:2]

    if max(height, width) > max_dimension:

        scale = max_dimension / max(height, width)

        image = cv2.resize(
            image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_AREA
        )

    height, width = image.shape[:2]

    # -----------------------------------
    # 3. CENTRAL REGION OF INTEREST
    # -----------------------------------

    # Ignore page borders and large background
    # regions around the handwriting.

    x_start = int(width * 0.20)
    x_end = int(width * 0.80)

    y_start = int(height * 0.20)
    y_end = int(height * 0.80)

    roi = image[
        y_start:y_end,
        x_start:x_end
    ]

    # -----------------------------------
    # 4. Grayscale
    # -----------------------------------

    gray = cv2.cvtColor(
        roi,
        cv2.COLOR_BGR2GRAY
    )

    # -----------------------------------
    # 5. Background normalization
    # -----------------------------------

    # Estimate the slowly changing paper
    # brightness and remove it.

    background = cv2.GaussianBlur(
        gray,
        (51, 51),
        0
    )

    normalized = cv2.subtract(
        background,
        gray
    )

    # -----------------------------------
    # 6. Threshold the ink
    # -----------------------------------

    _, mask = cv2.threshold(
        normalized,
        8,
        255,
        cv2.THRESH_BINARY
    )

    # -----------------------------------
    # 7. Remove tiny noise
    # -----------------------------------

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        np.ones((2, 2), np.uint8)
    )

    # -----------------------------------
    # 8. Connect nearby pen strokes
    # -----------------------------------

    close_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (7, 7)
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        close_kernel,
        iterations=2
    )

    # -----------------------------------
    # 9. Slightly thicken handwriting
    # -----------------------------------

    mask = cv2.dilate(
        mask,
        np.ones((3, 3), np.uint8),
        iterations=1
    )

    # -----------------------------------
    # 10. Find contours
    # -----------------------------------

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        raise ValueError("No digit detected.")

    roi_area = mask.shape[0] * mask.shape[1]

    # -----------------------------------
    # 11. Filter contours
    # -----------------------------------

    candidates = []

    for contour in contours:

        x, y, w, h = cv2.boundingRect(
            contour
        )

        area = cv2.contourArea(contour)

        # Ignore extremely small objects
        if area < 20:
            continue

        # Ignore objects occupying almost
        # the entire ROI (usually background)
        if w > roi_area ** 0.5 * 0.95:
            continue

        if h > roi_area ** 0.5 * 0.95:
            continue

        candidates.append(contour)

    if not candidates:
        raise ValueError(
            "Could not isolate the handwriting."
        )

    # -----------------------------------
    # 12. Combine candidate bounding boxes
    # -----------------------------------

    boxes = [
        cv2.boundingRect(c)
        for c in candidates
    ]

    x1 = min(
        x for x, y, w, h in boxes
    )

    y1 = min(
        y for x, y, w, h in boxes
    )

    x2 = max(
        x + w for x, y, w, h in boxes
    )

    y2 = max(
        y + h for x, y, w, h in boxes
    )

    # -----------------------------------
    # 13. Create digit mask
    # -----------------------------------

    digit_mask = np.zeros_like(mask)

    for contour in candidates:

        cv2.drawContours(
            digit_mask,
            [contour],
            -1,
            255,
            thickness=cv2.FILLED
        )

    # -----------------------------------
    # 14. Crop combined digit
    # -----------------------------------

    digit = digit_mask[
        y1:y2,
        x1:x2
    ]

    if digit.size == 0:
        raise ValueError(
            "Empty digit region."
        )

    # -----------------------------------
    # 15. Make square
    # -----------------------------------

    h, w = digit.shape

    size = max(h, w)

    canvas_size = size + 32

    canvas = np.zeros(
        (canvas_size, canvas_size),
        dtype=np.uint8
    )

    start_x = (
        canvas_size - w
    ) // 2

    start_y = (
        canvas_size - h
    ) // 2

    canvas[
        start_y:start_y + h,
        start_x:start_x + w
    ] = digit

    # -----------------------------------
    # 16. Resize to 28x28
    # -----------------------------------

    digit = cv2.resize(
        canvas,
        (28, 28),
        interpolation=cv2.INTER_AREA
    )

    # -----------------------------------
    # 17. Normalize
    # -----------------------------------

    digit = (
        digit.astype("float32") / 255.0
    )

    processed_image = digit.copy()

    # -----------------------------------
    # 18. CNN input
    # -----------------------------------

    digit = digit.reshape(
        1,
        28,
        28,
        1
    )

    return digit, processed_image


def recognize_digit(image_path):
    """
    Recognize a handwritten digit and return
    prediction + confidence.
    """

    processed_digit, processed_image = preprocess_digit(image_path)

    predictions = model.predict(
        processed_digit,
        verbose=0
    )[0]

    predicted_digit = int(np.argmax(predictions))

    confidence = float(
        predictions[predicted_digit] * 100
    )

    # Top 3 predictions
    top_indices = np.argsort(predictions)[-3:][::-1]

    top_predictions = []

    for index in top_indices:
        top_predictions.append({
            "digit": int(index),
            "confidence": round(
                float(predictions[index] * 100),
                2
            )
        })

    return {
    "digit": predicted_digit,
    "confidence": round(confidence, 2),
    "top_predictions": top_predictions,
    "processed_image": processed_image
    }