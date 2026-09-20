import matplotlib.pyplot as plt

from services.digit_service import recognize_digit


image_path = "test_images/seven.jpeg"

result = recognize_digit(image_path)

print("\n==============================")
print("SMARTNUMBER AI")
print("==============================")

print(f"Prediction: {result['digit']}")
print(f"Confidence: {result['confidence']}%")

print("\nTop 3 Predictions:")

for prediction in result["top_predictions"]:
    print(
        f"  {prediction['digit']} "
        f"→ {prediction['confidence']}%"
    )

print("==============================")


# Show what the CNN actually received
plt.imshow(
    result["processed_image"],
    cmap="gray"
)

plt.title(
    f"CNN Input - Predicted: {result['digit']}"
)

plt.axis("off")
plt.show()