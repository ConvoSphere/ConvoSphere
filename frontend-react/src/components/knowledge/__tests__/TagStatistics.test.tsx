import React from "react";
import { render, screen } from "@testing-library/react";
import TagStatistics from "../TagStatistics";

describe("TagStatistics", () => {
  it("renders all statistics with correct values", () => {
    render(
      <TagStatistics
        totalTags={10}
        systemTags={3}
        userTags={7}
        totalUsage={42}
      />,
    );
    expect(screen.getByText("Total Tags")).toBeInTheDocument();
    expect(screen.getByText("System Tags")).toBeInTheDocument();
    expect(screen.getByText("User Tags")).toBeInTheDocument();
    expect(screen.getByText("Total Usage")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("7")).toBeInTheDocument();
    expect(screen.getByText("42")).toBeInTheDocument();
  });
});
