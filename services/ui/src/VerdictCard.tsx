// Displays one verdict exactly as the API sent it. No verdict logic lives here.
import { DIMENSIONS, title, type Verdict } from "./verdict";

const GATES = { evidence: "Evidence", feasibility: "Feasibility", risk: "Risk", duplicate: "Duplicate" } as const;

function stability({ stability, sensitivity: { flipped, runs } }: Verdict) {
  return stability === "STABLE"
    ? `Stable: ${flipped} of ${runs} sensitivity checks changed the verdict.`
    : `Borderline: ${flipped} of ${runs} sensitivity checks changed the verdict.`;
}

function ScoreScale({ score, thresholds: { T_no, T_go } }: Verdict) {
  const label = `Score ${score} of 100. Lower threshold ${T_no}, GO threshold ${T_go}.`;
  return (
    <figure>
      <svg className="scale" role="img" aria-label={label} viewBox="0 0 100 10" preserveAspectRatio="none">
        <rect className="track" x="0" y="3" width="100" height="4" />
        <rect className="reached" x="0" y="3" width={score} height="4" />
        <rect className="mark" x={T_no - 0.25} y="1" width="0.5" height="8" />
        <rect className="mark" x={T_go - 0.25} y="1" width="0.5" height="8" />
      </svg>
      <figcaption>
        <strong>{score}</strong> of 100. Lower threshold {T_no}, GO threshold {T_go}.
      </figcaption>
    </figure>
  );
}

export function VerdictCard({ verdict, label }: { verdict: Verdict; label?: string }) {
  const abstained = verdict.verdict === "INSUFFICIENT_EVIDENCE";
  const weakest = verdict.weakest_dimension && DIMENSIONS[verdict.weakest_dimension];
  return (
    <article className="card" aria-label="Verdict card">
      {label && (
        <p role="note" className="fixture">
          {label}. These are sample values; your idea was not evaluated.
        </p>
      )}
      <h2 className={verdict.verdict}>{title(verdict.verdict)}</h2>
      {abstained ? (
        <p>There was not enough evidence to give a score.</p>
      ) : (
        <>
          <p>{stability(verdict)}</p>
          <ScoreScale {...verdict} />
        </>
      )}
      <p>Confidence: {Math.round(verdict.confidence * 100)}%</p>

      <h3 id="gates">Gates</h3>
      <ul className="gates" aria-labelledby="gates">
        {(Object.keys(GATES) as (keyof typeof GATES)[]).map((gate) => (
          <li key={gate} className={verdict.gates[gate]}>
            {GATES[gate]}: {verdict.gates[gate]}
          </li>
        ))}
      </ul>

      {verdict.scores.length > 0 && (
        <>
          <h3>Dimension scores</h3>
          <table>
            <thead>
              <tr>
                <th scope="col">Dimension and reason</th>
                <th scope="col">Score</th>
                <th scope="col">Weight</th>
              </tr>
            </thead>
            <tbody>
              {verdict.scores.map((s) => (
                <tr key={s.dimension}>
                  <th scope="row">
                    {DIMENSIONS[s.dimension]}
                    <small>{s.reason}</small>
                    <small>Evidence: {s.evidence_ids.join(", ")}</small>
                  </th>
                  <td>{s.score} of 5</td>
                  <td>{verdict.weights[s.dimension]}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
      {weakest && (
        <p>
          Weakest dimension: {weakest}. Score floor: {verdict.thresholds.floor}.
        </p>
      )}

      {verdict.what_would_make_go.length > 0 && (
        <>
          <h3>What would make it GO</h3>
          <ul>
            {verdict.what_would_make_go.map((w) => (
              <li key={w.change}>{`${w.change}: score ${w.new_score}, ${w.new_verdict}`}</li>
            ))}
          </ul>
        </>
      )}
    </article>
  );
}
