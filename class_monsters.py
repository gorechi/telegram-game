from functions import randomitem, howmany, tprint
from class_basic import Loot, Money
from class_weapon import Weapon
from class_protection import Shield, Armor
from class_items import Rune
from settings import *
from random import randint as dice
from math import ceil

class Monster:
    def __init__(self,
                 game,
                 name=s_monster_name,
                 name1=s_monster_name1,
                 stren=s_monster_strength,
                 health=s_monster_health,
                 actions=s_monster_actions,
                 state=s_monster_state,
                 agressive=s_is_monster_agressive,
                 carry_weapon=s_is_monster_carry_weapon,
                 carry_shield=s_is_monster_carry_shield,
                 wear_armor=s_is_monster_wear_armor):
        self.game = game
        self.name = name
        self.name1 = name1
        self.stren = int(stren)
        self.health = int(health)
        self.actions = actions.split(',')
        self.state = state
        self.weapon = self.game.no_weapon
        self.shield = self.game.no_shield
        self.removed_shield = self.game.no_shield
        self.armor = self.game.no_armor
        self.money = s_monster_money
        self.current_position = 0
        self.start_health = self.health
        self.loot = Loot(self.game)
        self.stink = False
        self.hide = False
        self.run = False
        self.wounded = False
        self.weakness = []
        self.key_hole = s_monster_see_through_keyhole
        self.empty = False
        if carry_weapon == 'False':
            self.carry_weapon = False
        else:
            self.carry_weapon = True
        if wear_armor == 'False':
            self.wear_armor = False
        else:
            self.wear_armor = True
        if carry_shield == 'False':
            self.carry_shield = False
        else:
            self.carry_shield = True
        if agressive == 'True':
            self.agressive = True
        else:
            self.agressive = False
        self.exp = self.stren * dice(1, s_monster_exp_multiplier_limit) + dice(1, self.health)

    def on_create(self):
        return True

    def __str__(self):
        return self.name
    
    def g(self, words_list):
        return words_list[self.gender]

    def give(self, item):
        if isinstance(item, Weapon) and self.weapon.empty and self.carry_weapon:
            if item.twohanded and not self.shield.empty:
                    shield = self.shield
                    self.shield = self.game.no_shield
                    self.game.new_castle.plan[self.current_position].loot.pile.append(shield)
            self.weapon = item
        elif isinstance(item, Shield) and self.shield.empty and self.carry_shield:
            if not self.weapon.empty and self.weapon.twohanded:
                self.loot.pile.append(item)
                return True
            else:
                self.shield = item
                return True
        elif isinstance(item, Armor) and self.armor.empty and self.wear_armor:
            self.armor = item
        elif isinstance(item, Rune):
            if item.damage >= item.defence:
                if self.weapon.enchant(item):
                    return True
                if self.armor.enchant(item):
                    return True
                if self.shield.enchant(item):
                    return True
                self.loot.pile.append(item)
                return True
            else:
                if self.shield.enchant(item):
                    return True
                if self.armor.enchant(item):
                    return True
                if self.weapon.enchant(item):
                    return True
                self.loot.pile.append(item)
                return True
        else:
            self.loot.pile.append(item)

    def action(self):
        return randomitem(self.weapon.actions)

    def get_weakness(self, weapons=None): # weapons - массив оружий, 0 или более элементов
        if weapons:
            weaknesses = []
            for weapon in weapons:
                element = weapon.element()
                found = False
                for w in self.weakness:
                    if w[0] == element:
                        weaknesses.append(w[1])
                        found = True
                if not found:
                    weaknesses.append(1)
            return weaknesses
        else:
            return self.weakness
    
    def mele(self):
        room = self.game.new_castle.plan[self.current_position]
        if room.light:
            return dice(1, self.stren)
        else:
            return dice(1, self.stren) // dice(1, 3)

    def attack(self, target):
        game = self.game
        new_castle = self.game.new_castle
        room = new_castle.plan[self.current_position]
        if room.light:
            self_name = self.name
        else:
            self_name = s_monster_name_in_darkness
        text = []
        mele_attack = self.mele()
        if not self.weapon.empty:
            weapon_attack = self.weapon.attack()
            text.append(f'{self_name} {self.action()} {target.name1} используя {self.weapon.name1} и '
                        f'наносит {str(mele_attack)}+{howmany(weapon_attack, "единицу,единицы,единиц")} урона. ')
        else:
            weapon_attack = 0
            text.append(f'{self_name} бьет {target.name1} не используя оружия и '
                        f'наносит {howmany(mele_attack, "единицу,единицы,единиц")} урона. ')
        total_attack = weapon_attack + mele_attack
        target_defence = target.defence(self)
        if (total_attack - target_defence) > 0:
            total_damage = weapon_attack + mele_attack - target_defence
            text.append(f'{target.name} теряет {howmany(total_damage, "жизнь,жизни,жизней")}.')
        else:
            total_damage = 0
            text.append(f'{self_name} не {self.g(["смог", "смогла"])} пробить защиту {target.name1}.')
        if not target.shield.empty:
            rand = dice(1, s_shield_crushed_upper_limit)
            dam = total_attack * target.shield.accumulated_damage
            if rand < dam:
                text.append(f'{self_name} наносит настолько сокрушительный удар, что ломает щит соперника.')
                target.shield = self.game.no_shield
        target.health -= total_damage
        if target.health <= 0:
            game.state = 0
            target.lose(self)
            self.win(target)
            text.append(f'{target.name} терпит сокрушительное поражение и позорно убегает ко входу в замок.')
            tprint(game, text, 'off')
        else:
            tprint(game, text)
        return True

    def defence(self, attacker):
        result = 0
        if not self.shield.empty:
            result += self.shield.protect(attacker)
            if self.hide:
                dice_result = dice(s_shield_damage_when_hiding_min, s_shield_damage_when_hiding_max) / 100
                self.shield.accumulated_damage += dice_result
            else:
                dice_result = dice(s_shield_damage_min, s_shield_damage_max) / 100
                self.shield.accumulated_damage += dice_result
        if not self.armor.empty:
            result += self.armor.protect(attacker)
        return result

    def lose(self, winner=None):
        game = self.game
        new_castle = self.game.new_castle
        result = dice(1, 10)
        where = new_castle.plan[self.current_position]
        if where.loot.empty:
            new_loot = Loot(game)
            where.loot = new_loot
        if result < 6 or self.wounded:
            if self.money > 0:
                a = Money(game, self.money)
                where.loot.pile.append(a)
                where.loot.pile.extend(self.loot.pile)
            if not self.shield.empty:
                where.loot.pile.append(self.shield)
            if not self.armor.empty:
                where.loot.pile.append(self.armor)
            if not self.weapon.empty:
                where.loot.pile.append(self.weapon)
            where.center = game.empty_thing
        else:
            self.wounded = True
            if where.light:
                name = self.name
                lost_weapon = f'На пол падает {self.weapon.name}. '
                lost_shield = f'На пол падает {self.shield.name}. '
            else:
                name = 'Противник'
                lost_weapon = 'Слышно, что какое-то оружие ударилось об пол комнаты. '
                lost_shield = 'В темноте можно услышать, что что-то большое упало в углу. '
            alive_string = f'{name} остается в живых и '
            weakness_amount = ceil(self.stren * s_wounded_monster_strength_coefficient)
            ill_amount = ceil(self.start_health * s_wounded_monster_health_coefficient)
            if result < 10:
                if result == 6:
                    alive_string += 'получает легкое ранение в руку. '
                    if not self.weapon.empty:
                        alive_string += lost_weapon
                        where.loot.pile.append(self.weapon)
                        self.weapon = self.game.no_weapon
                    elif not self.shield.empty:
                        alive_string += lost_shield
                        where.loot.pile.append(self.shield)
                        self.shield = self.game.no_shield
                elif result == 7:
                    alive_string += f'истекает кровью, теряя при ' \
                                   f'этом {howmany(weakness_amount, "единицу,единицы,единиц")} силы. '
                    self.stren -= weakness_amount
                    self.health = self.start_health
                elif result == 8:
                    alive_string += f'приходит в ярость, получая при ' \
                                   f'этом {howmany(weakness_amount, "единицу,единицы,единиц")} силы и ' \
                                   f'теряя {howmany(ill_amount, "жизнь,жизни,жизней")}. '
                    self.stren += weakness_amount
                    self.health = self.start_health - ill_amount
                else:
                    alive_string += f'получает контузию, теряя при ' \
                                   f'этом {howmany(weakness_amount, "единицу,единицы,единиц")} силы и ' \
                                   f'получая {howmany(ill_amount, "жизнь,жизни,жизней")}. '
                    self.stren -= weakness_amount
                    self.health = self.start_health + ill_amount
                if self.place(new_castle, old_place = where):
                    alive_string += f'{name} убегает из комнаты.'
                    tprint(game, alive_string)
                    where.center = game.empty_thing
                else:
                    alive_string += f'Пытаясь убежать {name.lower()} на всей скорости врезается в стену и умирает.'
                    tprint(game, alive_string)
                    where.center = game.empty_thing
            else:
                alive_string += f'получает ранение в ногу и не может двигаться, теряя при ' \
                               f'этом {howmany(weakness_amount, "единицу,единицы,единиц")} силы ' \
                               f'и {howmany(ill_amount, "жизнь,жизни,жизней")}.'
                self.stren -= weakness_amount
                self.health = self.start_health - ill_amount
                tprint(game, alive_string)

    def win(self, loser=None):
        self.health = self.start_health

    def place(self, castle, room_to_place=None, old_place=None):
        if room_to_place:
            room = room_to_place
        else:
            empty_rooms = [a for a in castle.plan if (a.center.empty and a.ambush.empty and a != old_place and a.position != 0)]
            room = randomitem(empty_rooms, False)
        if dice(1, s_monster_hide_possibility) == 1:
            places_to_hide = []
            for i in room.furniture:
                if i.can_hide:
                    places_to_hide.append(i)
            places_to_hide.append(room)
            where_to_hide = randomitem(places_to_hide, False)
            where_to_hide.ambush = self  # Монстр садится в засаду
        else:
            room.center = self
        self.current_position = room.position
        if self.stink:
            print('У нас есть вонючка!')
            print(self.name, room.position)
            castle.stink(room, 3)
            castle.stink_map()
        return True


