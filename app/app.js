import { loadOperatorState } from "./operator-transport.js";

const titles = {
  overview: ["Recovery overview", "Evidence-backed recovery state for autonomous agent incidents."],
  incident: ["Incident detail", "Action-level recovery evidence, residual truth and containment state."],
  assessment: ["Recoverability assessment", "Customer-facing evidence identity, readiness and remediation."],
};

const qs = (id) => document.getElementById(id);
const text = (id, value) => { qs(id).textContent = value; };

function human(value) { return String(value ?? "-").replaceAll("_", " "); }
function pill(status) {
  const normalized = String(status ?? "").toLowerCase();
  if (normalized.includes("verified")) return "safe";
  if (normalized.includes("failed") || normalized.includes("residual")) return "warning";
  return "neutral";
}
function candidateRow(title, status, detail) {
  return `<div class="candidate"><div class="candidate-top"><strong>${title}</strong><span class="pill ${pill(status)}">${human(status)}</span></div><p>${detail}</p></div>`;
}
function renderLifecycle(data) {
  const status = data.incident.status;
  const steps = [
    ["Incident", "Recorded", "done"],
    ["Containment", status.containment_active ? "Active" : "Released", status.containment_active ? "warn" : "done"],
    ["Recovery", human(status.recovery_status), status.recovery_status === "executed" ? "done" : ""],
    ["Verification", human(status.verification_status), status.verification_status === "verified" ? "done" : ""],
    ["Restoration", human(status.restoration_status), status.restoration_status === "recorded_authorized" ? "done" : "warn"],
  ];
  qs("lifecycle").innerHTML = steps.map(([name, detail, state]) => `<div class="lifecycle-step ${state}"><strong>${name}</strong><span>${detail}</span></div>`).join("");
}
function renderOverview(data) {
  const o = data.overview;
  text("metric-recoverability", `${Math.round(o.recoverability_fraction * 100)}%`);
  text("metric-verification", human(o.verification_status));
  text("metric-containment", o.containment_active ? "Active" : "Released");
  text("metric-residuals", o.irreversible_residual_count);
  text("incident-name", human(data.incident.scenario));
  text("incident-state", o.containment_active ? "Contained" : "Released");
  text("next-action", human(data.incident.next_action.action));
  text("readiness-total", o.consequential_actions);
  text("readiness-recoverable", o.structurally_recoverable);
  text("readiness-missing", o.missing_runtime_bindings);
  text("readiness-restoration", o.restoration_eligible ? "yes" : "no");
  qs("readiness-fill").style.width = `${Math.round(o.recoverability_fraction * 100)}%`;
  renderLifecycle(data);
}
function renderIncident(data) {
  qs("candidate-list").innerHTML = data.incident.recovery_candidates.map((item) => candidateRow(human(item.action_type), item.status, `${human(item.recovery_class)} | recovery evidence: ${item.recovery_evidence_event_id ? "present" : "missing"} | verification evidence: ${item.verification_evidence_event_id ? "present" : "missing"}`)).join("");
  const outcomes = data.incident.recovery_outcomes;
  qs("side-effect-list").innerHTML = data.incident.side_effects.map((item) => candidateRow(human(item.action_type), outcomes[item.action_type] || item.recovery_class, `${human(item.recovery_class)} | resources: ${(item.resource_keys || []).join(", ") || "none"}`)).join("");
  text("state-crm-before", data.incident.before.crm_contacts["c-1"].owner);
  text("state-crm-after", data.incident.after_recovery.crm_contacts["c-1"].owner);
  text("state-memory", data.incident.after_recovery.memory["sales:last_instruction"] ?? "cleared");
  text("state-messages", data.incident.after_recovery.messages.length);
}
function renderAssessment(data) {
  const a = data.assessment;
  const identity = a.evidence_identity;
  text("assessment-sha", identity.sha256);
  text("evidence-short", `SHA ${identity.sha256.slice(0, 10)}`);
  text("assessment-env", human(a.environment));
  text("assessment-scenario", human(identity.scenario));
  text("assessment-incident", identity.incident_id);
  qs("remediation-list").innerHTML = a.remediation.length ? a.remediation.map((item) => candidateRow(`${item.priority} ${human(item.kind)}`, item.priority, human(item.evidence))).join("") : candidateRow("No derived remediation", "verified", "Current evidence has no remediation blockers.");
  qs("claim-list").innerHTML = a.claim_limits.map((item) => `<span class="claim">${human(item)}</span>`).join("");
}
function bindNavigation() {
  document.querySelectorAll(".nav-item").forEach((button) => button.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach((item) => item.classList.remove("active"));
    document.querySelectorAll(".view").forEach((view) => view.classList.remove("active"));
    button.classList.add("active");
    qs(`view-${button.dataset.view}`).classList.add("active");
    const [title, subtitle] = titles[button.dataset.view];
    text("page-title", title); text("page-subtitle", subtitle);
  }));
}
async function load() {
  bindNavigation();
  try {
    const state = await loadOperatorState();
    if (state.mode !== "fixture") {
      throw new Error("Persisted API transport is connected but canonical console projection is not yet available");
    }
    const data = state.fixture;
    renderOverview(data); renderIncident(data); renderAssessment(data);
  } catch (error) {
    console.error(error); qs("error-banner").hidden = false;
  }
}
load();
