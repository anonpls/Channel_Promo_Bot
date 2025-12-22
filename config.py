import os
import dotenv


def getToken():
    dotenv.load_dotenv(override=True)
    return os.getenv("token")

def getAdm():
    dotenv.load_dotenv(override=True)
    return [admin_id for admin_id in os.getenv('admin', '').split(',')]

def getAdmChat():
    dotenv.load_dotenv(override=True)
    return os.getenv("adm_chat_id")

def setAdmChat(chat_id):
    with open('.env', 'r') as f:
            lines = f.readlines()
    with open('.env', 'w') as f:
            for line in lines:
                if line.startswith('adm_chat_id'):
                    f.write(f"adm_chat_id = {chat_id}\n")
                else:
                    f.write(line)

def getChannel():
    dotenv.load_dotenv(override=True)
    return os.getenv("channel")

def getChannelLink():
    dotenv.load_dotenv(override=True)
    return os.getenv("channel_link")
