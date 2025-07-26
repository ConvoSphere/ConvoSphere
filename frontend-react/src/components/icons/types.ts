/**
 * Icon System Types
 *
 * This file contains all type definitions for the icon system.
 */

import React from "react";

// Icon name types - organized by category
export type NavigationIconName =
  | "dashboard"
  | "home"
  | "menu"
  | "bars"
  | "more"
  | "ellipsis";

export type ActionIconName =
  | "plus"
  | "edit"
  | "delete"
  | "save"
  | "close"
  | "check"
  | "send"
  | "download"
  | "upload"
  | "eye"
  | "eyeInvisible"
  | "lock"
  | "unlock"
  | "reload"
  | "sync"
  | "redo"
  | "undo"
  | "rollback"
  | "forward"
  | "backward"
  | "play"
  | "pause"
  | "stop"
  | "stepForward"
  | "stepBackward"
  | "fastForward"
  | "fastBackward"
  | "shrink"
  | "arrowsAlt"
  | "fullscreen"
  | "fullscreenExit"
  | "zoomIn"
  | "zoomOut"
  | "compress"
  | "expand"
  | "swap"
  | "swapLeft"
  | "swapRight"
  | "sortAscending"
  | "sortDescending"
  | "filter"
  | "funnelPlot"
  | "orderedList"
  | "unorderedList"
  | "copy"
  | "scissor"
  | "printer"
  | "link"
  | "share"
  | "like"
  | "dislike"
  | "star"
  | "heart"
  | "fire"
  | "thunderbolt"
  | "bulb";

export type CommunicationIconName =
  | "message"
  | "mail"
  | "phone"
  | "user"
  | "userAdd"
  | "team"
  | "logout"
  | "login"
  | "key";

export type MediaIconName =
  | "camera"
  | "video"
  | "audio"
  | "picture"
  | "file"
  | "folder"
  | "cloud";

export type SystemIconName =
  | "setting"
  | "tool"
  | "appstore"
  | "api"
  | "database"
  | "wifi"
  | "signal"
  | "poweroff"
  | "global"
  | "translation"
  | "environment"
  | "calendar"
  | "clock";

export type DataIconName =
  | "barchart"
  | "table"
  | "border"
  | "borderInner"
  | "borderOuter"
  | "borderTop"
  | "borderBottom"
  | "borderLeft"
  | "borderRight"
  | "borderVerticle"
  | "borderHorizontal"
  | "radiusUpleft"
  | "radiusUpright"
  | "radiusBottomleft"
  | "radiusBottomright";

export type FeedbackIconName =
  | "exclamation"
  | "info"
  | "warning"
  | "checkCircle"
  | "loading"
  | "search"
  | "bell"
  | "robot";

export type TextFormatIconName =
  | "bold"
  | "italic"
  | "underline"
  | "strikethrough"
  | "fontSize"
  | "fontColors"
  | "highlight"
  | "alignLeft"
  | "alignCenter"
  | "alignRight"
  | "verticalAlignTop"
  | "verticalAlignMiddle"
  | "verticalAlignBottom";

// Combined icon name type
export type IconName =
  | NavigationIconName
  | ActionIconName
  | CommunicationIconName
  | MediaIconName
  | SystemIconName
  | DataIconName
  | FeedbackIconName
  | TextFormatIconName;

// Icon size options
export type IconSize = "xs" | "sm" | "md" | "lg" | "xl";

// Icon variant options
export type IconVariant =
  | "primary"
  | "secondary"
  | "accent"
  | "success"
  | "warning"
  | "error"
  | "info"
  | "muted";

// Main icon component props
export interface IconProps {
  name: IconName;
  size?: IconSize;
  variant?: IconVariant;
  className?: string;
  style?: React.CSSProperties;
  onClick?: () => void;
}

// Icon mapping interface
export interface IconMapping {
  [key: string]: React.ComponentType<any>;
}
