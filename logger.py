import logging

from logging.config import dictConfig


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'file_handler': {
            'level': 'INFO',
            'filename': 'media.log',
            'class': 'logging.FileHandler',
            'formatter': 'standard'
        }
    },
    'loggers': {
        'movie': {
            'handlers': ['file_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
        'utilities': {
            'handlers': ['file_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
        'front_ui': {
            'handlers': ['file_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
        'detail_ui': {
            'handlers': ['file_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
        'library_ui': {
            'handlers': ['file_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
        'database': {
            'handlers': ['file_handler'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING)
