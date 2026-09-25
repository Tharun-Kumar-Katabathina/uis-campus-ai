import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import RoleSelector from "../RoleSelector";

describe("RoleSelector", () => {
  it("renders all four roles", () => {
    render(<RoleSelector onSelect={vi.fn()} />);

    for (const role of ["student", "faculty", "staff", "admin"]) {
      expect(
        screen.getByRole("button", { name: new RegExp(role, "i") }),
      ).toBeInTheDocument();
    }
  });

  it("calls onSelect with the clicked role", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn().mockResolvedValue(undefined);
    render(<RoleSelector onSelect={onSelect} />);

    await user.click(screen.getByRole("button", { name: /staff/i }));

    expect(onSelect).toHaveBeenCalledWith("staff");
  });

  it("shows an error message if onSelect rejects", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn().mockRejectedValue(new Error("network down"));
    render(<RoleSelector onSelect={onSelect} />);

    await user.click(screen.getByRole("button", { name: /student/i }));

    expect(await screen.findByText(/couldn't sign in/i)).toBeInTheDocument();
  });
});
