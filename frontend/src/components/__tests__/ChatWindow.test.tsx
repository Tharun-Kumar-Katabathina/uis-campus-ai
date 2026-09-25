import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import ChatWindow from "../ChatWindow";
import * as api from "../../lib/api";

vi.mock("../../lib/api", () => ({
  ApiError: class ApiError extends Error {},
  sendChatMessage: vi.fn(),
  sendFeedback: vi.fn(),
}));

beforeEach(() => {
  sessionStorage.clear();
  vi.mocked(api.sendChatMessage).mockReset();
  vi.mocked(api.sendFeedback).mockReset();
});

afterEach(() => {
  sessionStorage.clear();
});

describe("ChatWindow", () => {
  it("shows the empty-state prompt when there are no messages", () => {
    render(<ChatWindow token="t" role="student" onSignOut={vi.fn()} />);

    expect(
      screen.getByText(/ask a question about uis academics/i),
    ).toBeInTheDocument();
  });

  it("sends a message and renders the user + assistant bubbles with sources", async () => {
    const user = userEvent.setup();
    vi.mocked(api.sendChatMessage).mockResolvedValue({
      answer: "Fall registration opens July 6 [1].",
      sources: [
        {
          title: "Academic Calendar",
          url: "https://example.edu/cal",
          relevance: 0.9,
        },
      ],
      verified: true,
      intent: "registration",
    });

    render(
      <ChatWindow token="test-token" role="student" onSignOut={vi.fn()} />,
    );

    await user.type(
      screen.getByLabelText(/ask a question/i),
      "When does fall registration open?",
    );
    await user.click(screen.getByRole("button", { name: /send/i }));

    expect(
      await screen.findByText("When does fall registration open?"),
    ).toBeInTheDocument();
    expect(
      await screen.findByText("Fall registration opens July 6 [1]."),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Academic Calendar" }),
    ).toBeInTheDocument();
    expect(api.sendChatMessage).toHaveBeenCalledWith(
      "test-token",
      "When does fall registration open?",
    );
  });

  it("shows an error message when the chat request fails", async () => {
    const user = userEvent.setup();
    vi.mocked(api.sendChatMessage).mockRejectedValue(new api.ApiError("boom"));

    render(<ChatWindow token="t" role="student" onSignOut={vi.fn()} />);

    await user.type(screen.getByLabelText(/ask a question/i), "hello");
    await user.click(screen.getByRole("button", { name: /send/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /something went wrong/i,
    );
  });

  it("submits feedback for the clicked message with its question and answer", async () => {
    const user = userEvent.setup();
    vi.mocked(api.sendChatMessage).mockResolvedValue({
      answer: "Fall registration opens July 6 [1].",
      sources: [],
      verified: true,
      intent: "registration",
    });
    vi.mocked(api.sendFeedback).mockResolvedValue(undefined);

    render(
      <ChatWindow token="test-token" role="student" onSignOut={vi.fn()} />,
    );

    await user.type(
      screen.getByLabelText(/ask a question/i),
      "When does fall registration open?",
    );
    await user.click(screen.getByRole("button", { name: /send/i }));
    await screen.findByText("Fall registration opens July 6 [1].");

    await user.click(screen.getByLabelText("Helpful"));

    expect(api.sendFeedback).toHaveBeenCalledWith("test-token", {
      question: "When does fall registration open?",
      answer: "Fall registration opens July 6 [1].",
      helpful: true,
    });
  });
});
