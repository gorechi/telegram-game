from functions import *
from class_basic import Loot, Money
from class_weapon import Weapon
from class_protection import Shield, Armor
from class_items import Rune

class Monster:
    def __init__(self, game, name='', name1='', stren=10, health=20, actions='бьет', state='стоит', agressive=False,
                 carryweapon=True, carryshield=True, wearArmor=True):
        self.game = game
        self.name = name
        self.name1 = name1
        self.stren = int(stren)
        self.health = int(health)
        self.actions = actions.split(',')
        self.state = state
        self.weapon = ''
        self.shield = ''
        self.removed_shield = None
        self.armor = ''
        self.money = 5
        self.currentPosition = 0
        self.startHealth = self.health
        self.loot = Loot(self.game)
        self.stink = False
        self.hide = False
        self.run = False
        self.wounded = False
        self.keyHole = 'видит какую-то неясную фигуру.'
        if carryweapon == 'False':
            self.carryweapon = False
        else:
            self.carryweapon = True
        if wearArmor == 'False':
            self.wearArmor = False
        else:
            self.wearArmor = True
        if carryshield == 'False':
            self.carryshield = False
        else:
            self.carryshield = True
        if agressive == 'True':
            self.agressive = True
        else:
            self.agressive = False
        self.exp = self.stren * dice(1, 10) + dice(1, self.health)

    def on_create(self):
        return True

    def __str__(self):
        return self.name

    def give(self, item):
        if isinstance(item, Weapon) and self.weapon == '' and self.carryweapon:
            if item.twohanded:
                if self.shield != '':
                    shield = self.shield
                    self.shield = ''
                    self.game.newCastle.plan[self.currentPosition].loot.pile.append(shield)
            self.weapon = item
        elif isinstance(item, Shield) and self.shield == '' and self.carryshield:
            if self.weapon != '':
                if self.weapon.twohanded:
                    self.loot.pile.append(item)
                    return True
                else:
                    self.shield = item
                    return True
            self.shield = item
            return True
        elif isinstance(item, Armor) and self.armor == '' and self.wearArmor:
            self.armor = item
        elif isinstance(item, Rune):
            if item.damage >= item.defence:
                if self.weapon != '':
                    if self.weapon.enchant(item):
                        return True
                if self.armor != '':
                    if self.armor.enchant(item):
                        return True
                if self.shield != '':
                    if self.shield.enchant(item):
                        return True
                self.loot.pile.append(item)
                return True
            else:
                if self.shield != '':
                    if self.shield.enchant(item):
                        return True
                if self.armor != '':
                    if self.armor.enchant(item):
                        return True
                if self.weapon != '':
                    if not self.weapon.enchant(item):
                        return True
                self.loot.pile.append(item)
                return True
        else:
            self.loot.pile.append(item)

    def action(self):
        if self.weapon == '':
            return randomitem(self.actions)
        else:
            return randomitem(self.weapon.actions)

    def mele(self):
        room = self.game.newCastle.plan[self.currentPosition]
        if room.light:
            return dice(1, self.stren)
        else:
            return dice(1, self.stren) // dice(1, 3)

    def attack(self, target):
        game = self.game
        newCastle = self.game.newCastle
        room = newCastle.plan[self.currentPosition]
        if room.light:
            selfName = self.name
            selfName1 = self.name1
        else:
            selfName = 'Кто-то страшный'
            selfName1 = 'черт знает кого'
        text = []
        meleAttack = self.mele()
        if self.weapon != '':
            weaponAttack = self.weapon.attack()
            text.append(selfName + ' ' + self.action() + ' ' + target.name1 + ' используя ' + self.weapon.name1 \
                      + ' и наносит ' + str(meleAttack) + '+' \
                      + howmany(weaponAttack, 'единицу,единицы,единиц') + ' урона. ')
        else:
            weaponAttack = 0
            text.append(selfName + ' бьет ' + target.name1 + ' не используя оружия и наносит ' + howmany(
                meleAttack, 'единицу,единицы,единиц') + ' урона. ')
        totalAttack = weaponAttack + meleAttack
        targetDefence = target.defence(self)
        if (totalAttack - targetDefence) > 0:
            totalDamage = weaponAttack + meleAttack - targetDefence
            if targetDefence == 0:
                text.append(target.name + ' беззащитен и теряет ' + howmany(totalDamage, 'жизнь,жизни,жизней') + '.')
            else:
                text.append(target.name + ' использует для защиты ' + target.shield.name + ' и теряет ' \
                          + howmany(totalDamage, 'жизнь,жизни,жизней') + '.')
        else:
            totalDamage = 0
            text.append(selfName + ' не смог пробить защиту ' + target.name1 + '.')
        if target.shield != '':
            shield = target.shield
            rand = dice(1, 100)
            dam = totalAttack * target.shield.accumulated_damage
            print ('shield acc damage: ', target.shield.accumulated_damage, 'rand: ', rand, 'dam: ', dam)
            if rand < dam:
                text.append(selfName + ' наносит настолько сокрушительный удар, что ломает щит соперника.')
                game.allShields.remove(shield)
                target.shield = ''
        target.health -= totalDamage
        if target.health <= 0:
            game.state = 0
            target.lose(self)
            self.win(target)
            text.append(target.name + ' терпит сокрушительное поражение и позорно убегает ко входу в замок.')
            tprint(game, text, 'off')
        else:
            tprint(game, text)
        return True

    def defence(self, attacker):
        result = 0
        if self.shield != '':
            result += self.shield.protect(attacker)
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
        game = self.game
        newCastle = self.game.newCastle
        result = dice(1, 10)
        where = newCastle.plan[self.currentPosition]
        if where.loot == '':
            b = Loot()
            where.loot = b
        if result < 6 or self.wounded:
            if self.money > 0:
                a = Money(self.money)
                where.loot.pile.append(a)
                where.loot.pile.extend(self.loot.pile)
            if self.shield != '':
                where.loot.pile.append(self.shield)
            if self.weapon != '':
                where.loot.pile.append(self.weapon)
            where.center = ''
        else:
            self.wounded = True
            aliveString = self.name + ' остается вживых и '
            weaknessAmount = ceil(self.stren * 0.4)
            illAmount = ceil(self.startHealth * 0.4)
            if result < 10:
                if result == 6:
                    aliveString += 'получает легкое ранение в руку. '
                    if self.weapon != '':
                        aliveString += 'На пол падает ' + self.weapon.name + '. '
                        where.loot.pile.append(self.weapon)
                        self.weapon = ''
                    elif self.shield != '':
                        aliveString += 'На пол падает ' + self.shield.neme + '. '
                        where.loot.pile.append(self.shield)
                        self.shield = ''
                elif result == 7:
                    aliveString += 'истекает кровью, теряя при этом ' \
                                   + howmany(weaknessAmount, 'единицу,единицы,единиц') + ' силы. '
                    self.stren -= weaknessAmount
                    self.health = self.startHealth
                elif result == 8:
                    aliveString += 'приходит в ярость, получая при этом ' \
                                   + howmany(weaknessAmount, 'единицу,единицы,единиц') + ' силы и теряя ' \
                                   + howmany(illAmount, 'жизнь,жизни,жизней') + '. '
                    self.stren += weaknessAmount
                    self.health = self.startHealth - illAmount
                else:
                    aliveString += 'получает контузию, теряя при этом ' \
                                   + howmany(weaknessAmount, 'единицу,единицы,единиц') + ' силы и получая ' \
                                   + howmany(illAmount, 'жизнь,жизни,жизней') + '. '
                    self.stren -= weaknessAmount
                    self.health = self.startHealth + illAmount
                runningMonsters = [self]
                if self.place(newCastle):
                    aliveString += self.name + ' убегает из комнаты.'
                    tprint(game, aliveString)
                    where.center = ''
            else:
                aliveString += 'получает ранение в ногу и не может двигаться, теряя при этом '  \
                               + howmany(weaknessAmount, 'единицу,единицы,единиц') + ' силы и ' \
                               + howmany(illAmount, 'жизнь,жизни,жизней') + '.'
                self.stren -= weaknessAmount
                self.health = self.startHealth - illAmount
                tprint(game, aliveString)

    def win(self, loser):
        self.health = self.startHealth

    def place(self, castle, roomr_to_place = None):
        if roomr_to_place:
            room = roomr_to_place
        else:
            emptyRooms = [a for a in castle.plan if (a.center == '' and a.ambush == '')]
            room = randomitem(emptyRooms, False)
        if dice(1, 5) == 1:
            places_to_hide = []
            for i in room.furniture:
                if i.can_hide:
                    places_to_hide.append(i)
            places_to_hide.append(room)
            where_to_hide = randomitem(places_to_hide, False)
            where_to_hide.ambush = self  # Монстр садится в засаду
        else:
            room.center = self
        self.currentPosition = room.position
        if self.stink:
            print('У нас есть вонючка!')
            print(self.name, room.position)
            castle.stink(room, 3)
            castle.stink_map()
        return True


