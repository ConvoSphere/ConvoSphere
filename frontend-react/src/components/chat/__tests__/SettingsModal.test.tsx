import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import SettingsModal from "../SettingsModal";

describe("SettingsModal", () => {
  it("renders modal with settings info", () => {
    render(<SettingsModal open={true} onClose={jest.fn()} />);
    expect(screen.getByText("Chat Settings")).toBeInTheDocument();
    expect(screen.getByText("Knowledge Base Integration:")).toBeInTheDocument();
    expect(screen.getByText("Auto-Search:")).toBeInTheDocument();
    expect(screen.getByText("Context Management:")).toBeInTheDocument();
  });

  it("calls onClose when Close button is clicked", () => {
    const onClose = jest.fn();
    render(<SettingsModal open={true} onClose={onClose} />);
    fireEvent.click(screen.getByText("Close"));
    expect(onClose).toHaveBeenCalled();
  });
});
