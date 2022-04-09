import dateutil.parser
from app_server import AppServer


aps = AppServer('127.0.0.1', 3000)
aps.auth('johndoe@e.mail', 'hunter2')
print(aps.attempt_book(dateutil.parser.isoparse('2022-04-10'), 'комната 1', 5))
print(aps.attempt_unbook(dateutil.parser.isoparse('2022-04-10'), 'комната 1', 5))
