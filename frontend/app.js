/* DOC - The Good Doctor Savant HUD Application JavaScript Code */

const API = "/api/v1";
let currentPatientId = "";

// Auto-run system stats on startup
document.addEventListener("DOMContentLoaded", () => {
    fetchStats();
    addTerminalLine("Cargando base de conocimiento médico...");
    addTerminalLine("Inicializando memoria prodigiosa autista (Savant Mode: ON)...");
});

function addTerminalLine(text, colorClass = "") {
    const terminal = document.getElementById("terminalLog");
    const div = document.createElement("div");
    div.className = `terminal-line ${colorClass}`;
    div.textContent = `[${new Date().toLocaleTimeString()}] ${text}`;
    terminal.appendChild(div);
    terminal.scrollTop = terminal.scrollHeight;
}

function setExample(n) {
    const examples = [
        "Hace 20 minutos comencé con un dolor de pecho opresivo muy fuerte. Siento que me aprieta el pecho y el dolor se me va hacia la mandíbula y el brazo izquierdo. Tengo sudoración fría y náuseas. Me cuesta un poco respirar.",
        "Tengo tos con flema verde-amarillenta desde hace 4 días, dolor de garganta fuerte al tragar y fiebre de 39.1°C que no baja con paracetamol. Me duele todo el cuerpo.",
        "Desde ayer siento un dolor punzante muy agudo en la parte inferior derecha del abdomen. Empeora notablemente cuando camino, toso o me muevo rápido. Tuve náuseas y pérdida de apetito."
    ];
    document.getElementById("symptomInput").value = examples[n-1];
    addTerminalLine(`Ejemplo ${n} cargado en la consola de ingestión.`);
}

function selectBodyPart(part) {
    const selectedText = document.getElementById("selectedPart");
    const paths = document.querySelectorAll(".body-part");
    
    // Remove active styles from all
    paths.forEach(p => p.classList.remove("active"));
    
    if (part === "all") {
        selectedText.textContent = "Todos";
        addTerminalLine("Filtro de mapas anatómicos reseteado a cuerpo completo.");
        return;
    }
    
    selectedText.textContent = part.toUpperCase();
    
    // Highlight SVG Node
    const node = document.getElementById(`node_${part}`);
    if (node) {
        node.classList.add("active");
    }
    
    addTerminalLine(`Foco anatómico establecido en: ${part.toUpperCase()}`);
    
    // Auto-prepend context to symptom box if empty
    const txtBox = document.getElementById("symptomInput");
    if (!txtBox.value) {
        txtBox.value = `Tengo molestias localizadas en la zona de: ${part}. `;
        txtBox.focus();
    }
}

async function fetchStats() {
    try {
        const r = await fetch(`${API}/stats`);
        if (r.ok) {
            const data = await r.json();
            document.getElementById("statPatients").textContent = data.patients || 0;
            document.getElementById("statConsults").textContent = data.consultations || 0;
            document.getElementById("statKnowledge").textContent = data.knowledge_entries || 0;
            addTerminalLine("Sincronización con base de datos hospitalaria exitosa.", "text-emerald-400");
        }
    } catch (e) {
        addTerminalLine("Error al sincronizar estadísticas del sistema.", "text-rose-400");
    }
}