class Plant(Monster):
    def __init__(self,
                 game,
                 name=s_monster_name,
                 name1=s_monster_name1,
                 stren=s_monster_strength,
                 health=s_monster_health,
                 actions=s_monster_actions,
                 state='растёт',
                 agressive=False,
                 carry_weapon=False,
                 carry_shield=False):
        super().__init__(game, name, name1, stren, health, actions, state, agressive, carry_weapon, carry_shield)
        self.carry_shield = False
        self.carry_weapon = False
        self.wear_armor = False
        self.agressive = False
        self.empty = False

    def grow(self):
        new_plant = Plant(self.name, self.name1, self.stren, self.health, 'бьет', 'растет', False, False, False)
        return new_plant

    def win(self, loser=None):
        new_castle = self.game.new_castle
        self.health = self.start_health
        for i in range(4):
            if new_castle.plan[self.current_position].doors[i] == 1:
                if i == 0 and new_castle.plan[self.current_position - new_castle.rooms].center.empty:
                    copy = self.grow()
                    new_castle.plan[self.current_position - new_castle.rooms].center = copy
                    copy.current_position = self.current_position - new_castle.rooms
                elif i == 1 and new_castle.plan[self.current_position + 1].center.empty:
                    copy = self.grow()
                    new_castle.plan[self.current_position + 1].center = copy
                    copy.current_position = self.current_position + 1
                elif i == 2 and new_castle.plan[self.current_position + new_castle.rooms].center.empty:
                    copy = self.grow()
                    new_castle.plan[self.current_position + new_castle.rooms].center = copy
                    copy.current_position = self.current_position + new_castle.rooms
                elif i == 3 and new_castle.plan[self.current_position - 1].center.empty:
                    copy = self.grow()
                    new_castle.plan[self.current_position - 1].center = copy
                    copy.current_position = self.current_position - 1

    def lose(self, winner=None):
        game = self.game
        new_castle = game.new_castle
        where = new_castle.plan[self.current_position]
        if where.loot.empty:
            new_loot = Loot()
            where.loot = new_loot
        if self.money > 0:
            a = Money(game, self.money)
            where.loot.pile.append(a)
            where.loot.pile.extend(self.loot.pile)
        where.center = game.empty_thing

    def place(self, castle, roomr_to_place = None, old_place = None):
        if roomr_to_place:
            room = roomr_to_place
        else:
            empty_rooms = [a for a in castle.plan if (a.center.empty and a.ambush.empty)]
            room = randomitem(empty_rooms, False)
        room.center = self
        self.current_position = room.position

