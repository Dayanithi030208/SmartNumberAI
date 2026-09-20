from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid

from services.digit_service import recognize_digit


app = Flask(__name__)

# -----------------------------------
# Configuration
# -----------------------------------

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png"
}


# -----------------------------------
# Routes
# -----------------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return {
        "status": "success",
        "message": "SmartNumber AI backend is running"
    }


@app.route("/api/recognize", methods=["POST"])
def recognize():

    # -----------------------------------
    # Check image
    # -----------------------------------

    if "image" not in request.files:
        return {
            "success": False,
            "error": "No image uploaded"
        }, 400

    file = request.files["image"]

    if file.filename == "":
        return {
            "success": False,
            "error": "No image selected"
        }, 400

    # -----------------------------------
    # Check extension
    # -----------------------------------

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return {
            "success": False,
            "error": "Unsupported image format"
        }, 400

    # -----------------------------------
    # Generate safe temporary filename
    # -----------------------------------

    filename = (
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )

    file_path = UPLOAD_FOLDER / filename

    try:

        # Save uploaded image
        file.save(file_path)

        # -----------------------------------
        # Run ML recognition
        # -----------------------------------

        result = recognize_digit(
            str(file_path)
        )

        # -----------------------------------
        # Return JSON
        # -----------------------------------

        return {
        "success": True,
        "digit": result["digit"],
        "confidence": result["confidence"],
        "confidence_level": result["confidence_level"],
        "top_predictions": result["top_predictions"]
    }

    except Exception as error:

        return {
            "success": False,
            "error": str(error)
        }, 500

    finally:

        # -----------------------------------
        # Delete temporary image
        # -----------------------------------

        if file_path.exists():
            file_path.unlink()


# -----------------------------------
# Run application
# -----------------------------------

if __name__ == "__main__":
    app.run(debug=True)