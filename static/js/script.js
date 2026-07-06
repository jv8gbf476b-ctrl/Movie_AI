const photo1 = document.getElementById("photo1");
const photo2 = document.getElementById("photo2");

const preview1 = document.getElementById("preview1");
const preview2 = document.getElementById("preview2");

const generateBtn = document.getElementById("generateBtn");
const copyBtn = document.getElementById("copyBtn");

const scene = document.getElementById("scene");
const mood = document.getElementById("mood");
const service = document.getElementById("service");
const romance = document.getElementById("romance");
const camera = document.getElementById("camera");
const director = document.getElementById("director");

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

generateBtn.addEventListener("click", async () => {
    if (!photo1.files[0] || !photo2.files[0]) {
        alert("写真を2枚選んでください");
        return;
    }

    generateBtn.innerText = "生成中...";
    generateBtn.disabled = true;
    result.value = "Geminiが写真を解析して、映画監督モードでプロンプトを作成中...";

    const formData = new FormData();
    formData.append("photo1", photo1.files[0]);
    formData.append("photo2", photo2.files[0]);
    formData.append("scene", scene.value);
    formData.append("mood", mood.value);
    formData.append("service", service.value);
    formData.append("romance", romance.value);
    formData.append("camera", camera.value);
    formData.append("director", director.value);

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
        generateBtn.innerText = "AIプロンプト生成";
        generateBtn.disabled = false;
    }
});

copyBtn.addEventListener("click", async () => {
    if (!result.value) return;

    await navigator.clipboard.writeText(result.value);

    copyBtn.innerText = "✅ コピー完了";

    setTimeout(() => {
        copyBtn.innerText = "コピー";
    }, 1500);
});
