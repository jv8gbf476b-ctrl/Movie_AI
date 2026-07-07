const photo1 = document.getElementById("photo1");
const photo2 = document.getElementById("photo2");

const preview1 = document.getElementById("preview1");
const preview2 = document.getElementById("preview2");

const aiDirector = document.getElementById("aiDirector");
const romanceMode = document.getElementById("romanceMode");
const romanceLevel = document.getElementById("romanceLevel");

const manualSettings = document.getElementById("manualSettings");

const scene = document.getElementById("scene");
const mood = document.getElementById("mood");
const romance = document.getElementById("romance");
const camera = document.getElementById("camera");
const director = document.getElementById("director");
const service = document.getElementById("service");

const generateBtn = document.getElementById("generateBtn");
const copyBtn = document.getElementById("copyBtn");
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

function updateModeView() {
    if (aiDirector.value === "on") {
        manualSettings.style.display = "none";
    } else {
        manualSettings.style.display = "block";
    }

    if (romanceMode.value === "on") {
        romanceLevel.disabled = false;
    } else {
        romanceLevel.disabled = true;
    }
}

photo1.addEventListener("change", () => {
    preview(photo1, preview1);
});

photo2.addEventListener("change", () => {
    preview(photo2, preview2);
});

aiDirector.addEventListener("change", updateModeView);
romanceMode.addEventListener("change", updateModeView);

generateBtn.addEventListener("click", async () => {
    if (!photo1.files[0]) {
        alert("画像①を選んでください");
        return;
    }

    generateBtn.innerText = "生成中...";
    generateBtn.disabled = true;
    result.value = "Movie_AIが画像を解析して、AI監督として最適な演出を考えています...";

    const formData = new FormData();

    formData.append("photo1", photo1.files[0]);

    if (photo2.files[0]) {
        formData.append("photo2", photo2.files[0]);
    }

    formData.append("aiDirector", aiDirector.value);
    formData.append("romanceMode", romanceMode.value);
    formData.append("romanceLevel", romanceLevel.value);

    formData.append("scene", scene.value);
    formData.append("mood", mood.value);
    formData.append("romance", romance.value);
    formData.append("camera", camera.value);
    formData.append("director", director.value);
    formData.append("service", service.value);

    try {
        const response = await fetch("/generate", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            result.value = "エラー:\n" + (data.error || "生成に失敗しました");
            return;
        }

        result.value = data.prompt || "プロンプトが空でした。";

    } catch (error) {
        result.value = "通信エラー:\n" + error.message;
    } finally {
        generateBtn.innerText = "🎬 AIプロンプト生成";
        generateBtn.disabled = false;
    }
});

copyBtn.addEventListener("click", async () => {
    if (!result.value) return;

    await navigator.clipboard.writeText(result.value);

    copyBtn.innerText = "✅ コピー完了";

    setTimeout(() => {
        copyBtn.innerText = "📋 コピー";
    }, 1500);
});

updateModeView();
