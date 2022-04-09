from app_server import AppServer


aps = AppServer('127.0.0.1', 3000)
aps.auth('johndoe@e.mail', 'hunter2')
aps.try_protected()
