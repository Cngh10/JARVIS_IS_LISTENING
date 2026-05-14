import pywhatkit as kit

def send_whatsapp(message):
    # Format: +977XXXXXXXXXX (Nepali number)
    phone_number = "+9779818503936"

    kit.sendwhatmsg_instantly(phone_number, message, wait_time=10, tab_close=True)

    return "Message sent on WhatsApp"