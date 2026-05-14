import os
import webbrowser
import re
import urllib.parse
try:
    import pywhatkit as kit
    KIT_AVAILABLE = True
except Exception:
    kit = None
    KIT_AVAILABLE = False
    print("pywhatkit not available - WhatsApp features will be disabled")


CONTACTS = {
    "sam": "+97798185*****",
    "chandan": "+97798185*****"
    "gmail": "itssinghchandan10@gmail.com"
}


# COMMAND DETECTION
def is_system_command(command):
    command = command.lower()

    keywords = [
        "open", "launch", "start",
        "search", "play",
        "volume", "mute",
        "shutdown", "restart",
        "whatsapp", "message",
        "lock", "sleep"
    ]

    return any(word in command for word in keywords)


# EXECUTE COMMAND
def execute(command):
    command = command.lower()

    # OPEN APPS
    if "open chrome" in command:
        os.system("open -a 'Google Chrome'")
        return "Opening Chrome"

    if "open safari" in command:
        os.system("open -a 'Safari'")
        return "Opening Safari"

    if "open whatsapp" in command:
        os.system("open -a 'WhatsApp'")
        return "Opening WhatsApp"

    if "open youtube" in command:
        webbrowser.open("https://youtube.com")
        return "Opening YouTube"

    if "open google" in command:
        webbrowser.open("https://google.com")
        return "Opening Google"

    # PLAY YOUTUBE
    if "play" in command and "youtube" in command:
        query = command.replace("play", "").replace("on youtube", "").strip()

        if not query:
            return "What should I play?"

        url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)
        webbrowser.open(url)

        return f"Playing {query} on YouTube"

    # SEARCH YOUTUBE
    if "search youtube for" in command:
        query = command.replace("search youtube for", "").strip()

        if not query:
            return "What should I search?"

        url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)
        webbrowser.open(url)

        return f"Searching YouTube for {query}"

    # GOOGLE SEARCH
    if "search google for" in command:
        query = command.replace("search google for", "").strip()

        if not query:
            return "What should I search?"

        url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
        webbrowser.open(url)

        return f"Searching Google for {query}"

    #  WHATSAPP MESSAGE
    if "send message" in command:
        try:
            match = re.search(r"send message to (.+?) saying (.+)", command)

            if match:
                name = match.group(1).strip()
                message = match.group(2).strip()

                number = CONTACTS.get(name)

                if not number:
                    return f"I don't have {name} in contacts"

                if not KIT_AVAILABLE:
                    return "WhatsApp functionality is not available on this system"

                kit.sendwhatmsg_instantly(
                    number,
                    message,
                    wait_time=10,
                    tab_close=True
                )

                return f"Sending message to {name}"

            return "Say: send message to NAME saying MESSAGE"

        except Exception as e:
            print("WhatsApp error:", e)
            return "Failed to send message"

    # VOLUME
    if "volume up" in command:
        os.system("osascript -e 'set volume output volume (output volume of (get volume settings) + 10)'")
        return "Increasing volume"

    if "volume down" in command:
        os.system("osascript -e 'set volume output volume (output volume of (get volume settings) - 10)'")
        return "Decreasing volume"

    if "mute" in command:
        os.system("osascript -e 'set volume output muted true'")
        return "Muted"

    if "unmute" in command:
        os.system("osascript -e 'set volume output muted false'")
        return "Unmuted"

    #  SYSTEM CONTROL
    if "lock" in command:
        os.system("/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession -suspend")
        return "Locking your Mac/windows"

    if "sleep" in command:
        os.system("pmset sleepnow")
        return "Sleeping system"

    if "restart" in command:
        os.system("sudo shutdown -r now")
        return "Restarting system"

    if "shutdown" in command:
        os.system("sudo shutdown -h now")
        return "Shutting down system"

    # FALLBACK SEARCH
    if "search" in command:
        query = command.replace("search", "").strip()

        if not query:
            return "What should I search?"

        url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
        webbrowser.open(url)

        return f"Searching for {query}"

    return None
