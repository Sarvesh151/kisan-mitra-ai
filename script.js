/* =========================================================
   KISAN MITRA AI - COMPLETE FRONTEND SCRIPT
   Crop analysis + organized results + chat + voice
========================================================= */

const imageInput = document.getElementById("imageInput");
const chooseImageBtn = document.getElementById("chooseImageBtn");
const uploadBox = document.getElementById("uploadBox");
const previewImage = document.getElementById("previewImage");
const previewPlaceholder = document.getElementById("previewPlaceholder");
const analyzeBtn = document.getElementById("analyzeBtn");
const analysisStatus = document.getElementById("analysisStatus");
const resultSection = document.getElementById("resultSection");
const resultContent = document.getElementById("resultContent");

let selectedFile = null;
let currentDiseaseContext = null;

const API_BASE_URL = ""; // same-origin Flask API





/* =========================================================
   ORGANIZED RESULT DESIGN
========================================================= */

const resultStyle = document.createElement("style");

resultStyle.textContent = `

.km-result-wrapper {
    width: 100%;
    max-width: 1100px;
    margin: auto;
    color: #23452f;
    font-family: Arial, sans-serif;
}


/* RESULT HEADER */

.km-result-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 18px 20px;
    margin-bottom: 12px;
    border-bottom: 1px solid #dfe9e2;
}

.km-result-icon {
    width: 58px;
    height: 58px;
    border-radius: 16px;
    background: #eaf7e9;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 30px;
}

.km-result-header small {
    display: block;
    color: #5d8068;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 1px;
    margin-bottom: 3px;
}

.km-result-header h2 {
    margin: 0;
    color: #183d26;
    font-size: 28px;
}


/* DISEASE SUMMARY */

.km-disease-card {
    background:
        linear-gradient(
            135deg,
            #f1faf3,
            #f8fcf9
        );

    border: 1px solid #d7eadb;
    border-radius: 10px;

    padding: 17px;
    margin-bottom: 9px;
}

.km-disease-title {
    font-size: 21px;
    font-weight: 700;
    color: #173d25;

    margin-bottom: 14px;
}

.km-disease-meta {
    display: grid;

    grid-template-columns:
        repeat(4, minmax(0, 1fr));

    gap: 12px;
}

.km-meta-item {
    display: flex;
    align-items: center;
    gap: 7px;

    font-size: 14px;
}

.km-meta-item strong {
    color: #23452f;
}


/* COMMON SECTION */

.km-section {
    border-radius: 9px;

    padding: 12px 15px;

    margin: 9px 0;

    border: 1px solid;
}

.km-section h3 {
    margin: 0 0 7px;

    font-size: 16px;
    font-weight: 700;
}

.km-section p {
    margin: 0;

    line-height: 1.55;
    font-size: 14px;
}

.km-section ul {
    margin: 5px 0 0 18px;
    padding: 0;
}

.km-section li {
    margin: 4px 0;

    font-size: 14px;
    line-height: 1.4;
}


/* DESCRIPTION */

.km-description {
    background: #fff8e9;
    border-color: #f5d99b;
}

.km-description h3 {
    color: #a35b0a;
}


/* SYMPTOMS */

.km-symptoms {
    background: #eef6ff;
    border-color: #c8defb;
}

.km-symptoms h3 {
    color: #24518e;
}


/* CAUSES */

.km-causes {
    background: #f7f0ff;
    border-color: #dfc9f5;
}

.km-causes h3 {
    color: #69429b;
}


/* TREATMENT */

.km-treatment {
    background: #f0f8f1;
    border-color: #cfe7d2;
}

.km-treatment h3 {
    color: #2f7041;
}


/* PREVENTION */

.km-prevention {
    background: #eef6ff;
    border-color: #c8defb;
}

.km-prevention h3 {
    color: #28528b;
}


/* MEDICINE */

.km-medicine-section {
    background: #fff1f3;
    border-color: #f4cbd2;
}

.km-medicine-section > h3 {
    color: #b42332;
}

.km-medicine-card {
    background: white;

    border: 1px solid #efd5da;
    border-radius: 8px;

    padding: 14px;
    margin-top: 10px;
}

.km-medicine-title {
    font-size: 16px;
    font-weight: 700;

    color: #6e1f2a;

    margin-bottom: 11px;
}

.km-medicine-info {
    display: grid;

    grid-template-columns:
        repeat(4, minmax(0, 1fr));

    gap: 10px;

    font-size: 13px;
}

.km-medicine-info strong {
    color: #344b3a;
}

.km-safety {
    margin-top: 11px;

    padding: 9px 11px;

    background: #fff8e7;

    border: 1px solid #f1dda5;
    border-radius: 7px;

    font-size: 12px;
    line-height: 1.5;
}


/* VIDEOS */

.km-video-section {
    background: #f5f5ff;
    border-color: #d9d9f4;
}

.km-video-section h3 {
    color: #4e4e91;
}

.km-video-grid {
    display: grid;

    grid-template-columns:
        repeat(2, minmax(0, 1fr));

    gap: 10px;
}

.km-video-card {
    background: white;

    border: 1px solid #ddd9f2;
    border-radius: 8px;

    padding: 12px;
}

.km-video-card h4 {
    margin: 0 0 7px;

    font-size: 14px;
}

.km-video-card p {
    font-size: 12px;
    margin: 5px 0;
}

.km-watch {
    display: inline-block;

    margin-top: 7px;

    padding: 7px 10px;

    border-radius: 6px;

    background: #eee;

    color: #333;

    text-decoration: none;

    font-size: 12px;
}


/* SAFETY */

.km-safety-section {
    background: #fff8e7;
    border-color: #f0d99b;
}

.km-safety-section h3 {
    color: #98620c;
}


/* ERROR */

.error-message {
    padding: 14px;

    border-radius: 9px;

    background: #fff0f0;

    border: 1px solid #efbcbc;

    color: #a12626;
}


/* CHAT VOICE BUTTONS */

.chat-tools {
    display: flex;

    gap: 5px;

    margin-top: 8px;
}

.speak-btn,
.stop-speak-btn {
    border: 1px solid #cfe0d3;

    background: #fff;

    border-radius: 7px;

    padding: 6px 10px;

    cursor: pointer;
}

.speak-btn:disabled,
.stop-speak-btn:disabled {
    opacity: .55;

    cursor: not-allowed;
}


/* MOBILE */

@media (max-width: 800px) {

    .km-disease-meta,
    .km-medicine-info {
        grid-template-columns:
            repeat(2, 1fr);
    }

    .km-video-grid {
        grid-template-columns: 1fr;
    }
}


@media (max-width: 520px) {

    .km-disease-meta,
    .km-medicine-info {
        grid-template-columns: 1fr;
    }

    .km-result-header h2 {
        font-size: 23px;
    }

    .km-section {
        padding: 11px;
    }
}

`;

