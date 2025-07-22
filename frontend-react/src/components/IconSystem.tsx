import React from 'react';
import { useThemeStore } from '../store/themeStore';
import {
  DashboardOutlined,
  MessageOutlined,
  TeamOutlined,
  BookOutlined,
  ToolOutlined,
  SettingOutlined,
  UserOutlined,
  AppstoreOutlined,
  ApiOutlined,
  BarChartOutlined,
  RobotOutlined,
  BellOutlined,
  SearchOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SaveOutlined,
  CloseOutlined,
  CheckOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  LoadingOutlined,
  SendOutlined,
  DownloadOutlined,
  UploadOutlined,
  EyeOutlined,
  EyeInvisibleOutlined,
  LockOutlined,
  UnlockOutlined,
  HomeOutlined,
  LogoutOutlined,
  LoginOutlined,
  UserAddOutlined,
  KeyOutlined,
  MailOutlined,
  PhoneOutlined,
  CalendarOutlined,
  ClockCircleOutlined,
  EnvironmentOutlined,
  GlobalOutlined,
  TranslationOutlined,
  BulbOutlined,
  ThunderboltOutlined,
  FireOutlined,
  HeartOutlined,
  StarOutlined,
  LikeOutlined,
  DislikeOutlined,
  ShareAltOutlined,
  LinkOutlined,
  CopyOutlined,
  ScissorOutlined,
  PrinterOutlined,
  CameraOutlined,
  VideoCameraOutlined,
  AudioOutlined,
  PictureOutlined,
  FileOutlined,
  FolderOutlined,
  CloudOutlined,
  DatabaseOutlined,
  WifiOutlined,
  SignalFilled,
  PoweroffOutlined,
  ReloadOutlined,
  SyncOutlined,
  RedoOutlined,
  UndoOutlined,
  RollbackOutlined,
  ForwardOutlined,
  BackwardOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  StopOutlined,
  StepForwardOutlined,
  StepBackwardOutlined,
  FastForwardOutlined,
  FastBackwardOutlined,
  ShrinkOutlined,
  ArrowsAltOutlined,
  FullscreenOutlined,
  FullscreenExitOutlined,
  ZoomInOutlined,
  ZoomOutOutlined,
  CompressOutlined,
  ExpandOutlined,
  SwapOutlined,
  SwapLeftOutlined,
  SwapRightOutlined,
  SortAscendingOutlined,
  SortDescendingOutlined,
  FilterOutlined,
  FunnelPlotOutlined,
  OrderedListOutlined,
  UnorderedListOutlined,
  BarsOutlined,
  MenuOutlined,
  MoreOutlined,
  EllipsisOutlined,
  VerticalAlignTopOutlined,
  VerticalAlignMiddleOutlined,
  VerticalAlignBottomOutlined,
  AlignLeftOutlined,
  AlignCenterOutlined,
  AlignRightOutlined,
  BoldOutlined,
  ItalicOutlined,
  UnderlineOutlined,
  StrikethroughOutlined,
  FontSizeOutlined,
  FontColorsOutlined,
  HighlightOutlined,
  TableOutlined,
  BorderOutlined,
  BorderInnerOutlined,
  BorderOuterOutlined,
  BorderTopOutlined,
  BorderBottomOutlined,
  BorderLeftOutlined,
  BorderRightOutlined,
  BorderVerticleOutlined,
  BorderHorizontalOutlined,
  RadiusUpleftOutlined,
  RadiusUprightOutlined,
  RadiusBottomleftOutlined,
  RadiusBottomrightOutlined,
} from '@ant-design/icons';

