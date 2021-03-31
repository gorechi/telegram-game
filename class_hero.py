from  functions import *
from constants import  *
from class_items import Money, Potion, Key, Rune, Book
from class_weapon import Weapon
from class_protection import Shield, Armor
from class_monsters import Monster

class Hero:
    def __init__(self, game, name, name1, gender, stren=10, dext=2, intel=0, health=20, weapon='', shield='', actions='бьет',
                 pockets=[]):
        self.game = game
        self.name = name
        self.name1 = name1
        self.gender = gender
        self.stren = int(stren)
        self.startStren = self.stren
        self.dext = int(dext)
        self.startDext = self.dext
        self.intel = int(intel)
        self.startIntel = self.intel
        self.health = int(health)
        self.actions = actions.split(',')
        self.weapon = weapon
        self.armor = ''
        self.shield = shield
        self.removed_shield = None
        self.pockets = pockets
        self.money = Money(self.game, 0)
        self.currentPosition = 0
        self.gameOver = False
        self.startHealth = self.health
        self.wins = 0
        self.rage = 0
        self.hide = False
        self.run = False
        self.level = 1
        self.exp = 0
        self.levels = [0, 100, 200, 350, 500, 750, 1000, 1300, 1600, 2000, 2500, 3000]
        self.elements = {'огонь': 0, 'вода': 0, 'земля': 0, 'воздух': 0, 'магия': 0}
        self.elementLevels = {'1': 2, '2': 4, '3': 7, '4': 10}
        self.weapon_mastery = {'рубящее': 0, "колющее": 0, "ударное": 0}
        self.directionsDict = {0: (0 - self.game.newCastle.rooms),
                               1: 1,
                               2: self.game.newCastle.rooms,
                               3: (0 - 1),
                               'наверх': (0 - self.game.newCastle.rooms),
                               'направо': 1,
                               'вправо': 1,
                               'налево': (0 - 1),
                               'лево': (0 - 1),
                               'влево': (0 - 1),
                               'вниз': self.game.newCastle.rooms,
                               'низ': self.game.newCastle.rooms,
                               'вверх': (0 - self.game.newCastle.rooms),
                               'верх': (0 - self.game.newCastle.rooms),
                               'право': 1}
        self.doorsDict = {'наверх': 0,
                          'направо': 1,
                          'вправо': 1,
                          'право': 1,
                          'налево': 3,
                          'влево': 3,
                          'лево': 3,
                          'вниз': 2,
                          'низ': 2,
                          'вверх': 0,
                          'верх': 0}

    def __str__(self):
        return 'hero'

    def do(self, command):
        commandDict = {'осмотреть': self.lookaround,
                       'идти': self.go,
                       'атаковать': self.fight,
                       'взять': self.take,
                       'обыскать': self.search,
                       'открыть': self.open,
                       'использовать': self.use,
                       'читать': self.read,
                       'чинить': self.repair,
                       'улучшить': self.enchant}
        a = command.find(' ')
        fullCommand = []
        if a < 0:
            a = len(command)
        fullCommand.append(command[:a])
        fullCommand.append(command[a + 1:])
        if fullCommand[0] == '?':
            text = []
            text.append(self.name + " может:")
            for i in commandDict.keys():
                text.append(i)
            tprint(self.game, text)
            return True
        c = commandDict.get(fullCommand[0], False)
        if not c:
            tprint(self.game, 'Такого ' + self.name + ' не умеет!')
        elif len(fullCommand) == 1:
            c()
        else:
            c(fullCommand[1])

    def repair(self, what=None):
        message = []
        if self.shield != '':
            if what.lower == 'щит' or what.lower == self.shield.name or what.lower == self.shield.name1:
                item = self.shield
        elif self.removed_shield != '':
            if what.lower == 'щит' or what.lower == self.removed_shield.name or what.lower == self.removed_shield.name1:
                item = self.removed_shield
        else:
            item = None
        if not what:
            message.append(self.name + ' не может чинить что-нибудь. Нужно понимать, какую вещь ремонтировать.')
        elif not item:
            message.append(self.name + ' не умеет чинить такие штуки.')
        elif item == '':
            message.append(self.name + ' осматривает свой рюкзак и не находит такой штуки.')
        else:
            need_money = item.accumulated_damage*10//1
            if need_money == 0:
                message.append(item.name1 + ' не нужно ремонтировать.')
            elif self.money.howmuchmoney >= need_money:
                item.accumulated_damage = 0
                self.money.howmuchmoney -= need_money
                message.append(self.name + ' успешно чинит ' + item.name1)
            else:
                message.append(self.name +
                               ' и рад бы починить ' +
                               item.name1 +
                               ', но ему не хватает денег на запчасти.')
        tprint(self.game, message)

    def inpockets(self, itemType):
        itemList = []
        for item in self.pockets:
            if isinstance(item, itemType):
                itemList.append(item)
        return itemList

    def action(self):
        if self.weapon == '':
            return randomitem(self.actions)
        else:
            return randomitem(self.weapon.actions)

    def second_weapon(self):
        for i in self.pockets:
            if isinstance(i, Weapon):
                return i
        return False

    def run_away(self, target):
        game = self.game
        room = game.newCastle.plan[self.currentPosition]
        if room.light:
            tprint(game, self.name + ' сбегает с поля боя.')
        else:
            tprint(game, self.name + ' в кромешной тьме пытается убежать хоть куда-нибудь.')
        a = dice(1, 2)
        if a == 1 and self.weapon != '':
            tprint(game, 'Убегая ' + self.name + ' роняет из рук ' + self.weapon.name1)
            if target.weapon == '' and target.carryweapon:
                target.weapon = self.weapon
            else:
                room.loot.pile.append(self.weapon)
            self.weapon = ''
        elif a == 2 and self.shield != '':
            tprint(game, 'Убегая ' + self.name + ' теряет ' + self.shield.name1)
            if target.shield == '' and target.carryshield:
                target.shield = self.shield
            else:
                room.loot.pile.append(self.shield)
            self.shield = ''
        a = dice(0, len(self.pockets))
        if a > 0:
            firstLine = self.name + ' бежит настолько быстро, что не замечает, как теряет:'
            text = [firstLine]
            for i in range(a):
                b = dice(0, len(self.pockets) - 1)
                text.append(self.pockets[b].name1)
                room.loot.pile.append(self.pockets[b])
                self.pockets.pop(b)
            tprint(game, text)
        availableDirections = []
        for i in range(4):
            if room.doors[i] == 1:
                availableDirections.append(i)
        if room.light:
            direction = availableDirections[dice(0,len(availableDirections)-1)]
        else:
            direction = dice(0, 3)
            if direction not in availableDirections:
                return False
        self.currentPosition += self.directionsDict[direction]
        room = game.newCastle.plan[self.currentPosition]
        room.visited = '+'
        game.state = 0
        self.lookaround()
        if room.center != '':
            if room.center.agressive and room.light:
                self.fight(room.center, True)
        return self.name + ' еле стоит на ногах.'

    def attack(self, target, action):
        game = self.game
        room = game.newCastle.plan[self.currentPosition]
        if room.light:
            targetName = target.name
            targetName1 = target.name1
            if self.rage > 1:
                rage = dice(2, self.rage)
            else:
                rage = 1
            meleAttack = dice(1, self.stren) * rage
        else:
            targetName = 'Неизвестная тварь из темноты'
            targetName1 = 'черт знает кого'
            rage = 1
            meleAttack = dice(1, self.stren) // dice (1, 3)
        self.run = False
        canUse = []
        for i in self.pockets:
            if i.canUseInFight:
                canUse.append(i)
        if action == '' or action == 'у' or action == 'ударить':
            tprint(game, showsides(self, target, game.newCastle))
            self.rage = 0
            self.hide = False
            if self.weapon != '':
                weaponAttack = self.weapon.attack()
                critical_probability = self.weapon_mastery[self.weapon.type] * 5
                damage_text = ' урона. '
                if dice(1, 100) <= critical_probability:
                    weaponAttack = weaponAttack * 2
                    damage_text = ' критического урона. '
                string1 = self.name + ' ' + self.action() + ' ' + targetName1 + ' используя ' + self.weapon.name + \
                          ' и наносит ' + str(meleAttack) + '+' + howmany(weaponAttack, 'единицу,единицы,единиц') + \
                          damage_text
            else:
                weaponAttack = 0
                string1 = self.name + ' бьет ' + targetName1 + ' не используя оружие и наносит ' + howmany(
                    meleAttack, 'единицу,единицы,единиц') + ' урона. '
            targetDefence = target.defence(self)
            if (weaponAttack + meleAttack - targetDefence) > 0:
                totalDamage = weaponAttack + meleAttack - targetDefence
            else:
                totalDamage = 0
            if totalDamage == 0:
               string2 = self.name + ' не смог пробить защиту ' + targetName1 + '.'
            elif targetDefence == 0:
               string2 = targetName + ' не имеет защиты и теряет ' + howmany(totalDamage, 'жизнь,жизни,жизней') + '.'
            else:
               string2 = targetName + ' использует для защиты ' + target.shield.name1 + ' и теряет ' + howmany(
                    totalDamage, 'жизнь,жизни,жизней') + '.'
            target.health -= totalDamage
            return string1 + string2
        elif action == 'з' or action == 'защититься' or action == 'защита':
            result = self.use_shield(target)
            if result:
                return result
        elif action == 'б' or action == 'бежать' or action == 'убежать':
            self.rage = 0
            self.hide = False
            result = self.run_away(target)
            if not result:
                return self.name + ' с разбега врезается в стену и отлетает в сторону. Схватка продолжается.'
            else:
                return result
        elif (action == 'и' or action == 'использовать') and len(canUse) > 0:
            tprint(game, 'Во время боя ' + self.name + ' может использовать:')
            for i in self.pockets:
                if i.canUseInFight:
                    tprint(game, i.name)
            while True:
                a = input('Что нужно использовать?')
                if a == 'ничего' or a == '':
                    break
                else:
                    itemUsed = False
                    for i in canUse:
                        if i.name == a or i.name1 == a:
                            if i.use(self, inaction=True) and isinstance(i, Potion):
                                self.pockets.remove(i)
                            itemUsed = True
                            break
                    if itemUsed:
                        break
                    tprint(game, 'Что-то не выходит')
        elif (action == 'с' or action == 'сменить оружие' or action == 'сменить'):
            weapon = self.weapon
            spareWeapon = False
            for item in self.pockets:
                if isinstance(item, Weapon):
                    spareWeapon = item
            self.weapon = spareWeapon
            self.pockets.remove(spareWeapon)
            self.pockets.append(weapon)
            message = [self.name + ' меняет ' + weapon.name1 + ' на ' + spareWeapon.name1 + '.']
            tprint(game, message)
        return True

    def use_shield(self, target):
        game = self.game
        if self.shield == '':
            return False
        else:
            tprint(game, showsides(self, target, game.newCastle))
            self.hide = True
            self.rage += 1
            return (self.name + ' уходит в глухую защиту, терпит удары и накапливает ярость.')

    def show(self):
        if self.weapon != '':
            string1 = ', а {0} в его руке добавляет к ней еще {1}+{2}.'.format(self.weapon.realname()[0],
                                                                               self.weapon.damage,
                                                                               self.weapon.permdamage())
        else:
            string1 = ' и он предпочитает сражаться голыми руками.'
        if self.shield != '':
            string2 = 'Его защищает {0} ({1}+{2})'.format(self.shield.realname()[0],
                                                           self.shield.protection,
                                                           self.shield.permprotection())
        else:
            string2 = 'У него нет защиты'
        tprint(self.game,
            '{0} - это смелый герой {7} уровня. Его сила - {1}{2} {3} и сейчас у него {4} здоровья, '
            'что составляет {5}% от максимально возможного.\n{0} имеет при себе {6} золотом.'.format(
                self.name, self.stren, string1, string2, howmany(self.health, 'единица,единицы,единиц'),
                self.health * 100 // self.startHealth, howmany(self.money.howmuchmoney, 'монету,монеты,монет'),
                self.level))

    def defence(self, attacker):
        result = 0
        if self.shield != '':
            result += self.shield.protect(attacker)
            print ('hero hide: ', self.hide)
            if self.hide:
                dice_result = dice(50, 75)/100
                print('dice result: ', dice_result)
                self.shield.accumulated_damage += dice_result
            else:
                dice_result = dice(10, 25) / 100
                print('dice result: ', dice_result)
                self.shield.accumulated_damage += dice_result
        if self.armor != '':
            result += self.armor.protect(attacker)
        return result

    def lose(self, winner):
        self.health = self.startHealth
        self.stren = self.startStren
        self.dext = self.startDext
        self.intel = self.startIntel
        self.currentPosition = 0

    def win(self, loser):
        self.health = self.startHealth
        self.stren = self.startStren
        self.dext = self.startDext
        self.intel = self.startIntel
        self.wins += 1
        tprint(self.game, self.name + ' получает ' + howmany(loser.exp, 'единицу,единицы,единиц') + ' опыта!')
        self.exp += loser.exp
        if self.exp > self.levels[self.level]:
            self.levelup()

    def levelup(self):
        self.game.state = 3
        level_up_message = []
        level_up_message.append(self.name + ' получает новый уровень!')
        level_up_message.append('Что необходимо прокачать: здоровье, силу, ловкость или интеллект?')
        tprint(self.game, level_up_message, 'levelup')
        self.level += 1
        return True

    def gameover(self, goaltype, goal):
        if goaltype == 'killall':
            if self.game.newCastle.monsters() == 0:
                tprint(self.game, self.name + ' убил всех монстров в замке и выиграл в этой игре!')
                return True
            else:
                return False
        return False

    def lookaround(self, a=''):
        game = self.game
        newCastle = self.game.newCastle
        if a == '':
            newCastle.plan[self.currentPosition].show(game.player)
            newCastle.plan[self.currentPosition].map()
        elif a == 'себя':
            self.show()
        elif a == 'рюкзак':
            text = []
            if len(self.pockets) == 0 and self.money.howmuchmoney == 0:
                text.append(self.name + ' осматривает свой рюкзак и обнаруживает, что тот абсолютно пуст.')
            else:
                text.append(self.name + ' осматривает свой рюкзак и обнаруживает в нем:')
                for i in range(len(self.pockets)):
                    text.append(str(i+1) + ': ' + self.pockets[i].show())
                text.append(self.money.show())
            tprint(game, text)
        elif a in self.directionsDict.keys():
            if newCastle.plan[self.currentPosition].doors[self.doorsDict[a]] == 0:
                tprint (game, self.name + ' осматривает стену и не находит ничего заслуживающего внимания.')
            else:
                tprint(game, newCastle.plan[self.directionsDict[a]].showThroughKeyHole(self))
        if newCastle.plan[self.currentPosition].center != '':
            if (a == newCastle.plan[self.currentPosition].center.name or a == newCastle.plan[
                self.currentPosition].center.name1 or a == newCastle.plan[self.currentPosition].center.name[
                0]) and newCastle.plan[self.currentPosition].monster():
                tprint(game, showsides(self, newCastle.plan[self.currentPosition].center, newCastle))

        if self.weapon != '':
            if a == self.weapon.name or a == self.weapon.name1 or a == 'оружие':
                tprint(game, self.weapon.show())
        if self.shield != '':
            if a == self.shield.name or a == self.shield.name1 or a == 'защиту':
                tprint(game, self.shield.show())

        if len(self.pockets) > 0:
            text = []
            for i in self.pockets:
                if a == i.name or a == i.name1:
                    text.append(i.show())
            tprint(game, text)

    def go(self, direction):
        game = self.game
        newCastle = self.game.newCastle
        room = newCastle.plan[self.currentPosition]
        if direction not in self.directionsDict.keys():
            tprint(game, self.name + ' не знает такого направления!')
            return False
        elif room.doors[self.doorsDict[direction]] == 0:
            if room.light:
                message = ['Там нет двери. ' + self.name + ' не может туда пройти!']
            else:
                message = ['В темноте ' + self.name + ' врезается во что-то носом.']
            tprint(game, message)
            return False
        elif room.doors[self.doorsDict[direction]] == 2:
            if room.light:
                message = ['Эта дверь заперта. ' + self.name + ' не может туда пройти, нужен ключ!']
            else:
                message = ['В темноте ' + self.name + ' врезается во что-то носом.']
            tprint(game, message)
            return False
        else:
            self.currentPosition += self.directionsDict[direction]
            room = newCastle.plan[self.currentPosition]
            room.visited = '+'
            room.show(self)
            room.map()
            if room.monster():
                if room.center.agressive and room.light:
                    self.fight(room.center.name, True)
            return True

    def fight(self, enemy, agressive = False):
        game = self.game
        newCastle = self.game.newCastle
        room = newCastle.plan[self.currentPosition]
        whoisfighting = room.monster()
        if not whoisfighting:
            tprint(game, 'Не нужно кипятиться. Тут некого атаковать')
            return False
        if (whoisfighting.name != enemy
                    and whoisfighting.name1 != enemy
                    and whoisfighting.name[0] != enemy) \
                    and enemy != '':
            tprint(game, self.name + ' не может атаковать. В комнате нет такого существа.')
            return False
        game.state = 1
        if agressive:
            whoFirst = 2
        else:
            whoFirst = dice(1, 2)
        if whoFirst == 1:
            tprint(game, game.player.name + ' начинает схватку!', 'fight')
            self.attack(whoisfighting, 'атаковать')
        else:
            if room.light:
                message = [whoisfighting.name + ' начинает схватку!']
            else:
                message = ['Что-то жуткое и непонятное нападает первым из темноты.']
            tprint(game, message, 'fight')
            tprint(game, whoisfighting.attack(self))
            return True

    def search(self, item=False):
        game = self.game
        newCastle = self.game.newCastle
        room = newCastle.plan[self.currentPosition]
        message = []
        print ('room.center: ', room.center)
        chestinroom = False
        enemyinroom = False
        if room.center != '':
            if isinstance(room.center, Monster):
                enemyinroom = room.center
        if room.ambush != '':
            enemyinambush = room.ambush
        else:
            enemyinambush = False
        if not room.light:
            message.append('В комнате настолько темно, что невозможно что-то отыскать.')
            tprint(game, message)
            return True
        if enemyinroom:
            message.append(enemyinroom.name + " мешает толком осмотреть комнату.")
            tprint(game, message)
            return True
        if enemyinambush and not item:
            room.center = enemyinambush
            room.ambush = ''
            enemyinambush = False
            enemyinroom = room.center
            message.append('Неожиданно из засады выскакивает ' + enemyinroom.name + ' и нападает на ' + self.name1)
            tprint (game, message)
            self.fight(enemyinroom, True)
            return True
        if not item:
            if chestinroom:
                message.append("В комнате стоит " + chestinroom.name)
            for furniture in room.furniture:
                message.append(furniture.where + ' ' + furniture.state + ' ' + furniture.name)
            if room.loot != '' and len(room.loot.pile) > 0:
                message.append('В комнате есть:')
                for i in room.loot.pile:
                    message.append(i.name)
            else:
                message.append('В комнате нет ничего интересного.')
            tprint(game, message)
            return True
        else:
            searchableItems = []
            searchableItems.extend(room.furniture)
            whatToSearch = False
            if chestinroom:
                searchableItems.append(chestinroom)
            for i in searchableItems:
                if i.name.lower() == item.lower() or i.name1.lower() == item.lower():
                    whatToSearch = i
            if not whatToSearch:
                message.append('В комнате нет такой вещи.')
            elif whatToSearch.locked:
                message.append('Нельзя обыскать ' + whatToSearch.name1 + '. Там заперто.')
            elif len(whatToSearch.loot.pile) > 0:
                message.append(self.name + ' осматривает ' + whatToSearch.name1 + ' и находит:')
                for i in whatToSearch.loot.pile:
                    message.append(i.name)
                    room.loot.pile.append(i)
                if len(whatToSearch.loot.pile) > 0:
                    message.append('Все эти вещи теперь лежат навиду.')
            elif len(whatToSearch.loot.pile) == 0:
                message.append(whatToSearch.name + ' ' + whatToSearch.empty)
            tprint(game, message)
            return True

    def can_take(self, obj):
        classes = [Weapon, Shield, Armor]
        for i in classes:
            if isinstance(obj, i):
                return False
        return True

    def take(self, item='все'):
        game = self.game
        castle = self.game.newCastle
        currentLoot = castle.plan[self.currentPosition].loot
        print("+"*40)
        for i in currentLoot.pile:
            print(i.name)
        print("+" * 40)
        if currentLoot == '':
            tprint(game, 'Здесь нечего брать.')
            return False
        elif item == 'все' or item == 'всё' or item == '':
            items_to_remove = []
            for item in currentLoot.pile:
                if self.can_take(item):
                    item.take(self)
                    items_to_remove.append(item)
            for item in items_to_remove:
                currentLoot.pile.remove(item)
            return True
        else:
            for i in currentLoot.pile:
                if i.name.lower() == item or i.name1.lower() == item:
                    i.take(self)
                    currentLoot.pile.remove(i)
                    return True
        tprint(game, 'Такой вещи здесь нет.')
        return False

    def drop(self, object):
        game = self.game
        newCastle = self.game.newCastle
        currentLoot = newCastle.plan[self.currentPosition].loot
        currentLoot.pile.append(object)
        if self.armor == object:
            self.armor = ''
        if self.shield == object:
            self.shield = ''
        if self.weapon == object:
            self.weapon = ''
        if object in self.pockets:
            self.pockets.remove(object)

    def open(self, item=''):
        game = self.game
        newCastle = self.game.newCastle
        room = newCastle.plan[self.currentPosition]
        key = False
        for i in self.pockets:
            if isinstance(i, Key):
                key = i
        if not key:
            message = ['Чтобы что-то открыть нужен хотя бы один ключ.']
            tprint(game, message)
            return False
        whatIsInRoom = []
        if len(room.furniture) > 0:
            for furniture in room.furniture:
                if furniture.locked:
                    whatIsInRoom.append(furniture)
        print (whatIsInRoom)
        print ('item: ', item)
        if item == '' or (not self.doorsDict.get(item, False) and self.doorsDict.get(item, True) != 0):
            if len(whatIsInRoom) == 0:
                if room.light:
                    message = ['В комнате нет вещей, которые можно открыть.']
                else:
                    message = [self.name + ' шарит в темноте руками, но не нащупывает ничего интересного']
                tprint(game, message)
                return False
            elif item == '' and len(whatIsInRoom) > 1:
                if room.light:
                    message = ['В комнате слишком много запертых вещей. ' +
                               self.name +
                               ' не понимает, что ему нужно открыть.']
                else:
                    message = [self.name + ' шарит в темноте руками, но не нащупывает ничего интересного']
                tprint(game, message)
                return False
            elif item != '':
                if room.light:
                    for furniture in whatIsInRoom:
                        if furniture.name.lower() == item.lower() or furniture.name1.lower() == item.lower():
                            self.pockets.remove(key)
                            furniture.locked = False
                            message = [self.name + ' отпирает ' + furniture.name1 + ' ключом.']
                            tprint(game, message)
                            return True
                    message = [self.name + ' не находит в комнате такой вещи. Отпирать нечего.']
                    tprint(game, message)
                else:
                    message = [self.name + ' шарит в темноте руками, но не нащупывает ничего интересного']
                tprint(game, message)
                return True
            else:
                if room.light:
                    self.pockets.remove(key)
                    whatIsInRoom[0].locked = False
                    message = [self.name + ' отпирает ' + whatIsInRoom[0].name1 + ' ключом.']
                else:
                    message = [self.name + ' шарит в темноте руками, но не нащупывает ничего интересного']
                tprint(game, message)
                return True
        else:
            if not room.light:
                message = [self.name + ' ничего не видит и не может нащупать замочную скважину.']
                tprint (game, message)
                return False
            if not self.doorsDict.get(item, False) and self.doorsDict.get(item, True) != 0:
                tprint(game, self.name + ' не может это открыть.')
                return False
            elif newCastle.plan[self.currentPosition].doors[self.doorsDict[item]] != 2:
                tprint(game, 'В той стороне нечего открывать.')
                return False
            else:
                self.pockets.remove(key)
                room.doors[self.doorsDict[item]] = 1
                j = self.doorsDict[item] + 2 if (self.doorsDict[item] + 2) < 4 else self.doorsDict[item] - 2
                newCastle.plan[self.currentPosition + self.directionsDict[item]].doors[j] = 1
                tprint(game, self.name + ' открывает дверь.')

    def use(self, item='', infight=False):
        game = self.game
        newCastle = self.game.newCastle
        if item == '':
            tprint(game, self.name + ' не понимает, что ему надо использовать.')
        elif item.isdigit():
            if int(item)-1 < len(self.pockets):
                i = self.pockets[int(item)-1]
                if isinstance(i, Potion) and i.use(self, False):
                    self.pockets.remove(i)
                elif not isinstance(i, Potion):
                    i.use(self, False)
                return True
            else:
                tprint(game, self.name + ' не нашел такой вещи у себя в карманах.')
                return False
        else:
            for i in self.pockets:
                if i.name.lower() == item.lower() or i.name1.lower() == item.lower():
                    if isinstance(i, Potion)  and i.use(self, inaction = False):
                        self.pockets.remove(i)
                    else:
                        i.use(self, inaction = False)
                    return True
            tprint(game, self.name + ' не нашел такой вещи у себя в карманах.')

    def enchant(self, item=''):
        game = self.game
        newCastle = self.game.newCastle
        runeList = self.inpockets(Rune)
        if len(runeList) == 0:
            tprint(game, self.name + 'не может ничего улучшать. В карманах не нашлось ни одной руны.')
            return False
        if item == '':
            tprint(game, self.name + ' не понимает, что ему надо улучшить.')
            return False
        elif item == 'оружие' and self.weapon != '':
            game.selectedItem = self.weapon
        elif item in ['защиту', 'защита'] and self.shield != '':
            game.selectedItem = self.shield
        elif item.isdigit() and int(item)-1 <= len(self.pockets):
            game.selectedItem = self.pockets[int(item)-1]
        else:
            for i in self.pockets:
                if i.name.lower() == item.lower() or i.name1.lower() == item.lower():
                    game.selectedItem = i
                else:
                    tprint(game, self.name + ' не нашел такой вещи у себя в карманах.')
                    return False
        if game.selectedItem != '' and isinstance(game.selectedItem, Weapon) or isinstance(game.selectedItem, Shield):
            text = []
            text.append(self.name + ' может использовать следующие руны:')
            for rune in runeList:
                text.append(str(runeList.index(rune)+1) + ': ' + str(rune))
            text.append('Введите номер руны или "отмена" для прекращения улучшения')
            #Здесь нужна доработка т.к. управление переходит на работу с рунами
            game.state = 2
            tprint(game, text, 'enchant')
        else:
            tprint(game, self.name + ' не может улучшить эту вещь.')
            return False

    def read(self, what):
        books = []
        message = []
        for i in self.pockets:
            if isinstance(i, Book):
                books.append(i)
        if len(books) > 0:
            book = None
            for i in books:
                if not what:
                    book = randomitem(books, False)
                    message.append(self.name + ' роется в рюкзаке и находит первую попавшуюся книгу.')
                elif i.name.lower() == what.lower() or i.name1.lower() == what.lower():
                    book = i
                    message.append(self.name + ' читает ' + book.alt_name + '.')
            message.append(book.text)
            message += book.print_mastery(self)
            message.append('Он решает больше не носить книгу с собой и оставляет ее в незаметном месте.')
            self.weapon_mastery[book.weapon_type] += 1
            print (self.weapon_mastery)
            self.pockets.remove(book)
        else:
            message.append('В рюкзаке нет ни одной книги. Грустно, когда нечего почитать.')
        tprint(self.game, message)
        return True

