import logging
import sys
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['level'] = record.levelname
        log_record['loggerName'] = record.name

def setup_logging():
    """
    Configures the root logger to output structured JSON logs to stdout.
    """
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    
    # Get the root logger
    logger = logging.getLogger()
    
    # Remove any existing handlers
    logger.handlers = []

    # Add a new StreamHandler to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    # Silence overly verbose loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("opentelemetry").setLevel(logging.WARNING)