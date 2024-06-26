from math import ceil
from random import randint as dice
from random import choice

from class_basic import Loot, Money
from class_items import Rune
from class_protection import Armor, Shield
from class_weapon import Weapon
from functions import howmany, randomitem, tprint, roll


class Monster:
    """
    Базовый класс монстров, определяющий общие атрибуты и методы для всех монстров в игре.
    Этот класс содержит атрибуты, такие как имя, сила, здоровье, действия, состояние и другие,
    которые характеризуют монстра. Также включает в себя методы для управления состоянием монстра,
    такие как атака, защита, перемещение и другие действия.
    """
    
    _dark_damage_divider_die = 3
    """Кубик, который кидается, чтобы выяснить, во сколько раз уменьшится урон от атаки в темноте."""
    
    _add_poison_level = 3
    """Значение, которое прибавляется к уровню отравления чтобы рассчитать кубик отравления."""
       
    _money = 5
    """Сколько у монстра по умолчанию денег."""

    _see_through_keyhole = 'видит какую-то неясную фигуру.'
    """Что отображается если монстра увидеть через замочную скважину."""
  
    _exp_multiplier_limit = 10
    """
    Верхняя граница значения множителя, на который 
    умножается сила монстра при рассчете полученного за него опыта.

    """

    _names_in_darkness = {
            'nom': 'Кто-то страшный',
            "accus": 'черт знает кого',
            'gen': 'черт знает кого',
            'dat': 'черт знает кому',
            'prep': 'ком-то',
            'inst': 'черт знает кем'
        }
    """Лексемы монстра в темноте."""

    _wounded_monster_strength_coefficient = 0.4
    """Коэффициент, на который умножается сила монстра если он ранен."""
    
    _wounded_monster_health_coefficient = 0.4
    """Коэффициент, на который умножается здоровье монстра если он ранен."""
    
    _hide_possibility = 5
    """Вероятность, с которой монстр садится в засаду (если 5, то вероятность 1/5)."""
    
    _poison_base_protection_die = 5
    """Кубик, который кидается чтобы определить базовую защиту от отравления."""

    _poison_additional_protection_die = 5
    """
    Кубик, который кидается чтобы определить дополнительную защиту от яда
    когда у героя или монстра ядовитые доспехи или щит.

    """

    _weak_strength_die = 6
    """Кубик, определяющий, какая часть силы теряется монстром при ослаблении"""

    _weak_health_die = 6
    """Кубик, определяющий, какая часть здоровья теряется монстром при ослаблении"""
    
    _types = {
        'basic': {
            "nom": "обычные противники",
            "accus": "обычных противников",
            "gen": "обычных противников",
            "dat": "обычным противникам",
            "prep": "обычных противниках",
            "inst": "обычными противниками"
        },
        'shapeshifter': {
            "nom": "оборотни",
            "accus": "оборотней",
            "gen": "оборотней",
            "dat": "оборотням",
            "prep": "оборотнях",
            "inst": "оборотнями"
        },
        'undead': {
            "nom": "мертвецы",
            "accus": "мертвецов",
            "gen": "мертвецов",
            "dat": "мертвецам",
            "prep": "мертвецах",
            "inst": "мертвецами"
        },
        'plant': {
            "nom": "растения",
            "accus": "растения",
            "gen": "растений",
            "dat": "растениям",
            "prep": "растениях",
            "inst": "растениями"
        },
        'animal': {
            "nom": "животные",
            "accus": "животных",
            "gen": "животных",
            "dat": "животным",
            "prep": "животных",
            "inst": "животными"
        },
        'vampire': {
            "nom": "вампиры",
            "accus": "вампиров",
            "gen": "вампиров",
            "dat": "вампирам",
            "prep": "вампирах",
            "inst": "вампирами"
        }
    }
    """Лексемы разных типов противников"""
    
    def __init__(self,
                 game,
                 name='',
                 lexemes={},
                 stren=5,
                 health=10,
                 actions=['бьет'],
                 state='стоит',
                 agressive=False,
                 carry_weapon=True,
                 carry_shield=False,
                 wear_armor=False,
                 hit_chance=5,
                 parry_chance=2,
                 corpse=True,
                 can_resurrect=False):
        self.game = game
        self.name = name
        self.monster_type = 'basic'
        self.lexemes = lexemes
        self.stren = stren
        self.health = health
        self.actions = actions
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
        self.money = Monster._money
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
        self.key_hole = Monster._see_through_keyhole
        self.empty = False
        self.prefered_weapon = None
        self.carry_weapon = carry_weapon
        self.wear_armor = wear_armor
        self.carry_shield = carry_shield
        self.agressive = agressive
        self.exp = self.stren * roll([Monster._exp_multiplier_limit]) + roll([self.health])
        self.wounds_list = [
            self.hand_wound,
            self.bleed,
            self.rage,
            self.contusion,
            self.leg_wound,
            self.become_a_zombie
        ]

    
    def __format__(self, format:str) -> str:
        if format == 'pronoun':
            if self.gender == 0:
                return 'он'
            return 'она'
        return self.lexemes.get(format, '')
    
    
    def get_weaker(self) -> bool:
        """
        Метод уменьшает силу и здоровье монстра на случайное значение, 
        определенное броском кубика.
        """
        stren_die = roll([Monster._weak_strength_die])
        health_die = roll([Monster._weak_health_die])
        self.stren = int(self.stren * (1 - stren_die/10))
        self.health = int(self.health * (1 - health_die/10))
        return True
    
    
    def on_create(self):
        """Метод вызывается после создания экземпляра класса Монстр."""
        
        if self.prefered_weapon:
            self.weapon = self.game.create_random_weapon(weapon_type=self.prefered_weapon)
        return True

    
    def __str__(self):
        """
        Метод для представления объекта класса в виде строки.
        Возвращает имя монстра.
        """
        return self.name
        
    
    def g(self, he_word:str, she_word:str) -> str:
        """
        Метод получает на вход два слова и
        выбирает нужное слово в зависимости от пола монстра. 
        Первым должно идти слово, соответствующее мужскому полу, 
        а вторым - соответствующее женскому.
        
        """
        if self.gender == 0:
            return he_word
        return she_word


    
    def check_name(self, message:str) -> bool:
        room = self.current_position
        if room.light:
            names_list = self.get_names_list(['nom', "accus"])
        else:
            names_list =  ['противник']
        return message.lower() in names_list
    
    
    def get_names_list(self, cases:list=None) -> list:
        names_list = ['монстр', 
                      'врага', 
                      'монстра', 
                      'враг', 
                      'противника', 
                      'противник',
                      self.name[0].lower()]
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list
    
    
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
            poison_die = dice(1, Monster._poison_level)
        else:
            poison_die = 0
        base_protection_die = dice(1, Monster._poison_base_protection_die)
        if target.armor.is_poisoned() or target.shield.is_poisoned():
            additional_protection_die = dice(1, Monster._poison_additional_protection_die)
        else:
            additional_protection_die = 0
        protection = base_protection_die + additional_protection_die
        if poison_die > protection:
            target.poisoned = True
            return f'{target.name} получает отравление, {target.g("он", "она")} теперь неважно себя чувствует.'
        return None
        
            
    def vampire_suck(self, total_damage) -> str:
        """
        Метод вампирского высасывания здоровья из соперника.
        В базовом классе ничего не делает.
        
        """
        return None
    
    
    def take_rune(self, rune:Rune) -> bool:
        """Метод обрабатывает ситуацию, когда монстр подбирает руну."""
        
        item = self.choose_what_to_enchant(rune)
        if not item:
            self.loot.pile.append(rune)
            return False
        item.enchant(rune)
        return True
    
    
    def choose_what_to_enchant(self, rune:Rune):
        items = [
            self.weapon,
            self.armor,
            self.shield
        ]
        items = [i for i in items if i.can_be_enchanted()]
        if not items:
            return None
        if rune.damage >= rune.defence:
            return items[0]
        else:
            return items[-1]
    
    
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
        """
        Этот метод оснащает монстра оружием. Если оружие двуручное и у монстра уже есть щит,
        то щит помещается в лут текущей позиции монстра, а затем монстру назначается новое оружие.
        Возвращает True после оснащения оружием.
        """
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
        """
        Метод позволяет монстру выбрать щит из лута. Если монстр не может носить щиты, у него уже есть двуручное оружие,
        или в луте нет щитов, метод возвращает False. В противном случае монстр берет случайный щит из лута и метод возвращает True.
        """
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
        """
        Этот метод позволяет монстру взять доспехи из лута. Метод проверяет, есть ли у монстра уже доспехи,
        может ли монстр носить доспехи и есть ли доспехи в луте. Если одно из условий не выполняется, метод возвращает False.
        В противном случае монстр берет случайные доспехи из лута, и метод возвращает True.
        """
        all_armor = loot.get_items_by_class(Armor)
        if not self.armor.empty or not self.wear_armor or not all_armor:
            return False
        armor = randomitem(all_armor)
        self.armor = armor
        loot.remove(armor)
        return True
    
    
    def take_loot(self, loot:Loot) -> bool:
        """
        Метод позволяет монстру взять лут: оружие, щит и доспехи из переданного лута.
        После попытки взять каждый из этих предметов, весь оставшийся лут добавляется к луту монстра.
        """
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
        """
        Генерирует атаку в ближнем бою на цель. Если монстр отравлен, его атака уменьшается.
        В зависимости от освещенности в комнате, атака может быть уменьшена.
        """
        if self.poisoned:
            poison_stren = dice(1, self.stren // 2)
        else:
            poison_stren = 0
        if target.check_light():
            return dice(1, self.stren - poison_stren)
        else:
            return dice(1, self.stren - poison_stren) // dice(1, Monster._dark_damage_divider_die)

    
    def generate_weapon_attack(self, target) -> int:
        """
        Генерирует атаку с использованием оружия на цель. Если у монстра нет оружия, атака равна 0.
        """
        if not self.weapon.empty:
            return self.weapon.attack(target)
        return 0
    
    
    
    def break_enemy_shield(self, target, total_attack:int) -> str:
        """Метод проверяет, смог ли монстр сломать вражеский щит."""
        
        shield = target.shield
        if not shield.empty and shield.check_if_broken():
            return f' {self.name} наносит настолько сокрушительный удар, что ломает щит соперника.'
        return None
    
    
    def attack(self, target) ->bool:
        """
        Осуществляет атаку на цель. В зависимости от условий освещенности, использует имя монстра или общее название в темноте.
        Генерирует атаку в ближнем бою и атаку оружием, суммирует их и вычитает защиту цели. Рассчитывает общий урон и применяет его к цели.
        В случае смерти цели, обновляет состояние игры и выводит соответствующее сообщение. Возвращает результат атаки.
        """
        game = self.game
        self_name = self.get_name_in_darkness(target)
        total_attack, message = self.generate_attack(target)
        target_defence = target.defence(self)
        if target_defence < 0:
            message.append(f'{target.name} {target.g("смог", "смогла")} увернуться от атаки и не потерять ни одной жизни.')
            tprint(game, message)
            return False
        total_damage = total_attack - target_defence
        if total_damage > 0:
            message.append(f'{target.name} теряет {howmany(total_damage, ["жизнь", "жизни", "жизней"])}.')
            message += [
                self.break_enemy_shield(target=target, total_attack=total_attack),
                self.poison_enemy(target=target),
                self.vampire_suck(total_damage=total_damage)
            ]
        else:
            total_damage = 0
            message.append(f'{self_name} не {self.g("смог", "смогла")} пробить защиту {target:accus}.')
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

    
    def generate_attack(self, target) -> list[int, list[str]]:
        message = []
        self_name = self.get_name_in_darkness(target)
        mele_attack = self.generate_mele_attack(target)
        weapon_attack = self.generate_weapon_attack(target=target)
        total_attack = weapon_attack + mele_attack
        if weapon_attack > 0:
            message.append(f'{self_name} {self.action()} {target:accus} используя {self.weapon:accus} и '
                        f'наносит {mele_attack}+{howmany(weapon_attack, ["единицу", "единицы", "единиц"])} урона.')
        else:
            message.append(f'{self_name} бьет {target:accus} не используя оружия и '
                        f'наносит {howmany(mele_attack, ["единицу", "единицы", "единиц"])} урона.')
        return total_attack, message
    
    
    def get_name_in_darkness(self, target):
        if target.check_light():
            return self.name
        return Monster._names_in_darkness['nom']
    
    
    def hit_chance(self):
        """
        Возвращает шанс попадания по цели.
        """
        return self.hit_chance
    
    
    def defence(self, attacker):
        result = 0
        weapon = attacker.weapon
        if not self.shield.empty:
            result += self.shield.protect(attacker)
            self.shield.take_damage(self.hide)
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
        """
        Обрабатывает смерть монстра, удаляя его из списка монстров на этаже и в комнате, уменьшая общее количество монстров.
        Монстр становится мертвым и превращается в труп навсегда.
        """
        room = self.current_position
        self.floor.all_monsters.remove(self)
        self.floor.monsters_in_rooms[room].remove(self)
        self.game.how_many_monsters -= 1
        self.alive = False
        self.become_a_corpse(for_good=True)
        return True
    
    
    def become_a_zombie(self) -> bool:
        """
        Обрабатывает превращение монстра в зомби, удаляя его из списка монстров на этаже и в комнате, уменьшая общее количество монстров.
        Монстр становится мертвым, но может быть воскрешен.
        """
        room = self.current_position
        self.floor.all_monsters.remove(self)
        self.floor.monsters_in_rooms[room].remove(self)
        self.game.how_many_monsters -= 1
        self.alive = False
        self.become_a_corpse(for_good=False)
        return True
    
    
    def resurrect(self) -> bool:
        """
        Обрабатывает воскрешение монстра, добавляя его обратно в список монстров на этаже и в комнате, увеличивая общее количество монстров.
        Монстр становится живым и слабеет.
        """
        room = self.current_position
        self.floor.all_monsters.append(self)
        self.floor.monsters_in_rooms[room].append(self)
        self.game.how_many_monsters += 1
        self.alive = True
        self.get_weaker()
        return True
    
    
    def become_a_corpse(self, for_good:bool) -> bool:
        """
        Обрабатывает превращение монстра в труп. Если монстр умирает навсегда, он собирает добычу и становится трупом.
        Возвращает True, если монстр стал трупом.
        """
        if not self.corpse:
            return False
        self.gather_loot()
        corpse_name = f'труп {self:gen}'
        new_corpse = Corpse(self.game, corpse_name, self.loot, self.current_position, self, not for_good)
        return True
        
    
    def gather_loot(self):
        """
        Собирает добычу с монстра, включая деньги, щит, броню и оружие.
        """
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
        """
        Обрабатывает поражение монстра. Определяет, умрет ли монстр, станет зомби или получит ранение в зависимости от результата броска кубика.
        """
        if self.can_resurrect:
            die = 15
        else:
            die = 10
        result = dice(1, die)
        if result < 6 or self.wounded or not self.can_run:
            return self.finally_die()
        else:
            return self.get_wounded()
            
            
    def lose_weapon_text(self) -> str:
        """
        Возвращает текстовое сообщение о потере оружия монстром. Текст зависит от освещенности в комнате.
        """
        room = self.current_position
        if room.light:
            return f'На пол падает {self.weapon.name}. '
        else:
            return'Слышно, что какое-то оружие ударилось об пол комнаты. '
    
    
    def lose_shield_text(self) -> str:
        """
        Возвращает текстовое сообщение о потере щита монстром. Текст зависит от освещенности в комнате.
        """
        room = self.current_position
        if room.light:
            return f'На пол падает {self.shield.name}. '
        else:
            return 'В темноте можно услышать, что что-то большое упало в углу. '
    
    
    def get_self_name_in_room(self) -> str:
        """
        Возвращает имя монстра или общее название "Противник" в зависимости от освещенности в комнате.
        """
        room = self.current_position
        if room.light:
            return self.get_name('nom')
        else:
            return 'Противник'
    
    
    def get_wounded(self) -> bool:        
        """
        Обрабатывает получение ранения монстром. Может привести к различным последствиям, включая превращение в зомби.
        """
        self.wounded = True
        wound = randomitem(self.wounds_list)
        return wound()
        
        
    def hand_wound(self) -> bool:
        """
        Обрабатывает получение ранения в руку. Если у монстра есть оружие или щит, он их теряет.
        Возвращает True, указывая на то, что монстр остается в живых.
        """
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
        """
        Обрабатывает ситуацию, когда монстр истекает кровью. Это приводит к потере силы,
        но здоровье восстанавливается до начального уровня. Возвращает True.
        """
        weakness_amount = ceil(self.stren * Monster._wounded_monster_strength_coefficient)
        self.stren -= weakness_amount
        self.health = self.start_health
        text = f'{self.get_self_name_in_room(self)} остается в живых и истекает кровью, теряя при ' \
                        f'этом {howmany(weakness_amount, ["единицу", "единицы", "единиц"])} силы. '
        text += self.try_to_run_away()
        tprint(self.game, text)
        return True
        
    
    def rage(self) -> bool:
        """
        Обрабатывает вход в состояние ярости. Монстр получает увеличение силы, но теряет часть здоровья.
        Возвращает True.
        """
        strengthening_amount = ceil(self.stren * Monster._wounded_monster_strength_coefficient)
        ill_amount = ceil(self.start_health * Monster._wounded_monster_health_coefficient)
        self.stren += strengthening_amount
        self.health = self.start_health - ill_amount
        text = f'{self.get_self_name_in_room(self)} остается в живых и приходит в ярость, получая при ' \
                        f'этом {howmany(strengthening_amount, ["единицу", "единицы", "единиц"])} силы и ' \
                        f'теряя {howmany(ill_amount, ["жизнь", "жизни", "жизней"])}. '
        text += self.try_to_run_away()
        tprint(self.game, text)
        return True
    
    
    def contusion(self) -> bool:
        """
        Обрабатывает получение контузии. Монстр теряет силу, но получает дополнительное здоровье.
        Возвращает True.
        """
        weakness_amount = ceil(self.stren * Monster._wounded_monster_strength_coefficient)
        health_boost_amount = ceil(self.start_health * Monster._wounded_monster_health_coefficient)
        self.stren -= weakness_amount
        self.health = self.start_health + health_boost_amount
        text = f'{self.get_self_name_in_room(self)} остается в живых и получает контузию, теряя при ' \
                        f'этом {howmany(weakness_amount, ["единицу", "единицы", "единиц"])} силы и ' \
                        f'получая {howmany(health_boost_amount, ["жизнь", "жизни", "жизней"])}. '
        text += self.try_to_run_away()
        tprint(self.game, text)
        return True

    
    def leg_wound(self) -> bool:
        """
        Обрабатывает получение ранения в ногу. Монстр теряет силу и часть здоровья, а также не может двигаться.
        Возвращает True.
        """
        weakness_amount = ceil(self.stren * Monster._wounded_monster_strength_coefficient)
        ill_amount = ceil(self.start_health * Monster._wounded_monster_health_coefficient)
        self.stren -= weakness_amount
        self.health = self.start_health - ill_amount
        tprint(self.game, f'{self.get_self_name_in_room(self)} остается в живых и получает ранение в ногу и не может двигаться, теряя при ' \
                            f'этом {howmany(weakness_amount, ["единицу", "единицы", "единиц"])} силы ' \
                            f'и {howmany(ill_amount, ["жизнь", "жизни", "жизней"])}.')
        return True
    
    
    def try_to_run_away(self) -> str:
        """
        Пытается убежать из комнаты. Если удачно, возвращает сообщение об убегании.
        В противном случае монстр умирает, врезавшись в стену.
        """
        name = self.get_self_name_in_room()
        if self.place(self.floor, old_place = self.current_position):
            return f'{name} убегает из комнаты.'
        else:
            self.finally_die()
            return f'Пытаясь убежать {name.lower()} на всей скорости врезается в стену и умирает.'

    
    def win(self, loser=None):
        """
        Восстанавливает здоровье монстра до начального уровня после победы.
        """
        self.health = self.start_health

    
    def place(self, floor, room_to_place=None, old_place=None):
        """
        Перемещает монстра в новую комнату. Если комната не указана, выбирает случайную.
        Возвращает True, если перемещение успешно, иначе False.
        """
        if room_to_place:
            room = room_to_place
        else:
            empty_rooms = [a for a in floor.plan if (not a.monsters() 
                                                     and not a.monster_in_ambush()
                                                     and not a.trader 
                                                     and a != old_place 
                                                     and a.position != 0)]
            if not bool(empty_rooms):
                return False
            room = randomitem(empty_rooms)
        self.current_position = room
        floor.monsters_in_rooms[room].append(self)
        if old_place:
            floor.monsters_in_rooms[old_place].remove(self)
        if self.can_hide and dice(1, Monster._hide_possibility) == 1:
            places_to_hide = []
            for i in room.furniture:
                if i.can_hide:
                    places_to_hide.append(i)
            places_to_hide.append(room)
            self.hiding_place = randomitem(places_to_hide)
        if self.stink:
            floor.stink(room, 3)
            floor.stink_map()
        self.floor = floor
        return True


class Plant(Monster):
    """
    Класс Plant наследует класс Monster и представляет собой тип монстра - растение.
    Растения не могут носить оружие, щиты, броню, не агрессивны, не могут красть, прятаться или бегать.
    """
    def __init__(self,
                 game,
                 name='',
                 lexemes={},
                 stren=0,
                 health=0,
                 actions=[],
                 state='растёт',
                 agressive=False,
                 carry_weapon=False,
                 carry_shield=False):
        """
        Инициализирует экземпляр класса Plant с заданными параметрами.
        """
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


    def grow_in_room(self, room):
        """
        Метод для размножения растения. Создает новый экземпляр растения в указанной комнате.
        """
        new_plant = Plant(self.game, self.name, self.lexemes, self.stren, self.health, 'бьет', 'растет', False, False, False)
        new_plant.place(floor=room.floor, room_to_place=room)
        self.game.how_many_monsters += 1

    
    def win(self, loser=None):
        """
        Метод, вызываемый при победе растения над противником. Восстанавливает здоровье растения до начального уровня
        и пытается размножиться в соседние комнаты.
        """
        self.health = self.start_health
        self.grow()


    def grow(self):
        available_rooms = self.floor.get_rooms_around(self.current_position)
        roms_without_monsters = [room for room in available_rooms if not room.has_a_monster()]
        target_rooms = randomitem(roms_without_monsters, how_many=2)
        for room in target_rooms:
            self.grow_in_room(room)


    def place(self, floor, room_to_place = None, old_place = None):
        """
        Метод для размещения растения в комнате. Если комната не указана, выбирается случайная комната без монстров.
        """
        if room_to_place:
            room = room_to_place
        else:
            empty_rooms = [a for a in floor.plan if (not a.monsters() and not a.monster_in_ambush())]
            room = randomitem(empty_rooms)
        self.current_position = room
        self.floor = floor


class Berserk(Monster):
    """
    Класс Berserk наследует класс Monster и представляет собой тип монстра - берсерка.
    Берсерки известны своей агрессивностью и способностью накапливать ярость в бою, что делает их более сильными.
    """
    
    _rage_coefficient = 3
    """Какая часть потерянного здоровья берсерка уходит в его ярость (если 3, то 1/3)."""
    

    def __init__(self,
                 game,
                 name='',
                 lexemes={},
                 stren=0,
                 health=0,
                 actions=[],
                 state='мечется',
                 agressive=True,
                 carry_weapon=True,
                 carry_shield=True,
                 wear_armor=True):
        """
        Инициализирует экземпляр класса Berserk с заданными параметрами.
        
        :param game: ссылка на игру
        :param name: имя берсерка
        :param lexemes: лексемы, связанные с берсерком
        :param stren: сила берсерка
        :param health: здоровье берсерка
        :param actions: действия, которые может выполнять берсерк
        :param state: состояние берсерка
        :param agressive: является ли берсерк агрессивным
        :param carry_weapon: несет ли берсерк оружие
        :param carry_shield: несет ли берсерк щит
        :param wear_armor: носит ли берсерк броню
        """
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
        self.agressive = True  # Берсерки всегда агрессивны
        self.carry_shield = False  # Берсерки не носят щиты, предпочитая атаковать
        self.rage = 0  # Начальное значение ярости берсерка
        self.base_health = health  # Запоминаем начальное здоровье для расчета ярости
        self.agressive = True
        self.carry_shield = False
        self.rage = 0
        self.base_health = health
        self.empty = False
        self.can_resurrect=False
        self.can_run = True

   
    
    def generate_mele_attack(self, target):
        self.rage = (int(self.base_health) - int(self.health)) // Berserk._rage_coefficient
        if self.poisoned:
            poison_stren = dice(1, self.stren // 2)
        else:
            poison_stren = 0
        return dice(1, (self.stren + self.rage - poison_stren))


class Shapeshifter(Monster):
    """
    Класс Shapeshifter наследует класс Monster и представляет собой тип монстра - перевертыша.
    Перевертыши могут изменять свою форму, принимая облик своих противников.
    """
    def __init__(self, 
                game, 
                name='',
                lexemes={}, 
                stren=10, 
                health=20, 
                actions='бьет', 
                state='стоит', 
                agressive=True,
                carry_weapon=False, 
                carry_shield=True, 
                wear_armor=True):
        """
        Инициализирует экземпляр класса Shapeshifter с заданными параметрами.
        
        :param game: ссылка на игру
        :param name: имя перевертыша
        :param lexemes: лексемы, связанные с перевертышем
        :param stren: сила перевертыша
        :param health: здоровье перевертыша
        :param actions: действия, которые может выполнять перевертыш
        :param state: состояние перевертыша
        :param agressive: является ли перевертыш агрессивным
        :param carry_weapon: несет ли перевертыш оружие
        :param carry_shield: несет ли перевертыш щит
        :param wear_armor: носит ли перевертыш броню
        """
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
        self.shifted = False  # Флаг, указывающий на то, сменил ли перевертыш форму
        self.agressive = True
        self.empty = False
        self.start_stren = stren  # Начальная сила перевертыша для восстановления после боя
        self.can_run = True

    
    def defence(self, attacker):
        """
        Защита перевертыша, которая позволяет ему сменить форму, приняв облик атакующего.
        
        :param attacker: экземпляр атакующего
        :return: результат защиты
        """
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
                              f'У {self.g("него", "нее")} теперь сила {str(self.stren)}{weapon_string}')
        result = 0
        if not self.shield.empty:
            result += self.shield.protect(attacker)
            self.shield.take_damage(self.hide)
        if not self.armor.empty:
            result += self.armor.protect(attacker)
        return result
    
    
    def win(self, loser=None):
        """
        Восстанавливает начальные параметры перевертыша после победы в бою.
        
        :param loser: экземпляр проигравшего (не используется)
        """
        self.health = self.start_health
        self.stren = self.start_stren
        self.gender = self.start_gender
        self.shifted = False
        if self.weapon_changed:
            self.weapon = self.game.no_weapon
            self.weapon_changed = False


class Vampire(Monster):
    """
    Класс Vampire наследует класс Monster и представляет собой тип монстра - вампира.
    Вампиры обладают уникальной способностью высасывать здоровье из своих противников.
    """
    
    _suck_coefficient = 2
    """Какую часть урона вампир высасывает себе (если 2, то 1/2)."""

    def __init__(self, 
                 game, 
                 name='',
                 lexemes={}, 
                 stren=10, 
                 health=20, 
                 actions='бьет', 
                 state='стоит', 
                 agressive=False,
                 carry_weapon=True, 
                 carry_shield=True,
                 wear_armor=True):
        """
        Инициализирует экземпляр класса Vampire с заданными параметрами.
        
        :param game: ссылка на игру
        :param name: имя вампира
        :param lexemes: лексемы, связанные с вампиром
        :param stren: сила вампира
        :param health: здоровье вампира
        :param actions: действия, которые может выполнять вампир
        :param state: состояние вампира
        :param agressive: является ли вампир агрессивным
        :param carry_weapon: несет ли вампир оружие
        :param carry_shield: несет ли вампир щит
        :param wear_armor: носит ли вампир броню
        """
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
        self.can_run = True

    
    def vampire_suck(self, total_damage):
        """
        Высасывает здоровье из соперника, основываясь на общем нанесенном уроне.
        
        :param total_damage: общий урон, нанесенный сопернику
        :return: строка, описывающая действие и количество восстановленного здоровья
        """
        
        sucked = total_damage // Vampire._suck_coefficient
        self.health += sucked
        return f'{self.name} высасывает себе {str(sucked)} {howmany(sucked, ["жизнь", "жизни", "жизней"])}.'
    
    
    def place(self, floor, room_to_place = None, old_place = None):
        """
        Размещает вампира в комнате на этаже, учитывая возможность скрыться.
        
        :param floor: этаж, на котором нужно разместить вампира
        :param room_to_place: комната, в которой нужно разместить вампира (опционально)
        :param old_place: предыдущее местоположение вампира (опционально)
        :return: True, если вампир успешно размещен
        """
        if room_to_place:
            room = room_to_place
        else:
            empty_rooms = [a for a in floor.plan if (not a.monster_in_ambush() and not a.light and not a == old_place)]
            room = randomitem(empty_rooms)
        places_to_hide = []
        for i in room.furniture:
            if i.can_hide:
                places_to_hide.append(i)
        places_to_hide.append(room)
        where_to_hide = randomitem(places_to_hide)
        self.current_position = room
        self.hiding_place = where_to_hide
        self.floor = floor
        return True


class Animal(Monster):
    """Класс Animal наследует класс Monster и представляет собой тип монстра - животное."""
    
    def __init__(self, 
                 game, 
                 name='',
                 lexemes={}, 
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
        self.can_run = True
        self.wounds_list = [
            self.bleed,
            self.rage,
            self.contusion,
            self.leg_wound,
            self.become_a_zombie
        ]



class WalkingDead(Monster):
    """Класс WalkingDead наследует класс Monster и представляет собой тип монстра - ходячего мертвеца. 
    Эти существа обладают способностью воскрешаться после смерти и могут быть встречены в различных локациях игры."""
    
    def __init__(self, 
                 game, 
                 name='',
                 lexemes={}, 
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
        self.corpse = True
        self.can_run = True
        self.wounds_list = [
            self.rage,
            self.leg_wound,
            self.become_a_zombie,
            self.become_a_zombie,
            self.become_a_zombie,
        ]


class Corpse():
    """Класс Corpse представляет собой труп, который может воскреснуть или содержать лут. 
    Он связан с игровым миром, может быть размещен в комнате и имеет возможность воскрешения."""
    
    _places = (
        'В центре комнаты',
        'У стены',
        'Под окном',
        'У двери',
        'В тени'
    )
    """Массив возможных мест, где могут валяться трупы"""

    _states = (
        'лежит',
        'гниет',
        'воняет',
        'валяется'
    )
    """Массив возможных состояний трупов"""

    _depiction = (
        'изуродованный',
        'полуразложившийся',
        'окровавленный',
        'обезображенный',
        'почти не тронутый',
        'холодный',
        'скрюченный'
    )
    """Массив возможный прилагательных для трупа"""
    
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
        self.examined:bool = False
        self.creature = creature
        self.description:str = self.generate_description()
        self.place(room)
        self.can_resurrect:bool = can_resurrect
        
    
    def try_to_rise(self) -> bool:
        """Пытается воскресить существо, если это возможно."""
        if not self.creature or not self.can_resurrect:
            return False
        die = self.creature.resurrection_die
        if roll([die]) == 1:
            return self.rise_from_dead()
        return False
    
    
    def rise_from_dead(self):
        """Воскрешает существо и удаляет труп из игры."""
        self.creature.resurrect()
        self.creature.take_loot(self.loot)
        self.room.morgue.remove(self)
        self.game.all_corpses.remove(self)
        return True
    
    
    def place(self, room) -> bool:
        """Размещает труп в указанной комнате."""
        room.morgue.append(self)
        self.game.all_corpses.append(self)
        return True
    
    
    def generate_description(self) -> str:
        """Генерирует описание трупа."""
        place = choice(Corpse._places)
        state = choice(Corpse._states)
        depiction = choice(Corpse._depiction)
        description = f'{place} {state} {depiction} {self.name}'
        return description
    
    def check_name(self, message:str) -> bool:
        return message.lower() == self.name
    
    
    def get_examined(self, who) -> bool:
        if self.examined:
            return False
        if self.try_to_rise():
            tprint (self.game, f'{who.name} пытается осмотреть {self.name}, но неожиданно он возвращается к жизни.')
            return False
        return who.increase_monster_knowledge(self.creature.monster_type)
        
        