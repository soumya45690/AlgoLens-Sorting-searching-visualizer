const $ = (id) => document.getElementById(id);

const arrayInput = $("arrayInput");
const algorithmSelect = $("algorithmSelect");
const targetInput = $("targetInput");
const targetGroup = $("targetGroup");
const speedSelect = $("speedSelect");

const randomBtn = $("randomBtn");
const runBtn = $("runBtn");
const stopBtn = $("stopBtn");

const barsContainer = $("barsContainer");
const stepNotify = $("stepNotify");
const statusPill = $("statusPill");
const arrayDisplay = $("arrayDisplay");
const stepHistory = $("stepHistory");
const stepCounter = $("stepCounter");

const codeOutput = $("codeOutput");
const timeOutput = $("timeOutput");
const spaceOutput = $("spaceOutput");
const complexityNote = $("complexityNote");

let currentArray = [];
let isRunning = false;
let stopRequested = false;
let runId = 0;
let displayedSteps = 0;

const SPEEDS = {
    slow: 1100,
    normal: 550,
    fast: 180
};

const ALGORITHM_NAMES = {
    bubble: "Bubble Sort",
    selection: "Selection Sort",
    insertion: "Insertion Sort",
    merge: "Merge Sort",
    quick: "Quick Sort",
    counting: "Counting Sort",
    linear: "Linear Search",
    binary: "Binary Search"
};


// --------------------------------------------------
// ARRAY INPUT
// --------------------------------------------------

function parseArray() {
    const raw = arrayInput.value.trim();

    if (!raw) {
        throw new Error("Please enter some numbers.");
    }

    const parts = raw.split(/[\s,]+/).filter(Boolean);

    if (parts.length < 2 || parts.length > 50) {
        throw new Error("Enter between 2 and 50 numbers.");
    }

    const values = parts.map((part) => {
        if (!/^-?\d+$/.test(part)) {
            throw new Error(`"${part}" is not a valid integer.`);
        }

        const number = Number(part);

        if (!Number.isSafeInteger(number)) {
            throw new Error("Please enter safe integer values.");
        }

        return number;
    });

    return values;
}


// --------------------------------------------------
// STATUS
// --------------------------------------------------

function setStatus(message, type = "ready") {
    statusPill.textContent = message;
    statusPill.className = "status-pill";

    if (type === "running") {
        statusPill.classList.add("running");
    }

    if (type === "error") {
        statusPill.classList.add("error");
    }
}


function setBusy(busy) {
    isRunning = busy;

    runBtn.disabled = busy;
    randomBtn.disabled = busy;
    algorithmSelect.disabled = busy;
    arrayInput.disabled = busy;
    targetInput.disabled = busy;
    speedSelect.disabled = busy;

    stopBtn.disabled = !busy;
}


// --------------------------------------------------
// DRAW THE ARRAY BARS
// --------------------------------------------------

function drawBars(values, highlights = [], kind = "none") {
    barsContainer.innerHTML = "";

    if (!Array.isArray(values) || values.length === 0) {
        arrayDisplay.innerHTML = "";
        return;
    }

    const maxValue = Math.max(...values);
    const minValue = Math.min(...values);

    const largestMagnitude = Math.max(
        Math.abs(maxValue),
        Math.abs(minValue),
        1
    );

    const maxHeight = 210;

    values.forEach((value, index) => {
        const item = document.createElement("div");
        item.className = "bar-item";

        const label = document.createElement("div");
        label.className = "bar-value";
        label.textContent = value;

        const bar = document.createElement("div");
        bar.className = "bar";

        // Scale using absolute magnitude so negative values
        // can also be visualized.
        const height = Math.max(
            8,
            (Math.abs(value) / largestMagnitude) * maxHeight
        );

        bar.style.height = `${height}px`;
        bar.title = `Index ${index}: ${value}`;

        if (highlights.includes(index)) {
            if (kind === "swap") {
                bar.classList.add("swap");
            } else if (kind === "sorted" || kind === "found") {
                bar.classList.add("sorted");
            } else {
                bar.classList.add("compare");
            }
        }

        const indexLabel = document.createElement("div");
        indexLabel.className = "bar-index";
        indexLabel.textContent = index;

        item.appendChild(label);
        item.appendChild(bar);
        item.appendChild(indexLabel);

        barsContainer.appendChild(item);
    });

    renderArray(values, highlights, kind);
}


// --------------------------------------------------
// DISPLAY THE ARRAY AS NUMBER CHIPS
// --------------------------------------------------

