import React, { useRef } from "react";
import { useDrop } from "react-dnd";
import { useTranslation } from "react-i18next";
import { useThemeStore } from "../../store/themeStore";
import type { WidgetConfig } from "../widgets/WidgetBase";
import DraggableWidget from "./DraggableWidget";

interface DroppableGridProps {
  widgets: WidgetConfig[];
  onWidgetMove: (
    widgetId: string,
    newPosition: { x: number; y: number },
  ) => void;
  onWidgetResize: (
    widgetId: string,
    newSize: { width: number; height: number },
  ) => void;
  editMode: boolean;
  renderWidget: (widget: WidgetConfig) => React.ReactNode;
}

const DroppableGrid: React.FC<DroppableGridProps> = ({
  widgets,
  onWidgetMove,
  onWidgetResize,
  editMode,
  renderWidget,
}) => {
  const { t } = useTranslation();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  const gridRef = useRef<HTMLDivElement>(null);

  const [{ isOver }, drop] = useDrop({
    accept: "WIDGET",
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
    drop: (item: { id: string }, monitor) => {
      if (!monitor.didDrop()) {
        // Widget was dropped on the grid, not on another widget
        const gridRect = gridRef.current?.getBoundingClientRect();
        const dropOffset = monitor.getClientOffset();

        if (gridRect && dropOffset) {
          const x = Math.floor((dropOffset.x - gridRect.left) / 50); // 50px grid size
          const y = Math.floor((dropOffset.y - gridRect.top) / 50);
          onWidgetMove(item.id, { x, y });
        }
      }
    },
  });

  const gridStyle: React.CSSProperties = {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
    gap: 24,
    padding: "0 0 24px 0",
    minHeight: "400px",
    position: "relative",
    ...(editMode && {
      backgroundImage: `
        linear-gradient(${colors.colorBorder} 1px, transparent 1px),
        linear-gradient(90deg, ${colors.colorBorder} 1px, transparent 1px)
      `,
      backgroundSize: "50px 50px",
    }),
    ...(isOver &&
      editMode && {
        backgroundColor: `${colors.colorPrimary}05`,
        border: `2px dashed ${colors.colorPrimary}`,
        borderRadius: "8px",
      }),
  };

  const renderGridCell = (widget: WidgetConfig) => {
    const position = widget.position || { x: 0, y: 0 };

    return (
      <div
        key={widget.id}
        style={{
          gridColumn: `span ${widget.size === "full" ? 2 : 1}`,
          gridRow: `span ${widget.size === "full" ? 2 : 1}`,
          display: "flex",
          justifyContent: "center",
          alignItems: "flex-start",
        }}
      >
        <DraggableWidget
          widget={widget}
          onMove={onWidgetMove}
          onResize={onWidgetResize}
          editMode={editMode}
          position={position}
        >
          {renderWidget(widget)}
        </DraggableWidget>
      </div>
    );
  };

  if (widgets.length === 0) {
    return (
      <div
        ref={(node) => {
          drop(node);
          if (gridRef.current !== node) {
            gridRef.current = node;
          }
        }}
        style={{
          ...gridStyle,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "400px",
          border: editMode ? `2px dashed ${colors.colorBorder}` : "none",
          borderRadius: "8px",
        }}
      >
        <div style={{ textAlign: "center", color: colors.colorTextSecondary }}>
          {editMode
            ? t("dashboard.drop_widgets_here")
            : t("dashboard.no_widgets")}
        </div>
      </div>
    );
  }

  return (
    <div
      ref={(node) => {
        drop(node);
        if (gridRef.current !== node) {
          gridRef.current = node;
        }
      }}
      style={gridStyle}
    >
      {widgets.map(renderGridCell)}
    </div>
  );
};

export default DroppableGrid;