class Plant(Monster):
    def __init__(self, game, name='', name1='', stren=10, health=20, actions='бьет', state='растёт', agressive=False,
                 carryweapon=False, carryshield=False):
        super().__init__(game, name, name1, stren, health, actions, state, agressive, carryweapon, carryshield)
        self.carryshield = False
        self.carryweapon = False
        self.wearArmor = False
        self.agressive = False

    def grow(self):
        newPlant = Plant(self.name, self.name1, self.stren, self.health, 'бьет', 'растет', False, False, False)
        return newPlant

    def win(self, loser):
        game = self.game
        newCastle = self.game.newCastle
        self.health = self.startHealth
        for i in range(4):
            if newCastle.plan[self.currentPosition].doors[i] == 1:
                if i == 0 and newCastle.plan[self.currentPosition - newCastle.rooms].center == '':
                    copy = self.grow()
                    newCastle.plan[self.currentPosition - newCastle.rooms].center = copy
                    copy.currentPosition = self.currentPosition - newCastle.rooms
                elif i == 1 and newCastle.plan[self.currentPosition + 1].center == '':
                    copy = self.grow()
                    newCastle.plan[self.currentPosition + 1].center = copy
                    copy.currentPosition = self.currentPosition + 1
                elif i == 2 and newCastle.plan[self.currentPosition + newCastle.rooms].center == '':
                    copy = self.grow()
                    newCastle.plan[self.currentPosition + newCastle.rooms].center = copy
                    copy.currentPosition = self.currentPosition + newCastle.rooms
                elif i == 3 and newCastle.plan[self.currentPosition - 1].center == '':
                    copy = self.grow()
                    newCastle.plan[self.currentPosition - 1].center = copy
                    copy.currentPosition = self.currentPosition - 1

    def lose(self, winner):
        game = self.game
        newCastle = self.game.newCastle
        where = newCastle.plan[self.currentPosition]
        if where.loot == '':
            b = Loot()
            where.loot = b
        if self.money > 0:
            a = Money(game, self.money)
            where.loot.pile.append(a)
            where.loot.pile.extend(self.loot.pile)
        if self.shield != '':
            where.loot.pile.append(self.shield)
        if self.weapon != '':
            where.loot.pile.append(self.weapon)
        where.center = ''

    def place(self, castle, roomr_to_place = None):
        if roomr_to_place:
            room = roomr_to_place
        else:
            emptyRooms = [a for a in castle.plan if (a.center == '' and a.ambush == '')]
            room = randomitem(emptyRooms, False)
        room.center = self
        self.currentPosition = room.position

