import type { ChatMessage } from "./chat";
import type { ChatExportOptions } from "../components/chat/ChatExport";

// Note: jsPDF would need to be installed: npm install jspdf
// For now, we'll create a placeholder implementation

interface AdvancedExportOptions extends ChatExportOptions {
  includeHeader?: boolean;
  includeFooter?: boolean;
  pageSize?: "A4" | "Letter" | "Legal";
  orientation?: "portrait" | "landscape";
  margins?: {
    top: number;
    bottom: number;
    left: number;
    right: number;
  };
  font?: {
    family: string;
    size: number;
  };
  styling?: {
    primaryColor: string;
    secondaryColor: string;
    backgroundColor: string;
  };
}

interface BatchExportOptions {
  conversations: Array<{
    id: string;
    title: string;
    messages: ChatMessage[];
  }>;
  format: "json" | "pdf" | "markdown" | "txt" | "csv";
  includeMetadata: boolean;
  includeTimestamps: boolean;
  zipFiles: boolean;
}

class AdvancedExportService {
  async exportToPDF(
    messages: ChatMessage[],
    options: AdvancedExportOptions,
    conversationTitle?: string
  ): Promise<void> {
    try {
      // TODO: Implement actual PDF generation with jsPDF
      // For now, we'll create a simple HTML-based PDF
      const htmlContent = this.generatePDFHTML(messages, options, conversationTitle);
      
      // Create a temporary iframe for PDF generation
      const iframe = document.createElement("iframe");
      iframe.style.display = "none";
      document.body.appendChild(iframe);
      
      iframe.contentDocument!.write(htmlContent);
      iframe.contentDocument!.close();
      
      // Trigger print dialog for PDF generation
      setTimeout(() => {
        iframe.contentWindow!.print();
        document.body.removeChild(iframe);
      }, 1000);
      
    } catch (error) {
      console.error("Error generating PDF:", error);
      throw new Error("Failed to generate PDF");
    }
  }

  async batchExport(options: BatchExportOptions): Promise<void> {
    try {
      const { conversations, format, includeMetadata, includeTimestamps, zipFiles } = options;
      
      if (zipFiles) {
        await this.createZippedBatchExport(conversations, format, includeMetadata, includeTimestamps);
      } else {
        await this.createIndividualBatchExport(conversations, format, includeMetadata, includeTimestamps);
      }
    } catch (error) {
      console.error("Error in batch export:", error);
      throw new Error("Failed to perform batch export");
    }
  }

  async scheduleExport(
    conversationId: string,
    options: AdvancedExportOptions,
    schedule: {
      frequency: "once" | "daily" | "weekly" | "monthly";
      time: string; // HH:mm format
      timezone: string;
      startDate: string;
      endDate?: string;
    }
  ): Promise<string> {
    try {
      // TODO: Implement export scheduling
      const scheduleId = `schedule-${Date.now()}`;
      
      // Save schedule to localStorage for now
      const schedules = JSON.parse(localStorage.getItem("export-schedules") || "[]");
      schedules.push({
        id: scheduleId,
        conversationId,
        options,
        schedule,
        createdAt: new Date().toISOString(),
        status: "active",
      });
      localStorage.setItem("export-schedules", JSON.stringify(schedules));
      
      return scheduleId;
    } catch (error) {
      console.error("Error scheduling export:", error);
      throw new Error("Failed to schedule export");
    }
  }

  async getScheduledExports(): Promise<any[]> {
    try {
      const schedules = JSON.parse(localStorage.getItem("export-schedules") || "[]");
      return schedules;
    } catch (error) {
      console.error("Error getting scheduled exports:", error);
      return [];
    }
  }

  async cancelScheduledExport(scheduleId: string): Promise<void> {
    try {
      const schedules = JSON.parse(localStorage.getItem("export-schedules") || "[]");
      const updatedSchedules = schedules.filter((s: any) => s.id !== scheduleId);
      localStorage.setItem("export-schedules", JSON.stringify(updatedSchedules));
    } catch (error) {
      console.error("Error canceling scheduled export:", error);
      throw new Error("Failed to cancel scheduled export");
    }
  }

