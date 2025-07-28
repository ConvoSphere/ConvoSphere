import { config } from "../config";

export interface AssistantTemplate {
  id: string;
  name: string;
  description: string;
  category: "support" | "creative" | "technical" | "business" | "education" | "custom";
  personality: string;
  instructions: string;
  model: string;
  tools: string[];
  temperature: number;
  maxTokens: number;
  isActive: boolean;
  tags: string[];
  examples: Array<{
    user: string;
    assistant: string;
  }>;
  metadata?: Record<string, any>;
}

export interface TemplateCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
}

class AssistantTemplateService {
  private baseUrl = config.apiUrl;

  // Predefined templates
  private defaultTemplates: AssistantTemplate[] = [
    {
      id: "customer-support",
      name: "Customer Support Agent",
      description: "Hilfsbereiter Kundenservice-Agent für allgemeine Anfragen",
      category: "support",
      personality: "Freundlich, geduldig und lösungsorientiert. Ich helfe Kunden bei ihren Fragen und Problemen.",
      instructions: "Du bist ein professioneller Kundenservice-Agent. Antworte freundlich und hilfreich. Wenn du eine Frage nicht beantworten kannst, leite sie an einen menschlichen Kollegen weiter.",
      model: "gpt-4",
      tools: ["web_search", "file_reader"],
      temperature: 0.7,
      maxTokens: 1000,
      isActive: true,
      tags: ["support", "customer", "help"],
      examples: [
        {
          user: "Ich kann mich nicht in mein Konto einloggen",
          assistant: "Das tut mir leid zu hören! Lassen Sie mich Ihnen dabei helfen. Können Sie mir sagen, welche Fehlermeldung Sie sehen? Haben Sie Ihr Passwort kürzlich geändert?"
        },
        {
          user: "Wie kann ich mein Passwort zurücksetzen?",
          assistant: "Gerne helfe ich Ihnen dabei! Sie können Ihr Passwort über die 'Passwort vergessen' Funktion auf der Login-Seite zurücksetzen. Soll ich Ihnen die Schritte erklären?"
        }
      ]
    },
    {
      id: "creative-writer",
      name: "Creative Writer",
      description: "Kreativer Autor für Texte, Geschichten und Marketing-Inhalte",
      category: "creative",
      personality: "Kreativ, inspirierend und ausdrucksstark. Ich helfe dabei, fesselnde Geschichten und Texte zu schreiben.",
      instructions: "Du bist ein kreativer Autor. Schreibe fesselnde, originelle Texte. Passe deinen Stil an das gewünschte Genre und die Zielgruppe an.",
      model: "gpt-4",
      tools: ["web_search"],
      temperature: 0.9,
      maxTokens: 1500,
      isActive: true,
      tags: ["creative", "writing", "storytelling"],
      examples: [
        {
          user: "Schreibe eine kurze Geschichte über einen magischen Garten",
          assistant: "Im Herzen der alten Stadt lag ein Garten, den nur wenige kannten. Seine Blumen leuchteten in Farben, die es nirgendwo sonst gab..."
        },
        {
          user: "Erstelle einen Marketing-Text für ein neues Produkt",
          assistant: "Entdecken Sie die Zukunft des [Produktname] - entwickelt für Menschen, die mehr erwarten..."
        }
      ]
    },
    {
      id: "technical-expert",
      name: "Technical Expert",
      description: "Technischer Experte für komplexe Probleme und Code-Reviews",
      category: "technical",
      personality: "Präzise, analytisch und lösungsorientiert. Ich helfe bei technischen Problemen und Code-Reviews.",
      instructions: "Du bist ein technischer Experte. Gib präzise, technisch korrekte Antworten. Erkläre komplexe Konzepte verständlich.",
      model: "gpt-4",
      tools: ["code_interpreter", "web_search"],
      temperature: 0.3,
      maxTokens: 2000,
      isActive: true,
      tags: ["technical", "coding", "debugging"],
      examples: [
        {
          user: "Kannst du diesen Code reviewen?",
          assistant: "Gerne schaue ich mir Ihren Code an. Ich sehe einige Verbesserungsmöglichkeiten in Bezug auf Performance und Sicherheit..."
        },
        {
          user: "Wie kann ich diese Performance-Probleme lösen?",
          assistant: "Basierend auf Ihrer Beschreibung würde ich folgende Optimierungen vorschlagen..."
        }
      ]
    },
    {
      id: "business-analyst",
      name: "Business Analyst",
      description: "Business Analyst für Datenanalyse und strategische Beratung",
      category: "business",
      personality: "Analytisch, strategisch und ergebnisorientiert. Ich helfe bei der Datenanalyse und strategischen Entscheidungen.",
      instructions: "Du bist ein Business Analyst. Analysiere Daten und Trends. Gib strategische Empfehlungen basierend auf Fakten.",
      model: "gpt-4",
      tools: ["data_analysis", "web_search"],
      temperature: 0.5,
      maxTokens: 1500,
      isActive: true,
      tags: ["business", "analytics", "strategy"],
      examples: [
        {
          user: "Analysiere diese Verkaufsdaten",
          assistant: "Basierend auf den Daten sehe ich folgende Trends: [Analyse]. Meine Empfehlung wäre..."
        },
        {
          user: "Wie können wir unsere Conversion-Rate verbessern?",
          assistant: "Hier sind die wichtigsten Hebel für eine bessere Conversion-Rate: [Strategien]..."
        }
      ]
    },
    {
      id: "language-tutor",
      name: "Language Tutor",
      description: "Geduldiger Sprachlehrer für verschiedene Sprachen",
      category: "education",
      personality: "Geduldig, ermutigend und anpassungsfähig. Ich helfe beim Sprachenlernen mit individueller Betreuung.",
      instructions: "Du bist ein Sprachlehrer. Erkläre Grammatik verständlich. Korrigiere Fehler freundlich und konstruktiv.",
      model: "gpt-4",
      tools: ["web_search"],
      temperature: 0.7,
      maxTokens: 1000,
      isActive: true,
      tags: ["education", "language", "tutoring"],
      examples: [
        {
          user: "Kannst du mir die deutsche Grammatik erklären?",
          assistant: "Gerne! Lassen Sie uns mit den Grundlagen beginnen. Die deutsche Grammatik hat vier Fälle..."
        },
        {
          user: "Korrigiere bitte diesen Satz",
          assistant: "Hier ist die korrigierte Version: [Korrektur]. Der Fehler lag in der [Erklärung]..."
        }
      ]
    }
  ];

