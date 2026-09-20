from pathlib import Path

from services.digit_service import recognize_digit


# -----------------------------------
# Expected digit from filename
# -----------------------------------

EXPECTED_DIGITS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9
}


# -----------------------------------
# Test directory
# -----------------------------------

TEST_DIR = Path("test_images")


def get_expected_digit(filename):
    """
    Extract expected digit from filename.
    Example:
        seven.jpeg -> 7
    """

    name = Path(filename).stem.lower()

    for word, digit in EXPECTED_DIGITS.items():

        if name.startswith(word):
            return digit

    return None


def main():

    print()
    print("=" * 70)
    print("SMARTNUMBER AI - REAL WORLD EVALUATION")
    print("=" * 70)

    image_files = sorted(
        [
            file
            for file in TEST_DIR.iterdir()
            if file.suffix.lower() in [
                ".jpg",
                ".jpeg",
                ".png"
            ]
        ]
    )

    if not image_files:
        print("\nNo test images found.")
        return

    results = []

    print()

    print(
        f"{'Image':<15}"
        f"{'Expected':<12}"
        f"{'Predicted':<12}"
        f"{'Confidence':<14}"
        f"Result"
    )

    print("-" * 70)

    for image_file in image_files:

        expected = get_expected_digit(
            image_file.name
        )

        if expected is None:
            print(
                f"{image_file.name:<15}"
                f"{'Unknown':<12}"
            )
            continue

        try:

            result = recognize_digit(
                str(image_file)
            )

            predicted = result["digit"]
            confidence = result["confidence"]

            correct = predicted == expected

            results.append(correct)

            symbol = "✓" if correct else "✗"

            print(
                f"{image_file.name:<15}"
                f"{expected:<12}"
                f"{predicted:<12}"
                f"{confidence:<14.2f}%"
                f"{symbol}"
            )

        except Exception as error:

            print(
                f"{image_file.name:<15}"
                f"{expected:<12}"
                f"{'ERROR':<12}"
                f"{'-':<14}"
                f"✗"
            )

            print(
                f"    Error: {error}"
            )

            results.append(False)

    # -----------------------------------
    # Overall accuracy
    # -----------------------------------

    total = len(results)

    correct = sum(results)

    accuracy = (
        correct / total * 100
        if total > 0
        else 0
    )

    print()
    print("-" * 70)

    print(
        f"Correct: {correct}/{total}"
    )

    print(
        f"Real-world accuracy: {accuracy:.2f}%"
    )

    print("=" * 70)
    print()


if __name__ == "__main__":
    main()