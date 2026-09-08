import random
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# loading stuff from .env instead of hardcoding it
load_dotenv()

bot_name = os.getenv("BOT_NAME", "DecodeBot")
typing_delay = float(os.getenv("TYPING_DELAY", "0.4"))
DEBUG = os.getenv("DEBUG", "False") == "True"

user_name = ""  # will fill this in once user tells us their name

# keywords for matching stuff, probably should add more later
greetings = ["hi", "hello", "hey", "yo", "sup"]
byes = ["bye", "exit", "quit", "goodbye"]
thanks_words = ["thanks", "thank you", "ty"]
mood_qs = ["how are you", "how r u", "how you doing"]
good_words = ["good", "great", "fine", "awesome", "im good"]
bad_words = ["byebad", "sad", "tired", "not great", "meh"]

greet_replies = ["Hey! What's up?", "Hello!", "Hii, kaise ho?"]
bye_replies = ["okay bye!", "see ya", "cya later"]
thanks_replies = ["np!", "anytime :)", "no worries"]


def get_name_from_text(msg):
    # super basic, just checking a couple common phrasings
    if "my name is" in msg:
        return msg.split("my name is")[-1].strip().split(" ")[0]
    if "i am" in msg:
        return msg.split("i am")[-1].strip().split(" ")[0]
    if "im " in msg:
        return msg.split("im ")[-1].strip().split(" ")[0]
    return None


def respond(msg):
    global user_name

    msg = msg.lower().strip()

    if DEBUG:
        print(f"[debug] got input: {msg!r}")

    if msg == "":
        return "u didn't type anything lol"

    # check name first before other stuff, otherwise "hi i am bob" gets caught by greeting
    name_check = get_name_from_text(msg)
    if name_check:
        user_name = name_check.capitalize()
        return f"oh nice to meet you {user_name}!"

    if msg in byes or any(b in msg for b in byes):
        if user_name:
            return random.choice(bye_replies) + " " + user_name
        else:
            return random.choice(bye_replies)

    if any(g in msg for g in greetings):
        r = random.choice(greet_replies)
        if user_name:
            r += f" ({user_name})"
        return r

    if any(t in msg for t in thanks_words):
        return random.choice(thanks_replies)

    if any(m in msg for m in mood_qs):
        return "im just running on if-else statements but doing fine lol, you?"

    # gotta check bad before good bc "not good" contains "good"
    if any(b in msg for b in bad_words):
        return "aw that sucks, hope it gets better"

    if any(g in msg for g in good_words):
        return "nice!! glad to hear that"

    if "time" in msg:
        now = datetime.now()
        return "its " + now.strftime("%I:%M %p") + " rn"

    if "help" in msg or "what can you do" in msg:
        return """i can do:
- greetings (hi/hello/hey)
- say bye
- tell u the time
- remember ur name if u tell me
- ask how ur doing
thats about it tbh, still building this out"""

    # nothing matched, fallback
    fallback_options = [
        "idk what that means, try again?",
        "hmm i dont have a rule for that yet",
        "not sure i understand, can u rephrase",
    ]
    return random.choice(fallback_options)


def main():
    print(bot_name + ": hey! im " + bot_name + ", type help if u wanna see what i do")
    print()

    while True:
        user_input = input("you: ")

        reply = respond(user_input)

        # little fake typing delay, makes it feel less instant/robotic
        time.sleep(typing_delay)
        print(bot_name + ": " + reply)
        print()

        check = user_input.lower().strip()
        if check in byes or any(b in check for b in byes):
            break


main()
