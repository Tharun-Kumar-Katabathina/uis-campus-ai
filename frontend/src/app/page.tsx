"use client";

import { useEffect, useState } from "react";
import ChatWindow from "../components/ChatWindow";
import RoleSelector from "../components/RoleSelector";
import { demoLogin } from "../lib/api";
import { clearSession, loadSession, saveSession } from "../lib/storage";
import type { Role } from "../lib/types";

export default function Home() {
  const [session, setSession] = useState<{ role: Role; token: string } | null>(
    null,
  );
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // sessionStorage isn't available during SSR, so this can't be a lazy
    // useState initializer without a hydration mismatch (server renders
    // "signed out", client would render "signed in" on the same pass).
    // Reading it after mount, then rendering nothing until `ready`, keeps
    // the first client render identical to the SSR output.
    const stored = loadSession();
    if (stored) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setSession({ role: stored.role as Role, token: stored.token });
    }
    setReady(true);
  }, []);

  async function handleRoleSelect(role: Role) {
    const { access_token } = await demoLogin(role);
    saveSession({ role, token: access_token });
    setSession({ role, token: access_token });
  }

  function handleSignOut() {
    clearSession();
    setSession(null);
  }

  return (
    <div className="flex flex-1 flex-col items-center bg-zinc-50 font-sans dark:bg-black">
      {!ready ? null : session ? (
        <ChatWindow
          token={session.token}
          role={session.role}
          onSignOut={handleSignOut}
        />
      ) : (
        <div className="flex flex-1 flex-col items-center justify-center px-6">
          <RoleSelector onSelect={handleRoleSelect} />
        </div>
      )}
    </div>
  );
}
