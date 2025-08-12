import React from "react";
import { useParams } from "react-router-dom";
import ChatContainer from "./chat/components/ChatContainer";

const Chat: React.FC = () => {
  const { threadId, assistantId } = useParams<{
    threadId?: string;
    assistantId?: string;
  }>();

  return (
    <ChatContainer
      threadId={threadId}
      assistantId={assistantId}
      showToolbar={true}
      showMetadata={false}
      allowAttachments={true}
      maxMessages={100}
    />
  );
};

export default Chat;
