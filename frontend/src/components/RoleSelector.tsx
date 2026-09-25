"use client";

import { useState } from "react";
import type { Role } from "../lib/types";

const ROLES: Role[] = ["student", "faculty", "staff", "admin"];

interface RoleSelectorProps {
  onSelect: (role: Role) => Promise<void>;
}

export default function RoleSelector({ onSelect }: RoleSelectorProps) {
  const [loadingRole, setLoadingRole] = useState<Role | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSelect(role: Role) {
    setLoadingRole(role);
    setError(null);
    try {
      await onSelect(role);
    } catch {
      setError("Couldn't sign in. Is the backend running?");
    } finally {
      setLoadingRole(null);
    }
  }

  return (
    <div className="flex flex-col items-center gap-4 text-center">
      <h2 className="text-lg font-medium text-black dark:text-zinc-50">
        Sign in to try UIS CampusAI
      </h2>
      <p className="max-w-sm text-sm text-zinc-600 dark:text-zinc-400">
        No account needed — pick a role to see how retrieval changes with access
        level.
      </p>
      <div className="flex flex-wrap justify-center gap-2">
        {ROLES.map((role) => (
          <button
            key={role}
            type="button"
            onClick={() => handleSelect(role)}
            disabled={loadingRole !== null}
            className="rounded-full border border-black/[.08] px-5 py-2 text-sm font-medium capitalize transition-colors hover:bg-black/[.04] disabled:opacity-50 dark:border-white/[.145] dark:hover:bg-[#1a1a1a]"
          >
            {loadingRole === role ? "Signing in…" : role}
          </button>
        ))}
      </div>
      {error && (
        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
      )}
    </div>
  );
}
