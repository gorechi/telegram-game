from math import ceil
from random import randint as dice
from random import choice

from src.class_basic import Loot, Money
from src.class_items import Rune
from src.class_protection import Armor, Shield
from src.class_weapon import Weapon
from src.class_fight import Fight
from src.functions.functions import howmany, randomitem, tprint, roll


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
    
    _initiative_die = 20
    """Кубик инициативы"""

    
    _types = {
        'basic': {
            "nom": "обычные противники",
            "accus": "обычных противников",
            "gen": "обычных противников",
            "dat": "обычным противникам",
            "prep": "обычных противниках",
            "inst": "обычными противниками"
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
        },
        'skeleton': {
            "nom": "скелеты",
            "accus": "скелетов",
            "gen": "скелетов",
            "dat": "скелетам",
            "prep": "скелетах",
            "inst": "скелетами"
        }

    }
    """Лексемы разных типов противников"""
    
    def __init__(self,
                 game,
                 name:str='',
                 lexemes:dict[str, str]={},
                 stren:int=50,
                 health:int=10,
                 actions:list[str]=['бьет'],
                 state:str='стоит',
                 agressive:bool=False,
                 carry_weapon:bool=True,
                 carry_shield:bool=False,
                 wear_armor:bool=False,
                 hit_chance:int=5,
                 parry_chance:int=2,
                 corpse:bool=True,
                 can_resurrect:bool=False):
        self.game = game
        self.name = name
        self.monster_type = 'basic'
        self.lexemes = lexemes
        self.stren = stren
        self.health = health
        self.actions = actions
        self.state = state
        self.corpse = corpse
        self.initiative = 2
        self.gender = 0
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
        self.last_attacker = None
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
    
    
    def make_noise_when_dead(self):
        return 0
    
    
    def check_light(self) -> bool:
        """Метод проверки, есть ли в комнате свет."""
        
        room = self.current_position
        if room.light:
            return True
        if self.weapon.element() in Rune._glowing_elements:
            return True
        if self.shield.element() in Rune._glowing_elements:
            return True
        if self.armor.element() in Rune._glowing_elements:
            return True
        return False
    
    
    def generate_initiative(self) -> int:
        return roll([Monster._initiative_die]) + self.initiative

    
    def is_hero(self) -> bool:
        return False
    
    
    def generate_in_fight_description(self, index:int) -> str:
        if self.current_position.light:
            line = f'{index}: {self.name}: сила - d{self.stren}'
            line += self.generate_weapon_text()
            line += self.generate_protection_text()
            line += f', жизней - {self.health}. '
            return line
        return Monster._names_in_darkness['nom']
    
    
    def generate_weapon_text(self) -> str:
        if not self.weapon.empty:
            return f'+d{self.weapon.damage}+{self.weapon.perm_damage()}'
        return ''
    
    
    def generate_protection_text(self) -> str:
        if not self.shield.empty and self.armor.empty:
            return f', защита - d{self.shield.protection}+{self.shield.perm_protection()}'
        elif self.shield.empty and not self.armor.empty:
            return f', защита - d{self.armor.protection}+{self.armor.perm_protection()}'
        elif not self.shield.empty and not self.armor.empty:
            return f', защита - d{self.armor.protection}+{self.armor.perm_protection()} + d{self.shield.protection}+{self.shield.perm_protection()}'
        return ''

    
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
            names_list =  ['противник', 'противника']
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
    
    
    def get_poison_protection(self) -> int:
        base_protection_die = roll([Monster._poison_base_protection_die])
        additional_protection_die = 0
        if self.armor.is_poisoned() or self.shield.is_poisoned():
            additional_protection_die = roll([Monster._poison_additional_protection_die])
        return base_protection_die + additional_protection_die
    
    
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
        protection = target.get_poison_protection()
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
            weapons = [i for i in all_weapons if i.type == self.prefered_weapon]
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
    
    
    def attack(self, fight:Fight) -> list[str]:
        target = self.choose_target(fight)
        hero = fight.hero
        self_name = self.get_name_in_darkness(hero)
        if not target:
            return False
        total_attack, message = self.generate_attack(target, self_name)
        target_defence = target.defence(self)
        if target_defence < 0:
            message.append(f'{target.name} {target.g("смог", "смогла")} увернуться от атаки и не потерять ни одной жизни.')
            return message
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
        self.last_attacker = None
        return message
        
        
    def choose_target(self, fight:Fight):
        targets = fight.get_targets(self)
        if not targets:
            return False
        if not fight.check_light():
            return self.choose_target_in_darkness(targets)
        if self.last_attacker and self.last_attacker in targets:
            return self.last_attacker
        if fight.hero:
            return fight.hero
        return randomitem(targets)

    
    def choose_target_in_darkness(self, targets:list):
        return randomitem(targets)
    
    
    def generate_attack(self, target, self_name:str) -> list[int, list[str]]:
        message = []
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
        if not target:
            return self.name
        if target.check_light():
            return self.name
        return Monster._names_in_darkness['nom']
    
    
    def get_hit_chance(self):
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
        hit_dice = dice(1, (weapon.get_hit_chance() + attacker.get_hit_chance()))
        if parry_dice > hit_dice:
            result = -1
        return result

    
    def finally_die(self, fight:Fight) -> bool:
        """
        Обрабатывает смерть монстра, удаляя его из списка монстров на этаже и в комнате, уменьшая общее количество монстров.
        Монстр становится мертвым и превращается в труп навсегда.
        """
        room = self.current_position
        try:
            self.floor.all_monsters.remove(self)
        except ValueError:
            print ('Не можем удалить себя из списка монстров. Ну и пофигу.')
        try:
            self.floor.monsters_in_rooms[room].remove(self)
        except ValueError:
            print ('Не можем удалить себя из списка монстров. Ну и пофигу.')
        self.game.how_many_monsters -= 1
        self.alive = False
        self.become_a_corpse(for_good=True)
        return f'{self:nom} падает замертво на пол комнаты.'
    
    
    def become_a_zombie(self, fight:Fight) -> bool:
        """
        Обрабатывает превращение монстра в зомби, удаляя его из списка монстров на этаже и в комнате, уменьшая общее количество монстров.
        Монстр становится мертвым, но может быть воскрешен.
        """
        room = self.current_position
        try:
            self.floor.all_monsters.remove(self)
        except ValueError:
            print ('Не можем удалить себя из списка монстров. Ну и пофигу.')
        try:
            self.floor.monsters_in_rooms[room].remove(self)
        except ValueError:
            print ('Не можем удалить себя из списка монстров. Ну и пофигу.')
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
        new_corpse = Corpse(self.game, corpse_name, self.loot, self.current_position, self, not for_good)  # noqa: F841
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

        
    def lose(self, fight:Fight) -> list[str]:
        """
        Обрабатывает поражение монстра. Определяет, умрет ли монстр, станет зомби или получит ранение в зависимости от результата броска кубика.
        """
        die = 15 if self.can_resurrect else 10
        result = roll([die])
        if result < 6 or self.wounded or not self.can_run:
            return self.finally_die(fight)
        else:
            return self.get_wounded(fight)
            
            
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
    
    
    def get_wounded(self, fight:Fight) -> list[str]:        
        """
        Обрабатывает получение ранения монстром. Может привести к различным последствиям, включая превращение в зомби.
        """
        self.wounded = True
        wound = randomitem(self.wounds_list)
        return wound(fight)
        
        
    def hand_wound(self, fight:Fight) -> list[str]:
        """
        Обрабатывает получение ранения в руку. Если у монстра есть оружие или щит, он их теряет.
        Возвращает True, указывая на то, что монстр остается в живых.
        """
        message = [f'{self.get_self_name_in_room()} остается в живых иполучает ранение в руку. ']
        if not self.weapon.empty:
            message.append(self.lose_weapon_text())
            self.current_position.loot.add(self.weapon)
            self.weapon = self.game.no_weapon
        elif not self.shield.empty:
            message.append(self.lose_shield_text())
            self.current_position.loot.add(self.shield)
            self.shield = self.game.no_shield
        message.append(self.try_to_run_away(fight))
        return message
        
        
    def bleed(self, fight:Fight) -> list[str]:
        """
        Обрабатывает ситуацию, когда монстр истекает кровью. Это приводит к потере силы,
        но здоровье восстанавливается до начального уровня. Возвращает True.
        """
        weakness_amount = ceil(self.stren * Monster._wounded_monster_strength_coefficient)
        self.stren -= weakness_amount
        self.health = self.start_health
        message = [f'{self.get_self_name_in_room()} остается в живых и истекает кровью, теряя при '
                   f'этом {howmany(weakness_amount, ["единицу", "единицы", "единиц"])} силы.']
        message.append(self.try_to_run_away(fight))
        return message
        
    
    def rage(self, fight:Fight) -> list[str]:
        """
        Обрабатывает вход в состояние ярости. Монстр получает увеличение силы, но теряет часть здоровья.
        Возвращает True.
        """
        strengthening_amount = ceil(self.stren * Monster._wounded_monster_strength_coefficient)
        ill_amount = ceil(self.start_health * Monster._wounded_monster_health_coefficient)
        self.stren += strengthening_amount
        self.health = self.start_health - ill_amount
        message = [f'{self.get_self_name_in_room()} остается в живых и приходит в ярость, получая при '
                   f'этом {howmany(strengthening_amount, ["единицу", "единицы", "единиц"])} силы и '
                   f'теряя {howmany(ill_amount, ["жизнь", "жизни", "жизней"])}.']
        message.append(self.try_to_run_away(fight))
        return message
    
    
    def contusion(self, fight:Fight) -> list[str]:
        """
        Обрабатывает получение контузии. Монстр теряет силу, но получает дополнительное здоровье.
        Возвращает True.
        """
        weakness_amount = ceil(self.stren * Monster._wounded_monster_strength_coefficient)
        health_boost_amount = ceil(self.start_health * Monster._wounded_monster_health_coefficient)
        self.stren -= weakness_amount
        self.health = self.start_health + health_boost_amount
        message = [f'{self.get_self_name_in_room()} остается в живых и получает контузию, теряя при '
                   f'этом {howmany(weakness_amount, ["единицу", "единицы", "единиц"])} силы и '
                   f'получая {howmany(health_boost_amount, ["жизнь", "жизни", "жизней"])}.']
        message.append(self.try_to_run_away(fight))
        return message

    
    def leg_wound(self, fight:Fight) -> list[str]:
        """
        Обрабатывает получение ранения в ногу. Монстр теряет силу и часть здоровья, а также не может двигаться.
        Возвращает True.
        """
        weakness_amount = ceil(self.stren * Monster._wounded_monster_strength_coefficient)
        ill_amount = ceil(self.start_health * Monster._wounded_monster_health_coefficient)
        self.stren -= weakness_amount
        self.health = self.start_health - ill_amount
        message =  [f'{self.get_self_name_in_room()} остается в живых, получает ранение в ногу и отползает куда-то в темный угол, теряя при ' 
                    f'этом {howmany(weakness_amount, ["единицу", "единицы", "единиц"])} силы '
                    f'и {howmany(ill_amount, ["жизнь", "жизни", "жизней"])}.']
        return message
    
    
    def try_to_run_away(self, fight) -> str:
        """
        Пытается убежать из комнаты. Если удачно, возвращает сообщение об убегании.
        В противном случае монстр умирает, врезавшись в стену.
        """
        name = self.get_self_name_in_room()
        if self.place(self.floor, old_place = self.current_position):
            return f'{name} убегает из комнаты.'
        else:
            self.finally_die(fight)
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


    def choose_target(self, fight:Fight):
        targets = fight.get_targets(self)
        if self.last_attacker and self.last_attacker in targets:
            return self.last_attacker
        return False
    
    
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
    
    
    def choose_target(self, fight:Fight):
        targets = fight.get_targets(self)
        if targets:
            return randomitem(targets)
        return False


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

    
    def choose_target(self, fight:Fight):
        classes_to_exclude = [
            'Vampire',
            'Plant',
            'Skeleton',
            'WalkingDead'
        ]
        return fight.get_fighter_by_health(self, classes_to_exclude, 'Min')

    
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


