export function projectPersistedIncident(detail) {
  const incident = detail?.incident;
  if (!incident || incident.authority !== "none") {
    throw new Error("Persisted incident detail must be a non-authorizing read model");
  }

  const status = incident.status || {};
  const sideEffects = incident.side_effects || [];
  const candidates = incident.recovery_candidates || [];
  const residuals = incident.residuals || [];

  return {
    overview: {
      recoverability_fraction: sideEffects.length ? candidates.length / sideEffects.length : 0,
      consequential_actions: sideEffects.length,
      structurally_recoverable: candidates.length,
      missing_runtime_bindings: null,
      containment_active: Boolean(status.containment_active),
      verification_status: status.verification_status || "not_recorded",
      irreversible_residual_count:
        status.irreversible_residual_count ??
        residuals.filter((item) => item.irreversible === true).length,
      restoration_eligible: status.restoration_status === "recorded_authorized",
    },
    incident: {
      ...incident,
      scenario: "persisted incident evidence",
      recovery_outcomes: Object.fromEntries(
        candidates.map((item) => [item.action_type, item.status])
      ),
    },
    assessment: null,
  };
}
