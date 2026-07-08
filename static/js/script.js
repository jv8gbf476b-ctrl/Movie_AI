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

    reader.onload = e => {
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

function setLoading(button, text) {
    button.disabled = true;
    button.innerText = text;
}

function resetButton(button, text) {
    button.disabled = false;
    button.innerText = text;
}

function renderPlan(plan) {

    currentPlan = plan;

    planSubject.textContent = plan.subject_type || "未判定";
    planScene.textContent = plan.scene || "未判定";
    planMood.textContent = plan.mood || "未判定";
    planRomance.textContent = plan.romance || "none";
    planCamera.textContent = plan.camera || "未判定";
    planTime.textContent = plan.time || "未判定";
    planStyle.textContent = plan.style || "未判定";
    planService.textContent = plan.service || "Kling";
    planReason.textContent = plan.reason_ja || "AIコメントはありません。";
}

photo1.addEventListener("change", () => preview(photo1, preview1));
photo2.addEventListener("change", () => preview(photo2, preview2));

romanceMode.addEventListener("change", updateRomanceView);

selectBtn.addEventListener("click", async () => {

    if (!photo1.files.length) {
        alert("画像①を選択してください。");
        return;
    }

    setLoading(selectBtn, "🤖 AI分析中...");

    result.value = "";
    planReason.textContent = "AI Selectが分析しています...";

    try {

        const response = await fetch("/recommend", {
            method: "POST",
            body: buildFormData()
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "AI Selectに失敗しました。");
        }

        renderPlan(data.plan);

    } catch (e) {

        planReason.textContent = e.message;

    } finally {

        resetButton(selectBtn, "✨ AI Select");

    }

});

generateBtn.addEventListener("click", async () => {

    if (!photo1.files.length) {
        alert("画像①を選択してください。");
        return;
    }

    if (!currentPlan) {
        alert("先にAI Selectを実行してください。");
        return;
    }

    setLoading(generateBtn, "🎬 生成中...");

    result.value = "Movie_AIが映画品質のプロンプトを生成しています...";

    try {

        const formData = buildFormData();

        formData.append(
            "plan",
            JSON.stringify(currentPlan)
        );

        const response = await fetch("/generate", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "プロンプト生成に失敗しました。");
        }

        result.value = data.prompt || "";

    } catch (e) {

        result.value = e.message;

    } finally {

        resetButton(
            generateBtn,
            "🎬 このプランでプロンプト生成"
        );

    }

});

copyBtn.addEventListener("click", async () => {

    if (!result.value.trim()) return;

    await navigator.clipboard.writeText(result.value);

    copyBtn.textContent = "✅ コピー完了";

    setTimeout(() => {
        copyBtn.textContent = "📋 コピー";
    }, 1500);

});

updateRomanceView();
