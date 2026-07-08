const photo1 = document.getElementById("photo1");
const photo2 = document.getElementById("photo2");

const preview1 = document.getElementById("preview1");
const preview2 = document.getElementById("preview2");

const romanceMode = document.getElementById("romanceMode");
const romanceLevel = document.getElementById("romanceLevel");
const userSituation = document.getElementById("userSituation");

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

    romanceLevel.disabled =
        romanceMode.value === "off";

}

function buildFormData() {

    const formData = new FormData();

    formData.append(
        "photo1",
        photo1.files[0]
    );

    if (photo2.files[0]) {

        formData.append(
            "photo2",
            photo2.files[0]
        );

    }

    formData.append(
        "romanceMode",
        romanceMode.value
    );

    formData.append(
        "romanceLevel",
        romanceLevel.value
    );

    formData.append(
        "userSituation",
        userSituation.value.trim()
    );

    return formData;

}

function renderPlan(plan) {

    currentPlan = plan;

    planSubject.innerText = plan.subject_type || "未判定";
    planScene.innerText = plan.scene || "未判定";
    planMood.innerText = plan.mood || "未判定";
    planRomance.innerText = plan.romance || "未判定";
    planCamera.innerText = plan.camera || "未判定";
    planTime.innerText = plan.time || "未判定";
    planStyle.innerText = plan.style || "未判定";
    planService.innerText = plan.service || "Kling";

    planReason.innerText =
        plan.reason_ja ||
        "おすすめ理由はありません。";

}

photo1.addEventListener(
    "change",
    () => preview(photo1, preview1)
);

photo2.addEventListener(
    "change",
    () => preview(photo2, preview2)
);

romanceMode.addEventListener(
    "change",
    updateRomanceView
);

selectBtn.addEventListener(
    "click",
    async () => {

        if (!photo1.files[0]) {

            alert("画像①を選んでください");

            return;

        }

        selectBtn.disabled = true;
        selectBtn.innerText = "分析中...";

        result.value = "";

        planReason.innerText =
            "AI Selectが画像を分析しています...";

        try {

            const response = await fetch(
                "/recommend",
                {
                    method: "POST",
                    body: buildFormData()
                }
            );

            const data = await response.json();

            if (!response.ok) {

                planReason.innerText =
                    data.error || "エラー";

                return;

            }

            renderPlan(data.plan);

        }

        catch (error) {

            planReason.innerText =
                error.message;

        }

        finally {

            selectBtn.disabled = false;
            selectBtn.innerText = "✨ AI Select";

        }

    }
);

generateBtn.addEventListener(
    "click",
    async () => {

        if (!photo1.files[0]) {

            alert("画像①を選んでください");

            return;

        }

        if (!currentPlan) {

            alert(
                "先にAI Selectを実行してください"
            );

            return;

        }

        generateBtn.disabled = true;
        generateBtn.innerText = "生成中...";

        result.value =
            "プロンプト生成中...";

        const formData = buildFormData();

        formData.append(
            "plan",
            JSON.stringify(currentPlan)
        );

        try {

            const response = await fetch(
                "/generate",
                {
                    method: "POST",
                    body: formData
                }
            );

            const data = await response.json();

            if (!response.ok) {

                result.value =
                    data.error || "エラー";

                return;

            }

            result.value = data.prompt;

        }

        catch (error) {

            result.value =
                error.message;

        }

        finally {

            generateBtn.disabled = false;

            generateBtn.innerText =
                "🎬 このプランでプロンプト生成";

        }

    }
);

copyBtn.addEventListener(
    "click",
    async () => {

        if (!result.value) return;

        await navigator.clipboard.writeText(
            result.value
        );

        copyBtn.innerText =
            "✅ コピー完了";

        setTimeout(() => {

            copyBtn.innerText =
                "📋 コピー";

        }, 1500);

    }
);

updateRomanceView();
