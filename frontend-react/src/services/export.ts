import type { ChatMessage } from "./chat";
import type { ChatExportOptions } from "../components/chat/ChatExport";
import * as XLSX from 'xlsx';
import PptxGenJS from 'pptxgenjs';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import html2pdf from 'html2pdf.js';

// Extended export options interface
export interface ExtendedChatExportOptions extends ChatExportOptions {
  format: "json" | "pdf" | "markdown" | "txt" | "csv" | "excel" | "powerpoint" | "html";
  template?: "default" | "professional" | "minimal" | "detailed" | "custom";
  excelOptions?: {
    includeCharts?: boolean;
    multipleSheets?: boolean;
    autoFilter?: boolean;
    freezeHeader?: boolean;
  };
  powerpointOptions?: {
    includeCharts?: boolean;
    slideLayout?: "title-content" | "two-column" | "timeline" | "summary";
    theme?: "default" | "modern" | "corporate" | "creative";
  };
  pdfOptions?: {
    pageSize?: "A4" | "Letter" | "Legal" | "A3";
    orientation?: "portrait" | "landscape";
    margins?: { top: number; right: number; bottom: number; left: number };
    header?: boolean;
    footer?: boolean;
    pageNumbers?: boolean;
  };
}

class ExportService {
  async exportChat(
    messages: ChatMessage[],
    options: ExtendedChatExportOptions,
    conversationTitle?: string
  ): Promise<void> {
    const filteredMessages = this.filterMessages(messages, options.messageFilter);
    
    switch (options.format) {
      case "json":
        return this.exportAsJSON(filteredMessages, options, conversationTitle);
      case "pdf":
        return this.exportAsPDF(filteredMessages, options, conversationTitle);
      case "markdown":
        return this.exportAsMarkdown(filteredMessages, options, conversationTitle);
      case "txt":
        return this.exportAsText(filteredMessages, options, conversationTitle);
      case "csv":
        return this.exportAsCSV(filteredMessages, options, conversationTitle);
      case "excel":
        return this.exportAsExcel(filteredMessages, options, conversationTitle);
      case "powerpoint":
        return this.exportAsPowerPoint(filteredMessages, options, conversationTitle);
      case "html":
        return this.exportAsHTML(filteredMessages, options, conversationTitle);
      default:
        throw new Error(`Unsupported export format: ${options.format}`);
    }
  }

  private filterMessages(
    messages: ChatMessage[],
    filter?: "all" | "user" | "assistant"
  ): ChatMessage[] {
    if (!filter || filter === "all") {
      return messages;
    }
    
    return messages.filter(message => message.role === filter);
  }

  // Excel Export with advanced features
  private async exportAsExcel(
    messages: ChatMessage[],
    options: ExtendedChatExportOptions,
    conversationTitle?: string
  ): Promise<void> {
    const workbook = XLSX.utils.book_new();
    
    // Main conversation sheet
    const mainData = messages.map((message, index) => ({
      'Message #': index + 1,
      'Role': message.role === 'user' ? '👤 User' : '🤖 Assistant',
      'Content': message.content,
      'Timestamp': options.includeTimestamps ? new Date(message.timestamp).toLocaleString() : '',
      'Metadata': options.includeMetadata ? JSON.stringify(message.metadata || {}) : '',
    }));

    const mainSheet = XLSX.utils.json_to_sheet(mainData);
    
    // Apply styling and formatting
    if (options.excelOptions?.freezeHeader) {
      mainSheet['!freeze'] = { rows: 1, cols: 0 };
    }
    
    if (options.excelOptions?.autoFilter) {
      mainSheet['!autofilter'] = { ref: `A1:E${mainData.length}` };
    }

    // Set column widths
    mainSheet['!cols'] = [
      { width: 10 }, // Message #
      { width: 15 }, // Role
      { width: 80 }, // Content
      { width: 20 }, // Timestamp
      { width: 30 }, // Metadata
    ];

    XLSX.utils.book_append_sheet(workbook, mainSheet, 'Conversation');

    // Summary sheet
    if (options.excelOptions?.multipleSheets) {
      const summaryData = [
        { 'Metric': 'Total Messages', 'Value': messages.length },
        { 'Metric': 'User Messages', 'Value': messages.filter(m => m.role === 'user').length },
        { 'Metric': 'Assistant Messages', 'Value': messages.filter(m => m.role === 'assistant').length },
        { 'Metric': 'Export Date', 'Value': new Date().toLocaleString() },
        { 'Metric': 'Conversation Title', 'Value': conversationTitle || 'Untitled' },
      ];

      const summarySheet = XLSX.utils.json_to_sheet(summaryData);
      summarySheet['!cols'] = [{ width: 20 }, { width: 15 }];
      XLSX.utils.book_append_sheet(workbook, summarySheet, 'Summary');
    }

    // Statistics sheet with charts data
    if (options.excelOptions?.includeCharts) {
      const statsData = [
        { 'Role': 'User', 'Count': messages.filter(m => m.role === 'user').length },
        { 'Role': 'Assistant', 'Count': messages.filter(m => m.role === 'assistant').length },
      ];

      const statsSheet = XLSX.utils.json_to_sheet(statsData);
      statsSheet['!cols'] = [{ width: 15 }, { width: 10 }];
      XLSX.utils.book_append_sheet(workbook, statsSheet, 'Statistics');
    }

    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    this.downloadFile(blob, `${conversationTitle || "chat"}_export.xlsx`);
  }