function renderArray(values, highlights = [], kind = "none") {
    arrayDisplay.innerHTML = "";

    values.forEach((value, index) => {
        const chip = document.createElement("div");
        chip.className = "array-chip";
        chip.textContent = value;

        if (highlights.includes(index)) {
            if (kind === "sorted" || kind === "found") {
                chip.style.background = "#e1f8ef";
                chip.style.borderColor = "#24b887";
            } else if (kind === "swap") {
                chip.style.background = "#ffe8ec";
                chip.style.borderColor = "#df5268";
            } else {
                chip.style.background = "#fff2dc";
                chip.style.borderColor = "#e89a36";
            }
        }

        arrayDisplay.appendChild(chip);
    });
}


// --------------------------------------------------
// STEP-BY-STEP EXPLANATION PANEL
// --------------------------------------------------

function resetStepHistory() {
    displayedSteps = 0;

    stepCounter.textContent = "0 steps";

    stepHistory.innerHTML = `
        <div class="empty-steps">
            <div class="empty-icon">↳</div>
            <h4>Preparing execution</h4>
            <p>
                Step-by-step explanations will appear here as
                the algorithm executes.
            </p>
        </div>
    `;
}


function getStepTitle(step, index) {
    const kind = String(step.kind || "none").toLowerCase();
    const message = String(step.message || "").toLowerCase();

    if (
        message.includes("found") ||
        message.includes("not found")
    ) {
        return "Search Result";
    }

    if (kind === "found") {
        return "Target Found";
    }

    if (kind === "swap") {
        return "Swap / Update";
    }

    if (kind === "sorted") {
        return "Sorted / Completed";
    }

    if (message.includes("compare")) {
        return "Compare Elements";
    }

    if (message.includes("pivot")) {
        return "Pivot Operation";
    }

    if (message.includes("merge")) {
        return "Merge Operation";
    }

    if (message.includes("search")) {
        return "Search Operation";
    }

    if (message.includes("complete")) {
        return "Algorithm Completed";
    }

    return `Execution Step ${index + 1}`;
}


function addStepCard(step, index) {
    // Remove the waiting placeholder when the first step arrives.
    if (displayedSteps === 0) {
        stepHistory.innerHTML = "";
    }

    displayedSteps++;

    stepCounter.textContent =
        `${displayedSteps} step${displayedSteps === 1 ? "" : "s"}`;

    const card = document.createElement("article");
    card.className = "step-card current";

    const number = document.createElement("div");
    number.className = "step-number";
    number.textContent = displayedSteps;

    const content = document.createElement("div");
    content.className = "step-content";

    const title = document.createElement("h4");
    title.textContent = getStepTitle(step, index);

    const explanation = document.createElement("p");

    explanation.textContent =
        step.message || "The algorithm is processing the current state.";

    const tag = document.createElement("span");
    tag.className = "step-tag";
    tag.textContent = step.kind || "processing";

    content.appendChild(title);
    content.appendChild(explanation);
    content.appendChild(tag);

    card.appendChild(number);
    card.appendChild(content);

    // Previous steps remain visible but are no longer active.
    const previous = stepHistory.querySelectorAll(".step-card");

    previous.forEach((previousCard) => {
        previousCard.classList.remove("current");
    });

    stepHistory.appendChild(card);

    // Keep the newest step visible.
    card.scrollIntoView({
        behavior: "smooth",
        block: "nearest"
    });
}


function addFinalStep(message) {
    addStepCard(
        {
            message: message,
            kind: "completed"
        },
        displayedSteps
    );
}


// --------------------------------------------------
// ANIMATION HELPERS
// --------------------------------------------------

function wait(milliseconds, thisRunId) {
    return new Promise((resolve) => {
        const startedAt = Date.now();

        function check() {
            if (stopRequested || thisRunId !== runId) {
                resolve(false);
                return;
            }

            if (Date.now() - startedAt >= milliseconds) {
                resolve(true);
                return;
            }

            setTimeout(check, 25);
        }

        check();
    });
}


function stopRun() {
    if (!isRunning) {
        return;
    }

    stopRequested = true;
    setStatus("Stopping...", "running");
    stepNotify.textContent = "Stopping the animation...";
}


// --------------------------------------------------
// SEARCH TARGET VISIBILITY
// --------------------------------------------------

function updateTargetVisibility() {
    const algorithm = algorithmSelect.value;

    targetGroup.hidden = !["linear", "binary"].includes(algorithm);
}


// --------------------------------------------------
// RESET THE RESULTS
// --------------------------------------------------

function resetResults() {
    resetStepHistory();

    stepNotify.textContent =
        "Starting algorithm execution...";

    codeOutput.textContent =
        "Your algorithm implementations will appear here after execution.";

    timeOutput.textContent = "—";
    spaceOutput.textContent = "—";

    complexityNote.textContent =
        "Complexity information will appear after execution.";
}


// --------------------------------------------------
// RUN THE ALGORITHM
// --------------------------------------------------