document.head.appendChild(resultStyle);


/* =========================================================
   IMAGE UPLOAD
========================================================= */

if (chooseImageBtn && imageInput) {

    chooseImageBtn.addEventListener(
        "click",
        () => {
            imageInput.click();
        }
    );

}


if (imageInput) {

    imageInput.addEventListener(
        "change",
        event => {

            const file =
                event.target.files &&
                event.target.files[0];

            if (file) {

                setSelectedFile(file);

            }

        }
    );

}


/* =========================================================
   DRAG & DROP
========================================================= */

if (uploadBox) {

    [
        "dragenter",
        "dragover"
    ].forEach(
        name => {

            uploadBox.addEventListener(
                name,
                event => {

                    event.preventDefault();

                    uploadBox.classList.add(
                        "drag-active"
                    );

                }
            );

        }
    );


    [
        "dragleave",
        "drop"
    ].forEach(
        name => {

            uploadBox.addEventListener(
                name,
                event => {

                    event.preventDefault();

                    uploadBox.classList.remove(
                        "drag-active"
                    );

                }
            );

        }
    );


    uploadBox.addEventListener(
        "drop",
        event => {

            const file =
                event.dataTransfer.files &&
                event.dataTransfer.files[0];

            if (file) {

                setSelectedFile(file);

            }

        }
    );

}