class Berserk(Monster):
    def __init__(self,
                 game,
                 name=s_monster_name,
                 name1=s_monster_name1,
                 stren=s_monster_strength,
                 health=s_monster_health,
                 actions=s_monster_actions,
                 state=s_monster_state,
                 agressive=s_is_monster_agressive,
                 carry_weapon=s_is_monster_carry_weapon,
                 carry_shield=s_is_monster_carry_shield,
                 wear_armor=s_is_monster_wear_armor):
        super().__init__(game,
                         name,
                         name1,
                         stren,
                         health,
                         actions,
                         state,
                         agressive,
                         carry_weapon,
                         carry_shield,
                         wear_armor)
        self.agressive = True
        self.carry_shield = False
        self.rage = 0
        self.base_health = health
        self.empty = False

    def mele(self):
        self.rage = (int(self.base_health) - int(self.health)) // s_berserk_rage_coefficient
        return dice(1, (self.stren + self.rage))

    def place(self, castle, roomr_to_place=None, old_place=None):
        if roomr_to_place:
            room = roomr_to_place
        else:
            empty_rooms = [a for a in castle.plan if (a.center.empty and a.ambush.empty)]
            room = randomitem(empty_rooms, False)
        room.center = self
        self.current_position = room.position

class Shapeshifter(Monster):
    def __init__(self, 
                game, 
                name='', 
                name1='', 
                stren=10, 
                health=20, 
                actions='бьет', 
                state='стоит', 
                agressive=True,
                carry_weapon=False, 
                carry_shield=True, 
                wear_armor=True):
        super().__init__(game, 
                         name, 
                         name1, 
                         stren, 
                         health, 
                         actions, 
                         state, 
                         agressive, 
                         carry_weapon, 
                         carry_shield,
                         wear_armor)
        self.shifted = False
        self.agressive = True
        self.empty = False

    def defence(self, attacker):
        if not self.shifted:
            self.shifted = True
            self.stren = attacker.stren
            self.gender = attacker.gender
            if not attacker.weapon.empty and self.weapon.empty:
                self.weapon = attacker.weapon
                weapon_string = f' и {self.weapon.name} в руках.'
            else:
                weapon_string = ''
            tprint(self.game, f'{self.name} меняет форму и становится точь в точь как {attacker.name}. '
                              f'У {self.g(["него", "нее"])} теперь сила {str(self.stren)}{weapon_string}')
        result = 0
        if not self.shield.empty:
            result += self.shield.protect(attacker)
            if self.hide:
                dice_result = dice(s_shield_damage_when_hiding_min, s_shield_damage_when_hiding_max) / 100
                self.shield.accumulated_damage += dice_result
            else:
                dice_result = dice(s_shield_damage_min, s_shield_damage_max) / 100
                self.shield.accumulated_damage += dice_result
        if not self.armor.empty:
            result += self.armor.protect(attacker)
        return result

    def lose(self, winner=None):
        game = self.game
        where = self.game.new_castle.plan[self.current_position]
        if where.loot.empty:
            new_loot = Loot(self.game)
            where.loot = new_loot
        if self.money > 0:
            a = Money(self.game, self.money)
            where.loot.pile.append(a)
            where.loot.pile.extend(self.loot.pile)
        if not self.shield.empty:
            where.loot.pile.append(self.shield)
        if not self.armor.empty:
            where.loot.pile.append(self.armor)
        where.center = game.empty_thing


