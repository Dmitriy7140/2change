import unittest
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

from services.interest_service import InterestService
from services.orchestrator import CurrencyOrchestrator


SUCCESS = "Наценки и курсы обновлены в БД и Google-таблице"


class InterestSyncTests(unittest.TestCase):
    def setUp(self):
        self.bot = Mock()
        self.logger = Mock()
        self.sheets = Mock()
        self.qdb = Mock()
        self.sheets.get_interest.return_value = {"usd_rub_c": 2.5}
        self.qdb.update_currency.return_value = {"usd_rub": 100.0}
        self.qdb.get_currencies.return_value = {
            "usd_rub": 97.5, "updated_at": "15-09-2026 12:00:00"
        }
        self.service = InterestService(
            self.bot, self.logger, self.sheets, self.qdb, []
        )
        self.orchestrator = CurrencyOrchestrator(
            self.qdb, self.service, self.logger
        )

    def run_cycles(self, count=1):
        def sleep(interval):
            nonlocal count
            self.assertEqual(interval, 20 * 60)
            count -= 1
            if count == 0:
                self.orchestrator.stop()

        with patch("services.orchestrator.time.sleep", side_effect=sleep):
            self.orchestrator._loop()

    def test_each_cycle_applies_latest_markups_before_recalculation(self):
        self.sheets.get_interest.side_effect = [
            {"usd_rub_c": 2.5}, {"usd_rub_c": 4.0}
        ]
        saved = {}
        observed = []
        self.qdb.set_coef.side_effect = lambda name, value: saved.update({name: value})

        def recalculate():
            observed.append(saved["usd_rub_c"])
            return {"usd_rub": 100.0}

        self.qdb.update_currency.side_effect = recalculate
        self.qdb.get_currencies.side_effect = lambda: {
            "usd_rub": 100 * (1 - saved["usd_rub_c"])
        }

        self.run_cycles(2)

        self.assertEqual(observed, [0.025, 0.04])
        self.sheets.set_currencies_with_interest.assert_has_calls([
            call({"usd_rub": 97.5}), call({"usd_rub": 96.0})
        ])
        self.bot.send_message.assert_not_called()
        self.assertEqual(self.logger.info.call_args_list.count(call(SUCCESS)), 2)

    def test_read_failure_retries_on_next_cycle(self):
        self.sheets.get_interest.side_effect = [
            TimeoutError("Google Sheets unavailable"), {"usd_rub_c": 2.5}
        ]

        self.run_cycles(2)

        self.qdb.set_coef.assert_called_once_with("usd_rub_c", 0.025)
        self.qdb.update_currency.assert_called_once_with()
        self.logger.error.assert_called_once()
        self.assertEqual(self.logger.info.call_args_list.count(call(SUCCESS)), 1)

    def test_invalid_or_empty_table_does_not_apply_or_publish_rates(self):
        for data in (["invalid value"], {}, None):
            with self.subTest(data=data):
                self.setUp()
                self.sheets.get_interest.return_value = data
                self.run_cycles()
                self.qdb.set_coef.assert_not_called()
                self.qdb.update_currency.assert_not_called()
                self.sheets.set_currencies_with_interest.assert_not_called()
                self.assertNotIn(call(SUCCESS), self.logger.info.call_args_list)

    def test_save_failure_does_not_recalculate_or_report_success(self):
        self.qdb.set_coef.side_effect = RuntimeError("Database unavailable")

        self.run_cycles()

        self.qdb.update_currency.assert_not_called()
        self.assertNotIn(call(SUCCESS), self.logger.info.call_args_list)
        self.logger.error.assert_called_once()

    def test_provider_failure_does_not_publish_or_report_success(self):
        self.qdb.update_currency.return_value = None

        self.run_cycles()

        self.sheets.set_raw_currencies.assert_not_called()
        self.sheets.set_currencies_with_interest.assert_not_called()
        self.assertNotIn(call(SUCCESS), self.logger.info.call_args_list)
        self.logger.error.assert_called()

    def test_sheet_write_failure_does_not_report_success(self):
        self.sheets.set_raw_currencies.side_effect = TimeoutError("Write failed")

        self.run_cycles()

        self.assertNotIn(call(SUCCESS), self.logger.info.call_args_list)
        self.logger.exception.assert_called_once()
        self.logger.error.assert_called_once()

    def test_unexpected_error_does_not_stop_subsequent_cycles(self):
        self.qdb.update_currency.side_effect = [
            RuntimeError("Unexpected error"), {"usd_rub": 100.0}
        ]

        self.run_cycles(2)

        self.sheets.set_currencies_with_interest.assert_called_once()
        self.logger.exception.assert_called_once()
        self.assertEqual(self.logger.info.call_args_list.count(call(SUCCESS)), 1)

    def test_manual_update_still_applies_markups_and_publishes_rates(self):
        self.sheets.fetch_table.return_value = [
            ["Country", "Markup", "", "Pair", "", "", "", "Rate"],
            ["Russia", "2.5", "", "USDT/RUB", "", "", "", "97.5"],
        ]
        message = SimpleNamespace(chat=SimpleNamespace(id=123))

        self.assertTrue(self.service.update_interest(message))

        self.qdb.set_coef.assert_called_once_with("usd_rub_c", 0.025)
        self.sheets.set_currencies_with_interest.assert_called_once_with(
            self.qdb.get_currencies.return_value
        )
        self.assertIn("USDT/RUB: 97.5 (2.5%)", self.bot.send_message.call_args.args[1])


if __name__ == "__main__":
    unittest.main()
