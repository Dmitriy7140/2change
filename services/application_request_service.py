class RequestHandler:
    def __init__(self, bot, sender_service):
        self.bot = bot
        self.sender_service = sender_service


    def register(self):

        @self.bot.callback_query_handler(func=lambda c: c.data.startswith("request/"))
        def handle(call):
            self.handle_request(call)

    def handle_request(self, call):
        self.bot.answer_callback_query(call.id)

        user_id = call.from_user.id
        user_ref = call.from_user.username
        chat_id = call.message.chat.id

        last_name = call.from_user.last_name or ""
        user_name = (call.from_user.first_name or "") + (" " + last_name if last_name else "")

        _, request, country = call.data.split("/")

        self.sender_service.send_application(
            user_id=user_id,
            user_name=user_name,
            user_ref=user_ref,
            chat_id=chat_id,
            country=int(country),
            reason=request
        )

