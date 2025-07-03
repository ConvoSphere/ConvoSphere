# WebSocket Feature

## Overview

WebSockets enable real-time, bidirectional communication between frontend and backend. Used for live chat, streaming AI responses, and instant updates.

---

## Features
- **Live Chat**: Echtzeit-Nachrichten zwischen User und Assistant
- **Streaming**: Token- oder Satzweises Senden von AI-Antworten
- **Status-Events**: Anzeige von Verbindungsstatus, Fehlern, Systemnachrichten

---

## API Endpoint
- **URL:** `/api/v1/ws/chat/{conversation_id}`
- **Protocol:** WebSocket (ws/wss)

---

## Events & Messages
- `user_message`: User sendet Nachricht
- `assistant_message`: AI sendet Antwort (ggf. gestreamt)
- `status`: Verbindungsstatus, z.B. "connected", "disconnected"
- `error`: Fehlernachrichten

---

## Beispiel-Client (Python)
```python
import websockets
import asyncio
import json

async def chat():
    uri = "ws://localhost:8000/api/v1/ws/chat/1234"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({"type": "user_message", "content": "Hello!"}))
        async for message in websocket:
            data = json.loads(message)
            print(data)

asyncio.run(chat())
```

---

## Fehlerbehandlung
- Prüfe Verbindungsstatus (`status` Event)
- Fange `error` Events ab und zeige sie dem User
- Implementiere Reconnect-Logik bei Verbindungsabbruch

---

## Best Practices
- Halte Verbindungen kurzlebig, wenn nicht benötigt
- Begrenze parallele Verbindungen pro User
- Nutze Heartbeats/Pings für Verbindungsüberwachung 