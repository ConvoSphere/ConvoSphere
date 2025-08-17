import React, { useMemo, useRef } from "react";
import { useDrop } from "react-dnd";
import { useTranslation } from "react-i18next";
import { useThemeStore } from "../../store/themeStore";
import type { WidgetConfig } from "../widgets/WidgetBase";
import DraggableWidget from "./DraggableWidget";

interface GridPosition {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

interface DroppableGridProps {
  widgets: WidgetConfig[];
  layout: GridPosition[];
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
  layout,
  onWidgetMove,
  onWidgetResize,
  editMode,
  renderWidget,
}) => {
  const { t } = useTranslation();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  const gridRef = useRef<HTMLDivElement>(null);

  const layoutById = useMemo(() => {
    const map = new Map<string, GridPosition>();
    layout.forEach((p) => map.set(p.id, p));
    return map;
  }, [layout]);

  const [{ isOver }, drop] = useDrop({
    accept: "WIDGET",
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
    drop: (item: { id: string }, monitor) => {
      if (!monitor.didDrop()) {
        const gridRect = gridRef.current?.getBoundingClientRect();
        const dropOffset = monitor.getClientOffset();
        if (gridRect && dropOffset) {
          const cellSize = 50;
          const x = Math.max(1, Math.floor((dropOffset.x - gridRect.left) / cellSize));
          const y = Math.max(1, Math.floor((dropOffset.y - gridRect.top) / cellSize));
          onWidgetMove(item.id, { x, y });
        }
      }
    },
  });

  const gridStyle: React.CSSProperties = {
    display: "grid",
    gridTemplateColumns: `repeat(24, 1fr)`,
    gridAutoRows: "50px",
    gap: 12,
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
    const pos = layoutById.get(widget.id) || { id: widget.id, x: 1, y: 1, width: 6, height: 6 };
    return (
      <div
        key={widget.id}
        style={{
          gridColumn: `${pos.x} / span ${pos.width}`,
          gridRow: `${pos.y} / span ${pos.height}`,
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
          position={{ x: pos.x, y: pos.y }}
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
          {editMode ? t("dashboard.drop_widgets_here") : t("dashboard.no_widgets")}
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
