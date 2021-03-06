
worker-local:
	watchmedo \
	auto-restart \
	--directory /app/reader/ \
	--recursive \
	--pattern '*.py' \
	-- \
	celery worker \
	--broker redis://${CELERY_HOST}:6379 \
	--app reader \
	--concurrency 2 \
	--beat \
	--loglevel info

worker-prod:
	echo "Starting remote syslog" && \
	touch /var/log/celery.log && \
	remote_syslog \
	--hostname "${PAPERTRAIL_HOSTNAME}" \
	--dest-port "${PAPERTRAIL_PORT}" \
	--dest-host "${PAPERTRAIL_URL}" \
	--pid-file /var/run/remote_syslog.pid \
	/var/log/celery.log && \
	echo "Starting celery" && \
	celery worker \
	--broker redis://${CELERY_HOST}:6379 \
	--app reader \
	--concurrency 2 \
	--beat \
	--logfile /var/log/celery.log \
	--loglevel info

web-local:
	./manage.py runserver 0.0.0.0:8000

web-prod:
	echo "Starting reader app as `whoami`" && \
	echo "Starting remote syslog" && \
	mkdir -p /var/log/gunicorn && \
	touch /var/log/gunicorn/access.log && \
	touch /var/log/gunicorn/error.log && \
	remote_syslog \
	--hostname "${PAPERTRAIL_HOSTNAME}" \
	--dest-port "${PAPERTRAIL_PORT}" \
	--dest-host "${PAPERTRAIL_URL}" \
	--pid-file /var/run/remote_syslog.pid \
	/var/log/gunicorn/access.log \
	/var/log/gunicorn/error.log && \
	echo "Running migrations" && \
	./manage.py migrate && \
	echo "Starting gunicorn" && \
	gunicorn reader.wsgi:application \
	--name reader \
	--workers 2 \
	--bind 0.0.0.0:8005 \
	--capture-output \
	--log-level info \
	--error-logfile /var/log/gunicorn/error.log \
	--access-logfile /var/log/gunicorn/access.log
