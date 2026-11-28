import { type SubmitEvent, useEffect, useState } from "react";
import { type ApiError, call, type Profile } from "./account";

const EMPTY = { skills: "", hours_per_week: "", weeks_available: "", team_size: "1", compute: "laptop", goal: "portfolio", interests: "" };
type Fields = typeof EMPTY;

const list = (text: string) =>
  text
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
const shown = (p: Profile): Fields => ({
  skills: p.skills.join(", "),
  hours_per_week: String(p.hours_per_week),
  weeks_available: String(p.weeks_available),
  team_size: String(p.team_size),
  compute: p.compute,
  goal: p.goal,
  interests: p.interests.join(", "),
});

const TEXT = [
  ["skills", "Skills, separated by commas", "text"],
  ["hours_per_week", "Hours per week", "number"],
  ["weeks_available", "Weeks available", "number"],
  ["team_size", "Team size", "number"],
  ["interests", "Interests, separated by commas", "text"],
] as const;
const CHOICES = [
  ["compute", "Computer you can use", { laptop: "Laptop", free_gpu: "Free GPU", paid: "Paid compute" }],
  ["goal", "Goal", { portfolio: "Portfolio", startup: "Startup", course_project: "Course project" }],
] as const;

export function ProfileForm({ token, onSignedOut }: { token: string; onSignedOut: () => void }) {
  const [fields, setFields] = useState<Fields>(EMPTY);
  const [status, setStatus] = useState("Loading your profile...");
  const [error, setError] = useState("");

  function fail(problem: ApiError) {
    if (problem.status === 401) onSignedOut();
    else setError(problem.message);
  }

  // biome-ignore lint/correctness/useExhaustiveDependencies: load once for this token
  useEffect(() => {
    call<Profile>("/profile", { token }).then(
      (profile) => {
        setFields(shown(profile));
        setStatus(`Saved, version ${profile.version}.`);
      },
      (problem: ApiError) => {
        setStatus(problem.status === 404 ? "No profile saved yet." : "");
        if (problem.status !== 404) fail(problem);
      },
    );
  }, [token]);

  function change(name: keyof Fields, value: string) {
    setFields({ ...fields, [name]: value });
    setStatus("Unsaved changes.");
  }

  async function save(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const body: Profile = {
      skills: list(fields.skills),
      hours_per_week: Number(fields.hours_per_week),
      weeks_available: Number(fields.weeks_available),
      team_size: Number(fields.team_size),
      compute: fields.compute as Profile["compute"],
      goal: fields.goal as Profile["goal"],
      interests: list(fields.interests),
    };
    try {
      const saved = await call<Profile>("/profile", { token, method: "PUT", body });
      setFields(shown(saved));
      setStatus(`Saved, version ${saved.version}.`);
    } catch (problem) {
      fail(problem as ApiError);
    }
  }

  return (
    // the API validates; noValidate lets its message be the one shown
    <form onSubmit={save} noValidate>
      <h2>Your profile</h2>
      {status && <p role="status">{status}</p>}
      {TEXT.map(([name, label, kind]) => (
        <div className="field" key={name}>
          <label htmlFor={name}>{label}</label>
          <input id={name} type={kind} value={fields[name]} onChange={(e) => change(name, e.target.value)} />
        </div>
      ))}
      {CHOICES.map(([name, label, options]) => (
        <div className="field" key={name}>
          <label htmlFor={name}>{label}</label>
          <select id={name} value={fields[name]} onChange={(e) => change(name, e.target.value)}>
            {Object.entries(options).map(([value, text]) => (
              <option key={value} value={value}>
                {text}
              </option>
            ))}
          </select>
        </div>
      ))}
      <button type="submit">Save profile</button>
      {error && <p role="alert">{error}</p>}
    </form>
  );
}