class Skeleton(Monster):
    """Класс Skeleton наследует класс Monster и представляет собой тип монстра - скелета. 
    Скелеты имунны к колющему и режущему оружию, но получают дополнительный урон от ударного."""
    
    _weapon_type_weaknesses = {
        'ударное': 2,
        'колющее': 0.3,
        'рубящее': 0.5
    }
    
    def __init__(self, 
                 game, 
                 name='',
                 lexemes={}, 
                 stren=10, 
                 health=20, 
                 actions='бьет', 
                 state='стоит', 
                 agressive=True,
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
        self.can_run = False
        self.wounds_list = [
            self.rage,
            self.leg_wound,
            self.hand_wound
        ]
    
    
    def get_weakness(self, weapon:Weapon) -> float:
        """Метод возвращает значение коэффициента ославбления/усиления 
        при использовании против монстра определенного оружия."""    
        
        return Skeleton._weapon_type_weaknesses[weapon.type]
    
    
    def choose_target(self, fight:Fight):
        not_undead = fight.get_fighter_by_health(self, exclude=['Skeleton', 'WalkingDead'], mode='Min')
        if not_undead:
            return not_undead
        return fight.get_fighter_by_health(self, exclude=['Skeleton'], mode='Min')
    
    
    def make_noise_when_dead(self):
        return 1
    
    
    def get_poison_protection(self) -> int:
        return 100


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
        
        