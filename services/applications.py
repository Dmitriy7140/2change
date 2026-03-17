import datetime


class ApplicationCreator:
    country_names = {0: "Страна не указана", 1: "🇹🇷Турция", 2: "🇷🇺Россия", 3: "🇹🇭Тайланд", 4: "🇨🇳Китай", 5: "🇰🇷Корея",
                     6: "🇦🇪ОАЭ"}
    def __init__(self, country:int=None,client_name=None, reason:str=None, currency1=None, currency2=None,amount1=None, amount2=None, time=None ):#AMOUNT2 БУДЕТ ВЫСЧИТЫВАТЬСЯ ИСХОДЯ ИЗ ФУНКЦИИ ИНВЕСТИНГА
        self.country = int(country) if country else None
        self.client_name = client_name
        self.reason = reason
        self.currency1 = currency1
        self.currency2 = currency2
        self.amount1 = amount1
        self.amount2 = amount2
        if time is None:
            self.time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        else:
            self.time = time
    def create(self):
        """country_names = {1: "🇹🇷Турция", 2: "🇷🇺Россия", 3: "🇹🇭Тайланд", 4: "🇨🇳Китай", 5: "Корея", 6 : ОАЭ}"""

        msg=""

        intro = self.country_names.get(self.country, "Страна не указана") +"\n"+f"👤Клиент: {self.client_name}"
        if self.amount1 is not None:
            main_body =f"<b>🫵Отдаст: {self.amount1}</b> {self.currency1}" +'\n\n'+f"👉<b>Получит: {self.amount2}</b> {self.currency2}"
            rate =""
            if float(self.amount2) > float(self.amount1):
                rate = f"<b>📈Курс:</b> {float(self.amount2) / float(self.amount1):.2f}"
            elif float(self.amount1) > float(self.amount2):
                rate = f"<b>📈Курс:</b> {float(self.amount1) / float(self.amount2):.2f}"



            msg+= intro+"\n\n"+main_body+"\n\n"+rate+"\n\n"+f"🕘<i>{self.time}</i>"
            return msg
        else:

            msg += intro +"\n\n"+ f"\nПричина: {self.reason if self.reason else 'осталась в тайне'}"

            return msg