/* =========================================================
   SET SELECTED FILE
========================================================= */

function setSelectedFile(file) {

    if (
        !file.type ||
        !file.type.startsWith("image/")
    ) {

        showError(
            "Please select a valid image file."
        );

        return;

    }


    selectedFile = file;


    const reader =
        new FileReader();


    reader.onload =
        event => {

            if (previewImage) {

                previewImage.src =
                    event.target.result;

                previewImage.style.display =
                    "block";

            }


            if (previewPlaceholder) {

                previewPlaceholder.style.display =
                    "none";

            }


            if (analyzeBtn) {

                analyzeBtn.disabled =
                    false;

            }


            if (analysisStatus) {

                analysisStatus.textContent =
                    "Image selected. Click Analyze Crop to continue.";

            }


            if (resultSection) {

                resultSection.style.display =
                    "none";

            }

        };


    reader.readAsDataURL(file);

}


/* =========================================================
   ANALYZE CROP
========================================================= */

if (analyzeBtn) {

    analyzeBtn.addEventListener(
        "click",
        async () => {

            if (!selectedFile) {

                return;

            }


            analyzeBtn.disabled =
                true;


            analyzeBtn.textContent =
                "⏳ Analyzing Crop...";


            if (analysisStatus) {

                analysisStatus.textContent =
                    "AI is analyzing the leaf image. This may take a few seconds.";

            }


            if (resultSection) {

                resultSection.style.display =
                    "none";

            }


            const formData =
                new FormData();


            formData.append(
                "image",
                selectedFile
            );


            try {

                const response =
                    await fetch(
                        "/api/predict",
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
                        "Prediction failed."
                    );

                }


                /*
                   Save last crop analysis.
                   Chat can use this context.
                */

                currentDiseaseContext = {

                    prediction:
                        data.prediction || {},

                    disease:
                        data.disease || {}

                };


                displayResults(data);


                if (analysisStatus) {

                    analysisStatus.textContent =
                        "Analysis completed successfully.";

                }

            }


            catch (error) {

                showError(
                    error.message
                );

            }


            finally {

                analyzeBtn.disabled =
                    !selectedFile;


                analyzeBtn.textContent =
                    "🔍 Analyze Crop";

            }

        }
    );

}


/* =========================================================
   DISPLAY ORGANIZED RESULTS
========================================================= */

function ensureResultElements() {
    let section = document.getElementById("resultSection");
    let content = document.getElementById("resultContent");
    if (!section) {
        section = document.createElement("section");
        section.id = "resultSection";
        section.className = "result-section";
        const uploadSection = document.querySelector(".upload-section");
        if (uploadSection) uploadSection.insertAdjacentElement("afterend", section);
        else document.querySelector("main")?.appendChild(section);
    }
    if (!content) {
        content = document.createElement("div");
        content.id = "resultContent";
        content.className = "result-card";
        section.appendChild(content);
    }
    return { section, content };
}

