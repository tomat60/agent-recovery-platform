const DEFAULT_FIXTURE_URL = "./data/sample.json";

function assertNonAuthorizing(payload, label) {
  if (payload?.authority !== "none") {
    throw new Error(`${label} transport must remain non-authorizing`);
  }
  return payload;
}

async function getJson(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) throw new Error(`HTTP ${response.status} for ${url}`);
  return response.json();
}

export async function loadOperatorState() {
  const params = new URLSearchParams(window.location.search);
  const apiBase = params.get("api");
  if (!apiBase) {
    const fixture = await getJson(DEFAULT_FIXTURE_URL);
    if (fixture?.product?.authority !== "none") {
      throw new Error("UI fixture must remain non-authorizing");
    }
    return { mode: "fixture", fixture };
  }

  const base = apiBase.replace(/\/$/, "");
  const listing = assertNonAuthorizing(await getJson(`${base}/incidents`), "Incident list");
  const incident = listing.incidents?.[0];
  if (!incident?.incident_id) throw new Error("Persisted incident API returned no incidents");
  const detail = assertNonAuthorizing(
    await getJson(`${base}/incidents/${encodeURIComponent(incident.incident_id)}`),
    "Incident detail"
  );
  return { mode: "api", listing, detail };
}
