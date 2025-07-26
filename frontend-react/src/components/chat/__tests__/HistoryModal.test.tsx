import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import HistoryModal from "../HistoryModal";

describe("HistoryModal", () => {
  it("renders empty history message", () => {
    render(
      <HistoryModal open={true} conversationHistory={[]} onClose={jest.fn()} />,
    );
    expect(
      screen.getByText("No conversation history available"),
    ).toBeInTheDocument();
  });

  it("renders conversation history items", () => {
    const history = [
      { timestamp: "2023-01-01", content: "Hello" },
      { timestamp: "2023-01-02", content: "World" },
    ];
    render(
      <HistoryModal
        open={true}
        conversationHistory={history}
        onClose={jest.fn()}
      />,
    );
    expect(screen.getByText("Message 1")).toBeInTheDocument();
    expect(screen.getByText("Message 2")).toBeInTheDocument();
    expect(screen.getByText("Hello")).toBeInTheDocument();
    expect(screen.getByText("World")).toBeInTheDocument();
  });

  it("calls onClose when Close button is clicked", () => {
    const onClose = jest.fn();
    render(
      <HistoryModal open={true} conversationHistory={[]} onClose={onClose} />,
    );
    fireEvent.click(screen.getByText("Close"));
    expect(onClose).toHaveBeenCalled();
  });
});