async function runAlgorithm() {
    if (isRunning) {
        return;
    }

    let values;

    try {
        values = parseArray();
    } catch (error) {
        setStatus("Invalid input", "error");
        stepNotify.textContent = error.message;
        return;
    }

    const algorithm = algorithmSelect.value;
    const targetValue = targetInput.value.trim();

    if (["linear", "binary"].includes(algorithm)) {
        if (targetValue === "") {
            setStatus("Missing target", "error");
            stepNotify.textContent =
                "Please enter a target value to search for.";
            return;
        }

        if (!Number.isSafeInteger(Number(targetValue))) {
            setStatus("Invalid target", "error");
            stepNotify.textContent =
                "The search target must be a safe integer.";
            return;
        }
    }

    // Create a unique ID for this run.
    runId++;
    const thisRunId = runId;

    stopRequested = false;

    setBusy(true);
    setStatus("Running", "running");
    resetResults();

    currentArray = [...values];
    drawBars(currentArray);

    try {
        const payload = {
            array: values,
            algorithm: algorithm
        };

        if (["linear", "binary"].includes(algorithm)) {
            payload.target = Number(targetValue);
        }

        const response = await fetch("/api/run", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "The server could not run the algorithm."
            );
        }

        if (!Array.isArray(data.steps)) {
            throw new Error(
                "The server response does not contain a valid steps array."
            );
        }

        // Display all three language implementations.
        codeOutput.textContent =
            data.python_code ||
            "No implementation was returned by the server.";

        timeOutput.textContent =
            data.time_complexity || "Not provided";

        spaceOutput.textContent =
            data.space_complexity || "Not provided";

        complexityNote.textContent =
            `Algorithm: ${ALGORITHM_NAMES[algorithm] || algorithm}. ` +
            "Complexity describes how the algorithm's time and memory " +
            "requirements grow with the input size.";

        // Animate each step and display its explanation.
        for (let index = 0; index < data.steps.length; index++) {
            if (stopRequested || thisRunId !== runId) {
                break;
            }

            const step = data.steps[index];

            if (Array.isArray(step.array)) {
                currentArray = [...step.array];

                drawBars(
                    currentArray,
                    step.highlights || [],
                    step.kind || "none"
                );
            }

            const message =
                step.message || `Executing step ${index + 1}.`;

            stepNotify.textContent = message;

            addStepCard(step, index);

            const delay = SPEEDS[speedSelect.value] || SPEEDS.normal;
            const continued = await wait(delay, thisRunId);

            if (!continued) {
                break;
            }
        }

        if (thisRunId !== runId) {
            return;
        }

        if (stopRequested) {
            setStatus("Stopped");
            stepNotify.textContent =
                "Execution stopped. The displayed array shows the last recorded state.";

            addFinalStep("Execution was stopped by the user.");
        } else {
            setStatus("Completed");
            stepNotify.textContent =
                `${ALGORITHM_NAMES[algorithm]} execution completed.`;

            addFinalStep(
                `${ALGORITHM_NAMES[algorithm]} has finished executing. ` +
                "Review the steps above to understand how the algorithm progressed."
            );
        }

    } catch (error) {
        if (thisRunId !== runId) {
            return;
        }

        setStatus("Error", "error");
        stepNotify.textContent = error.message;

        addFinalStep(`Execution error: ${error.message}`);

    } finally {
        if (thisRunId === runId) {
            setBusy(false);
            stopRequested = false;
        }
    }
}


// --------------------------------------------------
// GENERATE A RANDOM ARRAY
// --------------------------------------------------

function generateRandomArray() {
    if (isRunning) {
        return;
    }

    const length = 8 + Math.floor(Math.random() * 5);
    const values = [];

    for (let index = 0; index < length; index++) {
        values.push(5 + Math.floor(Math.random() * 96));
    }

    arrayInput.value = values.join(", ");
    currentArray = [...values];

    drawBars(currentArray);

    resetResults();

    stepNotify.textContent =
        "Random array generated. Select an algorithm and run it.";

    setStatus("Ready");
}


// --------------------------------------------------
// EVENT LISTENERS
// --------------------------------------------------

algorithmSelect.addEventListener(
    "change",
    updateTargetVisibility
);

runBtn.addEventListener(
    "click",
    runAlgorithm
);

stopBtn.addEventListener(
    "click",
    stopRun
);

randomBtn.addEventListener(
    "click",
    generateRandomArray
);

arrayInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !isRunning) {
        runAlgorithm();
    }
});


// --------------------------------------------------
// INITIALIZE THE PAGE
// --------------------------------------------------

try {
    currentArray = parseArray();
    drawBars(currentArray);
} catch {
    currentArray = [45, 12, 78, 23, 9];
    drawBars(currentArray);
}

updateTargetVisibility();
resetStepHistory();
setStatus("Ready");