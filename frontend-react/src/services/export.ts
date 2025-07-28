import type { ChatMessage } from "./chat";
import type { ChatExportOptions } from "../components/chat/ChatExport";

class ExportService {
  async exportChat(
    messages: ChatMessage[],
    options: ChatExportOptions,
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

  private async exportAsJSON(
    messages: ChatMessage[],
    options: ChatExportOptions,
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

  private async exportAsPDF(
    messages: ChatMessage[],
    options: ChatExportOptions,
    conversationTitle?: string
  ): Promise<void> {
    // For PDF export, we'll use a simple HTML-to-PDF approach
    // In a real implementation, you might want to use a library like jsPDF or html2pdf
    const htmlContent = this.generateHTMLContent(messages, options, conversationTitle);
    
    // Create a temporary iframe to render the HTML
    const iframe = document.createElement("iframe");
    iframe.style.display = "none";
    document.body.appendChild(iframe);
    
    iframe.contentDocument!.write(htmlContent);
    iframe.contentDocument!.close();
    
    // For now, we'll create a simple text-based PDF-like export
    const textContent = this.generateTextContent(messages, options, conversationTitle);
    const blob = new Blob([textContent], { type: "text/plain" });
    
    this.downloadFile(blob, `${conversationTitle || "chat"}_export.txt`);
    
    document.body.removeChild(iframe);
  }

  private async exportAsMarkdown(
    messages: ChatMessage[],
    options: ChatExportOptions,
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
    options: ChatExportOptions,
    conversationTitle?: string
  ): Promise<void> {
    const textContent = this.generateTextContent(messages, options, conversationTitle);
    const blob = new Blob([textContent], { type: "text/plain" });
    this.downloadFile(blob, `${conversationTitle || "chat"}_export.txt`);
  }

  private async exportAsCSV(
    messages: ChatMessage[],
    options: ChatExportOptions,
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

  private generateHTMLContent(
    messages: ChatMessage[],
    options: ChatExportOptions,
    conversationTitle?: string
  ): string {
    let html = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>${conversationTitle || "Chat Export"}</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          .message { margin-bottom: 20px; padding: 10px; border-radius: 8px; }
          .user { background-color: #e3f2fd; }
          .assistant { background-color: #f3e5f5; }
          .timestamp { font-size: 12px; color: #666; }
          .metadata { font-size: 12px; color: #999; }
        </style>
      </head>
      <body>
        <h1>${conversationTitle || "Chat Export"}</h1>
    `;
    
    if (options.includeMetadata) {
      html += `
        <p><strong>Export Date:</strong> ${new Date().toLocaleString()}</p>
        <p><strong>Message Count:</strong> ${messages.length}</p>
        <hr>
      `;
    }
    
    messages.forEach(message => {
      const timestamp = options.includeTimestamps 
        ? `<div class="timestamp">${new Date(message.timestamp).toLocaleString()}</div>` 
        : "";
      
      const metadata = options.includeMetadata && message.metadata
        ? `<div class="metadata">Metadata: ${JSON.stringify(message.metadata)}</div>`
        : "";
      
      html += `
        <div class="message ${message.role}">
          <strong>${message.role === "user" ? "👤 User" : "🤖 Assistant"}</strong>
          ${timestamp}
          <div>${message.content}</div>
          ${metadata}
        </div>
      `;
    });
    
    html += "</body></html>";
    return html;
  }

  private generateTextContent(
    messages: ChatMessage[],
    options: ChatExportOptions,
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