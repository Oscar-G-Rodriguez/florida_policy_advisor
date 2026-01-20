import React, { useMemo, useState } from "react";

const ISSUE_AREAS = [
  { value: "labor_market", label: "Labor market" },
  { value: "housing", label: "Housing" },
  { value: "fiscal", label: "Fiscal outlook" },
  { value: "general", label: "General" },
];

const GEOGRAPHIES = [
  { value: "state", label: "State of Florida" },
  { value: "Miami-Dade County", label: "Miami-Dade County" },
  { value: "Orange County", label: "Orange County" },
  { value: "Duval County", label: "Duval County" },
];

const TIME_HORIZONS = [
  { value: "near_term", label: "Near term" },
  { value: "mid_term", label: "Mid term" },
  { value: "long_term", label: "Longer term" },
];

const POLICY_LENSES = [
  { value: "market", label: "More market-oriented" },
  { value: "equity", label: "More equity-oriented" },
];

export default function App() {
  const [issueArea, setIssueArea] = useState("labor_market");
  const [geography, setGeography] = useState("state");
  const [timeHorizon, setTimeHorizon] = useState("near_term");
  const [policyLens, setPolicyLens] = useState("market");
  const [budgetSensitivity, setBudgetSensitivity] = useState(0.5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [advice, setAdvice] = useState(null);
  const [memoPath, setMemoPath] = useState("");

  const geographyPayload = useMemo(() => {
    if (geography === "state") {
      return { level: "state", value: "Florida" };
    }
    return { level: "county", value: geography };
  }, [geography]);

  const handleGenerate = async () => {
    setLoading(true);
    setError("");
    setMemoPath("");
    try {
      const response = await fetch("/api/advice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          issue_area: issueArea,
          geography: geographyPayload,
          time_horizon: timeHorizon,
          budget_sensitivity: budgetSensitivity,
          policy_lens: policyLens,
        }),
      });
      if (!response.ok) {
        throw new Error("Unable to generate advice");
      }
      const data = await response.json();
      setAdvice(data);
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
    try {
      const response = await fetch("/api/memo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          inputs: {
            issue_area: issueArea,
            geography: geographyPayload,
            time_horizon: timeHorizon,
            budget_sensitivity: budgetSensitivity,
            policy_lens: policyLens,
          },
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
    } catch (err) {
      setError(err.message || "Unexpected error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <header className="hero">
        <div>
          <p className="eyebrow">Florida Policy Advisor</p>
          <h1>Evidence-backed policy options, ready in minutes.</h1>
          <p className="subhead">
            Generate neutral, citation-rich advice with a configurable policy lens. No code required.
          </p>
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
        </div>
        <div className="slider">
          <div>
            <span>Budget sensitivity</span>
            <small>Higher values prioritize lower-cost options.</small>
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
        {memoPath && <div className="note">Saved to {memoPath}</div>}
      </section>

      {advice && (
        <section className="results">
          <div className="card">
            <h2>Executive summary</h2>
            <p>{advice.summary}</p>
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
