import { useEffect, useState } from "react";
import { type ApiError, call, type Comparison, type Idea, type Summary, type Version } from "./account";
import { DIMENSIONS, title } from "./verdict";

const judged = (v: Summary, none: string) => (v ? `${title(v.verdict)}, score ${v.score}` : none);

export function History({ token, onSignedOut }: { token: string; onSignedOut: () => void }) {
  const [ideas, setIdeas] = useState<Idea[]>();
  const [chosen, setChosen] = useState<string[]>([]);
  const [versions, setVersions] = useState<{ title: string; versions: Version[] }>();
  const [comparison, setComparison] = useState<Comparison>();
  const [error, setError] = useState("");

  async function load<T>(path: string, show: (value: T) => void) {
    setError("");
    try {
      show(await call<T>(path, { token }));
    } catch (problem) {
      if ((problem as ApiError).status === 401) onSignedOut();
      else setError((problem as Error).message);
    }
  }

  // biome-ignore lint/correctness/useExhaustiveDependencies: load once for this token
  useEffect(() => {
    load<{ ideas: Idea[] }>("/ideas", (answer) => setIdeas(answer.ideas));
  }, [token]);

  const toggle = (id: string) => setChosen(chosen.includes(id) ? chosen.filter((c) => c !== id) : [...chosen, id]);

  return (
    <section>
      <h2>History</h2>
      {error && <p role="alert">{error}</p>}
      {!ideas && !error && <p role="status">Loading your ideas...</p>}
      {ideas?.length === 0 && <p>No ideas saved yet.</p>}
      {ideas && ideas.length > 0 && (
        <>
          <ul className="ideas">
            {ideas.map((idea) => (
              <li key={idea.idea_id}>
                <label>
                  <input
                    type="checkbox"
                    aria-label={`Select ${idea.title}`}
                    checked={chosen.includes(idea.idea_id)}
                    onChange={() => toggle(idea.idea_id)}
                  />
                  <strong>{idea.title}</strong>
                </label>
                <span>{`${judged(idea.verdict, "Not judged yet")}, version ${idea.latest_version}`}</span>
                <button
                  type="button"
                  className="secondary"
                  aria-label={`Versions of ${idea.title}`}
                  onClick={() => load(`/ideas/${encodeURIComponent(idea.idea_id)}/versions`, setVersions)}
                >
                  Versions
                </button>
              </li>
            ))}
          </ul>
          <button
            type="button"
            disabled={chosen.length !== 2}
            onClick={() => load(`/compare?a=${encodeURIComponent(chosen[0])}&b=${encodeURIComponent(chosen[1])}`, setComparison)}
          >
            Compare the two selected
          </button>
        </>
      )}
      {versions && (
        <>
          <h3>Versions of {versions.title}</h3>
          <ul>
            {versions.versions.map((v) => (
              <li key={v.version}>{`Version ${v.version}: ${v.text} (${judged(v.verdict, "not judged")})`}</li>
            ))}
          </ul>
        </>
      )}
      {comparison && (
        <>
          <h3>Comparison</h3>
          <table>
            <thead>
              <tr>
                <th scope="col">Dimension, score of 5</th>
                {comparison.ideas.map((idea) => (
                  <th scope="col" key={idea.idea_id}>{`${idea.title}, version ${idea.version}`}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="row">Verdict</th>
                {comparison.ideas.map((idea) => (
                  <td key={idea.idea_id}>{judged(idea.verdict, "Not judged")}</td>
                ))}
              </tr>
              {comparison.dimensions.map((d) => (
                <tr key={d}>
                  <th scope="row">{DIMENSIONS[d]}</th>
                  {comparison.ideas.map((idea) => (
                    <td key={idea.idea_id}>{idea.dimensions[d] ?? "No score"}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </section>
  );
}
