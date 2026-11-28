import { type SubmitEvent, useState } from "react";
import { call } from "./account";

export function SignIn({ notice, onToken }: { notice?: string; onToken: (token: string) => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function enter(create: boolean) {
    setBusy(true);
    setError("");
    try {
      const body = { email, password };
      if (create) await call("/auth/register", { method: "POST", body });
      onToken((await call<{ token: string }>("/auth/login", { method: "POST", body })).token);
    } catch (problem) {
      setError((problem as Error).message);
      setBusy(false);
    }
  }

  function submit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    enter(false);
  }

  return (
    <form onSubmit={submit}>
      <h2>Sign in</h2>
      {notice && <p>{notice}</p>}
      <label htmlFor="email">Email</label>
      <input id="email" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
      <label htmlFor="password">Password</label>
      <input
        id="password"
        type="password"
        autoComplete="current-password"
        required
        minLength={8}
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <div className="actions">
        <button type="submit" disabled={busy || !email || !password}>
          Sign in
        </button>
        <button type="button" className="secondary" disabled={busy || !email || password.length < 8} onClick={() => enter(true)}>
          Create account
        </button>
      </div>
      {error && <p role="alert">{error}</p>}
    </form>
  );
}
