import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import MessageBubble from "../MessageBubble";
import type { ChatMessage } from "../../lib/types";

describe("MessageBubble", () => {
  it("renders a user message without sources or feedback controls", () => {
    const message: ChatMessage = {
      id: "1",
      role: "user",
      content: "When does fall start?",
    };
    render(<MessageBubble message={message} />);

    expect(screen.getByText("When does fall start?")).toBeInTheDocument();
    expect(screen.queryByText("Sources")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Helpful")).not.toBeInTheDocument();
  });

  it("renders assistant sources as links", () => {
    const message: ChatMessage = {
      id: "2",
      role: "assistant",
      content: "Fall registration opens July 6 [1].",
      sources: [
        {
          title: "Academic Calendar",
          url: "https://example.edu/cal",
          relevance: 0.9,
        },
      ],
    };
    render(<MessageBubble message={message} />);

    const link = screen.getByRole("link", { name: "Academic Calendar" });
    expect(link).toHaveAttribute("href", "https://example.edu/cal");
  });

  it("calls onFeedback with the message id and helpful=true when thumbs up is clicked", async () => {
    const user = userEvent.setup();
    const onFeedback = vi.fn();
    const message: ChatMessage = {
      id: "3",
      role: "assistant",
      content: "Answer.",
      feedback: null,
    };
    render(<MessageBubble message={message} onFeedback={onFeedback} />);

    await user.click(screen.getByLabelText("Helpful"));

    expect(onFeedback).toHaveBeenCalledWith("3", true);
  });

  it("disables both feedback buttons once feedback has been given", () => {
    const message: ChatMessage = {
      id: "4",
      role: "assistant",
      content: "Answer.",
      feedback: "up",
    };
    render(<MessageBubble message={message} onFeedback={vi.fn()} />);

    expect(screen.getByLabelText("Helpful")).toBeDisabled();
    expect(screen.getByLabelText("Not helpful")).toBeDisabled();
  });
});