export type IconName = 
  | 'dashboard' | 'message' | 'team' | 'book' | 'tool' | 'setting' | 'user' | 'appstore'
  | 'api' | 'barchart' | 'robot' | 'bell' | 'search' | 'plus' | 'edit' | 'delete'
  | 'save' | 'close' | 'check' | 'exclamation' | 'info' | 'warning' | 'checkCircle'
  | 'loading' | 'send' | 'download' | 'upload' | 'eye' | 'eyeInvisible' | 'lock'
  | 'unlock' | 'home' | 'logout' | 'login' | 'userAdd' | 'key' | 'mail' | 'phone'
  | 'calendar' | 'clock' | 'environment' | 'global' | 'translation' | 'bulb'
  | 'thunderbolt' | 'fire' | 'heart' | 'star' | 'like' | 'dislike' | 'share'
  | 'link' | 'copy' | 'scissor' | 'printer' | 'camera' | 'video' | 'audio'
  | 'picture' | 'file' | 'folder' | 'cloud' | 'database' | 'wifi'
  | 'signal' | 'poweroff' | 'reload' | 'sync' | 'redo' | 'undo'
  | 'rollback' | 'forward' | 'backward' | 'play' | 'pause' | 'stop' | 'stepForward'
  | 'stepBackward' | 'fastForward' | 'fastBackward' | 'shrink' | 'arrowsAlt'
  | 'fullscreen' | 'fullscreenExit' | 'zoomIn' | 'zoomOut' | 'compress' | 'expand'
  | 'swap' | 'swapLeft' | 'swapRight' | 'sortAscending' | 'sortDescending'
  | 'filter' | 'funnelPlot' | 'orderedList' | 'unorderedList' | 'bars' | 'menu'
  | 'more' | 'ellipsis' | 'verticalAlignTop' | 'verticalAlignMiddle' | 'verticalAlignBottom'
  | 'alignLeft' | 'alignCenter' | 'alignRight' | 'bold' | 'italic' | 'underline'
  | 'strikethrough' | 'fontSize' | 'fontColors' | 'highlight' | 'table' | 'border'
  | 'borderInner' | 'borderOuter' | 'borderTop' | 'borderBottom' | 'borderLeft'
  | 'borderRight' | 'borderVerticle' | 'borderHorizontal' | 'radiusUpleft'
  | 'radiusUpright' | 'radiusBottomleft' | 'radiusBottomright';

export type IconSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';
export type IconVariant = 'primary' | 'secondary' | 'accent' | 'success' | 'warning' | 'error' | 'info' | 'muted';

interface IconProps {
  name: IconName;
  size?: IconSize;
  variant?: IconVariant;
  className?: string;
  style?: React.CSSProperties;
  onClick?: () => void;
}

