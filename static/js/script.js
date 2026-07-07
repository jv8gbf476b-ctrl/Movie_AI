const photo1 = document.getElementById("photo1");
const photo2 = document.getElementById("photo2");

const preview1 = document.getElementById("preview1");
const preview2 = document.getElementById("preview2");

const romanceMode = document.getElementById("romanceMode");
const romanceLevel = document.getElementById("romanceLevel");

const selectBtn = document.getElementById("selectBtn");
const generateBtn = document.getElementById("generateBtn");
const copyBtn = document.getElementById("copyBtn");

const result = document.getElementById("result");

const planSubject = document.getElementById("planSubject");
const planScene = document.getElementById("planScene");
const planMood = document.getElementById("planMood");
const planRomance = document.getElementById("planRomance");
const planCamera = document.getElementById("planCamera");
const planTime = document.getElementById("planTime");
const planStyle = document.getElementById("planStyle");
const planService = document.getElementById("planService");
const planReason = document.getElementById("planReason");

let currentPlan = null;

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

function updateRomanceView() {
    romanceLevel.disabled = romanceMode.value === "off";
}

function buildFormData() {
    const formData = new FormData();

    formData.append("photo1", photo1.files[0]);

    if (photo2.files[0]) {
        formData.append("photo2", photo2.files[0]);
    }

    formData.append("romanceMode", romanceMode.value);
    formData.append("romanceLevel", romanceLevel.value);

    return formData;
}

function renderPlan(plan) {
    currentPlan = plan;

    planSubject.innerText = plan.subject_type || "unknown";
    planScene.innerText = plan.scene || "unknown";
    planMood.innerText = plan.mood || "unknown";
    planRomance.innerText = plan.romance || "none";
    planCamera.innerText = plan.camera || "unknown";
    planTime.innerText = plan.time || "unknown";
    planStyle.innerText = plan.style || "unknown";
    planService.innerText = plan.service || "Kling";
    planReason.innerText = plan.reason_ja || "おすすめ理由はありません。";
}

photo1.addEventListener("change", () => {
    preview(photo1, preview1);
});

photo2.addEventListener("change", () => {
    preview(photo2, preview2);
});

romanceMode.addEventListener("change", updateRomanceView);

selectBtn.addEventListener("click", async () => {
    if (!photo1.files[0]) {
        alert("画像①を選んでください");
        return;
    }

    selectBtn.innerText = "分析中...";
    selectBtn.disabled = true;
    result.value = "";
    planReason.innerText = "AI Selectが画像を分析しています...";

    const formData = buildFormData();

    try {
        const response = await fetch("/recommend", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            planReason.innerText = "エラー: " + (data.error || "AI Selectに失敗しました");
            return;
        }

        renderPlan(data.plan);

    } catch (error) {
        planReason.innerText = "通信エラー: " + error.message;
    } finally {
        selectBtn.innerText = "✨ AI Select";
        selectBtn.disabled = false;
    }
});

generateBtn.addEventListener("click", async () => {
    if (!photo1.files[0]) {
        alert("画像①を選んでください");
        return;
    }

    if (!currentPlan) {
        alert("先にAI Selectを実行してください");
        return;
    }

    generateBtn.innerText = "生成中...";
    generateBtn.disabled = true;
    result.value = "AI Planをもとに、動画生成AI用プロンプトを作成中...";

    const formData = buildFormData();
    formData.append("plan", JSON.stringify(currentPlan));

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
        generateBtn.innerText = "🎬 このプランでプロンプト生成";
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

updateRomanceView();
