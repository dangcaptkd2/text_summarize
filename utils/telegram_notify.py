import requests

proxies = {
    "http": "http://180.148.128.125:80",
    "https": "http://180.148.128.125:80",
}


def telegram_bot_sendtext(bot_message, bot_chatID="-874978660"):
    try:
        bot_token = "5848101456:AAFnyhsbN1r68F-h3NfP1sVoYJ1yblcvvUY"
        bot_message = bot_message.replace("_", "\\_")
        command = (
            "https://api.telegram.org/bot"
            + bot_token
            + "/sendMessage?chat_id="
            + bot_chatID
            + "&parse_mode=Markdown&text="
            + bot_message
        )
        response = requests.get(command) #, proxies=proxies
        return response.json()
    except:
        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--message", default=None, type=str)
    args = parser.parse_args()
    if args.message == None:
        exit()
    if len(args.message) > 10:
        telegram_bot_sendtext(args.message)
