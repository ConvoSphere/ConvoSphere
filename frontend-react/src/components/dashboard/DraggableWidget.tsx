import React, { useRef } from "react";
import { useDrag, useDrop } from "react-dnd";
import { ResizableBox } from "react-resizable";
import { DragOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useThemeStore } from "../../store/themeStore";
import type { WidgetConfig } from "../widgets/WidgetBase";

interface DraggableWidgetProps {
  widget: WidgetConfig;
  children: React.ReactNode;
  onMove: (widgetId: string, newPosition: { x: number; y: number }) => void;
  onResize: (widgetId: string, newSize: { width: number; height: number }) => void;
  editMode: boolean;
  position: { x: number; y: number };
}

const DraggableWidget: React.FC<DraggableWidgetProps> = ({
  widget,
  children,
  onMove,
  onResize,
  editMode,
  position,
}) => {
  const { t } = useTranslation();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  const ref = useRef<HTMLDivElement>(null);

  const [{ isDragging }, drag] = useDrag({
    type: "WIDGET",
    item: { id: widget.id, type: widget.type },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
    canDrag: editMode,
  });

  const [{ isOver }, drop] = useDrop({
    accept: "WIDGET",
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
    drop: (item: { id: string }) => {
      if (item.id !== widget.id) {
        // Handle widget reordering if needed
        console.log("Widget dropped:", item.id, "onto:", widget.id);
      }
    },
  });

  const handleResize = (event: any, { size }: { size: { width: number; height: number } }) => {
    onResize(widget.id, size);
  };

  const getSizeStyles = () => {
    switch (widget.size) {
      case "small":
        return { width: 250, height: 200 };
      case "medium":
        return { width: 400, height: 300 };
      case "large":
        return { width: 600, height: 400 };
      case "full":
        return { width: "100%", height: 500 };
      default:
        return { width: 400, height: 300 };
    }
  };

  const sizeStyles = getSizeStyles();

  const widgetStyle: React.CSSProperties = {
    position: "relative",
    opacity: isDragging ? 0.5 : 1,
    cursor: editMode ? "move" : "default",
    border: editMode ? `2px dashed ${colors.colorPrimary}` : "none",
    borderRadius: "8px",
    transition: "all 0.3s ease",
    ...(isOver && editMode && {
      border: `2px solid ${colors.colorPrimary}`,
      backgroundColor: `${colors.colorPrimary}10`,
    }),
  };

  const dragHandleStyle: React.CSSProperties = {
    position: "absolute",
    top: "8px",
    right: "8px",
    zIndex: 1000,
    backgroundColor: colors.colorPrimary,
    color: "#FFFFFF",
    borderRadius: "4px",
    padding: "4px",
    cursor: "move",
    opacity: editMode ? 1 : 0,
    transition: "opacity 0.3s ease",
  };

  return (
    <div
      ref={(node) => {
        drag(drop(node));
        if (ref.current !== node) {
          ref.current = node;
        }
      }}
      style={widgetStyle}
      data-widget-id={widget.id}
    >
      {editMode && (
        <div style={dragHandleStyle}>
          <DragOutlined />
        </div>
      )}
      
      <ResizableBox
        width={sizeStyles.width}
        height={sizeStyles.height}
        onResize={handleResize}
        minConstraints={[200, 150]}
        maxConstraints={[800, 600]}
        resizeHandles={editMode ? ["se"] : []}
        handle={<div style={{ display: editMode ? "block" : "none" }} />}
      >
        <div style={{ width: "100%", height: "100%" }}>
          {children}
        </div>
      </ResizableBox>
    </div>
  );
};

export default DraggableWidget;