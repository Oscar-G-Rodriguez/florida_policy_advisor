import React, { useMemo, useState } from "react";

const ISSUE_AREAS = [
  { value: "all", label: "All sectors (holistic)" },
  { value: "labor_market", label: "Labor market" },
  { value: "housing", label: "Housing" },
  { value: "fiscal", label: "Fiscal outlook" },
  { value: "education", label: "Education" },
  { value: "health", label: "Health" },
  { value: "climate", label: "Climate & resilience" },
  { value: "infrastructure", label: "Infrastructure & transportation" },
  { value: "environment", label: "Environment & air quality" },
  { value: "public_safety", label: "Public safety" },
  { value: "energy", label: "Energy" },
  { value: "broadband", label: "Broadband" },
  { value: "demographics", label: "Demographics & migration" },
  { value: "business_dynamism", label: "Business dynamism" },
  { value: "agriculture", label: "Agriculture & food systems" },
  { value: "general", label: "General" },
];

const GEOGRAPHIES = [
  { value: "state", label: "State of Florida" },
  { value: "Miami-Dade County", label: "Miami-Dade County" },
  { value: "Orange County", label: "Orange County" },
  { value: "Duval County", label: "Duval County" },
];

const TIME_HORIZONS = [
  { value: "near_term", label: "Near term (6 months)" },
  { value: "mid_term", label: "Mid term (24 months)" },
  { value: "long_term", label: "Long term (60 months)" },
];

const POLICY_LENSES = [
  { value: "market", label: "More market-oriented" },
  { value: "equity", label: "More equity-oriented" },
];

const OBJECTIVES = [
  { value: "improve", label: "Improve conditions" },
  { value: "stabilize", label: "Stabilize at baseline" },
  { value: "resilience", label: "Improve + resilience" },
];

const SECTOR_OBJECTIVES = [
  "labor_market",
  "housing",
  "fiscal",
  "education",
  "health",
  "climate",
  "infrastructure",
  "environment",
  "public_safety",
  "energy",
  "broadband",
  "demographics",
  "business_dynamism",
  "agriculture",
];

