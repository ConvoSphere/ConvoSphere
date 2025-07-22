import config from '../config';

type MessageHandler = (msg: { sender: string; text: string }) => void;

class ChatWebSocket {
  private ws: WebSocket | null = null;
  private handler: MessageHandler | null = null;

  connect(token: string, onMessage: MessageHandler) {
    this.handler = onMessage;
    
    const wsUrl = `${config.wsUrl}${config.wsEndpoints.chat}?token=${token}`;
    this.ws = new WebSocket(wsUrl);
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (this.handler) this.handler(data);
    };
  }

  send(text: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ text }));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const chatWebSocket = new ChatWebSocket(); 