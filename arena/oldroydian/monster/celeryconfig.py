BROKER_HOST = 'localhost'
BROKER_PORT = 5672
BROKER_USER = 'mastercontroller'
BROKER_PASSWORD = 'XSPnDy5G'
BROKER_VHOST = 'arena'

CELERY_RESULT_BACKEND = 'amqp'
CELERYD_CONCURRENCY = 1
CELERYD_MAX_TASKS_PER_CHILD = 50
CELERYD_SOFT_TASK_TIME_LIMIT = 600
CELERY_IMPORTS = ("tentacle", )
