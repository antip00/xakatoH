import requests
import json


s = requests.Session()

payload = {
    'username': 'johndoe@e.mail',
    'password': 'hunter2'
}

p = s.post('http://127.0.0.1:3000/auth/token', data=payload)
print(p)

content = json.loads(p.content.decode('utf8'))
print(content)

g = s.get('http://127.0.0.1:3000/protected', headers={'Authorization': 'Bearer {}'.format(content['access_token'])})

print(g.content)