function displayResults(data) {
    const resultNodes = ensureResultElements();
    const liveResultSection = resultNodes.section;
    const liveResultContent = resultNodes.content;

    const prediction =
        data.prediction || {};


    const disease =
        data.disease || {};


    const medicines =
        Array.isArray(data.medicines)
            ? data.medicines
            : [];


    const videos =
        Array.isArray(data.videos)
            ? data.videos
            : [];


    const confidence =
        prediction.confidence !== null &&
        prediction.confidence !== undefined

            ? Number(
                prediction.confidence
            ).toFixed(2) + "%"

            : "N/A";


    liveResultContent.innerHTML = `

        <div class="km-result-wrapper">


            <!-- HEADER -->

            
            



            <!-- DISEASE SUMMARY -->

            <div class="km-disease-card">

                <div class="km-disease-title">

                    🦠

                    ${
                        escapeHtml(
                            disease.name ||
                            prediction.disease_id ||
                            "Unknown"
                        )
                    }

                </div>


                <div class="km-disease-meta">


                    <div class="km-meta-item">

                        🟢

                        <span>

                            <strong>
                                Confidence:
                            </strong>

                            ${
                                escapeHtml(
                                    confidence
                                )
                            }

                        </span>

                    </div>


                    <div class="km-meta-item">

                        🌱

                        <span>

                            <strong>
                                Crop:
                            </strong>

                            ${
                                escapeHtml(
                                    disease.crop ||
                                    "N/A"
                                )
                            }

                        </span>

                    </div>


                    <div class="km-meta-item">

                        🧬

                        <span>

                            <strong>
                                Disease Type:
                            </strong>

                            ${
                                escapeHtml(
                                    disease.type ||
                                    "N/A"
                                )
                            }

                        </span>

                    </div>


                    <div class="km-meta-item">

                        ⚠️

                        <span>

                            <strong>
                                Severity:
                            </strong>

                            ${
                                escapeHtml(
                                    disease.severity ||
                                    "N/A"
                                )
                            }

                        </span>

                    </div>


                </div>

            </div>



            <!-- DESCRIPTION -->

            <div class="km-section km-description">

                <h3>
                    📋 Description
                </h3>

                <p>

                    ${
                        escapeHtml(
                            disease.description ||
                            "Information not available."
                        )
                    }

                </p>

            </div>



            <!-- SYMPTOMS -->

            <div class="km-section km-symptoms">

                <h3>
                    🔍 Symptoms
                </h3>

                ${
                    makeList(
                        disease.symptoms
                    )
                }

            </div>



            <!-- CAUSES -->

            <div class="km-section km-causes">

                <h3>
                    🧪 Causes
                </h3>

                ${
                    makeList(
                        disease.causes
                    )
                }

            </div>



            <!-- TREATMENT -->

            <div class="km-section km-treatment">

                <h3>
                    🌱 Treatment / Management
                </h3>

                ${
                    makeList(
                        disease.treatment
                    )
                }

            </div>



            <!-- PREVENTION -->

            <div class="km-section km-prevention">

                <h3>
                    🛡️ Prevention
                </h3>

                ${
                    makeList(
                        disease.prevention
                    )
                }

            </div>



            <!-- MEDICINES -->

            <div class="km-section km-medicine-section">

                <h3>
                    💊 Medicine / Management Options
                </h3>

                ${
                    makeMedicines(
                        medicines
                    )
                }

            </div>



            <!-- VIDEOS -->

            ${
                videos.length

                    ? `

                        <div class="km-section km-video-section">

                            <h3>
                                🎥 Educational Videos
                            </h3>

                            ${
                                makeVideos(
                                    videos
                                )
                            }

                        </div>

                    `

                    : ""
            }


        </div>

    `;


    liveResultSection.style.display =
        "block";


    liveResultSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

}


/* =========================================================
   MAKE LIST
========================================================= */

function makeList(items) {

    const list =
        Array.isArray(items)
            ? items
            : [];


    if (!list.length) {

        return `
            <p>
                Information not available.
            </p>
        `;

    }


    return `

        <ul>

            ${
                list
                    .map(
                        item =>
                            `
                            <li>
                                ${
                                    escapeHtml(
                                        item
                                    )
                                }
                            </li>
                            `
                    )
                    .join("")
            }

        </ul>

    `;

}


/* =========================================================
   MEDICINES
========================================================= */

function makeMedicines(
    medicines
) {

    if (!medicines.length) {

        return `
            <p>
                No verified/reference medicine
                entry is currently stored for this disease.
            </p>
        `;

    }


    return medicines
        .map(
            medicine => `

                <div class="km-medicine-card">


                    <div class="km-medicine-title">

                        💊

                        ${
                            escapeHtml(
                                medicine.name ||
                                "Medicine"
                            )
                        }

                    </div>



                    <div class="km-medicine-info">


                        <div>

                            <strong>
                                Category:
                            </strong>

                            <br>

                            ${
                                escapeHtml(
                                    medicine.category ||
                                    "N/A"
                                )
                            }

                        </div>


                        <div>

                            <strong>
                                Formulation:
                            </strong>

                            <br>

                            ${
                                escapeHtml(
                                    medicine.formulation ||
                                    "N/A"
                                )
                            }

                        </div>


                        <div>

                            <strong>
                                Reference:
                            </strong>

                            <br>

                            ${
                                escapeHtml(
                                    medicine.dose_reference ||
                                    "N/A"
                                )
                            }

                        </div>


                        <div>

                            <strong>
                                Source:
                            </strong>

                            <br>

                            ${
                                escapeHtml(
                                    medicine.source ||
                                    "N/A"
                                )
                            }

                        </div>


                    </div>



                    <div class="km-safety">

                        ⚠️

                        <strong>
                            Safety:
                        </strong>

                        ${
                            escapeHtml(
                                medicine.safety_note ||
                                "Follow the current registered product label and local guidance."
                            )
                        }

                    </div>


                </div>

            `
        )
        .join("");

}