  // Template categories
  private categories: TemplateCategory[] = [
    {
      id: "support",
      name: "Support",
      description: "Kundenservice und Hilfe",
      icon: "🛟",
      color: "#1890ff"
    },
    {
      id: "creative",
      name: "Kreativ",
      description: "Schreiben und Design",
      icon: "🎨",
      color: "#722ed1"
    },
    {
      id: "technical",
      name: "Technisch",
      description: "Programmierung und IT",
      icon: "⚙️",
      color: "#13c2c2"
    },
    {
      id: "business",
      name: "Business",
      description: "Analytik und Strategie",
      icon: "📊",
      color: "#52c41a"
    },
    {
      id: "education",
      name: "Bildung",
      description: "Lernen und Lehren",
      icon: "📚",
      color: "#fa8c16"
    },
    {
      id: "custom",
      name: "Benutzerdefiniert",
      description: "Eigene Templates",
      icon: "🔧",
      color: "#eb2f96"
    }
  ];

  async getTemplates(token: string): Promise<AssistantTemplate[]> {
    try {
      const response = await fetch(`${this.baseUrl}/v1/assistants/templates`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const templates = await response.json();
        return [...this.defaultTemplates, ...templates];
      }

      // Fallback to default templates
      return this.defaultTemplates;
    } catch (error) {
      console.error("Error fetching templates:", error);
      return this.defaultTemplates;
    }
  }

  async getTemplateById(token: string, templateId: string): Promise<AssistantTemplate | null> {
    try {
      const response = await fetch(`${this.baseUrl}/v1/assistants/templates/${templateId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        return await response.json();
      }

      // Fallback to default templates
      return this.defaultTemplates.find(t => t.id === templateId) || null;
    } catch (error) {
      console.error("Error fetching template:", error);
      return this.defaultTemplates.find(t => t.id === templateId) || null;
    }
  }

  async createAssistantFromTemplate(
    token: string,
    templateId: string,
    customizations?: Partial<AssistantTemplate>
  ): Promise<any> {
    try {
      const template = await this.getTemplateById(token, templateId);
      if (!template) {
        throw new Error("Template not found");
      }

      const assistantData = {
        ...template,
        ...customizations,
        id: undefined, // Remove template ID
        name: customizations?.name || template.name,
        description: customizations?.description || template.description,
      };

      const response = await fetch(`${this.baseUrl}/v1/assistants`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(assistantData),
      });

      if (!response.ok) {
        throw new Error("Failed to create assistant");
      }

      return await response.json();
    } catch (error) {
      console.error("Error creating assistant from template:", error);
      throw error;
    }
  }

  async saveTemplate(token: string, template: Omit<AssistantTemplate, "id">): Promise<AssistantTemplate> {
    try {
      const response = await fetch(`${this.baseUrl}/v1/assistants/templates`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(template),
      });

      if (!response.ok) {
        throw new Error("Failed to save template");
      }

      return await response.json();
    } catch (error) {
      console.error("Error saving template:", error);
      throw error;
    }
  }

  async updateTemplate(token: string, templateId: string, updates: Partial<AssistantTemplate>): Promise<AssistantTemplate> {
    try {
      const response = await fetch(`${this.baseUrl}/v1/assistants/templates/${templateId}`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error("Failed to update template");
      }

      return await response.json();
    } catch (error) {
      console.error("Error updating template:", error);
      throw error;
    }
  }

  async deleteTemplate(token: string, templateId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/v1/assistants/templates/${templateId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to delete template");
      }
    } catch (error) {
      console.error("Error deleting template:", error);
      throw error;
    }
  }

  getCategories(): TemplateCategory[] {
    return this.categories;
  }

  getTemplatesByCategory(templates: AssistantTemplate[], category: string): AssistantTemplate[] {
    return templates.filter(template => template.category === category);
  }

  searchTemplates(templates: AssistantTemplate[], query: string): AssistantTemplate[] {
    const lowerQuery = query.toLowerCase();
    return templates.filter(template =>
      template.name.toLowerCase().includes(lowerQuery) ||
      template.description.toLowerCase().includes(lowerQuery) ||
      template.tags.some(tag => tag.toLowerCase().includes(lowerQuery))
    );
  }
}

export const assistantTemplateService = new AssistantTemplateService();
export default assistantTemplateService;