class Vampire(Monster):
    def __init__(self, 
                 game, 
                 name='', 
                 name1='', 
                 stren=10, 
                 health=20, 
                 actions='бьет', 
                 state='стоит', 
                 agressive=False,
                 carry_weapon=True, 
                 carry_shield=True,
                 wear_armor=True):
        super().__init__(game, 
                         name, 
                         name1, 
                         stren, 
                         health, 
                         actions, 
                         state, 
                         agressive, 
                         carry_weapon, 
                         carry_shield,
                         wear_armor)
        self.empty = False

    def attack(self, target):
        game = self.game
        new_castle = self.game.new_castle
        room = new_castle.plan[self.current_position]
        if room.light:
            self_name = self.name
        else:
            self_name = s_monster_name_in_darkness
        text = []
        mele_attack = self.mele()
        if not self.weapon.empty:
            weapon_attack = self.weapon.attack()
            text.append(f'{self_name} {self.action()} {target.name1} используя {self.weapon.name} и '
                        f'наносит {str(mele_attack)}+{str(weapon_attack)} единиц урона. ')
        else:
            weapon_attack = 0
            text.append(f'{self_name} {self.action()} {target.name1} не используя оружия и '
                        f'наносит {howmany(mele_attack, "единицу,единицы,единиц")} урона. ')
        target_defence = target.defence(self)
        total_attack = weapon_attack + mele_attack
        if (total_attack - target_defence) > 0:
            total_damage = weapon_attack + mele_attack - target_defence
        else:
            total_damage = 0
        if total_damage == 0:
            text.append(f'{self_name} не {self.g(["смог", "смогла"])} пробить защиту {target.name1}.')
        elif target_defence == 0:
            text.append(f'{target.name} {self.g(["беззащитен", "беззащитна"])} и теряет {howmany(total_damage, "жизнь,жизни,жизней")}. {self_name} '
                        f'высасывает {str(total_damage // s_vampire_suck_coefficient)} себе.')
        else:
            text.append(f'{target.name} использует для защиты {target.shield.name} и '
                        f'теряет {howmany(total_damage, "жизнь,жизни,жизней")}. {self_name} '
                        f'высасывает {str(total_damage // s_vampire_suck_coefficient)} себе.')
        if not target.shield.empty:
            shield = target.shield
            rand = dice(1, 100)
            dam = total_attack * target.shield.accumulated_damage
            if rand < dam:
                text.append(f'{self_name} наносит настолько сокрушительный удар, что ломает щит соперника.')
                game.all_shields.remove(shield)
                target.shield = self.game.no_shield
        target.health -= total_damage
        self.health += total_damage // s_vampire_suck_coefficient
        if target.health <= 0:
            game.state = 0
            target.lose(self)
            text.append(f'{target.name} терпит сокрушительное поражение и позорно убегает ко входу в замок.')
            tprint(game, text, 'off')
        else:
            tprint(game, text)
        return True

    def place(self, castle, roomr_to_place = None, old_place = None):
        if roomr_to_place:
            room = roomr_to_place
        else:
            empty_rooms = [a for a in castle.plan if (a.ambush.empty and not a.light and not a == old_place)]
            room = randomitem(empty_rooms, False)
        places_to_hide = []
        for i in room.furniture:
            if i.can_hide:
                places_to_hide.append(i)
        places_to_hide.append(room)
        where_to_hide = randomitem(places_to_hide, False)
        where_to_hide.ambush = self  # Монстр садится в засаду
        self.current_position = room.position
        return True

