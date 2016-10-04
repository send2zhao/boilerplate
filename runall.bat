::start "no1" "C:\Program Files\RabbitMQ Server\rabbitmq_server-3.6.2\sbin\rabbitmq-server.bat" restart

start "no2" python manage.py runserver

start "no3" python manage.py celery
