import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import SmartSuggestions from "../SmartSuggestions";

// Mock window.alert, falls verwendet
window.alert = jest.fn();

describe("SmartSuggestions", () => {
  it("renders the card title", () => {
    render(<SmartSuggestions />);
    expect(screen.getByText("Smart Suggestions")).toBeInTheDocument();
  });

  it("renders all suggestions", () => {
    render(<SmartSuggestions />);
    expect(
      screen.getByText("Summarize selected documents"),
    ).toBeInTheDocument();
    expect(screen.getByText("Find related documents")).toBeInTheDocument();
    expect(screen.getByText("Generate questions")).toBeInTheDocument();
  });

  it("calls action on suggestion click", () => {
    render(<SmartSuggestions />);
    const suggestion = screen.getByText("Summarize selected documents");
    fireEvent.click(suggestion);
    expect(window.alert).toHaveBeenCalled();
  });
});
