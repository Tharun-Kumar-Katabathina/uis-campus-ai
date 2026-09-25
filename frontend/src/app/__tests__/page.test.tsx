import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import Home from "../page";
import * as api from "../../lib/api";

vi.mock("../../lib/api", () => ({
  ApiError: class ApiError extends Error {},
  demoLogin: vi.fn(),
  sendChatMessage: vi.fn(),
  sendFeedback: vi.fn(),
}));

beforeEach(() => {
  sessionStorage.clear();
  vi.mocked(api.demoLogin).mockReset();
});

afterEach(() => {
  sessionStorage.clear();
});

describe("Home", () => {
  it("shows the role selector when there is no stored session", async () => {
    render(<Home />);

    expect(
      await screen.findByText(/sign in to try uis campusai/i),
    ).toBeInTheDocument();
  });

  it("signs in and shows the chat window after picking a role", async () => {
    const user = userEvent.setup();
    vi.mocked(api.demoLogin).mockResolvedValue({
      access_token: "abc123",
      role: "faculty",
    });

    render(<Home />);

    await user.click(await screen.findByRole("button", { name: /faculty/i }));

    expect(
      await screen.findByText(/signed in as faculty/i),
    ).toBeInTheDocument();
    expect(api.demoLogin).toHaveBeenCalledWith("faculty");
  });

  it("restores a session already stored in sessionStorage", async () => {
    sessionStorage.setItem(
      "campusai.session",
      JSON.stringify({ role: "admin", token: "stored-token" }),
    );

    render(<Home />);

    expect(await screen.findByText(/signed in as admin/i)).toBeInTheDocument();
  });

  it("returns to the role selector after signing out", async () => {
    const user = userEvent.setup();
    vi.mocked(api.demoLogin).mockResolvedValue({
      access_token: "abc123",
      role: "student",
    });

    render(<Home />);
    await user.click(await screen.findByRole("button", { name: /student/i }));
    await screen.findByText(/signed in as student/i);

    await user.click(screen.getByRole("button", { name: /switch role/i }));

    expect(
      await screen.findByText(/sign in to try uis campusai/i),
    ).toBeInTheDocument();
    expect(sessionStorage.getItem("campusai.session")).toBeNull();
  });
});
