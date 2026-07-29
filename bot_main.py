import telebot


from config import BOT_TOKEN, TEST_BOT_TOKEN, ADMIN_IDS, NOTIFICATION_CHAT, TEST_NOTIFICATION_CHAT, TEST_MODE, SUPPORT_CHAT_ID, FEEDBACK_CHAT_ID
from handlers.info import InfoHandlers
from services.take_application_service import ContactHandlers
from services.application_request_service import RequestHandler
from services.queue import QueueHandler
from services.application_confirm_service import ApplicationConfirmService
from utils import logger,  day_off
from database_main import QueueDB
from services.converter import FinInstr

from services.subscription import SubscriptionService
from services.application_creator_service import ApplicationCreator
from services.senders import SenderService
from services.exchange_service import ExchangeService
from services.state_manager import StateManager
from services.interest_service import InterestService
from services.orchestrator import CurrencyOrchestrator
from services.spam_service import SpamService
from services.menulink_service import MenuLinkService
from handlers.deeplinks import DeepLinkRouter

from handlers.turkey import TurkeyHandlers
from handlers.korea import KoreaHandlers
from handlers.esim import EsimHandlers
from handlers.china import ChinaHandlers
from handlers.russia import RussiaHandlers
from handlers.thailand import ThailandHandlers
from handlers.vietnam import VietnamHandlers
from handlers.bybit import BybitHandlers
from handlers.appstore import AppstoreHandlers
from handlers.start import StartHandlers
from handlers.manager import ManagerHandlers
from handlers.europe import EuropeHandlers
from handlers.survey import SurveyHandler


from sheets.interest import Interest
from sheets.links import AnalSheets
from database_users import UserDB

manager_chat_id = NOTIFICATION_CHAT if not TEST_MODE else TEST_NOTIFICATION_CHAT

class MyExceptionHandler(telebot.ExceptionHandler):

    def handle(self, exception):
        # Игнорируем ошибки, которые пришли от Telegram API
        if isinstance(exception, telebot.apihelper.ApiTelegramException):
            # Можно залогировать для отладки, но не слать в support
            logger.warning(f"Ignored Telegram API exception: {exception}")
            return False  # возвращаем False, чтобы бот не считал это обработанной критической ошибкой

        # Для всех остальных ошибок — логируем и шлем в SUPPORT_CHAT
        message = f"Ошибка в боте: {exception}"
        logger.error(message, exc_info=True)
        bot.send_message(SUPPORT_CHAT_ID, message)
        return True


qdb=QueueDB()
sheets_interest = Interest(logger)
user_db = UserDB()
anal_sheets = AnalSheets(user_db)


bot = telebot.TeleBot(BOT_TOKEN if not TEST_MODE else TEST_BOT_TOKEN, exception_handler=MyExceptionHandler())


subscription_service = SubscriptionService(bot, logger, TEST_MODE)



sender_service = SenderService(bot, qdb, manager_chat_id, day_off, logger)
sender_service.register_daily_send_handlers()

state_manager = StateManager(logger)
deeplink_router = DeepLinkRouter(logger)
start = StartHandlers(
    bot,
    user_db,
    state_manager,
    sender_service,
    deeplinks=deeplink_router,
)
start.register()

interest_service = InterestService(
    bot,
    logger,
    sheets_interest,
    qdb,
    ADMIN_IDS,

)

interest_service.register()
orchestra=CurrencyOrchestrator(qdb, interest_service, logger)
orchestra.start()
manager_handler = ManagerHandlers(
    bot=bot,
    qdb=qdb,
    state_manager=state_manager,
    day_off=day_off,
    manager_chat_id=manager_chat_id,
    application_creator=ApplicationCreator,
    track_user=user_db.track_user,
)

manager_handler.register()
finstr = FinInstr(
    qdb,
    logger,

)
exchange_service = ExchangeService(bot, logger, sender_service, finstr, state_manager, user_db)
exchange_service.register_handlers()


turkey_handlers = TurkeyHandlers(
    bot,
    subscription_service,
    sender_service.send_media,
    finstr,
    state_manager,
    track_user=user_db.track_user,
)
turkey_handlers.register()


russia_handlers = RussiaHandlers(
    bot,
    subscription_service,
    sender_service.send_media,
    finstr,
    state_manager,
    track_user=user_db.track_user,
)
russia_handlers.register()
bybit_handlers = BybitHandlers(
    bot,
    subscription_service,
    sender_service.send_media,
    finstr,
    state_manager,
    track_user=user_db.track_user,
)
bybit_handlers.register()


korea_handlers = KoreaHandlers(
    bot,
    subscription_service,
    sender_service.send_media,
    finstr,
    state_manager,
    track_user=user_db.track_user,
)
korea_handlers.register()


thailand_handlers = ThailandHandlers(
    bot,
    subscription_service,
    sender_service.send_media,
    finstr,
    state_manager,
    track_user=user_db.track_user,
)
thailand_handlers.register()
china_handlers = ChinaHandlers(
    bot,
    subscription_service,
    sender_service.send_media,
    finstr,
    state_manager,
    track_user=user_db.track_user,
)
china_handlers.register()


esim_handlers = EsimHandlers(
    bot,
    subscription_service,
    sender_service,
    state_manager,
    track_user=user_db.track_user,

)
esim_handlers.register()

vietnam_handlers = VietnamHandlers(
    bot,
    subscription_service,
    sender_service.send_media,
    finstr,
    state_manager,
    track_user=user_db.track_user,
)
vietnam_handlers.register()

appstore_handlers = AppstoreHandlers(
    bot,
    subscription_service,
    sender_service.send_media,
    state_manager,
    track_user=user_db.track_user,
)
appstore_handlers.register()

europe_handlers = EuropeHandlers(
    bot,
    finstr,
    state_manager,
    track_user=user_db.track_user,
)
europe_handlers.register()

survey_handler = SurveyHandler(
    bot,
    state_manager,
    logger,
    FEEDBACK_CHAT_ID,
)
survey_handler.register()
info_handlers = InfoHandlers(bot,
    track_user=user_db.track_user,)
info_handlers.register()

contact_handlers = ContactHandlers(bot, qdb, logger)
contact_handlers.register()


application_request_service = RequestHandler(bot, sender_service)
application_request_service.register()
queue_service = QueueHandler(bot, qdb, logger)
application_confirm_service = ApplicationConfirmService(bot, qdb, manager_chat_id, ApplicationCreator)
application_confirm_service.register()

# реестр deep-link'ов: собираем routes всех хендлеров для навигации по /start
for _h in (
    turkey_handlers, russia_handlers, bybit_handlers, korea_handlers,
    thailand_handlers, china_handlers, esim_handlers, vietnam_handlers,
    europe_handlers,
):
    deeplink_router.register(getattr(_h, "routes", {}))

# ВАЖНО: регистрируем ДО spam_service — у того глобальный catch-all на text,
# который иначе перехватит команду /menulink (telebot отдаёт первому хендлеру)
menulink_service = MenuLinkService(bot, logger)
menulink_service.register()

spam_service = SpamService(
    bot,
    user_db,
    state_manager,
    logger,

)
spam_service.register()