class Walker(Monster):
    def __init__(self, game, name='', name1='', stren=10, health=20, actions='бьет', state='стоит', agressive=True,
                 carryweapon=True, carryshield=True):
        super().__init__(game, name, name1, stren, health, actions, state, agressive, carryweapon, carryshield)

class Berserk(Monster):
    def __init__(self, game, name='', name1='', stren=10, health=20, actions='бьет', state='стоит', agressive=True,
                 carryweapon=True, carryshield=True):
        super().__init__(game, name, name1, stren, health, actions, state, agressive, carryweapon, carryshield)
        self.agressive = True
        self.carryshield = False
        self.rage = 0
        self.base_health = health

    def mele(self):
        self.rage = (int(self.base_health) - int(self.health)) // 3
        return dice(1, (self.stren + self.rage))

    def place(self, castle, roomr_to_place = None):
        if roomr_to_place:
            room = roomr_to_place
        else:
            emptyRooms = [a for a in castle.plan if (a.center == '' and a.ambush == '')]
            room = randomitem(emptyRooms, False)
        room.center = self
        self.currentPosition = room.position

class Shapeshifter(Monster):
    def __init__(self, game, name='', name1='', stren=10, health=20, actions='бьет', state='стоит', agressive=True,
                 carryweapon=False, carryshield=True):
        super().__init__(game, name, name1, stren, health, actions, state, agressive, carryweapon, carryshield)
        self.shifted = False
        self.agressive = True

    def defence(self, attacker):
        if not self.shifted:
            self.shifted = True
            self.stren = attacker.stren
            if attacker.weapon != '' and self.weapon == '':
                self.weapon = attacker.weapon
                weaponString = ' и ' + self.weapon.name + ' в руках.'
            else:
                weaponString = ''
            tprint(self.game, self.name +
                   ' меняет форму и становится точь в точь как ' +
                   attacker.name +
                   '. У него теперь сила ' +
                   str(self.stren) +
                   weaponString)
        result = 0
        if self.shield != '':
            result += self.shield.protect(attacker)
            if self.hide:
                dice_result = dice(50, 75) / 100
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
        where = self.game.newCastle.plan[self.currentPosition]
        if where.loot == '':
            b = Loot()
            where.loot = b
        if self.money > 0:
            a = Money(self.money)
            where.loot.pile.append(a)
            where.loot.pile.extend(self.loot.pile)
        if self.shield != '':
            where.loot.pile.append(self.shield)
        where.center = ''


