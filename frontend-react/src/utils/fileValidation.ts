import { message } from "antd";

export interface FileValidationConfig {
  maxFileSize: number;
  allowedTypes: string[];
  maxFiles?: number;
  allowedMimeTypes?: string[];
}

export interface FileValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface FileValidationError {
  fileName: string;
  error: string;
}

// MIME type mapping for better validation
const MIME_TYPE_MAP: Record<string, string[]> = {
  pdf: ["application/pdf"],
  doc: ["application/msword"],
  docx: ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
  txt: ["text/plain"],
  md: ["text/markdown", "text/plain"],
  xls: ["application/vnd.ms-excel"],
  xlsx: ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
  ppt: ["application/vnd.ms-powerpoint"],
  pptx: ["application/vnd.openxmlformats-officedocument.presentationml.presentation"],
  jpg: ["image/jpeg"],
  jpeg: ["image/jpeg"],
  png: ["image/png"],
  gif: ["image/gif"],
  mp3: ["audio/mpeg"],
  wav: ["audio/wav"],
  mp4: ["video/mp4"],
  avi: ["video/x-msvideo"],
  zip: ["application/zip"],
  rar: ["application/x-rar-compressed"],
  "7z": ["application/x-7z-compressed"],
};

export class FileValidator {
  private config: FileValidationConfig;

  constructor(config: FileValidationConfig) {
    this.config = config;
  }

  /**
   * Validate a single file
   */
  validateFile(file: File): FileValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Check file size
    if (file.size > this.config.maxFileSize) {
      errors.push(`File size exceeds ${this.formatFileSize(this.config.maxFileSize)}`);
    }

    // Check file type by extension
    const extension = this.getFileExtension(file.name);
    if (!this.config.allowedTypes.includes(extension.toLowerCase())) {
      errors.push(`File type .${extension} is not allowed`);
    }

    // Check MIME type if provided
    if (this.config.allowedMimeTypes && file.type) {
      const allowedMimeTypes = this.config.allowedMimeTypes;
      if (!allowedMimeTypes.includes(file.type)) {
        errors.push(`MIME type ${file.type} is not allowed`);
      }
    }

    // Check for suspicious file names
    if (this.isSuspiciousFileName(file.name)) {
      warnings.push("File name contains potentially suspicious characters");
    }

    // Check for empty files
    if (file.size === 0) {
      errors.push("File is empty");
    }

    // Check for very large files (warning)
    if (file.size > 50 * 1024 * 1024) { // 50MB
      warnings.push("Large file detected - upload may take longer");
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
    };
  }

  /**
   * Validate multiple files
   */
  validateFiles(files: File[]): {
    validFiles: File[];
    invalidFiles: FileValidationError[];
    warnings: string[];
  } {
    const validFiles: File[] = [];
    const invalidFiles: FileValidationError[] = [];
    const warnings: string[] = [];

    // Check max files limit
    if (this.config.maxFiles && files.length > this.config.maxFiles) {
      warnings.push(`Only ${this.config.maxFiles} files can be uploaded at once`);
    }

    files.forEach((file) => {
      const result = this.validateFile(file);
      
      if (result.isValid) {
        validFiles.push(file);
      } else {
        invalidFiles.push({
          fileName: file.name,
          error: result.errors.join(", "),
        });
      }

      warnings.push(...result.warnings);
    });

    return { validFiles, invalidFiles, warnings };
  }

  /**
   * Get file extension from filename
   */
  private getFileExtension(filename: string): string {
    return filename.split(".").pop()?.toLowerCase() || "";
  }

  /**
   * Check for suspicious file names
   */
  private isSuspiciousFileName(filename: string): boolean {
    const suspiciousPatterns = [
      /\.\./, // Directory traversal
      /[<>:"|?*]/, // Invalid characters
      /^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$/i, // Reserved names
      /\.(exe|bat|cmd|com|pif|scr|vbs|js|jar|msi|dmg|app)$/i, // Executable files
    ];

    return suspiciousPatterns.some(pattern => pattern.test(filename));
  }

  /**
   * Format file size for display
   */
  private formatFileSize(bytes: number): string {
    if (bytes === 0) return "0 Bytes";
    
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  }

  /**
   * Get MIME types for file extension
   */
  static getMimeTypesForExtension(extension: string): string[] {
    return MIME_TYPE_MAP[extension.toLowerCase()] || [];
  }

  /**
   * Check if file is an image
   */
  static isImage(file: File): boolean {
    return file.type.startsWith("image/");
  }

  /**
   * Check if file is a document
   */
  static isDocument(file: File): boolean {
    const docTypes = ["application/pdf", "application/msword", 
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                     "text/plain", "text/markdown"];
    return docTypes.includes(file.type);
  }

  /**
   * Check if file is a spreadsheet
   */
  static isSpreadsheet(file: File): boolean {
    const spreadsheetTypes = ["application/vnd.ms-excel",
                             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"];
    return spreadsheetTypes.includes(file.type);
  }
}

/**
 * Default validation configuration
 */
export const DEFAULT_FILE_VALIDATION_CONFIG: FileValidationConfig = {
  maxFileSize: 100 * 1024 * 1024, // 100MB
  allowedTypes: [
    "pdf", "doc", "docx", "txt", "md", 
    "xls", "xlsx", "ppt", "pptx",
    "jpg", "jpeg", "png", "gif",
    "mp3", "wav", "mp4", "avi",
    "zip", "rar", "7z"
  ],
  maxFiles: 10,
  allowedMimeTypes: [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "image/jpeg",
    "image/png",
    "image/gif",
    "audio/mpeg",
    "audio/wav",
    "video/mp4",
    "video/x-msvideo",
    "application/zip",
    "application/x-rar-compressed",
    "application/x-7z-compressed"
  ]
};

/**
 * Create a file validator with default configuration
 */
export const createFileValidator = (config?: Partial<FileValidationConfig>): FileValidator => {
  const finalConfig = { ...DEFAULT_FILE_VALIDATION_CONFIG, ...config };
  return new FileValidator(finalConfig);
};

/**
 * Show validation errors to user
 */
export const showValidationErrors = (errors: FileValidationError[]): void => {
  if (errors.length === 0) return;

  const errorMessages = errors.map(err => `${err.fileName}: ${err.error}`);
  
  if (errors.length === 1) {
    message.error(errorMessages[0]);
  } else {
    message.error(
      <div>
        <div>Multiple files have validation errors:</div>
        <ul style={{ margin: '8px 0 0 0', paddingLeft: '20px' }}>
          {errorMessages.map((msg, index) => (
            <li key={index}>{msg}</li>
          ))}
        </ul>
      </div>
    );
  }
};

/**
 * Show validation warnings to user
 */
export const showValidationWarnings = (warnings: string[]): void => {
  if (warnings.length === 0) return;

  const uniqueWarnings = [...new Set(warnings)];
  
  if (uniqueWarnings.length === 1) {
    message.warning(uniqueWarnings[0]);
  } else {
    message.warning(
      <div>
        <div>Upload warnings:</div>
        <ul style={{ margin: '8px 0 0 0', paddingLeft: '20px' }}>
          {uniqueWarnings.map((warning, index) => (
            <li key={index}>{warning}</li>
          ))}
        </ul>
      </div>
    );
  }
};