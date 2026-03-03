from dotenv import load_dotenv
import os


TEST_MODE = True #basically, local used only
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if dotenv_path:
    load_dotenv(dotenv_path)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]
NOTIFICATION_CHAT=os.getenv("NOTIFICATION_CHAT")
SUPPORT_CHAT_ID=os.getenv("SUPPORT_CHAT_ID")

TEST_BOT_TOKEN=os.getenv("TEST_BOT_TOKEN")
TEST_NOTIFICATION_CHAT=os.getenv("TEST_NOTIFICATION_CHAT")

API_KEY=os.getenv("API_KEY")


required = [BOT_TOKEN, ADMIN_IDS, NOTIFICATION_CHAT,API_KEY, SUPPORT_CHAT_ID]
if not all(required):
    raise ValueError("Отсутствует обязательная переменная окружения")