class Vampire(Monster):
    def __init__(self, game, name='', name1='', stren=10, health=20, actions='бьет', state='стоит', agressive=False,
                 carryweapon=True, carryshield=True):
        super().__init__(game, name, name1, stren, health, actions, state, agressive, carryweapon, carryshield)

    def attack(self, target):
        game = self.game
        newCastle = self.game.newCastle
        room = newCastle.plan[self.currentPosition]
        if room.light:
            selfName = self.name
            selfName1 = self.name1
        else:
            selfName = 'Кто-то страшный'
            selfName1 = 'черт знает кого'
        text = []
        meleAttack = self.mele()
        if self.weapon != '':
            weaponAttack = self.weapon.attack()
            text.append(selfName +
                        ' ' +
                        self.action() +
                        ' ' +
                        target.name1 +
                        ' используя ' +
                        self.weapon.name +
                        ' и наносит ' +
                        str(meleAttack) +
                        '+' +
                        str(weaponAttack) +
                        ' единиц урона. ')
        else:
            weaponAttack = 0
            text.append(selfName +
                        ' ' +
                        self.action() +
                        ' ' +
                        target.name1 +
                        ' не используя оружия и наносит ' +
                        howmany(meleAttack, 'единицу,единицы,единиц') +
                        ' урона. ')
        targetDefence = target.defence(self)
        totalAttack = weaponAttack + meleAttack
        if (totalAttack - targetDefence) > 0:
            totalDamage = weaponAttack + meleAttack - targetDefence
        else:
            totalDamage = 0
        if totalDamage == 0:
            text.append(selfName + ' не смог пробить защиту ' + target.name1 + '.')
        elif targetDefence == 0:
            text.append(target.name + ' беззащитен и теряет ' +
                        howmany(totalDamage, 'жизнь,жизни,жизней') +
                        '. ' +
                        selfName +
                        ' высасывает ' +
                        str(totalDamage // 2) +
                        ' себе.')
        else:
            text.append(target.name +
                        ' использует для защиты ' +
                        target.shield.name +
                        ' и теряет ' +
                        howmany(totalDamage, 'жизнь,жизни,жизней') +
                        '.' +
                        selfName +
                        ' высасывает ' +
                        str(totalDamage // 2) +
                        ' себе.')
        if target.shield != '':
            shield = target.shield
            rand = dice(1, 100)
            dam = totalAttack * target.shield.accumulated_damage
            print ('shield acc damage: ', target.shield.accumulated_damage, 'rand: ', rand, 'dam: ', dam)
            if rand < dam:
                text.append(selfName + ' наносит настолько сокрушительный удар, что ломает щит соперника.')
                game.allShields.remove(shield)
                target.shield = ''
        target.health -= totalDamage
        self.health += totalDamage // 2
        if target.health <= 0:
            game.state = 0
            target.lose(self)
            text.append(target.name + ' терпит сокрушительное поражение и позорно убегает ко входу в замок.')
            tprint(game, text, 'off')
        else:
            tprint(game, text)
        return True

    def place(self, castle, roomr_to_place = None):
        if roomr_to_place:
            room = roomr_to_place
        else:
            emptyRooms = [a for a in castle.plan if (a.ambush == '' and not a.light)]
            room = randomitem(emptyRooms, False)
        places_to_hide = []
        for i in room.furniture:
            if i.can_hide:
                places_to_hide.append(i)
        places_to_hide.append(room)
        where_to_hide = randomitem(places_to_hide, False)
        where_to_hide.ambush = self  # Монстр садится в засаду
        self.currentPosition = room.position
        return True

