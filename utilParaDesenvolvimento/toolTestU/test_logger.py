                                                  
import unittest
from unittest.mock import patch, MagicMock, call
import logging
from pathlib import Path

from persistencia.logger import StreamToLogger, setup_loggers


class TestStreamToLogger(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock(spec=logging.Logger)
        self.stream = StreamToLogger(self.mock_logger, logging.INFO)

    def test_write_envia_linha_unica_para_log(self):
        message = "hello world"
        self.stream.write(message + "\n")
        self.mock_logger.log.assert_called_once_with(logging.INFO, message)

    def test_write_envia_multiplas_linhas_para_log(self):
        messages = "first line\nsecond line\n"
        self.stream.write(messages)
        expected_calls = [call(logging.INFO, "first line"), call(logging.INFO, "second line")]
        self.mock_logger.log.assert_has_calls(expected_calls)
        self.assertEqual(self.mock_logger.log.call_count, 2)


@patch('persistencia.logger.sys')
@patch('persistencia.logger.Path')
@patch('persistencia.logger.logging')
@patch('persistencia.logger.RotatingFileHandler')
@patch('config.LOG_FORMAT', "%(message)s")
@patch('config.LOG_LEVEL', "INFO")
class TestSetupLoggers(unittest.TestCase):

                                                                                               
    def test_setup_loggers_configura_handlers_corretamente(self, mock_log_level, mock_log_format,
                                                           mock_rotating_handler, mock_logging, mock_path, mock_sys):

        mock_log_dir = MagicMock(spec=Path)
        mock_path.return_value.parent.parent.resolve.return_value.__truediv__.return_value = mock_log_dir

        loggers = {name: MagicMock() for name in ["main_app", "login_attempts", "stdout", "stderr"]}
        mock_logging.getLogger.side_effect = lambda name: loggers[name]

        setup_loggers()

        mock_log_dir.mkdir.assert_called_once_with(exist_ok=True)

        app_logger = loggers["main_app"]
        app_logger.setLevel.assert_called_once_with(logging.INFO)

        mock_rotating_handler.assert_any_call(
            mock_log_dir / "app.log", maxBytes=2097152, backupCount=5, encoding='utf-8'
        )
        self.assertGreaterEqual(app_logger.addHandler.call_count, 1)