async function analyzeSymptoms() {
    const input = document.getElementById("symptomInput");
    const text = input.value.trim();
    if (!text) {
        input.focus();
        return;
    }
    
    const btn = document.getElementById("submitBtn");
    const btnText = btn.querySelector(".btn-text");
    const spinner = btn.querySelector(".spinner");
    
    btn.disabled = true;
    btnText.classList.add("hidden");
    spinner.classList.remove("hidden");
    
    // Reset output panels
    document.getElementById("responsePlaceholder").classList.remove("hidden");
    document.getElementById("realResponseContent").classList.add("hidden");
    
    // Animate terminal logs (Shaun Murphy thinking stream)
    addTerminalLine(">>> INICIANDO ESCANEO DE BIOMARKERS SINTOMÁTICOS...", "text-cyan-400");
    
    setTimeout(() => addTerminalLine("[HIPERFOCO ACTIVADO] Aislando patrones fisiopatológicos primarios...", "text-cyan-400"), 300);
    setTimeout(() => addTerminalLine("[RECURSIVIDAD] Mapeando correspondencia con guías clínicas de vanguardia...", "text-cyan-400"), 600);
    setTimeout(() => addTerminalLine("[INGENIERÍA INVERSA] Descartando diagnósticos alternativos por exclusión diferencial...", "text-cyan-400"), 900);
    setTimeout(() => addTerminalLine("[APLICANDO NAVAJA DE OCCAM] Jerarquizando hipótesis según parsimonia científica...", "text-cyan-400"), 1200);

    try {
        const body = { symptoms: text };
        if (currentPatientId) body.patient_id = currentPatientId;
        
        const res = await fetch(`${API}/triage`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        
        if (!res.ok) throw new Error("Fallo en el servidor DOC.");
        
        const data = await res.json();
        
        // Save patient ID for sessions
        currentPatientId = currentPatientId || data.symptoms_parsed?._raw_text?.substring(0,16) || "paciente_" + Date.now().toString(36);
        
        // Render
        setTimeout(() => {
            renderTriageResults(data);
            btn.disabled = false;
            btnText.classList.remove("hidden");
            spinner.classList.add("hidden");
        }, 1500); // Give time for Shaun thinking animation to feel immersive
        
    } catch (e) {
        addTerminalLine(`ERROR CRÍTICO EN ESCANEO: ${e.message}`, "text-rose-400");
        btn.disabled = false;
        btnText.classList.remove("hidden");
        spinner.classList.add("hidden");
    }
}

function renderTriageResults(data) {
    document.getElementById("responsePlaceholder").classList.add("hidden");
    const container = document.getElementById("realResponseContent");
    container.classList.remove("hidden");
    
    // Urgency
    const urgency = data.urgency || "non-urgent";
    const badge = document.getElementById("urgencyBadge");
    const matchConf = document.getElementById("matchConfidence");
    
    const labels = {
        emergency: "🚨 CRÍTICO — ACUDA A EMERGENCIAS",
        high: "⚠️ ALTA PRIORIDAD — Evaluación urgente",
        "non-urgent": "✅ BAJA PRIORIDAD — Control domiciliario"
    };
    
    const badgeClasses = {
        emergency: "badge badge-emergency",
        high: "badge badge-high",
        "non-urgent": "badge badge-low"
    };
    
    badge.className = badgeClasses[urgency] || badgeClasses["non-urgent"];
    badge.textContent = labels[urgency] || labels["non-urgent"];
    
    // Match confidence
    const confVal = Math.round((data.confidence || 0) * 100);
    matchConf.textContent = `CONFIDENCIA: ${confVal}%`;
    matchConf.className = confVal > 70 ? "text-xs font-mono text-emerald-400" : "text-xs font-mono text-cyan-400";
    
    // Recommendation
    const recText = data.recommendation || "Sintomatología compatible con control ambulatorio.";
    document.getElementById("clinicalRecommendation").textContent = recText;
    
    // Differential Diagnoses List
    const diagList = document.getElementById("diagnosisList");
    diagList.innerHTML = "";
    
    const conditions = data.analysis?.possible_conditions || [];
    if (conditions.length === 0) {
        diagList.innerHTML = `<div class="text-xs text-slate-500">Ningún patrón patológico severo de alta correspondencia detectado.</div>`;
    } else {
        conditions.forEach(cond => {
            const name = typeof cond === 'string' ? cond : (cond.name || "Patología");
            const confBonus = cond.confidence_bonus ? `(+${Math.round(cond.confidence_bonus * 100)}% relevancia)` : "";
            const validation = cond.validation_method ? `<div class="text-[10px] text-cyan-400/80 mt-1">Verificación requerida: ${cond.validation_method}</div>` : "";
            
            const div = document.createElement("div");
            div.className = "p-2 bg-clinical/40 border border-cyan-500/10 rounded text-xs flex flex-col hover:border-cyan-500/30 transition-all";
            div.innerHTML = `
                <div class="flex items-center justify-between font-bold text-slate-200">
                    <span>${name}</span>
                    <span class="text-[10px] text-emerald-400 font-mono">${confBonus}</span>
                </div>
                ${validation}
            `;
            diagList.appendChild(div);
        });
    }
    
    // Suggested Questions list
    const qList = document.getElementById("suggestedQuestionsList");
    qList.innerHTML = "";
    const questions = data.suggested_questions || [];
    if (questions.length === 0) {
        qList.innerHTML = `<div class="text-xs text-slate-500">No se requieren preguntas complementarias en este ciclo de recursión.</div>`;
    } else {
        questions.forEach(q => {
            const div = document.createElement("div");
            div.className = "p-1.5 bg-cyan-400/5 hover:bg-cyan-400/10 border border-cyan-400/10 rounded cursor-pointer transition-all flex items-start gap-2";
            div.innerHTML = `<span>💬</span> <span>${q}</span>`;
            // Auto click to append to symptom input
            div.onclick = () => {
                const box = document.getElementById("symptomInput");
                box.value += `\n\nRespuesta a: "${q}": `;
                box.focus();
                addTerminalLine(`Complementando síntomas con repregunta clínica.`);
            };
            qList.appendChild(div);
        });
    }
    
    // BUILD THE AMAZING SAVANT MIND MAP GRAPH!
    buildSavantMindMap(data);
    
    // Log complete
    addTerminalLine(`[ESCANEO COMPLETADO] Diagnósticos generados con ${confVal}% de confianza diferencial.`, "text-emerald-400");
}

function buildSavantMindMap(data) {
    const placeholder = document.getElementById("thoughtMapPlaceholder");
    const network = document.getElementById("activeThoughtNetwork");
    
    placeholder.classList.add("hidden");
    network.classList.remove("hidden");
    network.innerHTML = "";
    
    // Create elements
    const header = document.createElement("div");
    header.className = "absolute top-2 left-2 text-[10px] text-slate-500 font-mono uppercase tracking-widest";
    header.textContent = "COGNITIVE TREE";
    network.appendChild(header);
    
    // Nodes container
    const nodesContainer = document.createElement("div");
    nodesContainer.className = "flex flex-col justify-around h-full w-full py-4";
    
    // Row 1: Parsed Symptoms
    const symptomsRow = document.createElement("div");
    symptomsRow.className = "flex justify-center gap-4 border-b border-cyan-500/5 pb-2";
    
    const symptoms = Object.keys(data.symptoms_parsed || {})
        .filter(k => !k.startsWith("_"))
        .slice(0, 3);
        
    if (symptoms.length === 0) symptoms.push("SymptomPattern");
    
    symptoms.forEach(sym => {
        const cleanName = sym.replace("sintoma_", "").replace(/_/g, " ").toUpperCase();
        const symDiv = document.createElement("div");
        symDiv.className = "text-[10px] font-mono px-2 py-1 bg-cyan-400/10 border border-cyan-400/30 text-cyan-400 rounded-full shadow-[0_0_10px_rgba(0,242,254,0.1)]";
        symDiv.textContent = cleanName;
        symptomsRow.appendChild(symDiv);
    });
    
    nodesContainer.appendChild(symptomsRow);
    
    // Row 2: Physiological Pathway Connectors (The Shaun Murphy mind-effect)
    const pathwayRow = document.createElement("div");
    pathwayRow.className = "flex justify-center py-2";
    
    const pathwayDiv = document.createElement("div");
    pathwayDiv.className = "text-[11px] font-bold text-slate-400 border border-pink-500/20 px-4 py-1.5 rounded bg-pink-500/5 shadow-[0_0_15px_rgba(255,0,127,0.15)] flex flex-col items-center animate-pulse";
    
    const urgency = data.urgency || "non-urgent";
    const systemMapped = urgency === "emergency" ? "PATHWAY: CARDIOVASCULAR ANOMALY" : "PATHWAY: ACUTE INFLAMMATORY RESPONSE";
    
    pathwayDiv.innerHTML = `
        <span class="text-pink-500 tracking-widest uppercase text-[9px] font-mono">[ ANALYZING METABOLIC FLUX ]</span>
        <span class="mt-1">${true ? 'SYS_OK' : 'SAVANT_MODE'} -> ${true ? 'LINKED' : 'DIRECT'}</span>
    `;
    pathwayRow.appendChild(pathwayDiv);
    nodesContainer.appendChild(pathwayRow);
    
    // Row 3: Final Condition Nodes
    const conditionsRow = document.createElement("div");
    conditionsRow.className = "flex justify-center gap-3 border-t border-cyan-500/5 pt-2";
    
    const conditions = data.analysis?.possible_conditions || [];
    conditions.slice(0, 2).forEach(cond => {
        const name = typeof cond === 'string' ? cond : (cond.name || "Deducción");
        const condDiv = document.createElement("div");
        condDiv.className = "text-[10px] font-bold px-2 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded shadow-[0_0_10px_rgba(57,255,20,0.1)] max-w-[150px] text-center truncate";
        condDiv.textContent = name.split(" ")[0] + " " + (name.split(" ")[1] || "");
        conditionsRow.appendChild(condDiv);
    });
    
    nodesContainer.appendChild(conditionsRow);
    network.appendChild(nodesContainer);
}