/* =========================================================
   VIDEOS
========================================================= */

function makeVideos(
    videos
) {

    if (!videos.length) {

        return `
            <p>
                No educational video available.
            </p>
        `;

    }


    return `

        <div class="km-video-grid">

            ${
                videos
                    .map(
                        video => `

                            <div class="km-video-card">

                                <h4>

                                    🎬

                                    ${
                                        escapeHtml(
                                            video.title ||
                                            "Educational Video"
                                        )
                                    }

                                </h4>


                                <p>

                                    <strong>
                                        Channel:
                                    </strong>

                                    ${
                                        escapeHtml(
                                            video.source_name ||
                                            "N/A"
                                        )
                                    }

                                </p>


                                <p>

                                    <strong>
                                        Language:
                                    </strong>

                                    ${
                                        escapeHtml(
                                            video.language ||
                                            "N/A"
                                        )
                                    }

                                </p>


                                <a
                                    class="km-watch"
                                    href="${
                                        escapeAttribute(
                                            video.video_url ||
                                            "#"
                                        )
                                    }"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >

                                    ▶ Watch on YouTube

                                </a>

                            </div>

                        `
                    )
                    .join("")
            }

        </div>

    `;

}


/* =========================================================
   ERROR
========================================================= */

function showError(
    message
) {

    const resultNodes = ensureResultElements();
    const liveResultSection = resultNodes.section;
    const liveResultContent = resultNodes.content;

    liveResultSection.style.display = "block";

    liveResultContent.innerHTML = `

        <div class="error-message">

            ❌

            ${
                escapeHtml(
                    message
                )
            }

        </div>

    `;


    if (analysisStatus) {

        analysisStatus.textContent =
            "Analysis failed. Please try again.";

    }


    liveResultSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

}


/* =========================================================
   SECURITY
========================================================= */

function escapeHtml(
    value
) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        String(
            value ?? ""
        );


    return div.innerHTML;

}


function escapeAttribute(
    value
) {

    return String(
        value ?? ""
    )

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#39;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        );

}


/* =========================================================
   KISAN MITRA AI CHAT
========================================================= */

const chatInput =
    document.getElementById(
        "chatInput"
    );


const sendChatBtn =
    document.getElementById(
        "sendChatBtn"
    );


const voiceBtn =
    document.getElementById(
        "voiceBtn"
    );


const chatMessages =
    document.getElementById(
        "chatMessages"
    );


const chatLanguage =
    document.getElementById(
        "chatLanguage"
    );


const voiceStatus =
    document.getElementById(
        "voiceStatus"
    );


let chatHistory = [];


/* =========================================================
   SEND CHAT BUTTON
========================================================= */

if (sendChatBtn) {

    sendChatBtn.addEventListener(
        "click",
        sendChatMessage
    );

}


if (chatInput) {

    chatInput.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendChatMessage();

            }

        }
    );

}


/* =========================================================
   SEND CHAT MESSAGE
========================================================= */

