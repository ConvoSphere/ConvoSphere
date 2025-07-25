// File size formatter
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Date formatter
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// Relative time formatter
export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  if (diffInSeconds < 60) {
    return 'just now';
  }
  
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''} ago`;
  }
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
  }
  
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) {
    return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
  }
  
  const diffInWeeks = Math.floor(diffInDays / 7);
  if (diffInWeeks < 4) {
    return `${diffInWeeks} week${diffInWeeks > 1 ? 's' : ''} ago`;
  }
  
  const diffInMonths = Math.floor(diffInDays / 30);
  if (diffInMonths < 12) {
    return `${diffInMonths} month${diffInMonths > 1 ? 's' : ''} ago`;
  }
  
  const diffInYears = Math.floor(diffInDays / 365);
  return `${diffInYears} year${diffInYears > 1 ? 's' : ''} ago`;
}

// Document type formatter
export function formatDocumentType(type: string): string {
  const typeMap: Record<string, string> = {
    'PDF': 'PDF Document',
    'DOCUMENT': 'Word Document',
    'TEXT': 'Text File',
    'SPREADSHEET': 'Spreadsheet',
    'PRESENTATION': 'Presentation',
    'IMAGE': 'Image',
    'AUDIO': 'Audio',
    'VIDEO': 'Video',
    'ARCHIVE': 'Archive',
    'CODE': 'Code File',
    'OTHER': 'Other'
  };
  
  return typeMap[type] || type;
}

// Language formatter
export function formatLanguage(language: string): string {
  const languageMap: Record<string, string> = {
    'en': 'English',
    'de': 'German',
    'fr': 'French',
    'es': 'Spanish',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'nl': 'Dutch',
    'sv': 'Swedish',
    'no': 'Norwegian',
    'da': 'Danish',
    'fi': 'Finnish',
    'pl': 'Polish',
    'tr': 'Turkish',
    'he': 'Hebrew',
    'th': 'Thai',
    'vi': 'Vietnamese',
    'id': 'Indonesian',
    'ms': 'Malay',
    'tl': 'Tagalog',
    'uk': 'Ukrainian',
    'cs': 'Czech',
    'sk': 'Slovak',
    'hu': 'Hungarian',
    'ro': 'Romanian',
    'bg': 'Bulgarian',
    'hr': 'Croatian',
    'sr': 'Serbian',
    'sl': 'Slovenian',
    'et': 'Estonian',
    'lv': 'Latvian',
    'lt': 'Lithuanian',
    'mt': 'Maltese',
    'ga': 'Irish',
    'cy': 'Welsh',
    'eu': 'Basque',
    'ca': 'Catalan',
    'gl': 'Galician',
    'is': 'Icelandic',
    'fo': 'Faroese',
    'sq': 'Albanian',
    'mk': 'Macedonian',
    'bs': 'Bosnian',
    'me': 'Montenegrin',
    'ka': 'Georgian',
    'hy': 'Armenian',
    'az': 'Azerbaijani',
    'kk': 'Kazakh',
    'ky': 'Kyrgyz',
    'uz': 'Uzbek',
    'tk': 'Turkmen',
    'tg': 'Tajik',
    'mn': 'Mongolian',
    'ne': 'Nepali',
    'si': 'Sinhala',
    'my': 'Burmese',
    'km': 'Khmer',
    'lo': 'Lao',
    'am': 'Amharic',
    'sw': 'Swahili',
    'zu': 'Zulu',
    'af': 'Afrikaans',
    'xh': 'Xhosa',
    'yo': 'Yoruba',
    'ig': 'Igbo',
    'ha': 'Hausa',
    'so': 'Somali',
    'om': 'Oromo',
    'ti': 'Tigrinya',
    'sn': 'Shona',
    'st': 'Southern Sotho',
    'tn': 'Tswana',
    'ts': 'Tsonga',
    've': 'Venda',
    'nr': 'Southern Ndebele',
    'ss': 'Swati',
    'nd': 'Northern Ndebele',
    'rw': 'Kinyarwanda',
    'ak': 'Akan',
    'tw': 'Twi',
    'ee': 'Ewe',
    'fon': 'Fon',
    'dyo': 'Jola-Fonyi',
    'kab': 'Kabyle',
    'shi': 'Tachelhit',
    'tzm': 'Central Atlas Tamazight',
    'ber': 'Berber',
    'arq': 'Algerian Arabic',
    'ary': 'Moroccan Arabic',
    'acm': 'Mesopotamian Arabic',
    'afb': 'Gulf Arabic',
    'ajp': 'South Levantine Arabic',
    'apc': 'North Levantine Arabic',
    'ayh': 'Hadrami Arabic',
    'ayl': 'Libyan Arabic',
    'ayn': 'Sanaani Arabic',
    'ayp': 'North Mesopotamian Arabic',
    'bbz': 'Babalia Creole Arabic',
    'pga': 'Sudanese Creole Arabic',
    'shu': 'Chadian Arabic',
    'ssh': 'Shihhi Arabic',
    'yhd': 'Judeo-Iraqi Arabic',
    'yud': 'Judeo-Tripolitanian Arabic',
    'ajt': 'Judeo-Tunisian Arabic',
    'jye': 'Judeo-Yemeni Arabic',
    'aec': 'Saidi Arabic',
    'avl': 'Eastern Egyptian Bedawi Arabic',
    'qaf': 'Qaf',
    'arb': 'Standard Arabic'
  };
  
  return languageMap[language.toLowerCase()] || language;
}

// Status formatter
export function formatStatus(status: string): string {
  const statusMap: Record<string, string> = {
    'UPLOADED': 'Uploaded',
    'PROCESSING': 'Processing',
    'PROCESSED': 'Processed',
    'ERROR': 'Error',
    'REPROCESSING': 'Reprocessing'
  };
  
  return statusMap[status] || status;
}

// Progress formatter
export function formatProgress(progress: number): string {
  return `${Math.round(progress)}%`;
}

// Token count formatter
export function formatTokenCount(tokens: number): string {
  if (tokens < 1000) {
    return tokens.toString();
  } else if (tokens < 1000000) {
    return `${(tokens / 1000).toFixed(1)}K`;
  } else {
    return `${(tokens / 1000000).toFixed(1)}M`;
  }
}

// Search score formatter
export function formatSearchScore(score: number): string {
  return `${(score * 100).toFixed(1)}%`;
}

// File extension formatter
export function getFileExtension(filename: string): string {
  return filename.split('.').pop()?.toLowerCase() || '';
}

// MIME type formatter
export function formatMimeType(mimeType: string): string {
  const typeMap: Record<string, string> = {
    'application/pdf': 'PDF Document',
    'application/msword': 'Word Document',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word Document',
    'application/vnd.ms-excel': 'Excel Spreadsheet',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel Spreadsheet',
    'application/vnd.ms-powerpoint': 'PowerPoint Presentation',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint Presentation',
    'text/plain': 'Text File',
    'text/markdown': 'Markdown File',
    'text/html': 'HTML File',
    'text/css': 'CSS File',
    'text/javascript': 'JavaScript File',
    'application/json': 'JSON File',
    'application/xml': 'XML File',
    'image/jpeg': 'JPEG Image',
    'image/png': 'PNG Image',
    'image/gif': 'GIF Image',
    'image/svg+xml': 'SVG Image',
    'audio/mpeg': 'MP3 Audio',
    'audio/wav': 'WAV Audio',
    'video/mp4': 'MP4 Video',
    'video/avi': 'AVI Video',
    'application/zip': 'ZIP Archive',
    'application/x-rar-compressed': 'RAR Archive',
    'application/x-7z-compressed': '7-Zip Archive'
  };
  
  return typeMap[mimeType] || mimeType;
}