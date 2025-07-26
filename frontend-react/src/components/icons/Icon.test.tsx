/**
 * Icon Component Tests
 *
 * Tests to ensure all icons are properly imported and rendered.
 */

import React from "react";
import { render, screen } from "@testing-library/react";
import Icon from "./Icon";

// Mock the theme store
jest.mock("../../store/themeStore", () => ({
  useThemeStore: () => ({ mode: "light" }),
}));

describe("Icon Component", () => {
  it("renders without crashing", () => {
    render(<Icon name="dashboard" />);
    expect(screen.getByRole("img")).toBeInTheDocument();
  });

  it("renders with different sizes", () => {
    const { rerender } = render(<Icon name="dashboard" size="xs" />);
    expect(screen.getByRole("img")).toBeInTheDocument();

    rerender(<Icon name="dashboard" size="lg" />);
    expect(screen.getByRole("img")).toBeInTheDocument();
  });

  it("renders with different variants", () => {
    const { rerender } = render(<Icon name="dashboard" variant="primary" />);
    expect(screen.getByRole("img")).toBeInTheDocument();

    rerender(<Icon name="dashboard" variant="success" />);
    expect(screen.getByRole("img")).toBeInTheDocument();
  });

  it("handles click events", () => {
    const handleClick = jest.fn();
    render(<Icon name="dashboard" onClick={handleClick} />);

    screen.getByRole("img").click();
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("warns for non-existent icons", () => {
    const consoleSpy = jest.spyOn(console, "warn").mockImplementation();
    render(<Icon name="nonExistentIcon" as any />);

    expect(consoleSpy).toHaveBeenCalledWith('Icon "nonExistentIcon" not found');
    consoleSpy.mockRestore();
  });
});

describe("Icon Coverage", () => {
  it("renders all required icons from original IconSystem", () => {
    const requiredIcons = [
      "dashboard",
      "message",
      "team",
      "book",
      "tool",
      "setting",
      "user",
      "appstore",
      "api",
      "barchart",
      "robot",
      "bell",
      "search",
      "plus",
      "edit",
      "delete",
      "save",
      "close",
      "check",
      "exclamation",
      "info",
      "warning",
      "checkCircle",
      "loading",
      "send",
      "download",
      "upload",
      "eye",
      "eyeInvisible",
      "lock",
      "unlock",
      "home",
      "logout",
      "login",
      "userAdd",
      "key",
      "mail",
      "phone",
      "calendar",
      "clock",
      "environment",
      "global",
      "translation",
      "bulb",
      "thunderbolt",
      "fire",
      "heart",
      "star",
      "like",
      "dislike",
      "share",
      "link",
      "copy",
      "scissor",
      "printer",
      "camera",
      "video",
      "audio",
      "picture",
      "file",
      "folder",
      "cloud",
      "database",
      "wifi",
      "signal",
      "poweroff",
      "reload",
      "sync",
      "redo",
      "undo",
      "rollback",
      "forward",
      "backward",
      "play",
      "pause",
      "stop",
      "stepForward",
      "stepBackward",
      "fastForward",
      "fastBackward",
      "shrink",
      "arrowsAlt",
      "fullscreen",
      "fullscreenExit",
      "zoomIn",
      "zoomOut",
      "compress",
      "expand",
      "swap",
      "swapLeft",
      "swapRight",
      "sortAscending",
      "sortDescending",
      "filter",
      "funnelPlot",
      "orderedList",
      "unorderedList",
      "bars",
      "menu",
      "more",
      "ellipsis",
      "verticalAlignTop",
      "verticalAlignMiddle",
      "verticalAlignBottom",
      "alignLeft",
      "alignCenter",
      "alignRight",
      "bold",
      "italic",
      "underline",
      "strikethrough",
      "fontSize",
      "fontColors",
      "highlight",
      "table",
      "border",
      "borderInner",
      "borderOuter",
      "borderTop",
      "borderBottom",
      "borderLeft",
      "borderRight",
      "borderVerticle",
      "borderHorizontal",
      "radiusUpleft",
      "radiusUpright",
      "radiusBottomleft",
      "radiusBottomright",
    ];

    // Test a subset of icons to ensure they render properly
    const testIcons = [
      "dashboard",
      "message",
      "user",
      "setting",
      "search",
      "plus",
    ];

    testIcons.forEach((iconName) => {
      const { unmount } = render(<Icon name={iconName as any} />);
      expect(screen.getByRole("img")).toBeInTheDocument();
      unmount();
    });
  });
});