async function sendChatMessage() {

    if (!chatInput) {

        return;

    }


    const question =
        chatInput.value.trim();


    if (!question) {

        return;

    }


    const language =
        chatLanguage
            ? chatLanguage.value
            : "Hindi";


    addChatMessage(
        "user",
        question
    );


    chatInput.value =
        "";


    const loadingMessage =
        addChatMessage(
            "ai",
            "🤔 Kisan Mitra AI is thinking..."
        );


    if (sendChatBtn) {

        sendChatBtn.disabled =
            true;

    }


    try {

        const response =
            await fetch(
                "/api/chat",
                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({
    question: question,
    language: language,
    history: chatHistory,
    disease_context: currentDiseaseContext,

    // Weather information chatbot ko bhejna
    weather_context: JSON.parse(
        localStorage.getItem("kisanWeatherContext") || "null"
    )
})
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
                "AI response failed."
            );

        }


        loadingMessage.remove();


        addChatMessage(
            "ai",
            data.answer
        );


        chatHistory.push({

            role:
                "user",

            content:
                question

        });


        chatHistory.push({

            role:
                "assistant",

            content:
                data.answer

        });


        if (
            chatHistory.length > 20
        ) {

            chatHistory =
                chatHistory.slice(
                    -20
                );

        }

    }


    catch (error) {

        loadingMessage.remove();


        addChatMessage(
            "ai",
            "❌ " +
            error.message
        );

    }


    finally {

        if (sendChatBtn) {

            sendChatBtn.disabled =
                false;

        }


        if (chatInput) {

            chatInput.focus();

        }

    }

}


/* =========================================================
   ADD CHAT MESSAGE
========================================================= */

function addChatMessage(
    type,
    text
) {

    const wrapper =
        document.createElement(
            "div"
        );


    wrapper.className =
        "chat-message " +
        type;


    if (
        type === "ai"
    ) {

        const avatar =
            document.createElement(
                "div"
            );


        avatar.className =
            "chat-avatar";


        avatar.textContent =
            "🤖";


        wrapper.appendChild(
            avatar
        );

    }


    const bubble =
        document.createElement(
            "div"
        );


    bubble.className =
        "chat-bubble";


    const textElement =
        document.createElement(
            "div"
        );


    textElement.textContent =
        text;


    bubble.appendChild(
        textElement
    );


    /*
       LISTEN + STOP BUTTONS
    */

    if (
        type === "ai" &&
        !text.includes(
            "is thinking"
        )
    ) {

        const tools =
            document.createElement(
                "div"
            );


        tools.className =
            "chat-tools";


        const speaker =
            document.createElement(
                "button"
            );


        speaker.type =
            "button";


        speaker.className =
            "speak-btn";


        speaker.textContent =
            "🔊 Listen";


        const stop =
            document.createElement(
                "button"
            );


        stop.type =
            "button";


        stop.className =
            "stop-speak-btn";


        stop.textContent =
            "■ Stop";


        stop.disabled =
            true;


        speaker.addEventListener(
            "click",
            () => {

                speakAnswer(
                    text,
                    chatLanguage
                        ? chatLanguage.value
                        : "Hindi",

                    speaker,
                    stop
                );

            }
        );


        stop.addEventListener(
            "click",
            () => {

                stopSpeaking(
                    speaker,
                    stop
                );

            }
        );


        tools.appendChild(
            speaker
        );


        tools.appendChild(
            stop
        );


        bubble.appendChild(
            tools
        );

    }


    wrapper.appendChild(
        bubble
    );


    if (chatMessages) {

        chatMessages.appendChild(
            wrapper
        );


        chatMessages.scrollTop =
            chatMessages.scrollHeight;

    }


    return wrapper;

}


/* =========================================================
   VOICE INPUT
========================================================= */

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;


let recognition =
    null;


if (SpeechRecognition) {

    recognition =
        new SpeechRecognition();


    recognition.continuous =
        false;


    recognition.interimResults =
        false;


    recognition.maxAlternatives =
        1;


    recognition.onstart =
        () => {

            if (voiceBtn) {

                voiceBtn.classList.add(
                    "listening"
                );

            }


            if (voiceStatus) {

                voiceStatus.textContent =
                    "🎙️ Listening...";

            }

        };


    recognition.onresult =
        event => {

            const transcript =
                event
                    .results[0][0]
                    .transcript;


            if (chatInput) {

                chatInput.value =
                    transcript;

            }


            if (voiceStatus) {

                voiceStatus.textContent =
                    "✅ Voice captured. Press send.";

            }

        };


    recognition.onerror =
        event => {

            if (voiceStatus) {

                voiceStatus.textContent =
                    "❌ Voice error: " +
                    event.error;

            }

        };


    recognition.onend =
        () => {

            if (voiceBtn) {

                voiceBtn.classList.remove(
                    "listening"
                );

            }

        };

}


