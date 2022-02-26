from math import ceil
from random import randint as dice

from class_basic import Loot, Money
from class_items import Rune
from class_protection import Armor, Shield
from class_weapon import Weapon
from functions import howmany, randomitem, tprint
from settings import *


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
                 wear_armor=s_is_monster_wear_armor,
                 hit_chance=s_monster_hit_chance,
                 parry_chance = s_monster_parry_chance):
        self.game = game
        self.name = name
        self.name1 = name1
        self.stren = stren
        self.health = health
        self.actions = actions.split(',')
        self.state = state
        self.run = False
        self.room = None
        self.alive = True
        self.hide = False
        self.hit_chance = hit_chance
        self.parry_chance = parry_chance
        self.weapon = self.game.no_weapon
        self.shield = self.game.no_shield
        self.removed_shield = self.game.no_shield
        self.armor = self.game.no_armor
        self.money = s_monster_money
        self.current_position = 0
        self.start_health = self.health
        self.loot = Loot(self.game)
        self.can_steal = True
        self.stink = False
        self.can_hide = True
        self.hiding_place = None
        self.can_run = True
        self.wounded = False
        self.venomous = 0
        self.poisoned = False
        self.weakness = []
        self.key_hole = s_monster_see_through_keyhole
        self.empty = False
        self.prefered_weapon = None
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
        if self.prefered_weapon:
            self.weapon = self.game.readobjects(howmany=1, object_class=Weapon, random=True, object_type=self.prefered_weapon)[0]
            print(self.name, self.weapon.name)
        return True

    def __str__(self):
        return self.name
    
    def g(self, words_list):
        return words_list[self.gender]

    def poison(self, who):
        """Функция проводит проверку, отравил монстр противника при атаке, или нет

        Args:
            who (obj Hero): Герой, которого атакует монстр

        Returns:
            boolean: Признак, отравил монстр героя, или нет
        """
        if self.venomous > 0:
            poison = self.venomous
        elif self.weapon.is_poisoned():
            poison = s_weapon_poison_level
        else:
            poison = s_monster_default_poison_die
        if (who.armor.is_poisoned() or who.shield.is_poisoned()) and poison > 0:
            poison_die = poison + s_monster_add_poison_level
        else:
            poison_die = s_monster_default_poison_die
        if dice(1, poison_die) > poison and not who.poisoned:
            return True
        return False
    
    def vampire_suck(self, total_damage):
        return False
    
    def give(self, item):
        if isinstance(item, Weapon) and self.weapon.empty and self.carry_weapon:
            if self.prefered_weapon and self.prefered_weapon != item.type:
                self.loot.pile.append(item)
                return False
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
        if self.poisoned:
            poison_stren = dice(1, self.stren // 2)
        else:
            poison_stren = 0
        if room.light:
            return dice(1, self.stren - poison_stren)
        else:
            return dice(1, self.stren - poison_stren) // dice(1, s_dark_damage_divider_dice)

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
        if target_defence < 0:
            total_damage = 0
            text.append(f'{target.name} {target.g(["смог", "смогла"])} увернуться от атаки и не потерять ни одной жизни.')
            tprint(game, text)
            return True
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
        if self.poison(target):
            target.poisoned = True
            text.append(f'{target.name} получает отравление, {target.g(["ему", "ей"])} совсем нехорошо.')
        target.health -= total_damage
        vampire_suck = self.vampire_suck(total_damage)
        if vampire_suck:
            text.append(vampire_suck)
        if target.health <= 0:
            game.state = 0
            target.lose(self)
            self.win(target)
            text.append(f'{target.name} терпит сокрушительное поражение и сбегает к ближайшему очагу.')
            tprint(game, text, 'direction')
        else:
            tprint(game, text)
        return True

    def hit_chance(self):
        return self.hit_chance
    
    def defence(self, attacker):
        result = 0
        weapon = attacker.weapon
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
        parry_chance = self.parry_chance
        if self.poisoned:
            parry_chance -= self.parry_chance // 2
        if parry_chance > 0:
            parry_dice = dice(1, parry_chance)
        else:
            parry_dice = 0
        hit_dice = dice(1, (weapon.hit_chance + attacker.hit_chance()))
        if parry_dice > hit_dice:
            result = -1
        return result

    def lose(self, winner=None):
        game = self.game
        result = dice(1, 10)
        where = self.room
        if where.loot.empty:
            new_loot = Loot(game)
            where.loot = new_loot
        if result < 6 or self.wounded or not self.can_run:
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
            game.all_monsters.remove(self)
            self.alive = False
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
                if self.place(game.new_castle, old_place = where):
                    alive_string += f'{name} убегает из комнаты.'
                    tprint(game, alive_string)
                else:
                    alive_string += f'Пытаясь убежать {name.lower()} на всей скорости врезается в стену и умирает.'
                    tprint(game, alive_string)
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
            empty_rooms = [a for a in castle.plan if (not a.monster() and not a.monster_in_ambush() and a != old_place and a.position != 0)]
            room = randomitem(empty_rooms, False)
        self.room = room
        if self.can_hide and dice(1, s_monster_hide_possibility) == 1:
            places_to_hide = []
            for i in room.furniture:
                if i.can_hide:
                    places_to_hide.append(i)
            places_to_hide.append(room)
            self.hiding_place = randomitem(places_to_hide, False)
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
        self.can_steal = False
        self.can_hide = False
        self.can_run = False
        self.hiding_place = None


    def grow(self, room):
        new_plant = Plant(self.game, self.name, self.name1, self.stren, self.health, 'бьет', 'растет', False, False, False)
        new_plant.room = room
        self.game.all_monsters.append(new_plant)
        return True

    def win(self, loser=None):
        new_castle = self.game.new_castle
        self.health = self.start_health
        room = self.room
        new_rooms = []
        for i in range(4):
            if room.doors[i] == 1:
                if i == 0: 
                    new_rooms.append(new_castle.plan[room.position - new_castle.rooms])
                elif i == 1: 
                    new_rooms.append(new_castle.plan[room.position + 1])
                elif i == 2:
                    new_rooms.append(new_castle.plan[room.position + new_castle.rooms])
                elif i == 3:
                    new_rooms.append(new_castle.plan[room.position - 1])
        for i in new_rooms:
            if not i.monster():
                self.grow(i)

    def place(self, castle, roomr_to_place = None, old_place = None):
        if roomr_to_place:
            room = roomr_to_place
        else:
            empty_rooms = [a for a in castle.plan if (not a.monster() and not a.monster_in_ambush())]
            room = randomitem(empty_rooms, False)
        self.room = room

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

    def vampire_suck(self, total_damage):
        sucked = total_damage // s_vampire_suck_coefficient
        self.health += sucked
        return f'{self.name} высасывает себе {str(sucked)} {howmany(sucked, "жизнь,жизни,жизней")}.'
    
    def place(self, castle, roomr_to_place = None, old_place = None):
        if roomr_to_place:
            room = roomr_to_place
        else:
            empty_rooms = [a for a in castle.plan if (not a.monster_in_ambush() and not a.light and not a == old_place)]
            room = randomitem(empty_rooms, False)
        places_to_hide = []
        for i in room.furniture:
            if i.can_hide:
                places_to_hide.append(i)
        places_to_hide.append(room)
        where_to_hide = randomitem(places_to_hide, False)
        self.room = room
        self.hiding_place = where_to_hide
        return True

