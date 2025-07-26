import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import TagCloud from "../TagCloud";
import { Tag as TagType } from "../../../services/knowledge";

describe("TagCloud", () => {
  const tags: TagType[] = [
    {
      id: "1",
      name: "Tag1",
      color: "#1890ff",
      usage_count: 10,
      is_system: false,
      description: "",
      created_at: "",
    },
    {
      id: "2",
      name: "Tag2",
      color: "#ff0000",
      usage_count: 5,
      is_system: true,
      description: "",
      created_at: "",
    },
  ];

  it("renders all tags", () => {
    render(<TagCloud tags={tags} />);
    expect(screen.getByText("Tag1 (10)")).toBeInTheDocument();
    expect(screen.getByText("Tag2 (5)")).toBeInTheDocument();
  });

  it("calls onTagSelect when a tag is clicked", () => {
    const onTagSelect = jest.fn();
    render(<TagCloud tags={tags} onTagSelect={onTagSelect} />);
    fireEvent.click(screen.getByText("Tag1 (10)"));
    expect(onTagSelect).toHaveBeenCalledWith(tags[0]);
  });
});
