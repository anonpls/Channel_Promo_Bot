import os
import dotenv


def setMessageWSub(msgs: list):
    with open('.env', 'r') as f:
            lines = f.readlines()
    with open('.env', 'w') as f:
            for line in lines:
                if line.startswith('sub_msg'):
                    f.write(f"sub_msg = {','.join(map(str, msgs))}\n")
                else:
                    f.write(line)


def setMessageWNoSub(msgs: list):
    with open('.env', 'r') as f:
            lines = f.readlines()
    with open('.env', 'w') as f:
            for line in lines:
                if line.startswith('nosub_msg'):
                    f.write(f"nosub_msg = {','.join(map(str, msgs))}\n")
                else:
                    f.write(line)


def getMessageWSub():
    dotenv.load_dotenv()
    msgs = [msg_id for msg_id in os.getenv('sub_msg', '').split(',')]
    return msgs 


def getMessageWNoSub():
    dotenv.load_dotenv()
    msgs = [msg_id for msg_id in os.getenv('nosub_msg', '').split(',')]
    return msgs 