export default function App() {
  const API_BASE = import.meta.env.VITE_API_BASE || "";
  const REQUIRE_API = import.meta.env.VITE_REQUIRE_API === "true";
  const [issueArea, setIssueArea] = useState("all");
  const [geography, setGeography] = useState("state");
  const [timeHorizon, setTimeHorizon] = useState("near_term");
  const [policyLens, setPolicyLens] = useState("market");
  const [budgetSensitivity, setBudgetSensitivity] = useState(0.5);
  const [objectiveMode, setObjectiveMode] = useState("improve");
  const [customObjectivesEnabled, setCustomObjectivesEnabled] = useState(false);
  const [customObjectives, setCustomObjectives] = useState(() =>
    Object.fromEntries(SECTOR_OBJECTIVES.map((sector) => [sector, "improve"]))
  );
  const [demoMode, setDemoMode] = useState(!API_BASE && !REQUIRE_API);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [advice, setAdvice] = useState(null);
  const [memoPath, setMemoPath] = useState("");
  const [serverStatus, setServerStatus] = useState("unchecked");
  const [serverCheckedAt, setServerCheckedAt] = useState("");

  const geographyPayload = useMemo(() => {
    if (geography === "state") {
      return { level: "state", value: "Florida" };
    }
    return { level: "county", value: geography };
  }, [geography]);

  const adviceInputs = useMemo(
    () => ({
      issue_area: issueArea,
      geography: geographyPayload,
      time_horizon: timeHorizon,
      budget_sensitivity: budgetSensitivity,
      policy_lens: policyLens,
      objective_mode: objectiveMode,
      objectives: customObjectivesEnabled ? customObjectives : null,
    }),
    [
      issueArea,
      geographyPayload,
      timeHorizon,
      budgetSensitivity,
      policyLens,
      objectiveMode,
      customObjectivesEnabled,
      customObjectives,
    ]
  );

  const demoResponse = useMemo(
    () => ({
      summary:
        "Cross-sector indicators point to affordability and capacity pressures; a balanced portfolio is recommended.",
      outlook_summary:
        "Outlook suggests rising pressure in housing and health, with mixed signals elsewhere.",
      forecast_info: "Demo mode (local sample)",
      objectives: customObjectivesEnabled ? customObjectives : { all: objectiveMode },
      outlook: [
        {
          metric_id: "housing_median_rent",
          sector: "housing",
          metric: "Median gross rent",
          horizon: "near term",
          predicted_value: 1820,
          baseline_value: 1725,
          unit: "USD",
          direction: "worsening",
          citations: ["census_acs_fl_county"],
          method_note: "demo",
        },
        {
          metric_id: "labor_unemployment_bls",
          sector: "labor_market",
          metric: "Unemployment rate (BLS)",
          horizon: "near term",
          predicted_value: 3.4,
          baseline_value: 3.2,
          unit: "%",
          direction: "worsening",
          citations: ["bls_unemployment"],
          method_note: "demo",
        },
      ],
      evidence: [
        {
          label: "Unemployment rate",
          claim: "Florida unemployment rate was 3.2% in 2025-12.",
          citations: ["bls_unemployment"],
        },
      ],
      options: [
        {
          title: "Affordable housing pipeline acceleration",
          description: "Streamline approvals and expand financing for affordable housing construction.",
          pros: ["Addresses supply constraints and rent pressures."],
          cons: ["Requires capital and multi-year delivery timelines."],
          implementation_notes: "Prioritize shovel-ready projects and partnerships.",
          sectors: ["housing"],
        },
      ],
      policy_bundles: [
        {
          name: "Housing acceleration + rental assistance",
          score: 1.12,
          rationale: "Targets housing_median_rent, housing_rent_burden",
          tradeoffs: [],
          policies: [],
        },
      ],
      risks: [
        "Short-term actions may not address longer-term structural constraints.",
        "Data is subject to revision; monitor updates during implementation.",
      ],
      citations: [
        {
          citation_id: "bls_unemployment",
          dataset_id: "bls_unemployment",
          url: "https://api.bls.gov/publicAPI/v2/timeseries/data/",
          retrieval_date: "2026-01-15",
        },
        {
          citation_id: "census_acs_fl_county",
          dataset_id: "census_acs_fl_county",
          url: "https://api.census.gov/data.html",
          retrieval_date: "2026-01-15",
        },
      ],
    }),
    [customObjectives, customObjectivesEnabled, objectiveMode]
  );

  const handleGenerate = async () => {
    setLoading(true);
    setError("");
    setNotice("");
    setMemoPath("");
    setAdvice(null);
    try {
      if (demoMode) {
        await new Promise((resolve) => setTimeout(resolve, 400));
        setAdvice(demoResponse);
      } else {
        const response = await fetch(`${API_BASE}/api/advice`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(adviceInputs),
        });
        if (!response.ok) {
          throw new Error("Unable to generate advice");
        }
        const data = await response.json();
        setAdvice(data);
      }
    } catch (err) {
      setError(err.message || "Unexpected error");
    } finally {
      setLoading(false);
    }
  };

  const handleMemo = async () => {
    if (!advice) return;
    setLoading(true);
    setError("");
    setNotice("");
    try {
      if (demoMode) {
        const blob = new Blob(["# Demo memo\n\nRun with the backend to generate memos."], {
          type: "text/markdown",
        });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "policy_memo_demo.md";
        link.click();
        window.URL.revokeObjectURL(url);
        setMemoPath("demo_mode");
      } else {
        const response = await fetch(`${API_BASE}/api/memo`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            inputs: adviceInputs,
            advice,
          }),
        });
        if (!response.ok) {
          throw new Error("Unable to generate memo");
        }
        const data = await response.json();
        setMemoPath(data.memo_path || "");
        const blob = new Blob([data.memo_markdown], { type: "text/markdown" });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "policy_memo.md";
        link.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (err) {
      setError(err.message || "Unexpected error");
    } finally {
      setLoading(false);
    }
  };

  const handleCheckServer = async () => {
    if (demoMode) {
      setServerStatus("demo");
      setServerCheckedAt(new Date().toLocaleTimeString());
      setNotice("Demo mode is active; no API server required.");
      return;
    }
    setServerStatus("checking");
    setError("");
    setNotice("");
    try {
      const response = await fetch(`${API_BASE}/health`);
      if (!response.ok) {
        throw new Error("Health check failed");
      }
      const data = await response.json();
      setServerStatus(data.status === "ok" ? "online" : "offline");
    } catch (err) {
      setServerStatus("offline");
      setError(err.message || "Unable to reach the API");
    } finally {
      setServerCheckedAt(new Date().toLocaleTimeString());
    }
  };

  const handleReset = () => {
    setIssueArea("all");
    setGeography("state");
    setTimeHorizon("near_term");
    setPolicyLens("market");
    setBudgetSensitivity(0.5);
    setObjectiveMode("improve");
    setCustomObjectivesEnabled(false);
    setCustomObjectives(Object.fromEntries(SECTOR_OBJECTIVES.map((sector) => [sector, "improve"])));
    setAdvice(null);
    setMemoPath("");
    setError("");
    setNotice("");
  };

  const handleClearResults = () => {
    setAdvice(null);
    setMemoPath("");
    setError("");
    setNotice("");
  };

  const handleExample = () => {
    setIssueArea("housing");
    setGeography("Miami-Dade County");
    setTimeHorizon("mid_term");
    setPolicyLens("equity");
    setBudgetSensitivity(0.7);
    setObjectiveMode("improve");
    setCustomObjectivesEnabled(true);
    setCustomObjectives({
      ...customObjectives,
      housing: "improve",
      labor_market: "stabilize",
      fiscal: "stabilize",
    });
    setAdvice(null);
    setMemoPath("");
    setError("");
    setNotice("Loaded example inputs. Click Generate Advice to continue.");
  };

  const handleCopyPayload = async () => {
    try {
      const payload = JSON.stringify(adviceInputs, null, 2);
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(payload);
      } else {
        window.prompt("Copy the request payload:", payload);
      }
      setNotice("Copied request payload to clipboard.");
    } catch (err) {
      setNotice("");
      setError("Unable to copy payload. Your browser may block clipboard access.");
    }
  };

  const formatForecastValue = (value, unit) => {
    if (value === null || value === undefined || Number.isNaN(value)) return "N/A";
    if (unit === "%") return `${value.toFixed(2)}%`;
    if (unit === "USD") {
      return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value);
    }
    if (unit === "ratio") return `${(value * 100).toFixed(1)}%`;
    if (unit === "count") return new Intl.NumberFormat("en-US").format(Math.round(value));
    return `${value.toFixed(2)} ${unit || ""}`.trim();
  };

  return (
    <div className="page">
      <header className="hero">
        <div className="hero-text">
          <p className="eyebrow">Florida Policy Advisor</p>
          <h1>Evidence-backed policy options, ready in minutes.</h1>
          <p className="subhead">
            Generate neutral, citation-rich advice with a configurable policy lens. No code required.
          </p>
        </div>
        <div className="hero-card">
          <div className="status-row">
            <span className={`status-dot ${serverStatus}`} aria-hidden="true" />
            <div>
              <p className="status-label">API status</p>
              <p className="status-value">
                {serverStatus === "demo" && "Demo mode"}
                {serverStatus === "checking" && "Checking..."}
                {serverStatus === "online" && "Online"}
                {serverStatus === "offline" && "Offline"}
                {serverStatus === "unchecked" && "Not checked"}
              </p>
              {serverCheckedAt && (
                <p className="status-meta">Last checked at {serverCheckedAt}</p>
              )}
            </div>
            <button className="ghost" onClick={handleCheckServer} disabled={loading}>
              Check server
            </button>
          </div>
          <div className="quickstart">
            <h3>Quick start</h3>
            <ol>
              <li>Pick the issue area, geography, and time horizon.</li>
              <li>Adjust the budget slider to match fiscal constraints.</li>
              <li>Click Generate Advice, then download the memo.</li>
            </ol>
          </div>
          <div className="quick-actions">
            <button type="button" className="secondary" onClick={handleExample} disabled={loading}>
              Load example inputs
            </button>
            <button type="button" className="secondary" onClick={handleCopyPayload} disabled={loading}>
              Copy request payload
            </button>
            <button type="button" className="secondary" onClick={handleClearResults} disabled={loading}>
              Clear results
            </button>
            <button type="button" className="ghost" onClick={handleReset} disabled={loading}>
              Reset all
            </button>
          </div>
        </div>
      </header>

      <section className="panel">
        <div className="panel-header">
          <h2>Inputs</h2>
          <p>Select an issue area and policy lens to shape prioritization.</p>
        </div>
        <div className="grid">
          <label>
            Issue area
            <select value={issueArea} onChange={(e) => setIssueArea(e.target.value)}>
              {ISSUE_AREAS.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Geography
            <select value={geography} onChange={(e) => setGeography(e.target.value)}>
              {GEOGRAPHIES.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Time horizon
            <select value={timeHorizon} onChange={(e) => setTimeHorizon(e.target.value)}>
              {TIME_HORIZONS.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Policy lens
            <select value={policyLens} onChange={(e) => setPolicyLens(e.target.value)}>
              {POLICY_LENSES.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Objective mode
            <select value={objectiveMode} onChange={(e) => setObjectiveMode(e.target.value)}>
              {OBJECTIVES.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Data mode
            <select value={demoMode ? "demo" : "live"} onChange={(e) => setDemoMode(e.target.value === "demo")}>
              <option value="live">Live API</option>
              <option value="demo">Demo (offline)</option>
            </select>
          </label>
        </div>
        <div className="objective-toggle">
          <label className="checkbox">
            <input
              type="checkbox"
              checked={customObjectivesEnabled}
              onChange={(e) => setCustomObjectivesEnabled(e.target.checked)}
            />
            Customize objectives by sector
          </label>
          <p className="muted">
            Use the global objective mode or override per sector for mixed strategies.
          </p>
        </div>
        {customObjectivesEnabled && (
          <div className="objective-grid">
            {SECTOR_OBJECTIVES.map((sector) => (
              <label key={sector}>
                {sector.replace("_", " ")}
                <select
                  value={customObjectives[sector]}
                  onChange={(e) =>
                    setCustomObjectives((prev) => ({
                      ...prev,
                      [sector]: e.target.value,
                    }))
                  }
                >
                  {OBJECTIVES.map((item) => (
                    <option key={item.value} value={item.value}>
                      {item.label}
                    </option>
                  ))}
                </select>
              </label>
            ))}
          </div>
        )}
        <div className="slider">
          <div>
            <span>Budget sensitivity</span>
            <small>Higher values prioritize lower-cost options.</small>
            <div className="slider-value">Current value: {budgetSensitivity.toFixed(2)}</div>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={budgetSensitivity}
            onChange={(e) => setBudgetSensitivity(parseFloat(e.target.value))}
          />
        </div>
        <div className="actions">
          <button onClick={handleGenerate} disabled={loading}>
            {loading ? "Working..." : "Generate Advice"}
          </button>
          <button onClick={handleMemo} disabled={loading || !advice} className="secondary">
            Download memo
          </button>
        </div>
        {error && <div className="error">{error}</div>}
        {notice && <div className="notice">{notice}</div>}
        {memoPath && <div className="note">Saved to {memoPath}</div>}
      </section>

      {advice && (
        <section className="results">
          <div className="card">
            <h2>Executive summary</h2>
            <p>{advice.summary}</p>
            {advice.objectives && Object.keys(advice.objectives).length > 0 && (
              <div className="objective-list">
                <h3>Objectives by sector</h3>
                <ul>
                  {Object.entries(advice.objectives).map(([sector, objective]) => (
                    <li key={sector}>
                      <strong>{sector.replace("_", " ")}:</strong> {objective}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
          <div className="card">
            <div className="card-header">
              <h2>Outlook</h2>
              {advice.forecast_info && <span className="meta-chip">{advice.forecast_info}</span>}
            </div>
            <p className="muted">{advice.outlook_summary}</p>
            {advice.outlook.length ? (
              <div className="forecast-grid">
                {advice.outlook.map((item) => (
                  <div key={`${item.sector}-${item.metric}`} className="forecast-item">
                    <div className="forecast-header">
                      <span className="tag">{item.sector.replace("_", " ")}</span>
                      <span className={`trend ${item.direction}`}>{item.direction}</span>
                    </div>
                    <h3>{item.metric}</h3>
                    <p className="forecast-value">
                      {formatForecastValue(item.predicted_value, item.unit)} by {item.horizon}
                    </p>
                    {item.baseline_value !== null && item.baseline_value !== undefined && (
                      <p className="forecast-baseline">
                        Latest observed: {formatForecastValue(item.baseline_value, item.unit)}
                      </p>
                    )}
                    <div className="citations">Citations: {item.citations.join(", ")}</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">No forecast data available yet. Add sector indicators to enable outlook.</p>
            )}
          </div>
          <div className="card">
            <h2>Evidence</h2>
            <ul>
              {advice.evidence.map((item) => (
                <li key={item.label}>
                  <strong>{item.label}:</strong> {item.claim}
                  <div className="citations">Citations: {item.citations.join(", ")}</div>
                </li>
              ))}
            </ul>
          </div>
          <div className="card">
            <h2>Recommended policy bundles</h2>
            {advice.policy_bundles && advice.policy_bundles.length ? (
              <div className="bundle-grid">
                {advice.policy_bundles.map((bundle) => (
                  <div key={bundle.name} className="bundle-item">
                    <h3>{bundle.name}</h3>
                    <p className="bundle-score">Score: {bundle.score}</p>
                    <p>{bundle.rationale}</p>
                    {bundle.tradeoffs && bundle.tradeoffs.length > 0 && (
                      <p className="muted">Tradeoffs: {bundle.tradeoffs.join(", ")}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">No policy bundles available for this request.</p>
            )}
          </div>
          <div className="card">
            <h2>Ranked policy options</h2>
            <div className="options">
              {advice.options.map((option) => (
                <div key={option.title} className="option">
                  <h3>{option.title}</h3>
                  <p>{option.description}</p>
                  <div className="pill-row">
                    <span>Pros</span>
                    <span>{option.pros.join("; ")}</span>
                  </div>
                  <div className="pill-row">
                    <span>Cons</span>
                    <span>{option.cons.join("; ")}</span>
                  </div>
                  <p className="notes">{option.implementation_notes}</p>
                  {option.sectors && option.sectors.length > 0 && (
                    <div className="tag-row">
                      {option.sectors.map((sector) => (
                        <span key={sector} className="tag-pill">
                          {sector.replace("_", " ")}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
          <div className="card">
            <h2>Risks and considerations</h2>
            <ul>
              {advice.risks.map((risk) => (
                <li key={risk}>{risk}</li>
              ))}
            </ul>
          </div>
          <div className="card">
            <h2>Citations</h2>
            <ul>
              {advice.citations.map((citation) => (
                <li key={citation.citation_id}>
                  <strong>{citation.citation_id}</strong>: {citation.url} (retrieved {citation.retrieval_date})
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}
    </div>
  );
}