if (voiceBtn) {

    voiceBtn.addEventListener(
        "click",
        startVoiceInput
    );

}


/* =========================================================
   START VOICE INPUT
========================================================= */

function startVoiceInput() {

    if (!recognition) {

        if (voiceStatus) {

            voiceStatus.textContent =
                "Voice input is not supported here. Please use Chrome.";

        }

        return;

    }


    const languages = {

        Hindi:
            "hi-IN",

        English:
            "en-IN",

        Bhojpuri:
            "hi-IN"

    };


    recognition.lang =
        languages[
            chatLanguage
                ? chatLanguage.value
                : "Hindi"
        ] || "hi-IN";


    try {

        recognition.start();

    }

    catch (error) {

        console.log(
            error
        );

    }

}


/* =========================================================
   VOICE OUTPUT
========================================================= */

let currentSpeechUtterance =
    null;


function cleanAIResponse(
    text
) {

    return String(
        text || ""
    )

        .replace(
            /```[\s\S]*?```/g,
            " "
        )

        .replace(
            /[*_#`]/g,
            ""
        )

        .replace(
            /\[([^\]]+)\]\([^\)]+\)/g,
            "$1"
        )

        .replace(
            /[•●▪◦]/g,
            " "
        )

        .replace(
            /\s+/g,
            " "
        )

        .trim();

}


/* =========================================================
   SPEAK ANSWER
========================================================= */

function speakAnswer(
    text,
    language,
    speakerButton = null,
    stopButton = null
) {

    if (
        !window.speechSynthesis
    ) {

        alert(
            "Voice output is not supported in this browser."
        );

        return;

    }


    stopSpeaking();


    const speechText =
        cleanAIResponse(
            text
        );


    if (!speechText) {

        return;

    }


    const languages = {

        Hindi:
            "hi-IN",

        English:
            "en-IN",

        Bhojpuri:
            "hi-IN"

    };


    const utterance =
        new SpeechSynthesisUtterance(
            speechText
        );


    currentSpeechUtterance =
        utterance;


    utterance.lang =
        languages[
            language
        ] || "hi-IN";


    utterance.rate =
        0.9;


    utterance.pitch =
        1;


    utterance.volume =
        1;


    utterance.onstart =
        () => {

            if (speakerButton) {

                speakerButton.disabled =
                    true;


                speakerButton.textContent =
                    "🔊 Speaking...";

            }


            if (stopButton) {

                stopButton.disabled =
                    false;

            }

        };


    utterance.onend =
        () => {

            resetSpeechButtons(
                utterance,
                speakerButton,
                stopButton
            );

        };


    utterance.onerror =
        () => {

            resetSpeechButtons(
                utterance,
                speakerButton,
                stopButton
            );

        };


    window.speechSynthesis.speak(
        utterance
    );

}


/* =========================================================
   RESET SPEECH BUTTONS
========================================================= */

function resetSpeechButtons(
    utterance,
    speakerButton,
    stopButton
) {

    if (speakerButton) {

        speakerButton.disabled =
            false;


        speakerButton.textContent =
            "🔊 Listen";

    }


    if (stopButton) {

        stopButton.disabled =
            true;

    }


    if (
        currentSpeechUtterance ===
        utterance
    ) {

        currentSpeechUtterance =
            null;

    }

}


/* =========================================================
   STOP SPEAKING
========================================================= */

function stopSpeaking(
    speakerButton = null,
    stopButton = null
) {

    if (
        window.speechSynthesis
    ) {

        window.speechSynthesis.cancel();

    }


    if (speakerButton) {

        speakerButton.disabled =
            false;


        speakerButton.textContent =
            "🔊 Listen";

    }


    if (stopButton) {

        stopButton.disabled =
            true;

    }


    currentSpeechUtterance =
        null;

}