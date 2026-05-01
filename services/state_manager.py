import time

class StateManager:
    def __init__(self, logger, ttl_seconds=900):  # 15 минут
        self.states = {}
        self.total = ttl_seconds
        self.logger = logger

    def set(self, chat_id, data):
        self.states[chat_id] = {
            "data": data,
            "created_at": time.time()
        }

    def get(self, chat_id):
        state = self.states.get(chat_id)
        if not state:
            self.logger.info(f"Не найдено состояние чата {chat_id}")
            return None

        # проверка TTL
        if time.time() - state["created_at"] > self.total:

            del self.states[chat_id]
            return None

        return state["data"]

    def clear(self, chat_id):

        self.states.pop(chat_id, None)

    def exists(self, chat_id):
        return self.get(chat_id) is not None