REM ** Start local developer server and datastore **
cd ..
dev_appserver.py --logs_path=naidom_logs --log_level=debug  naidom.api
cd naidom.api