  // PowerPoint Export with themes and layouts
  private async exportAsPowerPoint(
    messages: ChatMessage[],
    options: ExtendedChatExportOptions,
    conversationTitle?: string
  ): Promise<void> {
    const pptx = new PptxGenJS();
    
    // Set presentation properties
    pptx.author = 'Convosphere';
    pptx.company = 'Convosphere';
    pptx.title = conversationTitle || 'Chat Export';
    pptx.subject = 'Conversation Export';
    
    // Apply theme
    const theme = options.powerpointOptions?.theme || 'default';
    this.applyPowerPointTheme(pptx, theme);

    // Title slide
    const titleSlide = pptx.addSlide();
    titleSlide.addText(conversationTitle || 'Chat Export', {
      x: 1, y: 1, w: 8, h: 1.5,
      fontSize: 32,
      bold: true,
      align: 'center',
      color: '363636'
    });
    
    titleSlide.addText(`Exported on ${new Date().toLocaleString()}`, {
      x: 1, y: 2.5, w: 8, h: 0.5,
      fontSize: 14,
      align: 'center',
      color: '666666'
    });

    // Summary slide
    const summarySlide = pptx.addSlide();
    summarySlide.addText('Conversation Summary', {
      x: 0.5, y: 0.5, w: 9, h: 0.8,
      fontSize: 24,
      bold: true,
      color: '363636'
    });

    const summaryData = [
      { label: 'Total Messages', value: messages.length.toString() },
      { label: 'User Messages', value: messages.filter(m => m.role === 'user').length.toString() },
      { label: 'Assistant Messages', value: messages.filter(m => m.role === 'assistant').length.toString() },
    ];

    summaryData.forEach((item, index) => {
      summarySlide.addText(item.label, {
        x: 0.5, y: 1.5 + index * 0.8, w: 4, h: 0.6,
        fontSize: 16,
        bold: true,
        color: '363636'
      });
      
      summarySlide.addText(item.value, {
        x: 5, y: 1.5 + index * 0.8, w: 4, h: 0.6,
        fontSize: 16,
        color: '666666'
      });
    });

    // Message slides based on layout
    const layout = options.powerpointOptions?.slideLayout || 'title-content';
    const messagesPerSlide = layout === 'two-column' ? 2 : 1;

    for (let i = 0; i < messages.length; i += messagesPerSlide) {
      const slideMessages = messages.slice(i, i + messagesPerSlide);
      const slide = pptx.addSlide();
      
      this.addMessageSlide(slide, slideMessages, layout, i + 1, messages.length);
    }

    // Save the presentation
    const pptxBuffer = await pptx.write('arraybuffer');
    const blob = new Blob([pptxBuffer], { type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation' });
    this.downloadFile(blob, `${conversationTitle || "chat"}_export.pptx`);
  }

  // Enhanced PDF Export with jsPDF
  private async exportAsPDF(
    messages: ChatMessage[],
    options: ExtendedChatExportOptions,
    conversationTitle?: string
  ): Promise<void> {
    const pdfOptions = options.pdfOptions || {};
    const pageSize = pdfOptions.pageSize || 'A4';
    const orientation = pdfOptions.orientation || 'portrait';
    
    const pdf = new jsPDF({
      orientation: orientation as 'portrait' | 'landscape',
      unit: 'mm',
      format: pageSize as 'a4' | 'letter' | 'legal' | 'a3'
    });

    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const margin = pdfOptions.margins || { top: 20, right: 20, bottom: 20, left: 20 };
    
    let yPosition = margin.top;

    // Header
    if (pdfOptions.header) {
      pdf.setFontSize(20);
      pdf.setFont('helvetica', 'bold');
      pdf.text(conversationTitle || 'Chat Export', pageWidth / 2, yPosition, { align: 'center' });
      yPosition += 15;
      
      pdf.setFontSize(12);
      pdf.setFont('helvetica', 'normal');
      pdf.text(`Exported on ${new Date().toLocaleString()}`, pageWidth / 2, yPosition, { align: 'center' });
      yPosition += 20;
    }

    // Messages
    pdf.setFontSize(12);
    pdf.setFont('helvetica', 'normal');
    
    messages.forEach((message, index) => {
      const role = message.role === 'user' ? '👤 User' : '🤖 Assistant';
      const timestamp = options.includeTimestamps ? ` [${new Date(message.timestamp).toLocaleString()}]` : '';
      
      // Check if we need a new page
      if (yPosition > pageHeight - margin.bottom - 30) {
        if (pdfOptions.pageNumbers) {
          this.addPageNumber(pdf, pageWidth, pageHeight);
        }
        pdf.addPage();
        yPosition = margin.top;
      }

      // Role and timestamp
      pdf.setFont('helvetica', 'bold');
      pdf.setFontSize(11);
      pdf.text(`${role}${timestamp}`, margin.left, yPosition);
      yPosition += 8;

      // Message content
      pdf.setFont('helvetica', 'normal');
      pdf.setFontSize(10);
      
      const lines = pdf.splitTextToSize(message.content, pageWidth - margin.left - margin.right);
      lines.forEach(line => {
        if (yPosition > pageHeight - margin.bottom - 20) {
          if (pdfOptions.pageNumbers) {
            this.addPageNumber(pdf, pageWidth, pageHeight);
          }
          pdf.addPage();
          yPosition = margin.top;
        }
        pdf.text(line, margin.left, yPosition);
        yPosition += 6;
      });

      yPosition += 10;

      // Metadata
      if (options.includeMetadata && message.metadata) {
        pdf.setFontSize(8);
        pdf.setTextColor(100, 100, 100);
        const metadataText = `Metadata: ${JSON.stringify(message.metadata)}`;
        const metadataLines = pdf.splitTextToSize(metadataText, pageWidth - margin.left - margin.right);
        metadataLines.forEach(line => {
          if (yPosition > pageHeight - margin.bottom - 15) {
            if (pdfOptions.pageNumbers) {
              this.addPageNumber(pdf, pageWidth, pageHeight);
            }
            pdf.addPage();
            yPosition = margin.top;
          }
          pdf.text(line, margin.left, yPosition);
          yPosition += 4;
        });
        pdf.setTextColor(0, 0, 0);
        yPosition += 5;
      }
    });

    // Footer
    if (pdfOptions.footer) {
      this.addFooter(pdf, pageWidth, pageHeight, margin, messages.length);
    }

    // Page numbers
    if (pdfOptions.pageNumbers) {
      this.addPageNumber(pdf, pageWidth, pageHeight);
    }

    const pdfBlob = pdf.output('blob');
    this.downloadFile(pdfBlob, `${conversationTitle || "chat"}_export.pdf`);
  }

  // HTML Export with custom templates
  private async exportAsHTML(
    messages: ChatMessage[],
    options: ExtendedChatExportOptions,
    conversationTitle?: string
  ): Promise<void> {
    const template = options.template || 'default';
    const htmlContent = this.generateHTMLContentWithTemplate(messages, options, conversationTitle, template);
    
    const blob = new Blob([htmlContent], { type: 'text/html' });
    this.downloadFile(blob, `${conversationTitle || "chat"}_export.html`);
  }

  // Helper methods for PowerPoint
  private applyPowerPointTheme(pptx: PptxGenJS, theme: string): void {
    switch (theme) {
      case 'modern':
        pptx.defineLayout({ name: 'MODERN', width: 13.33, height: 7.5 });
        pptx.layout = 'MODERN';
        break;
      case 'corporate':
        pptx.defineLayout({ name: 'CORPORATE', width: 13.33, height: 7.5 });
        pptx.layout = 'CORPORATE';
        break;
      case 'creative':
        pptx.defineLayout({ name: 'CREATIVE', width: 13.33, height: 7.5 });
        pptx.layout = 'CREATIVE';
        break;
      default:
        // Use default theme
        break;
    }
  }

  private addMessageSlide(slide: any, messages: ChatMessage[], layout: string, currentIndex: number, totalMessages: number): void {
    const layoutConfig = {
      'title-content': this.addTitleContentLayout,
      'two-column': this.addTwoColumnLayout,
      'timeline': this.addTimelineLayout,
      'summary': this.addSummaryLayout
    };

    const layoutFunction = layoutConfig[layout as keyof typeof layoutConfig] || this.addTitleContentLayout;
    layoutFunction.call(this, slide, messages, currentIndex, totalMessages);
  }

  private addTitleContentLayout(slide: any, messages: ChatMessage[], currentIndex: number, totalMessages: number): void {
    const message = messages[0];
    const role = message.role === 'user' ? '👤 User' : '🤖 Assistant';
    
    slide.addText(`${role} - Message ${currentIndex}`, {
      x: 0.5, y: 0.5, w: 9, h: 0.8,
      fontSize: 18,
      bold: true,
      color: '363636'
    });

    slide.addText(message.content, {
      x: 0.5, y: 1.5, w: 9, h: 5,
      fontSize: 14,
      color: '666666',
      wrap: true
    });

    slide.addText(`Page ${Math.ceil(currentIndex / 1)} of ${Math.ceil(totalMessages / 1)}`, {
      x: 0.5, y: 6.8, w: 9, h: 0.5,
      fontSize: 10,
      color: '999999',
      align: 'right'
    });
  }

  private addTwoColumnLayout(slide: any, messages: ChatMessage[], currentIndex: number, totalMessages: number): void {
    messages.forEach((message, index) => {
      const role = message.role === 'user' ? '👤 User' : '🤖 Assistant';
      const x = index === 0 ? 0.5 : 5;
      
      slide.addText(`${role}`, {
        x: x, y: 0.5, w: 4, h: 0.5,
        fontSize: 14,
        bold: true,
        color: '363636'
      });

      slide.addText(message.content, {
        x: x, y: 1.2, w: 4, h: 5.5,
        fontSize: 12,
        color: '666666',
        wrap: true
      });
    });

    slide.addText(`Page ${Math.ceil(currentIndex / 2)} of ${Math.ceil(totalMessages / 2)}`, {
      x: 0.5, y: 6.8, w: 9, h: 0.5,
      fontSize: 10,
      color: '999999',
      align: 'right'
    });
  }

  private addTimelineLayout(slide: any, messages: ChatMessage[], currentIndex: number, totalMessages: number): void {
    const message = messages[0];
    const role = message.role === 'user' ? '👤 User' : '🤖 Assistant';
    
    slide.addText(`Timeline - Message ${currentIndex}`, {
      x: 0.5, y: 0.5, w: 9, h: 0.8,
      fontSize: 18,
      bold: true,
      color: '363636'
    });

    slide.addText(`${role}`, {
      x: 0.5, y: 1.5, w: 2, h: 0.5,
      fontSize: 14,
      bold: true,
      color: '363636'
    });

    slide.addText(message.content, {
      x: 2.5, y: 1.5, w: 7, h: 5,
      fontSize: 14,
      color: '666666',
      wrap: true
    });
  }

  private addSummaryLayout(slide: any, messages: ChatMessage[], currentIndex: number, totalMessages: number): void {
    slide.addText('Message Summary', {
      x: 0.5, y: 0.5, w: 9, h: 0.8,
      fontSize: 18,
      bold: true,
      color: '363636'
    });

    messages.forEach((message, index) => {
      const role = message.role === 'user' ? '👤 User' : '🤖 Assistant';
      const y = 1.5 + index * 1.2;
      
      slide.addText(`${role}:`, {
        x: 0.5, y: y, w: 2, h: 0.5,
        fontSize: 12,
        bold: true,
        color: '363636'
      });

      slide.addText(message.content.substring(0, 100) + (message.content.length > 100 ? '...' : ''), {
        x: 2.5, y: y, w: 7, h: 0.5,
        fontSize: 12,
        color: '666666'
      });
    });
  }

  // Helper methods for PDF
  private addPageNumber(pdf: jsPDF, pageWidth: number, pageHeight: number): void {
    const pageCount = pdf.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      pdf.setPage(i);
      pdf.setFontSize(10);
      pdf.setTextColor(100, 100, 100);
      pdf.text(`Page ${i} of ${pageCount}`, pageWidth / 2, pageHeight - 10, { align: 'center' });
      pdf.setTextColor(0, 0, 0);
    }
  }

  private addFooter(pdf: jsPDF, pageWidth: number, pageHeight: number, margin: any, messageCount: number): void {
    const footerText = `Convosphere Chat Export | ${messageCount} messages | ${new Date().toLocaleString()}`;
    pdf.setFontSize(8);
    pdf.setTextColor(100, 100, 100);
    pdf.text(footerText, pageWidth / 2, pageHeight - 5, { align: 'center' });
    pdf.setTextColor(0, 0, 0);
  }

  // HTML Template generation
  private generateHTMLContentWithTemplate(
    messages: ChatMessage[],
    options: ExtendedChatExportOptions,
    conversationTitle?: string,
    template: string = 'default'
  ): string {
    const templateConfig = {
      default: this.getDefaultHTMLTemplate,
      professional: this.getProfessionalHTMLTemplate,
      minimal: this.getMinimalHTMLTemplate,
      detailed: this.getDetailedHTMLTemplate,
      custom: this.getCustomHTMLTemplate
    };

    const templateFunction = templateConfig[template as keyof typeof templateConfig] || this.getDefaultHTMLTemplate;
    return templateFunction.call(this, messages, options, conversationTitle);
  }

  private getDefaultHTMLTemplate(messages: ChatMessage[], options: ExtendedChatExportOptions, conversationTitle?: string): string {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>${conversationTitle || "Chat Export"}</title>
        <style>
          body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5;
            line-height: 1.6;
          }
          .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
          }
          .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
          }
          .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
          }
          .header .meta {
            margin-top: 10px;
            opacity: 0.9;
            font-size: 0.9em;
          }
          .content {
            padding: 30px;
          }
          .message {
            margin-bottom: 25px;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid;
            position: relative;
          }
          .message.user {
            background-color: #e3f2fd;
            border-left-color: #2196f3;
          }
          .message.assistant {
            background-color: #f3e5f5;
            border-left-color: #9c27b0;
          }
          .message-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
          }
          .role {
            font-weight: 600;
            font-size: 1.1em;
          }
          .timestamp {
            font-size: 0.8em;
            color: #666;
          }
          .message-content {
            font-size: 1em;
            line-height: 1.6;
          }
          .metadata {
            margin-top: 10px;
            padding: 10px;
            background-color: rgba(0, 0, 0, 0.05);
            border-radius: 6px;
            font-size: 0.8em;
            color: #666;
          }
          @media print {
            body { background: white; }
            .container { box-shadow: none; }
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>${conversationTitle || "Chat Export"}</h1>
            <div class="meta">
              Exported on ${new Date().toLocaleString()} | ${messages.length} messages
            </div>
          </div>
          <div class="content">
            ${messages.map((message, index) => {
              const timestamp = options.includeTimestamps 
                ? `<div class="timestamp">${new Date(message.timestamp).toLocaleString()}</div>` 
                : "";
              
              const metadata = options.includeMetadata && message.metadata
                ? `<div class="metadata">Metadata: ${JSON.stringify(message.metadata)}</div>`
                : "";
              
              return `
                <div class="message ${message.role}">
                  <div class="message-header">
                    <div class="role">${message.role === "user" ? "👤 User" : "🤖 Assistant"}</div>
                    ${timestamp}
                  </div>
                  <div class="message-content">${message.content}</div>
                  ${metadata}
                </div>
              `;
            }).join('')}
          </div>
        </div>
      </body>
      </html>
    `;
  }

  private getProfessionalHTMLTemplate(messages: ChatMessage[], options: ExtendedChatExportOptions, conversationTitle?: string): string {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>${conversationTitle || "Chat Export"}</title>
        <style>
          body { 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
            margin: 0; 
            padding: 0;
            background-color: #fafafa;
            line-height: 1.7;
          }
          .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            min-height: 100vh;
          }
          .header {
            background: #1a1a1a;
            color: white;
            padding: 40px 30px;
            border-bottom: 1px solid #e0e0e0;
          }
          .header h1 {
            margin: 0;
            font-size: 2.2em;
            font-weight: 600;
            letter-spacing: -0.02em;
          }
          .header .meta {
            margin-top: 15px;
            opacity: 0.8;
            font-size: 0.95em;
            display: flex;
            gap: 20px;
          }
          .content {
            padding: 40px 30px;
          }
          .message {
            margin-bottom: 30px;
            padding: 25px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            background: white;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          }
          .message.user {
            border-left: 4px solid #2563eb;
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
          }
          .message.assistant {
            border-left: 4px solid #7c3aed;
            background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
          }
          .message-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
          }
          .role {
            font-weight: 600;
            font-size: 1.1em;
            color: #1f2937;
          }
          .timestamp {
            font-size: 0.85em;
            color: #6b7280;
            font-weight: 500;
          }
          .message-content {
            font-size: 1em;
            line-height: 1.7;
            color: #374151;
          }
          .metadata {
            margin-top: 15px;
            padding: 12px;
            background-color: #f9fafb;
            border-radius: 6px;
            font-size: 0.85em;
            color: #6b7280;
            border-left: 3px solid #d1d5db;
          }
          @media print {
            body { background: white; }
            .container { box-shadow: none; }
            .message { break-inside: avoid; }
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>${conversationTitle || "Chat Export"}</h1>
            <div class="meta">
              <span>📅 ${new Date().toLocaleDateString()}</span>
              <span>🕒 ${new Date().toLocaleTimeString()}</span>
              <span>💬 ${messages.length} messages</span>
            </div>
          </div>
          <div class="content">
            ${messages.map((message, index) => {
              const timestamp = options.includeTimestamps 
                ? `<div class="timestamp">${new Date(message.timestamp).toLocaleString()}</div>` 
                : "";
              
              const metadata = options.includeMetadata && message.metadata
                ? `<div class="metadata">📋 Metadata: ${JSON.stringify(message.metadata)}</div>`
                : "";
              
              return `
                <div class="message ${message.role}">
                  <div class="message-header">
                    <div class="role">${message.role === "user" ? "👤 User" : "🤖 Assistant"}</div>
                    ${timestamp}
                  </div>
                  <div class="message-content">${message.content}</div>
                  ${metadata}
                </div>
              `;
            }).join('')}
          </div>
        </div>
      </body>
      </html>
    `;
  }

  private getMinimalHTMLTemplate(messages: ChatMessage[], options: ExtendedChatExportOptions, conversationTitle?: string): string {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>${conversationTitle || "Chat Export"}</title>
        <style>
          body { 
            font-family: -apple-system, BlinkMacSystemFont, sans-serif; 
            margin: 0; 
            padding: 20px;
            background: white;
            line-height: 1.6;
            color: #333;
          }
          .container {
            max-width: 700px;
            margin: 0 auto;
          }
          .header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
          }
          .header h1 {
            margin: 0 0 10px 0;
            font-size: 2em;
            font-weight: 400;
          }
          .meta {
            color: #666;
            font-size: 0.9em;
          }
          .message {
            margin-bottom: 20px;
            padding: 15px 0;
            border-bottom: 1px solid #f0f0f0;
          }
          .message:last-child {
            border-bottom: none;
          }
          .role {
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
          }
          .content {
            color: #555;
          }
          .timestamp {
            font-size: 0.8em;
            color: #999;
            margin-top: 5px;
          }
          .metadata {
            font-size: 0.8em;
            color: #999;
            margin-top: 5px;
            font-style: italic;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>${conversationTitle || "Chat Export"}</h1>
            <div class="meta">
              ${new Date().toLocaleString()} • ${messages.length} messages
            </div>
          </div>
          ${messages.map((message) => {
            const timestamp = options.includeTimestamps 
              ? `<div class="timestamp">${new Date(message.timestamp).toLocaleString()}</div>` 
              : "";
            
            const metadata = options.includeMetadata && message.metadata
              ? `<div class="metadata">${JSON.stringify(message.metadata)}</div>`
              : "";
            
            return `
              <div class="message">
                <div class="role">${message.role === "user" ? "👤 User" : "🤖 Assistant"}</div>
                <div class="content">${message.content}</div>
                ${timestamp}
                ${metadata}
              </div>
            `;
          }).join('')}
        </div>
      </body>
      </html>
    `;
  }

  private getDetailedHTMLTemplate(messages: ChatMessage[], options: ExtendedChatExportOptions, conversationTitle?: string): string {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>${conversationTitle || "Chat Export"}</title>
        <style>
          body { 
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif; 
            margin: 0; 
            padding: 0;
            background: #f8f9fa;
            line-height: 1.6;
          }
          .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            min-height: 100vh;
          }
          .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 50px 40px;
            position: relative;
            overflow: hidden;
          }
          .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
          }
          .header-content {
            position: relative;
            z-index: 1;
          }
          .header h1 {
            margin: 0;
            font-size: 3em;
            font-weight: 700;
            letter-spacing: -0.02em;
          }
          .header .meta {
            margin-top: 20px;
            opacity: 0.9;
            font-size: 1.1em;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
          }
          .meta-item {
            display: flex;
            align-items: center;
            gap: 8px;
          }
          .content {
            padding: 50px 40px;
          }
          .message {
            margin-bottom: 35px;
            padding: 30px;
            border-radius: 16px;
            position: relative;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #e5e7eb;
          }
          .message.user {
            background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
            border-left: 6px solid #3b82f6;
          }
          .message.assistant {
            background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%);
            border-left: 6px solid #8b5cf6;
          }
          .message-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid rgba(0, 0, 0, 0.1);
          }
          .role {
            font-weight: 700;
            font-size: 1.2em;
            color: #1f2937;
            display: flex;
            align-items: center;
            gap: 8px;
          }
          .timestamp {
            font-size: 0.9em;
            color: #6b7280;
            font-weight: 500;
            background: rgba(255, 255, 255, 0.8);
            padding: 5px 12px;
            border-radius: 20px;
          }
          .message-content {
            font-size: 1.05em;
            line-height: 1.7;
            color: #374151;
          }
          .metadata {
            margin-top: 20px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.7);
            border-radius: 8px;
            font-size: 0.9em;
            color: #6b7280;
            border-left: 4px solid #d1d5db;
          }
          .stats {
            background: #f8fafc;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 40px;
            border: 1px solid #e5e7eb;
          }
          .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
          }
          .stat-item {
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          }
          .stat-number {
            font-size: 2em;
            font-weight: 700;
            color: #3b82f6;
            margin-bottom: 5px;
          }
          .stat-label {
            color: #6b7280;
            font-weight: 500;
          }
          @media print {
            body { background: white; }
            .container { box-shadow: none; }
            .message { break-inside: avoid; }
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <div class="header-content">
              <h1>${conversationTitle || "Chat Export"}</h1>
              <div class="meta">
                <div class="meta-item">
                  <span>📅</span>
                  <span>${new Date().toLocaleDateString()}</span>
                </div>
                <div class="meta-item">
                  <span>🕒</span>
                  <span>${new Date().toLocaleTimeString()}</span>
                </div>
                <div class="meta-item">
                  <span>💬</span>
                  <span>${messages.length} messages</span>
                </div>
                <div class="meta-item">
                  <span>👤</span>
                  <span>${messages.filter(m => m.role === 'user').length} user messages</span>
                </div>
                <div class="meta-item">
                  <span>🤖</span>
                  <span>${messages.filter(m => m.role === 'assistant').length} assistant messages</span>
                </div>
              </div>
            </div>
          </div>
          <div class="content">
            <div class="stats">
              <h2 style="margin-top: 0; color: #1f2937;">Conversation Statistics</h2>
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="stat-number">${messages.length}</div>
                  <div class="stat-label">Total Messages</div>
                </div>
                <div class="stat-item">
                  <div class="stat-number">${messages.filter(m => m.role === 'user').length}</div>
                  <div class="stat-label">User Messages</div>
                </div>
                <div class="stat-item">
                  <div class="stat-number">${messages.filter(m => m.role === 'assistant').length}</div>
                  <div class="stat-label">Assistant Messages</div>
                </div>
                <div class="stat-item">
                  <div class="stat-number">${Math.round(messages.reduce((acc, m) => acc + m.content.length, 0) / messages.length)}</div>
                  <div class="stat-label">Avg. Message Length</div>
                </div>
              </div>
            </div>
            ${messages.map((message, index) => {
              const timestamp = options.includeTimestamps 
                ? `<div class="timestamp">${new Date(message.timestamp).toLocaleString()}</div>` 
                : "";
              
              const metadata = options.includeMetadata && message.metadata
                ? `<div class="metadata">📋 <strong>Metadata:</strong> ${JSON.stringify(message.metadata)}</div>`
                : "";
              
              return `
                <div class="message ${message.role}">
                  <div class="message-header">
                    <div class="role">${message.role === "user" ? "👤 User" : "🤖 Assistant"}</div>
                    ${timestamp}
                  </div>
                  <div class="message-content">${message.content}</div>
                  ${metadata}
                </div>
              `;
            }).join('')}
          </div>
        </div>
      </body>
      </html>
    `;
  }

  private getCustomHTMLTemplate(messages: ChatMessage[], options: ExtendedChatExportOptions, conversationTitle?: string): string {
    // Custom template - can be extended with user-defined templates
    return this.getProfessionalHTMLTemplate(messages, options, conversationTitle);
  }

  // Original export methods (kept for backward compatibility)
  private async exportAsJSON(
    messages: ChatMessage[],
    options: ExtendedChatExportOptions,
    conversationTitle?: string
  ): Promise<void> {
    const exportData: any = {
      conversation: {
        title: conversationTitle || "Chat Export",
        messageCount: messages.length,
        exportDate: new Date().toISOString(),
      },
      messages: messages.map(msg => ({
        role: msg.role,
        content: msg.content,
        timestamp: options.includeTimestamps ? msg.timestamp : undefined,
        metadata: options.includeMetadata ? msg.metadata : undefined,
      })),
    };

    if (options.includeUserInfo) {
      exportData.userInfo = {
        exportOptions: options,
        exportVersion: "1.0",
      };
    }

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: "application/json",
    });
    
    this.downloadFile(blob, `${conversationTitle || "chat"}_export.json`);
  }

  private async exportAsMarkdown(
    messages: ChatMessage[],
    options: ExtendedChatExportOptions,
    conversationTitle?: string
  ): Promise<void> {
    let markdown = `# ${conversationTitle || "Chat Export"}\n\n`;
    
    if (options.includeMetadata) {
      markdown += `**Export Date:** ${new Date().toLocaleString()}\n`;
      markdown += `**Message Count:** ${messages.length}\n\n`;
    }
    
    markdown += "---\n\n";
    
    messages.forEach((message, index) => {
      const timestamp = options.includeTimestamps 
        ? `*${new Date(message.timestamp).toLocaleString()}*` 
        : "";
      
      markdown += `## ${message.role === "user" ? "👤 User" : "🤖 Assistant"}\n\n`;
      
      if (timestamp) {
        markdown += `${timestamp}\n\n`;
      }
      
      markdown += `${message.content}\n\n`;
      
      if (options.includeMetadata && message.metadata) {
        markdown += `**Metadata:** \`${JSON.stringify(message.metadata)}\`\n\n`;
      }
      
      if (index < messages.length - 1) {
        markdown += "---\n\n";
      }
    });
    
    const blob = new Blob([markdown], { type: "text/markdown" });
    this.downloadFile(blob, `${conversationTitle || "chat"}_export.md`);
  }

  private async exportAsText(
    messages: ChatMessage[],
    options: ExtendedChatExportOptions,
    conversationTitle?: string
  ): Promise<void> {
    const textContent = this.generateTextContent(messages, options, conversationTitle);
    const blob = new Blob([textContent], { type: "text/plain" });
    this.downloadFile(blob, `${conversationTitle || "chat"}_export.txt`);
  }

  private async exportAsCSV(
    messages: ChatMessage[],
    options: ExtendedChatExportOptions,
    conversationTitle?: string
  ): Promise<void> {
    const headers = ["Role", "Content"];
    if (options.includeTimestamps) headers.push("Timestamp");
    if (options.includeMetadata) headers.push("Metadata");
    
    let csv = headers.join(",") + "\n";
    
    messages.forEach(message => {
      const row = [
        `"${message.role}"`,
        `"${message.content.replace(/"/g, '""')}"`,
      ];
      
      if (options.includeTimestamps) {
        row.push(`"${new Date(message.timestamp).toISOString()}"`);
      }
      
      if (options.includeMetadata) {
        row.push(`"${JSON.stringify(message.metadata || {}).replace(/"/g, '""')}"`);
      }
      
      csv += row.join(",") + "\n";
    });
    
    const blob = new Blob([csv], { type: "text/csv" });
    this.downloadFile(blob, `${conversationTitle || "chat"}_export.csv`);
  }

  private generateTextContent(
    messages: ChatMessage[],
    options: ExtendedChatExportOptions,
    conversationTitle?: string
  ): string {
    let text = `${conversationTitle || "Chat Export"}\n`;
    text += "=".repeat(50) + "\n\n";
    
    if (options.includeMetadata) {
      text += `Export Date: ${new Date().toLocaleString()}\n`;
      text += `Message Count: ${messages.length}\n\n`;
      text += "-".repeat(50) + "\n\n";
    }
    
    messages.forEach((message, index) => {
      const timestamp = options.includeTimestamps 
        ? `[${new Date(message.timestamp).toLocaleString()}]` 
        : "";
      
      text += `${message.role === "user" ? "👤 User" : "🤖 Assistant"} ${timestamp}\n`;
      text += `${message.content}\n`;
      
      if (options.includeMetadata && message.metadata) {
        text += `Metadata: ${JSON.stringify(message.metadata)}\n`;
      }
      
      text += "\n";
      
      if (index < messages.length - 1) {
        text += "-".repeat(30) + "\n\n";
      }
    });
    
    return text;
  }

  private downloadFile(blob: Blob, filename: string): void {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
}

export const exportService = new ExportService();
export default exportService;