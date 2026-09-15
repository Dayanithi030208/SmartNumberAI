from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from services.digit_service import preprocess_digit


TEST_DIR = Path("test_images")


images = []

for image_file in sorted(TEST_DIR.iterdir()):

    if image_file.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
        continue

    try:
        _, processed = preprocess_digit(
            str(image_file)
        )

        images.append(
            (
                image_file.name,
                processed
            )
        )

    except Exception as error:

        print(
            f"Could not process {image_file.name}: {error}"
        )


# -----------------------------------
# Display each processed digit
# -----------------------------------

for filename, image in images:

    plt.figure(figsize=(4, 4))

    plt.imshow(
        image,
        cmap="gray"
    )

    plt.title(
        f"Processed: {filename}"
    )

    plt.axis("off")

    plt.show()