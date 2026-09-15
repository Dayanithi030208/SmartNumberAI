const statusText = document.getElementById("status");
const testButton = document.getElementById("testButton");


async function checkBackend() {

    try {

        const response = await fetch("/api/health");

        const data = await response.json();

        statusText.textContent = data.message;

    } catch (error) {

        statusText.textContent = "Backend connection failed.";

        console.error(error);
    }
}


testButton.addEventListener("click", checkBackend);

checkBackend();