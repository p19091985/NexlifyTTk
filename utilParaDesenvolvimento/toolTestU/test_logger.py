# test_logger.py (Versão Corrigida)
import unittest
from unittest.mock import patch, MagicMock, call
import logging
from pathlib import Path

# PRINCIPAL 2: Usa o caminho de importação absoluto 
# Agora o Python sabe onde encontrar o pacote 'persistencia'
from persistencia.logger import StreamToLogger, setup_loggers


class TestStreamToLogger(unittest.TestCase):
    """Testa a classe que redireciona streams para um logger."""

    def setUp(self):
        self.mock_logger = MagicMock(spec=logging.Logger)
        self.stream = StreamToLogger(self.mock_logger, logging.WARNING)

    def test_write_single_clean_line(self):
        message = "hello world"
        self.stream.write(message + "\n")
        self.mock_logger.log.assert_called_once_with(logging.WARNING, message)

    def test_write_multiple_lines(self):
        messages = "first line\nsecond line\n"
        self.stream.write(messages)
        expected_calls = [call(logging.WARNING, "first line"), call(logging.WARNING, "second line")]
        self.mock_logger.log.assert_has_calls(expected_calls)
        self.assertEqual(self.mock_logger.log.call_count, 2)


@patch('persistencia.logger.sys')
@patch('persistencia.logger.Path')
@patch('persistencia.logger.logging')
@patch('persistencia.logger.RotatingFileHandler')
@patch('persistencia.logger.config')
class TestSetupLoggers(unittest.TestCase):
    """Testa a função principal de configuração dos loggers."""

    def test_setup_loggers_configures_correctly(self, mock_config, mock_rotating_handler, mock_logging, mock_path,
                                                mock_sys):
        # Arrange
        mock_config.LOG_LEVEL = "INFO"
        mock_config.LOG_FORMAT = "%(message)s"
        mock_log_dir = MagicMock(spec=Path)
        mock_path.return_value.parent.parent.resolve.return_value.joinpath.return_value = mock_log_dir

        mock_app_logger, mock_login_logger, mock_stdout_logger, mock_stderr_logger = MagicMock(), MagicMock(), MagicMock(), MagicMock()
        mock_logging.getLogger.side_effect = [mock_app_logger, mock_login_logger, mock_stdout_logger,
                                              mock_stderr_logger]

        # Act
        setup_loggers()

        # Assert
        mock_log_dir.mkdir.assert_called_once_with(exist_ok=True)
        mock_logging.getLogger.assert_any_call("main_app")
        mock_app_logger.setLevel.assert_called_once_with(logging.INFO)
        mock_rotating_handler.assert_any_call(
            mock_log_dir / "app.log", maxBytes=2097152, backupCount=5, encoding='utf-8'
        )
        self.assertEqual(mock_app_logger.addHandler.call_count, 2)


if __name__ == '__main__':
    unittest.main()