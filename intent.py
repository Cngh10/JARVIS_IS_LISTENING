def classify_intent(text):
    text = text.lower()

    # COMMANDS
    if any(word in text for word in [
        "open", "launch", "start",
        "search", "play",
        "volume", "mute",
        "shutdown", "restart",
        "whatsapp", "message"
    ]):
        return "command"

    # MEMORY
    if "remember" in text:
        return "remember"

    if "what is my" in text or "recall" in text:
        return "recall"

    # GENERAL AI
    return "ai"