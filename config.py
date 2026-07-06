from dotenv import load_dotenv
import os


TEST_MODE = False#basically, local used only
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]
NOTIFICATION_CHAT = int(os.getenv("NOTIFICATION_CHAT", 0))
TEST_NOTIFICATION_CHAT = int(os.getenv("TEST_NOTIFICATION_CHAT", 0))
SUPPORT_CHAT_ID = int(os.getenv("SUPPORT_CHAT_ID", 0))
ADMIN_CHANNEL = int(os.getenv("ADMIN_CHANNEL", 0))
FEEDBACK_CHAT_ID = int(os.getenv("FEEDBACK_CHAT_ID", 0))  # канал «Обратная связь 2Change»
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://2change-tma.vercel.app")  # мини-апп (TMA)

TEST_BOT_TOKEN=os.getenv("TEST_BOT_TOKEN")


API_KEY=os.getenv("API_KEY")


required = [BOT_TOKEN, NOTIFICATION_CHAT,API_KEY, SUPPORT_CHAT_ID]
if not all(required):
    raise ValueError("Отсутствует обязательная переменная окружения")