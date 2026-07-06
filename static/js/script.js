const photo1 = document.getElementById("photo1");
const photo2 = document.getElementById("photo2");

const preview1 = document.getElementById("preview1");
const preview2 = document.getElementById("preview2");

const generateBtn = document.getElementById("generateBtn");
const copyBtn = document.getElementById("copyBtn");

const scene = document.getElementById("scene");
const mood = document.getElementById("mood");
const service = document.getElementById("service");

const result = document.getElementById("result");

function preview(fileInput, image) {

    const file = fileInput.files[0];

    if (!file) return;

    const reader = new FileReader();

    reader.onload = function (e) {

        image.src = e.target.result;
        image.style.display = "block";

    };

    reader.readAsDataURL(file);

}

photo1.addEventListener("change", () => {

    preview(photo1, preview1);

});

photo2.addEventListener("change", () => {

    preview(photo2, preview2);

});

generateBtn.addEventListener("click", () => {

    const prompt = `Create a realistic cinematic video.

Platform:
${service.value}

Scene:
${scene.value}

Mood:
${mood.value}

Use the two uploaded people as the main characters.

Requirements:
- Keep both faces consistent.
- Natural body movement.
- Natural eye contact.
- Realistic hands.
- Cinematic camera movement.
- High quality.
- 5 to 10 seconds.
- Soft lighting.
- Realistic background.
`;

    result.value = prompt;

});

copyBtn.addEventListener("click", async () => {

    if (!result.value) return;

    await navigator.clipboard.writeText(result.value);

    copyBtn.innerText = "✅ コピー完了";

    setTimeout(() => {

        copyBtn.innerText = "コピー";

    }, 1500);

});