  private generatePDFHTML(
    messages: ChatMessage[],
    options: AdvancedExportOptions,
    conversationTitle?: string
  ): string {
    const {
      includeHeader = true,
      includeFooter = true,
      pageSize = "A4",
      orientation = "portrait",
      margins = { top: 20, bottom: 20, left: 20, right: 20 },
      font = { family: "Arial", size: 12 },
      styling = {
        primaryColor: "#1890ff",
        secondaryColor: "#666666",
        backgroundColor: "#ffffff",
      },
    } = options;

    const pageSizeCSS = this.getPageSizeCSS(pageSize, orientation);
    
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>${conversationTitle || "Chat Export"}</title>
        <style>
          @media print {
            @page {
              size: ${pageSize} ${orientation};
              margin: ${margins.top}mm ${margins.right}mm ${margins.bottom}mm ${margins.left}mm;
            }
          }
          
          body {
            font-family: ${font.family}, sans-serif;
            font-size: ${font.size}px;
            line-height: 1.6;
            color: #333;
            background-color: ${styling.backgroundColor};
            margin: 0;
            padding: 20px;
          }
          
          .header {
            text-align: center;
            border-bottom: 2px solid ${styling.primaryColor};
            padding-bottom: 20px;
            margin-bottom: 30px;
          }
          
          .header h1 {
            color: ${styling.primaryColor};
            margin: 0;
            font-size: 24px;
          }
          
          .header .metadata {
            color: ${styling.secondaryColor};
            font-size: 14px;
            margin-top: 10px;
          }
          
          .message {
            margin-bottom: 20px;
            page-break-inside: avoid;
          }
          
          .message-header {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
          }
          
          .message-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
            font-weight: bold;
            color: white;
          }
          
          .user-avatar {
            background-color: ${styling.primaryColor};
          }
          
          .assistant-avatar {
            background-color: ${styling.secondaryColor};
          }
          
          .message-info {
            flex: 1;
          }
          
          .message-author {
            font-weight: bold;
            color: ${styling.primaryColor};
          }
          
          .message-time {
            color: ${styling.secondaryColor};
            font-size: 12px;
            margin-left: 10px;
          }
          
          .message-content {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid ${styling.primaryColor};
            white-space: pre-wrap;
          }
          
          .assistant-content {
            background-color: #f0f8ff;
            border-left-color: ${styling.secondaryColor};
          }
          
          .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid ${styling.secondaryColor};
            color: ${styling.secondaryColor};
            font-size: 12px;
          }
          
          .page-break {
            page-break-before: always;
          }
        </style>
      </head>
      <body>
        ${includeHeader ? `
          <div class="header">
            <h1>${conversationTitle || "Chat Export"}</h1>
            <div class="metadata">
              Export Date: ${new Date().toLocaleString()}<br>
              Message Count: ${messages.length}<br>
              Format: PDF
            </div>
          </div>
        ` : ""}
        
        ${messages.map((message, index) => `
          <div class="message">
            <div class="message-header">
              <div class="message-avatar ${message.role === "user" ? "user-avatar" : "assistant-avatar"}">
                ${message.role === "user" ? "👤" : "🤖"}
              </div>
              <div class="message-info">
                <span class="message-author">
                  ${message.role === "user" ? "User" : "Assistant"}
                </span>
                ${options.includeTimestamps ? `
                  <span class="message-time">
                    ${new Date(message.timestamp).toLocaleString()}
                  </span>
                ` : ""}
              </div>
            </div>
            <div class="message-content ${message.role === "assistant" ? "assistant-content" : ""}">
              ${message.content}
            </div>
          </div>
        `).join("")}
        
        ${includeFooter ? `
          <div class="footer">
            Generated by AI Assistant Platform<br>
            ${new Date().toLocaleString()}
          </div>
        ` : ""}
      </body>
      </html>
    `;
  }

  private getPageSizeCSS(pageSize: string, orientation: string): string {
    const sizes = {
      A4: { width: "210mm", height: "297mm" },
      Letter: { width: "8.5in", height: "11in" },
      Legal: { width: "8.5in", height: "14in" },
    };
    
    const size = sizes[pageSize as keyof typeof sizes] || sizes.A4;
    return orientation === "landscape" 
      ? `${size.height} ${size.width}`
      : `${size.width} ${size.height}`;
  }

  private async createZippedBatchExport(
    conversations: Array<{ id: string; title: string; messages: ChatMessage[] }>,
    format: string,
    includeMetadata: boolean,
    includeTimestamps: boolean
  ): Promise<void> {
    // TODO: Implement ZIP creation with JSZip
    console.log("Creating zipped batch export...");
    
    // For now, create individual files
    await this.createIndividualBatchExport(conversations, format, includeMetadata, includeTimestamps);
  }

  private async createIndividualBatchExport(
    conversations: Array<{ id: string; title: string; messages: ChatMessage[] }>,
    format: string,
    includeMetadata: boolean,
    includeTimestamps: boolean
  ): Promise<void> {
    for (const conversation of conversations) {
      try {
        const options: ChatExportOptions = {
          format: format as any,
          includeMetadata,
          includeTimestamps,
          includeUserInfo: true,
        };
        
        // Use the existing export service
        const { exportService } = await import("./export");
        await exportService.exportChat(conversation.messages, options, conversation.title);
        
        // Add delay between downloads to prevent browser blocking
        await new Promise(resolve => setTimeout(resolve, 1000));
      } catch (error) {
        console.error(`Error exporting conversation ${conversation.id}:`, error);
      }
    }
  }
}

export const advancedExportService = new AdvancedExportService();
export default advancedExportService;