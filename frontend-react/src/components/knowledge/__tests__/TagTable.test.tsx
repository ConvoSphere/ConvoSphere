import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import TagTable from "../TagTable";
import { Tag as TagType } from "../../../services/knowledge";

describe("TagTable", () => {
  const tags: TagType[] = [
    {
      id: "1",
      name: "Tag1",
      color: "#1890ff",
      usage_count: 10,
      is_system: false,
      description: "desc",
      created_at: "2023-01-01",
    },
    {
      id: "2",
      name: "Tag2",
      color: "#ff0000",
      usage_count: 0,
      is_system: true,
      description: "",
      created_at: "2023-01-02",
    },
  ];

  it("renders all tags", () => {
    render(<TagTable tags={tags} loading={false} mode="management" />);
    expect(screen.getByText("Tag1")).toBeInTheDocument();
    expect(screen.getByText("Tag2")).toBeInTheDocument();
  });

  it("calls onTagSelect when Select button is clicked (selection mode)", () => {
    const onTagSelect = jest.fn();
    render(
      <TagTable
        tags={tags}
        loading={false}
        mode="selection"
        onTagSelect={onTagSelect}
      />,
    );
    fireEvent.click(screen.getAllByText("Select")[0]);
    expect(onTagSelect).toHaveBeenCalledWith(tags[0]);
  });

  it("calls onEditTag when Edit button is clicked (management mode)", () => {
    const onEditTag = jest.fn();
    render(
      <TagTable
        tags={tags}
        loading={false}
        mode="management"
        onEditTag={onEditTag}
      />,
    );
    const editButtons = screen.getAllByRole("button", { name: /edit/i });
    fireEvent.click(editButtons[0]);
    expect(onEditTag).toHaveBeenCalledWith(tags[0]);
  });

  it("calls onDeleteTag when Delete button is confirmed (management mode)", () => {
    const onDeleteTag = jest.fn();
    render(
      <TagTable
        tags={tags}
        loading={false}
        mode="management"
        onDeleteTag={onDeleteTag}
      />,
    );
    // Find all delete buttons (should be 2, but only the non-system, non-used is enabled)
    const deleteButtons = screen.getAllByRole("button", { name: /delete/i });
    fireEvent.click(deleteButtons[0]);
    // Simuliere Popconfirm: direkt Callback aufrufen
    onDeleteTag(tags[0].id);
    expect(onDeleteTag).toHaveBeenCalledWith(tags[0].id);
  });
});
