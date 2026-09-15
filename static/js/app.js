let selectedFile = null;


// ------------------------------
// Get UI Elements
// ------------------------------

const statusText =
    document.getElementById("status");

const imageInput =
    document.getElementById("imageInput");

const dropZone =
    document.getElementById("dropZone");

const fileName =
    document.getElementById("fileName");

const previewContainer =
    document.getElementById("previewContainer");

const imagePreview =
    document.getElementById("imagePreview");

const recognizeButton =
    document.getElementById("recognizeButton");

const recognitionStatus =
    document.getElementById("recognitionStatus");

const resultCard =
    document.getElementById("resultCard");

const predictionsCard =
    document.getElementById("predictionsCard");

const predictedDigit =
    document.getElementById("predictedDigit");

const confidence =
    document.getElementById("confidence");

const confidenceLevel =
    document.getElementById("confidenceLevel");

const topPredictions =
    document.getElementById("topPredictions");


// ------------------------------
// Backend Health Check
// ------------------------------

async function checkBackend() {

    try {

        const response =
            await fetch("/api/health");

        const data =
            await response.json();

        statusText.textContent =
            data.message;

    } catch (error) {

        statusText.textContent =
            "Backend connection failed.";

        console.error(error);
    }
}


// ------------------------------
// Handle File
// ------------------------------

function handleFile(file) {

    if (!file) {
        return;
    }

    if (!file.type.startsWith("image/")) {

        recognitionStatus.textContent =
            "Please select an image file.";

        return;
    }


    // IMPORTANT:
    // Store the actual selected/dropped file

    selectedFile = file;


    // Update filename

    fileName.textContent =
        `Selected: ${file.name}`;


    // Update preview

    const imageURL =
        URL.createObjectURL(file);

    imagePreview.src =
        imageURL;

    previewContainer.hidden =
        false;


    // Reset previous result

    resultCard.hidden =
        true;

    predictionsCard.hidden =
        true;


    recognitionStatus.textContent =
        "Image ready for recognition.";
}


// ------------------------------
// Choose File
// ------------------------------

imageInput.addEventListener(
    "change",
    () => {

        const file =
            imageInput.files[0];

        handleFile(file);
    }
);


// ------------------------------
// Drag Over
// ------------------------------

dropZone.addEventListener(
    "dragover",
    (event) => {

        event.preventDefault();

        dropZone.classList.add(
            "dragging"
        );
    }
);


// ------------------------------
// Drag Leave
// ------------------------------

dropZone.addEventListener(
    "dragleave",
    () => {

        dropZone.classList.remove(
            "dragging"
        );
    }
);


// ------------------------------
// Drop
// ------------------------------

dropZone.addEventListener(
    "drop",
    (event) => {

        event.preventDefault();

        dropZone.classList.remove(
            "dragging"
        );


        const file =
            event.dataTransfer.files[0];


        // Store dropped file separately

        handleFile(file);
    }
);


// ------------------------------
// Recognition
// ------------------------------

async function recognizeDigit() {

    // IMPORTANT:
    // Use selectedFile instead of imageInput.files[0]

    if (!selectedFile) {

        recognitionStatus.textContent =
            "Please select or drop an image first.";

        return;
    }


    recognizeButton.disabled =
        true;

    recognizeButton.textContent =
        "Recognizing...";

    recognitionStatus.textContent =
        "AI is analyzing the image...";

    resultCard.hidden =
        true;

    predictionsCard.hidden =
        true;


    try {

        const formData =
            new FormData();


        formData.append(
            "image",
            selectedFile
        );


        const response =
            await fetch(
                "/api/recognize",
                {
                    method: "POST",
                    body: formData
                }
            );


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.error ||
                "Recognition failed."
            );
        }


        // ------------------------------
        // Display Result
        // ------------------------------

        predictedDigit.textContent =
            data.digit;

        confidence.textContent =
            `${data.confidence}%`;

        confidenceLevel.textContent =
            data.confidence_level;


        // ------------------------------
        // Top Predictions
        // ------------------------------

        topPredictions.innerHTML = "";


        data.top_predictions.forEach(
            prediction => {

                const item =
                    document.createElement("p");

                item.textContent =
                    `${prediction.digit} → ${prediction.confidence}%`;

                topPredictions.appendChild(
                    item
                );
            }
        );


        resultCard.hidden =
            false;

        predictionsCard.hidden =
            false;


        recognitionStatus.textContent =
            "Recognition completed.";

    } catch (error) {

        recognitionStatus.textContent =
            error.message;

        console.error(error);

    } finally {

        recognizeButton.disabled =
            false;

        recognizeButton.textContent =
            "Recognize Digit";
    }
}


// ------------------------------
// Recognize Button
// ------------------------------

recognizeButton.addEventListener(
    "click",
    recognizeDigit
);


// ------------------------------
// Start
// ------------------------------

checkBackend();