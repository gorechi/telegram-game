from math import ceil
from random import randint as dice
from random import choice

from class_basic import Loot, Money
from class_items import Rune
from class_protection import Armor, Shield
from class_weapon import Weapon
from functions import howmany, randomitem, tprint, roll
from settings import *


class Monster:
    """Базовый класс монстров."""
    
    def __init__(self,
                 game,
                 name=s_monster_name,
                 lexemes=s_monster_lexemes,
                 stren=s_monster_strength,
                 health=s_monster_health,
                 actions=s_monster_actions,
                 state=s_monster_state,
                 agressive=s_is_monster_agressive,
                 carry_weapon=s_is_monster_carry_weapon,
                 carry_shield=s_is_monster_carry_shield,
                 wear_armor=s_is_monster_wear_armor,
                 hit_chance=s_monster_hit_chance,
                 parry_chance=s_monster_parry_chance,
                 corpse=True,
                 can_resurrect=False):
        self.game = game
        self.name = name
        self.lexemes = lexemes
        self.stren = stren
        self.health = health
        self.actions = actions.split(',')
        self.state = state
        self.corpse = corpse
        self.floor = None
        self.run = False
        self.alive = True
        self.hide = False
        self.hit_chance = hit_chance
        self.parry_chance = parry_chance
        self.weapon = self.game.no_weapon
        self.shield = self.game.no_shield
        self.removed_shield = self.game.no_shield
        self.armor = self.game.no_armor
        self.money = s_monster_money
        self.current_position = None
        self.start_health = self.health
        self.loot = Loot(self.game)
        self.can_steal = True
        self.stink = False
        self.can_hide = True
        self.can_resurrect = can_resurrect
        self.hiding_place = None
        self.can_run = True
        self.wounded = False
        self.venomous = 0
        self.poisoned = False
        self.weakness = {}
        self.key_hole = s_monster_see_through_keyhole
        self.empty = False
        self.prefered_weapon = None
        booleans = {'False': False, 'True': True}
        self.carry_weapon = carry_weapon
        self.wear_armor = wear_armor
        self.carry_shield = carry_shield
        self.agressive = agressive
        self.exp = self.stren * dice(1, s_monster_exp_multiplier_limit) + dice(1, self.health)

    
    def get_weaker(self) -> bool:
        stren_die = roll([s_monster_weak_strength_die])
        health_die = roll([s_monster_weak_health_die])
        self.stren = int(self.stren * (1 - stren_die/10))
        self.health = int(self.health % (1 - health_die/10))
        return True
    
    
    def on_create(self):
        """Метод вызывается после создания экземпляра класса Монстр."""
        
        if self.prefered_weapon:
            self.weapon = self.game.create_random_weapon(howmany=1, weapon_type=self.prefered_weapon)[0]
        return True

    
    def __str__(self):
        return self.name
          
        
    def g(self, words_list:list) -> str:
        """
        Метод выбирает слово из полученного списка
        в зависимости от пола монстра.
        
        """
        
        return words_list[self.gender]

    
    def get_name(self, case:str) -> str:
        """
        Метод имя монстра, приведенное к определенному падежу.
        
        На вход передается строка с названием падежа:
        - accus - венительный
        - gen - родительный
        
        """       
        
        if self.lexemes:
            return self.lexemes.get(case)
        return self.name
    
    
    def poison_enemy(self, target) -> str:
        """
        Метод проводит проверку, отравил монстр противника при атаке, или нет.

        Параметры:
        - target (obj Hero): Герой, которого атакует монстр

        """
        if target.poisoned:
            return None
        if self.weapon.is_poisoned() or self.venomous:
            poison_die = dice(1, s_weapon_poison_level)
        else:
            poison_die = 0
        base_protection_die = dice(1, s_poison_base_protection_die)
        if target.armor.is_poisoned() or target.shield.is_poisoned():
            additional_protection_die = dice(1, s_poison_additional_protection_die)
        else:
            additional_protection_die = 0
        protection = base_protection_die + additional_protection_die
        if poison_die > protection:
            target.poisoned = True
            return f'{target.name} получает отравление, {target.g(["он", "она"])} теперь неважно себя чувствует.'
        return None
        
            
    def vampire_suck(self, total_damage) -> str:
        """
        Метод вампирского высасывания здоровья из соперника.
        В базовом классе ничего не делает.
        
        """
        return None
    
    
    def take_rune(self, item:Rune) -> bool:
        """Метод обрабатывает ситуацию, когда монстр подбирает руну."""
        
        if item.damage >= item.defence:
            if self.weapon.enchant(item):
                return True
            if self.armor.enchant(item):
                return True
            if self.shield.enchant(item):
                return True
            self.loot.pile.append(item)
            return False
        else:
            if self.shield.enchant(item):
                return True
            if self.armor.enchant(item):
                return True
            if self.weapon.enchant(item):
                return True
            self.loot.pile.append(item)
            return False
    
    
    def take_weapon(self, item:Weapon) -> bool:
        """Метод обрабатывает ситуацию, когда монстр подбирает оружие."""
        
        if not self.weapon.empty or not self.carry_weapon:
            return False
        if self.prefered_weapon and self.prefered_weapon != item.type:
            self.loot.add(item)
            return True
        return self.equip_weapon(item)
    
    
    def take_weapon_from_loot(self, loot:Loot) -> bool:
        """Метод обрабатывает ситуацию, когда монстр выбирает оружие из лута."""
        
        all_weapons = loot.get_items_by_class(Weapon)
        if self.prefered_weapon:
            weapons = [i for i in weapons if i.type == self.prefered_weapon]
        else:
            weapons = all_weapons
        if not self.weapon.empty or not self.carry_weapon or not weapons:
            return False
        weapon = randomitem(weapons)
        self.eqip_weapon(weapon)
        loot.remove(weapon)
        return True
    
        
    
    def equip_weapon(self, weapon:Weapon) -> bool:
        if weapon.twohanded and not self.shield.empty:
                shield = self.shield
                self.shield = self.game.no_shield
                self.current_position.loot.add(shield)
        self.weapon = weapon
        return True

    
    def take_shield(self, item:Shield) -> bool:
        """Метод обрабатывает ситуацию, когда монст подбирает щит."""
        
        if not self.shield.empty or not self.carry_shield:
            return False
        if self.weapon.twohanded:
            self.loot.add(item)
        else:
            self.shield = item
        return True
    
    
    def take_shield_from_loot(self, loot:Loot) -> bool:
        all_sields = loot.get_items_by_class(Shield)
        if not self.carry_shield or self.weapon.twohanded or not all_sields:
            return False
        shield = randomitem(all_sields)
        self.shield = shield
        loot.remove(shield)
        return True
    
    
    def take_armor(self, item:Armor) -> bool:
        """Метод обрабатывает ситуацию, когда монстр подбирает доспехи."""
        
        if not self.armor.empty or not self.wear_armor:
            return False
        self.armor = item
        return True
    
    
    def take_armor_from_loot(self, loot:Loot) -> bool:
        all_armor = loot.get_items_by_class(Armor)
        if not self.armor.empty or not self.wear_armor or not all_armor:
            return False
        armor = randomitem(all_armor)
        self.armor = armor
        loot.remove(armor)
        return True
    
    
    def take_loot(self, loot:Loot) -> bool:
        self.take_weapon_from_loot(loot)
        self.take_shield_from_loot(loot)
        self.take_armor_from_loot(loot)
        self.loot.add(loot)
    
    
    def take(self, item) -> bool:
        """
        Метод моделирует ситуацию, когда монстр получает 
        или подбирает какую-то штуку.
        
        """
        
        if isinstance(item, Weapon):
            return self.take_weapon(item=item)
        if isinstance(item, Shield):
            return self.take_shield(item=item)
        if isinstance(item, Armor):
            return self.take_armor(item=item)
        if isinstance(item, Rune):
            return self.take_rune(item=item)
        self.loot.add(item)
        return True

    
    def action(self) -> str:
        """Метод возвращает случайную строку действия монстра."""
        
        return randomitem(self.weapon.actions)

    
    def get_weakness(self, weapon:Weapon) -> float: 
        """
        Метод возвращает значение коэффициента ославбления/усиления 
        при использовании против монстра определенного оружия.
        
        """
        
        element = str(weapon.element())
        if self.weakness.get(element):
            return self.weakness[element]
        return 1
        
            
    def generate_mele_attack(self, target) -> int:
        if self.poisoned:
            poison_stren = dice(1, self.stren // 2)
        else:
            poison_stren = 0
        if target.check_light():
            return dice(1, self.stren - poison_stren)
        else:
            return dice(1, self.stren - poison_stren) // dice(1, s_dark_damage_divider_dice)

    
    def generate_weapon_attack(self, target) -> int:
        if not self.weapon.empty:
            return self.weapon.attack(target)
        return 0
    
    
    
    def break_enemy_shield(self, target, total_attack:int) -> str:
        """Метод проверяет, смог ли монстр сломать вражеский щит."""
        
        if target.shield.empty:
            return None
        else:
            shield = target.shield
            r = dice(1, s_shield_crushed_upper_limit)
            damage_to_shield = total_attack * target.shield.accumulated_damage
            if r < damage_to_shield:
                self.game.all_shields.remove(shield)
                target.shield = self.game.no_shield
            return f' {self.name} наносит настолько сокрушительный удар, что ломает щит соперника.'
    
    
    def attack(self, target):
        game = self.game
        message = []
        if target.check_light():
            self_name = self.name
        else:
            self_name = s_monster_name_in_darkness
        mele_attack = self.generate_mele_attack(target)
        weapon_attack = self.generate_weapon_attack(target=target)
        if weapon_attack > 0:
            message.append(f'{self_name} {self.action()} {target.name1} используя {self.weapon.name1} и '
                        f'наносит {str(mele_attack)}+{howmany(weapon_attack, "единицу,единицы,единиц")} урона. ')
        else:
            message.append(f'{self_name} бьет {target.name1} не используя оружия и '
                        f'наносит {howmany(mele_attack, "единицу,единицы,единиц")} урона. ')
        target_defence = target.defence(self)
        if target_defence < 0:
            message.append(f'{target.name} {target.g(["смог", "смогла"])} увернуться от атаки и не потерять ни одной жизни.')
            tprint(game, message)
            return False
        total_attack = weapon_attack + mele_attack
        total_damage = total_attack - target_defence
        if total_damage > 0:
            message.append(f'{target.name} теряет {howmany(total_damage, "жизнь,жизни,жизней")}.')
            message += [
                self.break_enemy_shield(target=target, total_attack=total_attack),
                self.poison_enemy(target=target),
                self.vampire_suck(total_damage=total_damage)
            ]
        else:
            total_damage = 0
            message.append(f'{self_name} не {self.g(["смог", "смогла"])} пробить защиту {target.name1}.')
        target.health -= total_damage
        if target.health <= 0:
            game.state = 0
            target.lose(self)
            self.win(target)
            message.append(f'{target.name} терпит сокрушительное поражение и сбегает к ближайшему очагу.')
            tprint(game, message, 'direction')
        else:
            tprint(game, message)
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

    
    def finally_die(self) -> bool:
        room = self.current_position
        self.floor.all_monsters.remove(self)
        self.floor.monsters_in_rooms[room].remove(self)
        self.game.how_many_monsters -= 1
        self.alive = False
        self.become_a_corpse(for_good=True)
        return True
    
    
    def become_a_zombie(self) -> bool:
        room = self.current_position
        self.floor.all_monsters.remove(self)
        self.floor.monsters_in_rooms[room].remove(self)
        self.game.how_many_monsters -= 1
        self.alive = False
        self.become_a_corpse(for_good=False)
        return True
    
    
    def resurrect(self) -> bool:
        room = self.current_position
        self.floor.all_monsters.append(self)
        self.floor.monsters_in_rooms[room].append(self)
        self.game.how_many_monsters += 1
        self.alive = True
        self.get_weaker()
        return True
    
    
    def become_a_corpse(self, for_good:bool) -> bool:
        if not self.corpse:
            return False
        self.gather_loot()
        corpse_name = f'труп {self.get_name("gen")}'
        new_corpse = Corpse(self.game, corpse_name, self.loot, self.current_position, self, not for_good)
        return True
        
    
    def gather_loot(self):
        loot = self.loot
        if self.money > 0:
            money = Money(self.game, self.money)
            loot.add(money)
        if not self.shield.empty:
            loot.add(self.shield)
        if not self.armor.empty:
            loot.add(self.armor)
        if not self.weapon.empty:
            loot.add(self.weapon)

        
    def lose(self, winner=None):
        if self.can_resurrect:
            die = 15
        else:
            die = 10
        result = dice(1, die)
        if result < 6 or self.wounded or not self.can_run:
            return self.finally_die()
        else:
            return self.get_wounded(result=result)
            
            
    def lose_weapon_text(self) -> str:
        room = self.current_position
        if room.light:
            return f'На пол падает {self.weapon.name}. '
        else:
            return'Слышно, что какое-то оружие ударилось об пол комнаты. '
    
    
    def lose_shield_text(self) -> str:
        room = self.current_position
        if room.light:
            return f'На пол падает {self.shield.name}. '
        else:
            return 'В темноте можно услышать, что что-то большое упало в углу. '
    
    
    def get_self_name_in_room(self) -> str:
        room = self.current_position
        if room.light:
            return self.name
        else:
            return 'Противник'
    
    
    def get_wounded(self, result:int) -> bool:        
        self.wounded = True
        results_dict = {
            result == 6: self.hand_wound,
            result == 7: self.bleed,
            result == 8: self.rage,
            result == 9: self.contusion,
            result == 10: self.leg_wound,
            result > 10: self.become_a_zombie
            
        }
        return results_dict[True]()
        
        
    def hand_wound(self) -> bool:
        if not self.weapon.empty:
            alive_text += self.lose_weapon_text()
            self.current_position.loot.add(self.weapon)
            self.weapon = self.game.no_weapon
        elif not self.shield.empty:
            alive_text += self.lose_shield_text()
            self.current_position.loot.add(self.shield)
            self.shield = self.game.no_shield
        text = f'{self.get_self_name_in_room(self)} остается в живых иполучает легкое ранение в руку. '
        text += self.try_to_run_away()
        tprint(self.game, text)
        return True
        
        
    def bleed(self) -> bool:
        weakness_amount = ceil(self.stren * s_wounded_monster_strength_coefficient)
        self.stren -= weakness_amount
        self.health = self.start_health
        text = f'{self.get_self_name_in_room(self)} остается в живых и истекает кровью, теряя при ' \
                        f'этом {howmany(weakness_amount, "единицу,единицы,единиц")} силы. '
        text += self.try_to_run_away()
        tprint(self.game, text)
        return True
        
    
    def rage(self) -> bool:
        strengthening_amount = ceil(self.stren * s_wounded_monster_strength_coefficient)
        ill_amount = ceil(self.start_health * s_wounded_monster_health_coefficient)
        self.stren += strengthening_amount
        self.health = self.start_health - ill_amount
        text = f'{self.get_self_name_in_room(self)} остается в живых и приходит в ярость, получая при ' \
                        f'этом {howmany(strengthening_amount, "единицу,единицы,единиц")} силы и ' \
                        f'теряя {howmany(ill_amount, "жизнь,жизни,жизней")}. '
        text += self.try_to_run_away()
        tprint(self.game, text)
        return True
    
    
    def contusion(self) -> bool:
        weakness_amount = ceil(self.stren * s_wounded_monster_strength_coefficient)
        health_boost_amount = ceil(self.start_health * s_wounded_monster_health_coefficient)
        self.stren -= weakness_amount
        self.health = self.start_health + health_boost_amount
        text = f'{self.get_self_name_in_room(self)} остается в живых и получает контузию, теряя при ' \
                        f'этом {howmany(weakness_amount, "единицу,единицы,единиц")} силы и ' \
                        f'получая {howmany(health_boost_amount, "жизнь,жизни,жизней")}. '
        text += self.try_to_run_away()
        tprint(self.game, text)
        return True

    
    def leg_wound(self) -> bool:
        weakness_amount = ceil(self.stren * s_wounded_monster_strength_coefficient)
        ill_amount = ceil(self.start_health * s_wounded_monster_health_coefficient)
        self.stren -= weakness_amount
        self.health = self.start_health - ill_amount
        tprint(self.game, f'{self.get_self_name_in_room(self)} остается в живых и получает ранение в ногу и не может двигаться, теряя при ' \
                            f'этом {howmany(weakness_amount, "единицу,единицы,единиц")} силы ' \
                            f'и {howmany(ill_amount, "жизнь,жизни,жизней")}.')
        return True
    
    
    def try_to_run_away(self) -> str:
        name = self.get_self_name_in_room()
        if self.place(self.floor, old_place = self.current_position):
            return f'{name} убегает из комнаты.'
        else:
            self.finally_die()
            return f'Пытаясь убежать {name.lower()} на всей скорости врезается в стену и умирает.'

    
    def win(self, loser=None):
        self.health = self.start_health

    
    def place(self, floor, room_to_place=None, old_place=None):
        if room_to_place:
            room = room_to_place
        else:
            empty_rooms = [a for a in floor.plan if (not a.monsters() 
                                                     and not a.monster_in_ambush()
                                                     and not a.traider 
                                                     and a != old_place 
                                                     and a.position != 0)]
            if not bool(empty_rooms):
                return False
            room = randomitem(empty_rooms, False)
        self.current_position = room
        floor.monsters_in_rooms[room].append(self)
        if old_place:
            floor.monsters_in_rooms[old_place].remove(self)
        if self.can_hide and dice(1, s_monster_hide_possibility) == 1:
            places_to_hide = []
            for i in room.furniture:
                if i.can_hide:
                    places_to_hide.append(i)
            places_to_hide.append(room)
            self.hiding_place = randomitem(places_to_hide, False)
        if self.stink:
            floor.stink(room, 3)
            floor.stink_map()
        self.floor = floor
        return True


class Plant(Monster):
    def __init__(self,
                 game,
                 name=s_monster_name,
                 lexemes=s_monster_lexemes,
                 stren=s_monster_strength,
                 health=s_monster_health,
                 actions=s_monster_actions,
                 state='растёт',
                 agressive=False,
                 carry_weapon=False,
                 carry_shield=False):
        super().__init__(game, name, lexemes, stren, health, actions, state, agressive, carry_weapon, carry_shield)
        self.carry_shield = False
        self.carry_weapon = False
        self.wear_armor = False
        self.agressive = False
        self.empty = False
        self.can_steal = False
        self.can_hide = False
        self.can_run = False
        self.hiding_place = None
        self.can_resurrect=False


    def grow(self, room):
        new_plant = Plant(self.game, self.name, self.lexemes, self.stren, self.health, 'бьет', 'растет', False, False, False)
        new_plant.room = room
        self.floor.all_monsters.append(new_plant)
        self.game.how_many_monsters += 1
        return True

    
    def win(self, loser=None):
        self.health = self.start_health
        room = self.current_position
        floor = self.floor
        new_rooms = []
        for i in range(4):
            if room.doors[i] == 1:
                if i == 0: 
                    new_rooms.append(floor.plan[room.position - floor.rooms])
                elif i == 1: 
                    new_rooms.append(floor.plan[room.position + 1])
                elif i == 2:
                    new_rooms.append(floor.plan[room.position + floor.rooms])
                elif i == 3:
                    new_rooms.append(floor.plan[room.position - 1])
        for i in new_rooms:
            if not i.monster():
                self.grow(i)

    
    def place(self, floor, roomr_to_place = None, old_place = None):
        if roomr_to_place:
            room = roomr_to_place
        else:
            empty_rooms = [a for a in floor.plan if (not a.monsters() and not a.monster_in_ambush())]
            room = randomitem(empty_rooms, False)
        self.current_position = room
        self.floor = floor


class Berserk(Monster):
    def __init__(self,
                 game,
                 name=s_monster_name,
                 lexemes=s_monster_lexemes,
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
                         lexemes,
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
        self.can_resurrect=False
   
    
    def generate_mele_attack(self, target):
        self.rage = (int(self.base_health) - int(self.health)) // s_berserk_rage_coefficient
        if self.poisoned:
            poison_stren = dice(1, self.stren // 2)
        else:
            poison_stren = 0
        return dice(1, (self.stren + self.rage - poison_stren))


class Shapeshifter(Monster):
    def __init__(self, 
                game, 
                name='',
                lexemes=s_monster_lexemes, 
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
                         lexemes, 
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
        self.start_stren = stren

    
    def defence(self, attacker):
        if not self.shifted:
            self.shifted = True
            self.stren = attacker.stren
            self.start_gender = attacker.gender
            self.gender = attacker.gender
            if not attacker.weapon.empty and self.weapon.empty:
                self.weapon_changed = True
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
    
    
    def win(self, loser=None):
        self.health = self.start_health
        self.stren = self.start_stren
        self.gender = self.start_gender
        self.shifted = False
        if self.weapon_changed:
            self.weapon = self.game.no_weapon
            self.weapon_changed = False
        

class Vampire(Monster):
    def __init__(self, 
                 game, 
                 name='',
                 lexemes=s_monster_lexemes, 
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
                         lexemes, 
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
        """Метод вампирского высасывания здоровья из соперника."""
        
        sucked = total_damage // s_vampire_suck_coefficient
        self.health += sucked
        return f'{self.name} высасывает себе {str(sucked)} {howmany(sucked, "жизнь,жизни,жизней")}.'
    
    
    def place(self, floor, roomr_to_place = None, old_place = None):
        if roomr_to_place:
            room = roomr_to_place
        else:
            empty_rooms = [a for a in floor.plan if (not a.monster_in_ambush() and not a.light and not a == old_place)]
            room = randomitem(empty_rooms, False)
        places_to_hide = []
        for i in room.furniture:
            if i.can_hide:
                places_to_hide.append(i)
        places_to_hide.append(room)
        where_to_hide = randomitem(places_to_hide, False)
        self.current_position = room
        self.hiding_place = where_to_hide
        self.floor = floor
        return True


class Animal(Monster):
    def __init__(self, 
                 game, 
                 name='',
                 lexemes=s_monster_lexemes, 
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
                         lexemes, 
                         stren, 
                         health, 
                         actions, 
                         state, 
                         agressive, 
                         carry_weapon, 
                         carry_shield,
                         wear_armor)
        self.empty = False


class WalkingDead(Monster):
    def __init__(self, 
                 game, 
                 name='',
                 lexemes=s_monster_lexemes, 
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
                         lexemes, 
                         stren, 
                         health, 
                         actions, 
                         state, 
                         agressive, 
                         carry_weapon, 
                         carry_shield,
                         wear_armor)
        self.empty = False
        self.can_resurrect = True


class Corpse():
    def __init__(self,
                 game,
                 name:str,
                 loot:Loot,
                 room,
                 creature=None,
                 can_resurrect=False):
        self.game = game
        self.name = name
        self.loot = loot
        self.room = room
        self.creature = creature
        self.description = self.generate_description()
        self.place(room)
        self.can_resurrect = can_resurrect
        
    
    def try_to_rise(self) -> bool:
        if not self.creature or not self.can_resurrect:
            return False
        die = self.creature.resurrection_die
        if roll([die]) == 1:
            self.rise_from_dead()
            return True
        return False
    
    
    def rise_from_dead(self):
        self.creature.resurrect()
        self.creature.take_loot(self.loot)
        self.room.morgue.remove(self)
        self.game.all_corpses.remove(self)
        tprint(self.game, f'В комнате {self.room.position} труп воосстал из мертвых.')
        return True
    
    
    def place(self, room) -> bool:
        room.morgue.append(self)
        self.game.all_corpses.append(self)
        return True
    
    
    def generate_description(self) -> str:
        place = choice(s_corpse_places)
        state = choice(s_corpse_states)
        depiction = choice(s_corpse_depiction)
        description = f'{place} {state} {depiction} {self.name}'
        return description