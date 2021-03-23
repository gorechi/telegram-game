import json

class Monster():
    def __init__(self):
        self.name = None
        self.name1 = None

file = 'monsters.json'
with open(file, encoding='utf-8') as read_data:
    parsed_data = json.load(read_data)
print(parsed_data)
monsters = []
for i in parsed_data:
    print(i)
    monster = Monster()
    for param in i:
        vars(monster)[param] = i[param]
    print(monster.name, monster.name1, monster.stren)