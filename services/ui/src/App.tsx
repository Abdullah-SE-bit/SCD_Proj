import { type SubmitEvent, useState } from "react";
import { checkIdea, type Run } from "./api";

type State = { step: "empty" } | { step: "loading" } | { step: "error"; message: string } | { step: "done"; run: Run };

export function App() {
  const [idea, setIdea] = useState("");
  const [state, setState] = useState<State>({ step: "empty" });

  async function submit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    setState({ step: "loading" });
    try {
      setState({ step: "done", run: await checkIdea(idea) });
    } catch (error) {
      setState({ step: "error", message: (error as Error).message });
    }
  }

  return (
    <main>
      <h1>Check a project idea</h1>
      <form onSubmit={submit}>
        <label htmlFor="idea">Your project idea</label>
        <textarea id="idea" rows={4} maxLength={2000} value={idea} onChange={(e) => setIdea(e.target.value)} />
        <button type="submit" disabled={!idea.trim() || state.step === "loading"}>
          Check this idea
        </button>
      </form>
      {state.step === "empty" && <p>No result yet.</p>}
      {state.step === "loading" && <p role="status">Checking your idea...</p>}
      {state.step === "error" && <p role="alert">{state.message} Try again.</p>}
      {state.step === "done" && (
        <section aria-label="Result">
          {state.run.label && <p className="fixture">{state.run.label}</p>}
          <p>Verdict: {state.run.verdict.verdict}</p>
        </section>
      )}
    </main>
  );
}
