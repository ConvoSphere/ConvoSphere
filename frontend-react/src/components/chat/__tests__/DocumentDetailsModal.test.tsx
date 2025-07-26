import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import DocumentDetailsModal from "../DocumentDetailsModal";
import { Document } from "../../../services/knowledge";

describe("DocumentDetailsModal", () => {
  const document: Document = {
    id: "1",
    title: "Doc 1",
    document_type: "pdf",
    file_size: 1234,
    created_at: "2023-01-01",
    tags: [{ id: "t1", name: "Tag1" }],
    language: "en",
    file_name: "doc1.pdf",
    description: "desc",
    author: "author",
    year: 2023,
    page_count: 1,
    keywords: ["kw1"],
    mime_type: "application/pdf",
    status: "processed",
    chunk_count: 1,
    total_tokens: 100,
    processed_at: "2023-01-02",
    source: "src",
  };

  it("renders document details", () => {
    render(
      <DocumentDetailsModal
        open={true}
        document={document}
        onClose={jest.fn()}
        onUse={jest.fn()}
      />,
    );
    expect(screen.getByText("Doc 1")).toBeInTheDocument();
    expect(screen.getByText("doc1.pdf")).toBeInTheDocument();
    expect(screen.getByText("Tag1")).toBeInTheDocument();
    expect(screen.getByText("Use in Chat")).toBeInTheDocument();
  });

  it("calls onClose when Close button is clicked", () => {
    const onClose = jest.fn();
    render(
      <DocumentDetailsModal
        open={true}
        document={document}
        onClose={onClose}
        onUse={jest.fn()}
      />,
    );
    fireEvent.click(screen.getByText("Close"));
    expect(onClose).toHaveBeenCalled();
  });

  it("calls onUse when Use in Chat button is clicked", () => {
    const onUse = jest.fn();
    render(
      <DocumentDetailsModal
        open={true}
        document={document}
        onClose={jest.fn()}
        onUse={onUse}
      />,
    );
    fireEvent.click(screen.getByText("Use in Chat"));
    expect(onUse).toHaveBeenCalledWith(document);
  });
});