const iconMap = {
  dashboard: DashboardOutlined,
  message: MessageOutlined,
  team: TeamOutlined,
  book: BookOutlined,
  tool: ToolOutlined,
  setting: SettingOutlined,
  user: UserOutlined,
  appstore: AppstoreOutlined,
  api: ApiOutlined,
  barchart: BarChartOutlined,
  robot: RobotOutlined,
  bell: BellOutlined,
  search: SearchOutlined,
  plus: PlusOutlined,
  edit: EditOutlined,
  delete: DeleteOutlined,
  save: SaveOutlined,
  close: CloseOutlined,
  check: CheckOutlined,
  exclamation: ExclamationCircleOutlined,
  info: InfoCircleOutlined,
  warning: WarningOutlined,
  checkCircle: CheckCircleOutlined,
  loading: LoadingOutlined,
  send: SendOutlined,
  download: DownloadOutlined,
  upload: UploadOutlined,
  eye: EyeOutlined,
  eyeInvisible: EyeInvisibleOutlined,
  lock: LockOutlined,
  unlock: UnlockOutlined,
  home: HomeOutlined,
  logout: LogoutOutlined,
  login: LoginOutlined,
  userAdd: UserAddOutlined,
  key: KeyOutlined,
  mail: MailOutlined,
  phone: PhoneOutlined,
  calendar: CalendarOutlined,
  clock: ClockCircleOutlined,
  environment: EnvironmentOutlined,
  global: GlobalOutlined,
  translation: TranslationOutlined,
  bulb: BulbOutlined,
  thunderbolt: ThunderboltOutlined,
  fire: FireOutlined,
  heart: HeartOutlined,
  star: StarOutlined,
  like: LikeOutlined,
  dislike: DislikeOutlined,
  share: ShareAltOutlined,
  link: LinkOutlined,
  copy: CopyOutlined,
  scissor: ScissorOutlined,
  printer: PrinterOutlined,
  camera: CameraOutlined,
  video: VideoCameraOutlined,
  audio: AudioOutlined,
  picture: PictureOutlined,
  file: FileOutlined,
  folder: FolderOutlined,
  cloud: CloudOutlined,
  database: DatabaseOutlined,
  wifi: WifiOutlined,
  signal: SignalFilled,
  poweroff: PoweroffOutlined,
  reload: ReloadOutlined,
  sync: SyncOutlined,
  redo: RedoOutlined,
  undo: UndoOutlined,
  rollback: RollbackOutlined,
  forward: ForwardOutlined,
  backward: BackwardOutlined,
  play: PlayCircleOutlined,
  pause: PauseCircleOutlined,
  stop: StopOutlined,
  stepForward: StepForwardOutlined,
  stepBackward: StepBackwardOutlined,
  fastForward: FastForwardOutlined,
  fastBackward: FastBackwardOutlined,
  shrink: ShrinkOutlined,
  arrowsAlt: ArrowsAltOutlined,
  fullscreen: FullscreenOutlined,
  fullscreenExit: FullscreenExitOutlined,
  zoomIn: ZoomInOutlined,
  zoomOut: ZoomOutOutlined,
  compress: CompressOutlined,
  expand: ExpandOutlined,
  swap: SwapOutlined,
  swapLeft: SwapLeftOutlined,
  swapRight: SwapRightOutlined,
  sortAscending: SortAscendingOutlined,
  sortDescending: SortDescendingOutlined,
  filter: FilterOutlined,
  funnelPlot: FunnelPlotOutlined,
  orderedList: OrderedListOutlined,
  unorderedList: UnorderedListOutlined,
  bars: BarsOutlined,
  menu: MenuOutlined,
  more: MoreOutlined,
  ellipsis: EllipsisOutlined,
  verticalAlignTop: VerticalAlignTopOutlined,
  verticalAlignMiddle: VerticalAlignMiddleOutlined,
  verticalAlignBottom: VerticalAlignBottomOutlined,
  alignLeft: AlignLeftOutlined,
  alignCenter: AlignCenterOutlined,
  alignRight: AlignRightOutlined,
  bold: BoldOutlined,
  italic: ItalicOutlined,
  underline: UnderlineOutlined,
  strikethrough: StrikethroughOutlined,
  fontSize: FontSizeOutlined,
  fontColors: FontColorsOutlined,
  highlight: HighlightOutlined,
  table: TableOutlined,
  border: BorderOutlined,
  borderInner: BorderInnerOutlined,
  borderOuter: BorderOuterOutlined,
  borderTop: BorderTopOutlined,
  borderBottom: BorderBottomOutlined,
  borderLeft: BorderLeftOutlined,
  borderRight: BorderRightOutlined,
  borderVerticle: BorderVerticleOutlined,
  borderHorizontal: BorderHorizontalOutlined,
  radiusUpleft: RadiusUpleftOutlined,
  radiusUpright: RadiusUprightOutlined,
  radiusBottomleft: RadiusBottomleftOutlined,
  radiusBottomright: RadiusBottomrightOutlined,
};

const sizeMap = {
  xs: 12,
  sm: 16,
  md: 20,
  lg: 24,
  xl: 32,
};

const Icon: React.FC<IconProps> = ({ 
  name, 
  size = 'md', 
  variant = 'primary',
  className = '',
  style = {},
  onClick 
}) => {
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  
  const IconComponent = iconMap[name];
  
  if (!IconComponent) {
    console.warn(`Icon "${name}" not found`);
    return null;
  }

  const getVariantColor = () => {
    switch (variant) {
      case 'primary':
        return colors.colorPrimary;
      case 'secondary':
        return colors.colorSecondary;
      case 'accent':
        return colors.colorAccent;
      case 'success':
        return colors.colorSuccess;
      case 'warning':
        return colors.colorWarning;
      case 'error':
        return colors.colorError;
      case 'info':
        return colors.colorInfo;
      case 'muted':
        return colors.colorTextSecondary;
      default:
        return colors.colorPrimary;
    }
  };

  const iconStyle: React.CSSProperties = {
    fontSize: sizeMap[size],
    color: getVariantColor(),
    cursor: onClick ? 'pointer' : 'default',
    transition: 'all var(--transition-duration) var(--transition-timing)',
    ...style,
  };

  const handleClick = () => {
    if (onClick) {
      onClick();
    }
  };

  return (
    <IconComponent
      style={iconStyle}
      className={`icon icon-${name} icon-${size} icon-${variant} ${className}`}
      onClick={handleClick}
    />
  );
};

export default Icon;