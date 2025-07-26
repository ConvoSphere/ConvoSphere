import React from "react";
import { render, screen } from "@testing-library/react";
import { Form, Input } from "antd";

describe("Antd Minimal Form", () => {
  test("renders a simple Form.Item with Input", () => {
    render(
      <Form>
        <Form.Item name="foo" label="Foo">
          <Input aria-label="Foo" />
        </Form.Item>
      </Form>,
    );
    expect(screen.getByLabelText(/foo/i)).toBeInTheDocument();
  });
});
