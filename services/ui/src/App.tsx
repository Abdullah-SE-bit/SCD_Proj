import { type SubmitEvent, useState } from "react";
import { checkIdea, type Run } from "./api";
import { History } from "./History";
import { ProfileForm } from "./ProfileForm";
import { SignIn } from "./SignIn";
import { VerdictCard } from "./VerdictCard";

type State = { step: "empty" } | { step: "loading" } | { step: "error"; message: string } | { step: "done"; run: Run };

const TABS = ["Check an idea", "Profile", "History"] as const;

export function App() {
  const [tab, setTab] = useState<(typeof TABS)[number]>(TABS[0]);
  // kept for this browser tab only; the API ends it after a few hours
  const [token, setToken] = useState(() => sessionStorage.getItem("token") ?? "");
  const [notice, setNotice] = useState("");

  function keep(value: string, message = "") {
    if (value) sessionStorage.setItem("token", value);
    else sessionStorage.removeItem("token");
    setToken(value);
    setNotice(message);
  }

  return (
    <main>
      <nav aria-label="Pages">
        {TABS.map((name) => (
          <button type="button" key={name} aria-current={tab === name ? "page" : undefined} onClick={() => setTab(name)}>
            {name}
          </button>
        ))}
        {token && (
          <button type="button" onClick={() => keep("")}>
            Sign out
          </button>
        )}
      </nav>
      <div hidden={tab !== TABS[0]}>
        <CheckIdea />
      </div>
      {tab !== TABS[0] && !token && <SignIn notice={notice} onToken={keep} />}
      {tab === "Profile" && token && <ProfileForm token={token} onSignedOut={() => keep("", "Your sign-in ended. Sign in again.")} />}
      {tab === "History" && token && <History token={token} onSignedOut={() => keep("", "Your sign-in ended. Sign in again.")} />}
    </main>
  );
}

function CheckIdea() {
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
    <>
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
      {state.step === "done" && <VerdictCard verdict={state.run.verdict} label={state.run.label} />}
    </>
  );
}
