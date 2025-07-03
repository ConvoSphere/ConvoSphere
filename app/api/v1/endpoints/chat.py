# Save user message
await conversation_service.add_message(
    conversation_id=conversation_id,
    user_id=current_user_id,
    content=message,
    role="user",
    message_type="text"
) 