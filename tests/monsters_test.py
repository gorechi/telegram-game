import unittest
from unittest.mock import MagicMock, patch

from src.class_basic import Loot, Money
from src.class_dice import Dice
from src.class_protection import Armor, Shield
from src.class_rune import Rune
from src.class_weapon import Weapon
from src.class_monsters import (
    Monster, Plant, Berserk, Vampire, Animal, Human, Demon,
    WalkingDead, Skeleton, Corpse,
)
from src.controllers.controller_monsters import MonstersController


class EmptyItem:
    """Пустой предмет экипировки (аналог game.no_weapon/no_shield/no_armor)."""

    empty = True
    twohanded = False
    fencing = False
    weapon_type = None

    def element(self):
        return 0

    def get_hit_chance(self):
        return 0

    def get_poison_level(self):
        return 0

    def is_poisoned(self):
        return False

    def check_if_broken(self):
        return False

    def protect(self, attacker):
        return 0

    def take_damage(self, is_hiding=False):
        return None

    def can_be_enchanted(self):
        return False


class FakeMonstersController:
    """Заглушка контроллера монстров, запоминающая вызовы kill/resurrect."""

    def __init__(self):
        self.all_objects = []
        self.how_many = 0

    def kill_monster(self, monster):
        if monster in self.all_objects:
            self.all_objects.remove(monster)
            self.how_many -= 1
        return True

    def resurrect_monster(self, monster):
        self.all_objects.append(monster)
        self.how_many += 1
        return True


class FakeActionController:
    def __init__(self):
        self.actions = []

    def add_actions(self, item):
        self.actions.append(item)

    def delete_actions_by_item(self, item):
        if item in self.actions:
            self.actions.remove(item)


class FakeEventsController:
    def __init__(self):
        self.pending_events = []

    def create_event(self, **kwargs):
        pass

    def delete_pending_events_by_subject(self, subject):
        self.pending_events = [e for e in self.pending_events if e.get('event_subject') is not subject]


class FakeGame:
    def __init__(self):
        self.all_corpses = []
        self.no_weapon = EmptyItem()
        self.no_shield = EmptyItem()
        self.no_armor = EmptyItem()
        self.monsters_controller = FakeMonstersController()
        self.events_controller = FakeEventsController()
        self.weapon_controller = None


class FakeRoom:
    def __init__(self, light=True, trader=False, enter_point=False,
                 position=1, floor=None, furniture=None):
        self.light = light
        self.trader = trader
        self.enter_point = enter_point
        self.position = position
        self.floor = floor
        self.furniture = furniture if furniture is not None else []
        self.loot = Loot(game=None)
        self.morgue = []
        self.action_controller = FakeActionController()
        self.monsters_list = []
        self.ambush = False
        self.torch = None

    def monsters(self):
        return self.monsters_list

    def monster_in_ambush(self):
        return self.ambush

    def set_stink(self, value):
        self.stink = value


class FakeFloor:
    def __init__(self, plan=None, floor_number=1):
        self.plan = plan if plan is not None else []
        self.floor_number = floor_number
        self.monsters_in_rooms = {}
        self.all_monsters = []
        self.stink_mapped = False

    def set_stink(self, value):
        self.stink_calls.append(value)

    def stink_map(self):
        self.stink_mapped = True

    def get_rooms_around(self, room):
        return [r for r in self.plan if r is not room]


class FakeFurniture:
    def __init__(self, can_hide=False):
        self.can_hide = can_hide


def make_monster(cls=Monster, game=None, **attrs):
    """Создает монстра с полным набором атрибутов для тестов."""
    game = game if game is not None else FakeGame()
    monster = cls(game)
    defaults = {
        'stren': Dice([6]),
        'health': 10,
        'start_health': 10,
        'poisoned': False,
        'poison_level': Dice([0]),
        'poison_protection': Dice([5]),
        'parry_chance': Dice([6]),
        'hit_chance': Dice([6]),
        'initiative': Dice([6]),
        'can_hide': False,
        'can_run': True,
        'can_resurrect': False,
        'carry_weapon': True,
        'carry_shield': True,
        'carry_money': True,
        'wear_armor': True,
        'preferred_weapon': '',
        'disturbed': False,
        'wounded': False,
        'gender': 0,
        'name': 'Монстр',
        'lexemes': {'nom': 'монстр', 'accus': 'монстра', 'gen': 'монстра',
                    'dat': 'монстру', 'prep': 'монстре', 'inst': 'монстром'},
        'weakness': {},
        'monster_type': 'basic',
        'corpse': True,
        'stink': False,
        'alive': True,
        'floor': None,
        'current_position': None,
    }
    defaults.update(attrs)
    for key, value in defaults.items():
        setattr(monster, key, value)
    return monster


def make_weapon(game=None, empty=False, twohanded=False, weapon_type=None,
                damage=None, actions=('бьет',), name='оружие', enchantable=True):
    game = game if game is not None else FakeGame()
    weapon = Weapon(game)
    weapon.empty = empty
    weapon.twohanded = twohanded
    weapon.fencing = False
    weapon.weapon_type = weapon_type
    weapon.damage = damage if damage is not None else Dice([6])
    weapon.hit_chance = Dice([6])
    weapon.actions = list(actions)
    weapon.name = name
    weapon.enchantable = enchantable
    weapon.lexemes = {'nom': name, 'accus': name, 'gen': name}
    weapon.get_poison_level = lambda: 0
    return weapon


def make_shield(game=None, empty=False, name='щит'):
    game = game if game is not None else FakeGame()
    shield = Shield(game)
    shield.empty = empty
    shield.name = name
    shield.lexemes = {'nom': name, 'accus': name, 'gen': name}
    shield.protection = Dice([4])
    shield.can_be_enchanted = lambda: False
    shield.is_poisoned = lambda: False
    shield.check_if_broken = lambda: False
    shield.protect = lambda attacker: 0
    shield.take_damage = lambda is_hiding=False: None
    return shield


def make_armor(game=None, empty=False, name='броня'):
    game = game if game is not None else FakeGame()
    armor = Armor(game)
    armor.empty = empty
    armor.name = name
    armor.lexemes = {'nom': name, 'accus': name, 'gen': name}
    armor.protection = Dice([4])
    armor.can_be_enchanted = lambda: False
    armor.is_poisoned = lambda: False
    return armor


def setup_world(monster, n_rooms=2):
    """Создает этаж с комнатами и помещает монстра в первую комнату."""
    game = monster.game
    floor = FakeFloor()
    rooms = [FakeRoom(floor=floor, position=i + 1) for i in range(n_rooms)]
    floor.plan = rooms
    for room in rooms:
        floor.monsters_in_rooms[room] = []
    monster.floor = floor
    monster.current_position = rooms[0]
    floor.monsters_in_rooms[rooms[0]].append(monster)
    floor.all_monsters = [monster]
    return floor, rooms[0], rooms


class TestMonsterBasics(unittest.TestCase):
    """Простые методы базового класса Monster."""

    def test_str_returns_name(self):
        monster = make_monster(name='Орк')
        self.assertEqual(str(monster), 'Орк')

    def test_g_male(self):
        monster = make_monster(gender=0)
        self.assertEqual(monster.g('он', 'она'), 'он')

    def test_g_female(self):
        monster = make_monster(gender=1)
        self.assertEqual(monster.g('он', 'она'), 'она')

    def test_want_to_fight_disturbed(self):
        monster = make_monster(disturbed=True)
        self.assertTrue(monster.want_to_fight(MagicMock()))

    def test_want_to_fight_calm(self):
        monster = make_monster(disturbed=False)
        self.assertFalse(monster.want_to_fight(MagicMock()))

    def test_calm_down(self):
        monster = make_monster(disturbed=True)
        monster.calm_down()
        self.assertFalse(monster.disturbed)

    def test_be_attacked_calls_fight(self):
        monster = make_monster()
        who = MagicMock()
        result = monster.be_attacked(who)
        who.fight.assert_called_once_with(monster)
        self.assertEqual(result, '')

    def test_format_pronoun_male(self):
        monster = make_monster(gender=0)
        self.assertEqual(f'{monster:pronoun}', 'он')

    def test_format_pronoun_female(self):
        monster = make_monster(gender=1)
        self.assertEqual(f'{monster:pronoun}', 'она')

    def test_format_case(self):
        monster = make_monster()
        self.assertEqual(f'{monster:accus}', 'монстра')

    def test_format_unknown_case(self):
        monster = make_monster()
        self.assertEqual(f'{monster:smth}', '')

    def test_make_noise_when_dead(self):
        self.assertEqual(make_monster().make_noise_when_dead(), 0)

    def test_get_names_list(self):
        monster = make_monster()
        names = monster.get_names_list(['nom', 'accus'])
        self.assertIn('монстр', names)
        self.assertIn('монстра', names)
        self.assertIn('враг', names)
        self.assertIn('противник', names)

    def test_check_name_in_light(self):
        monster = make_monster()
        monster.current_position = FakeRoom(light=True)
        self.assertTrue(monster.check_name('Монстр'))
        self.assertFalse(monster.check_name('Скелет'))

    def test_check_name_in_darkness(self):
        monster = make_monster()
        monster.current_position = FakeRoom(light=False)
        self.assertTrue(monster.check_name('Противник'))
        self.assertFalse(monster.check_name('Монстр'))

    def test_get_name_from_lexemes(self):
        monster = make_monster()
        self.assertEqual(monster.get_name('accus'), 'монстра')

    def test_get_name_without_lexemes(self):
        monster = make_monster(lexemes={})
        self.assertEqual(monster.get_name('accus'), 'Монстр')

    def test_get_poison_protection(self):
        monster = make_monster(poison_protection=Dice([1]))
        self.assertIn(monster.get_poison_protection(), range(1, 2))

    def test_get_poison_protection_with_poisoned_armor(self):
        monster = make_monster(poison_protection=Dice([1]))
        monster.armor = make_armor(game=monster.game)
        monster.armor.is_poisoned = lambda: True
        self.assertEqual(monster.get_poison_protection(), 3)

    def test_action_returns_weapon_action(self):
        monster = make_monster()
        monster.weapon = make_weapon(game=monster.game, actions=['ударяет', 'бьет'])
        self.assertIn(monster.action(), ['ударяет', 'бьет'])

    def test_generate_initiative(self):
        monster = make_monster(initiative=Dice([6]))
        self.assertIn(monster.generate_initiative(), range(1, 7))

    def test_generate_weapon_text_empty(self):
        monster = make_monster()
        self.assertEqual(monster.generate_weapon_text(), '')

    def test_generate_weapon_text_with_weapon(self):
        monster = make_monster()
        monster.weapon = make_weapon(game=monster.game, damage=Dice([6]))
        self.assertEqual(monster.generate_weapon_text(), '+d6')

    def test_generate_protection_text_shield_only(self):
        monster = make_monster()
        monster.shield = make_shield(game=monster.game, empty=False)
        self.assertEqual(monster.generate_protection_text(), ', защита - d4')

    def test_generate_protection_text_armor_only(self):
        monster = make_monster()
        monster.armor = make_armor(game=monster.game, empty=False)
        self.assertEqual(monster.generate_protection_text(), ', защита - d4')

    def test_generate_protection_text_both(self):
        monster = make_monster()
        monster.shield = make_shield(game=monster.game, empty=False)
        monster.armor = make_armor(game=monster.game, empty=False)
        self.assertEqual(monster.generate_protection_text(), ', защита - d4 + d4')

    def test_generate_protection_text_none(self):
        monster = make_monster()
        self.assertEqual(monster.generate_protection_text(), '')

    def test_get_weaker(self):
        monster = make_monster(stren=Dice([6]), health=10, start_health=10)
        result = monster.get_weaker()
        self.assertTrue(result)
        self.assertLess(monster.health, 10)
        self.assertLessEqual(monster.stren.modifier, 0)

    def test_get_weaker_floor_health(self):
        monster = make_monster(stren=Dice([6]), health=1, start_health=1)
        result = monster.get_weaker()
        self.assertTrue(result)
        self.assertGreaterEqual(monster.health, 1)

    def test_get_name_for_being_attacked_in_light(self):
        monster = make_monster()
        who = MagicMock()
        who.check_light.return_value = True
        self.assertEqual(monster.get_name_for_being_attacked(who), 'Монстра')

    def test_get_name_for_being_attacked_in_darkness(self):
        monster = make_monster()
        who = MagicMock()
        who.check_light.return_value = False
        self.assertEqual(monster.get_name_for_being_attacked(who),
                         'Кого-то, прячущегося в темноте')

    def test_generate_in_fight_description_in_light(self):
        monster = make_monster(stren=Dice([6]), health=10)
        monster.current_position = FakeRoom(light=True)
        result = monster.generate_in_fight_description(2)
        self.assertIn('2: Монстр: сила - dd6', result)
        self.assertIn('жизней - 10', result)

    def test_generate_in_fight_description_in_darkness(self):
        monster = make_monster()
        monster.current_position = FakeRoom(light=False)
        self.assertEqual(monster.generate_in_fight_description(2),
                         Monster._names_in_darkness['nom'])


class TestMonsterLight(unittest.TestCase):
    """Метод check_light."""

    def setUp(self):
        self.monster = make_monster()
        self.monster.current_position = FakeRoom(light=False)

    def make_glowing_weapon(self):
        weapon = make_weapon(game=self.monster.game, empty=False)
        rune = Rune(self.monster.game)
        rune.element = 1
        weapon.runes.append(rune)
        return weapon

    def test_light_in_room(self):
        self.monster.current_position.light = True
        self.assertTrue(self.monster.check_light())

    def test_glowing_weapon(self):
        self.monster.weapon = self.make_glowing_weapon()
        self.assertTrue(self.monster.check_light())

    def test_glowing_shield(self):
        shield = make_shield(game=self.monster.game, empty=False)
        rune = Rune(self.monster.game)
        rune.element = 2
        shield.runes.append(rune)
        self.monster.shield = shield
        self.assertTrue(self.monster.check_light())

    def test_glowing_armor(self):
        armor = make_armor(game=self.monster.game, empty=False)
        rune = Rune(self.monster.game)
        rune.element = 4
        armor.runes.append(rune)
        self.monster.armor = armor
        self.assertTrue(self.monster.check_light())

    def test_no_light(self):
        self.assertFalse(self.monster.check_light())


class TestMonsterFightStart(unittest.TestCase):
    """Инициализация боя монстром."""

    @patch('src.class_monsters.Fight')
    def test_fight_with_hero(self, fight_class):
        game = FakeGame()
        monster = make_monster(game=game)
        enemy = MagicMock()
        enemy.is_hero.return_value = True
        result = monster.fight(enemy)
        self.assertTrue(result)
        fight_class.assert_called_once_with(
            game=game, hero=enemy, who_started=monster,
            fighters=[monster, enemy])
        fight_class.return_value.start.assert_called_once_with()

    @patch('src.class_monsters.Fight')
    def test_fight_without_hero(self, fight_class):
        game = FakeGame()
        monster = make_monster(game=game)
        enemy = MagicMock()
        enemy.is_hero.return_value = False
        result = monster.fight(enemy)
        self.assertTrue(result)
        fight_class.assert_called_once_with(
            game=game, hero=None, who_started=monster,
            fighters=[monster, enemy])


class TestMonsterCombat(unittest.TestCase):
    """Боевые методы Monster."""

    def test_generate_mele_attack_normal(self):
        monster = make_monster(stren=Dice([6]))
        target = MagicMock()
        target.check_light.return_value = True
        self.assertIn(monster.generate_mele_attack(target), range(1, 7))

    def test_generate_mele_attack_poisoned_and_dark(self):
        monster = make_monster(stren=Dice([6]), poisoned=True)
        target = MagicMock()
        target.check_light.return_value = False
        result = monster.generate_mele_attack(target)
        self.assertIn(result, range(0, 7))

    def test_generate_weapon_attack_empty(self):
        monster = make_monster()
        self.assertEqual(monster.generate_weapon_attack(MagicMock()), 0)

    def test_generate_weapon_attack_with_weapon(self):
        monster = make_monster()
        weapon = make_weapon(game=monster.game, empty=False)
        weapon.attack = lambda target: 8
        monster.weapon = weapon
        self.assertEqual(monster.generate_weapon_attack(MagicMock()), 8)

    def test_break_enemy_shield_broken(self):
        monster = make_monster()
        target = make_monster()
        target.shield = make_shield(game=monster.game, empty=False)
        target.shield.check_if_broken = lambda: True
        result = monster.break_enemy_shield(target, 10)
        self.assertIn('сокрушительный', result)

    def test_break_enemy_shield_not_broken(self):
        monster = make_monster()
        target = make_monster()
        result = monster.break_enemy_shield(target, 10)
        self.assertIsNone(result)

    def test_get_hit_chance(self):
        monster = make_monster(hit_chance=Dice([6]))
        weapon = make_weapon(game=monster.game)
        weapon.get_hit_chance = lambda: 3
        monster.weapon = weapon
        self.assertIn(monster.get_hit_chance(), range(4, 10))

    def test_defence_dodge(self):
        monster = make_monster(parry_chance=Dice([1]))
        attacker = make_monster(game=monster.game, hit_chance=Dice([0]))
        attacker.weapon = make_weapon(game=monster.game)
        attacker.weapon.hit_chance = Dice([0])
        self.assertEqual(monster.defence(attacker), -1)

    def test_defence_with_shield_and_armor(self):
        monster = make_monster(parry_chance=Dice([0]))
        shield = make_shield(game=monster.game, empty=False)
        calls = []
        shield.protect = lambda attacker: 2
        shield.take_damage = lambda is_hiding=False: calls.append(is_hiding)
        monster.shield = shield
        armor = make_armor(game=monster.game, empty=False)
        armor.protect = lambda attacker: 3
        monster.armor = armor
        attacker = make_monster(game=monster.game, hit_chance=Dice([0]))
        attacker.weapon = make_weapon(game=monster.game)
        attacker.weapon.hit_chance = Dice([0])
        self.assertEqual(monster.defence(attacker), 5)
        self.assertEqual(calls, [False])

    def test_defence_poisoned_halves_parry(self):
        monster = make_monster(parry_chance=Dice([6]), poisoned=True)
        attacker = make_monster(game=monster.game, hit_chance=Dice([0]))
        attacker.weapon = make_weapon(game=monster.game)
        attacker.weapon.hit_chance = Dice([0])
        with patch.object(monster.parry_chance, 'roll', return_value=3):
            self.assertEqual(monster.defence(attacker), -1)

    def test_attack_no_target(self):
        monster = make_monster()
        monster.current_position = FakeRoom(light=True)
        fight = MagicMock()
        fight.get_targets.return_value = []
        result = monster.attack(fight)
        self.assertIn('не', result)

    def test_attack_dodge(self):
        monster = make_monster()
        target = make_monster()
        target.current_position = FakeRoom(light=True)
        target.defence = lambda attacker: -1
        fight = MagicMock()
        fight.get_targets.return_value = [target]
        fight.hero = None
        result = monster.attack(fight)
        self.assertIn('увернуться', ' '.join(result))

    def test_attack_deals_damage(self):
        monster = make_monster()
        weapon = make_weapon(game=monster.game, empty=False)
        weapon.attack = lambda target: 5
        monster.weapon = weapon
        target = make_monster()
        target.current_position = FakeRoom(light=True)
        target.defence = lambda attacker: 3
        fight = MagicMock()
        fight.get_targets.return_value = [target]
        fight.hero = None
        result = monster.attack(fight)
        self.assertLess(target.health, 10)
        self.assertIn('теряет', ' '.join(str(x) for x in result))
        self.assertIsNone(monster.last_attacker)

    def test_attack_cannot_pierce(self):
        monster = make_monster()
        target = make_monster()
        target.current_position = FakeRoom(light=True)
        target.defence = lambda attacker: 99
        fight = MagicMock()
        fight.get_targets.return_value = [target]
        fight.hero = None
        result = monster.attack(fight)
        self.assertIn('пробить', ' '.join(result))
        self.assertEqual(target.health, 10)

    def test_attack_vampire_suck(self):
        vampire = make_monster(Vampire)
        weapon = make_weapon(game=vampire.game, empty=False)
        weapon.attack = lambda target: 10
        vampire.weapon = weapon
        target = make_monster(game=vampire.game)
        target.current_position = FakeRoom(light=True)
        target.defence = lambda attacker: 0
        fight = MagicMock()
        fight.get_fighter_by_health.return_value = target
        result = vampire.attack(fight)
        self.assertIn('высасывает', ' '.join(str(x) for x in result))
        self.assertGreater(vampire.health, 10)

    def test_choose_target_no_targets(self):
        monster = make_monster()
        fight = MagicMock()
        fight.get_targets.return_value = []
        self.assertFalse(monster.choose_target(fight))

    def test_choose_target_in_darkness(self):
        monster = make_monster()
        target = make_monster()
        fight = MagicMock()
        fight.get_targets.return_value = [target]
        fight.check_light.return_value = False
        self.assertIs(monster.choose_target(fight), target)

    def test_choose_target_last_attacker(self):
        monster = make_monster()
        last_attacker = make_monster()
        monster.last_attacker = last_attacker
        fight = MagicMock()
        fight.get_targets.return_value = [last_attacker]
        fight.check_light.return_value = True
        self.assertIs(monster.choose_target(fight), last_attacker)

    def test_choose_target_hero(self):
        monster = make_monster()
        hero = MagicMock()
        fight = MagicMock()
        fight.get_targets.return_value = [hero]
        fight.check_light.return_value = True
        fight.hero = hero
        self.assertIs(monster.choose_target(fight), hero)

    def test_choose_target_random(self):
        monster = make_monster()
        target_a = make_monster()
        target_b = make_monster()
        fight = MagicMock()
        fight.get_targets.return_value = [target_a, target_b]
        fight.check_light.return_value = True
        fight.hero = None
        self.assertIn(monster.choose_target(fight), [target_a, target_b])

    def test_choose_target_in_darkness_returns_random(self):
        monster = make_monster()
        targets = [make_monster(), make_monster()]
        self.assertIn(monster.choose_target_in_darkness(targets), targets)

    def test_generate_attack_with_weapon(self):
        monster = make_monster()
        weapon = make_weapon(game=monster.game, empty=False, name='меч')
        weapon.attack = lambda target: 7
        monster.weapon = weapon
        target = make_monster()
        monster.generate_mele_attack = lambda target: 4
        total, message = monster.generate_attack(target, 'Монстр')
        self.assertEqual(total, 11)
        self.assertTrue(any('используя' in m for m in message))

    def test_generate_attack_without_weapon(self):
        monster = make_monster()
        target = make_monster()
        monster.generate_mele_attack = lambda target: 4
        total, message = monster.generate_attack(target, 'Монстр')
        self.assertEqual(total, 4)
        self.assertTrue(any('не используя' in m for m in message))

    def test_get_name_in_darkness_no_target(self):
        monster = make_monster(name='Орк')
        self.assertEqual(monster.get_name_in_darkness(None), 'Орк')

    def test_get_name_in_darkness_light(self):
        monster = make_monster(name='Орк')
        target = MagicMock()
        target.check_light.return_value = True
        self.assertEqual(monster.get_name_in_darkness(target), 'Орк')

    def test_get_name_in_darkness_dark(self):
        monster = make_monster(name='Орк')
        target = MagicMock()
        target.check_light.return_value = False
        self.assertEqual(monster.get_name_in_darkness(target),
                         Monster._names_in_darkness['nom'])


class TestMonsterPoison(unittest.TestCase):
    """Отравление врага монстром."""

    def test_poison_enemy_poisons(self):
        monster = make_monster(poison_level=Dice([10]))
        target = make_monster(poison_protection=Dice([1]))
        with patch.object(monster.poison_level, 'roll', return_value=5):
            result = monster.poison_enemy(target)
        self.assertIsNotNone(result)
        self.assertTrue(target.poisoned)
        self.assertIn('отравление', result)

    def test_poison_enemy_no_poison(self):
        monster = make_monster(poison_level=Dice([0]))
        target = make_monster(poison_protection=Dice([10]))
        result = monster.poison_enemy(target)
        self.assertIsNone(result)
        self.assertFalse(target.poisoned)

    def test_poison_enemy_already_poisoned(self):
        monster = make_monster(poison_level=Dice([10]))
        target = make_monster(poisoned=True)
        self.assertIsNone(monster.poison_enemy(target))

    def test_poison_enemy_target_has_poison_level(self):
        monster = make_monster(poison_level=Dice([10]))
        target = make_monster(poison_level=Dice([6]))
        self.assertIsNone(monster.poison_enemy(target))

    def test_base_vampire_suck_does_nothing(self):
        self.assertIsNone(make_monster().vampire_suck(10))


class TestMonsterTake(unittest.TestCase):
    """Взятие предметов монстром."""

    def test_take_rune_no_enchantable(self):
        monster = make_monster()
        rune = Rune(monster.game)
        rune.damage = 2
        rune.defence = 1
        result = monster.take_rune(rune)
        self.assertFalse(result)
        self.assertIn(rune, monster.loot.pile)

    def test_take_rune_enchant_weapon(self):
        monster = make_monster()
        monster.weapon = make_weapon(game=monster.game, empty=False)
        rune = Rune(monster.game)
        rune.damage = 2
        rune.defence = 1
        result = monster.take_rune(rune)
        self.assertTrue(result)
        self.assertIn(rune, monster.weapon.runes)

    def test_choose_what_to_enchant_none(self):
        monster = make_monster()
        rune = Rune(monster.game)
        self.assertIsNone(monster.choose_what_to_enchant(rune))

    def test_choose_what_to_enchant_weapon(self):
        monster = make_monster()
        monster.weapon = make_weapon(game=monster.game, empty=False)
        rune = Rune(monster.game)
        rune.damage = 2
        rune.defence = 1
        self.assertIs(monster.choose_what_to_enchant(rune), monster.weapon)

    def test_choose_what_to_enchant_shield(self):
        monster = make_monster()
        monster.weapon = make_weapon(game=monster.game, empty=False)
        shield = make_shield(game=monster.game, empty=False)
        shield.can_be_enchanted = lambda: True
        monster.shield = shield
        rune = Rune(monster.game)
        rune.damage = 1
        rune.defence = 2
        self.assertIs(monster.choose_what_to_enchant(rune), shield)

    def test_take_weapon_already_has(self):
        monster = make_monster()
        monster.weapon = make_weapon(game=monster.game, empty=False)
        self.assertFalse(monster.take_weapon(make_weapon(game=monster.game)))

    def test_take_weapon_no_carry(self):
        monster = make_monster(carry_weapon=False)
        self.assertFalse(monster.take_weapon(make_weapon(game=monster.game)))

    def test_take_weapon_wrong_preferred(self):
        monster = make_monster(preferred_weapon='ударное')
        item = make_weapon(game=monster.game, empty=False, weapon_type='колющее')
        result = monster.take_weapon(item)
        self.assertTrue(result)
        self.assertIn(item, monster.loot.pile)
        self.assertTrue(monster.weapon.empty)

    def test_take_weapon_equips(self):
        monster = make_monster()
        item = make_weapon(game=monster.game, empty=False)
        result = monster.take_weapon(item)
        self.assertTrue(result)
        self.assertIs(monster.weapon, item)

    def test_take_weapon_from_loot_preferred(self):
        monster = make_monster(preferred_weapon='ударное')
        weapon_ok = make_weapon(game=monster.game, empty=False, weapon_type='ударное')
        weapon_other = make_weapon(game=monster.game, empty=False, weapon_type='колющее')
        loot = Loot(monster.game)
        loot.add(weapon_ok)
        loot.add(weapon_other)
        result = monster.take_weapon_from_loot(loot)
        self.assertTrue(result)
        self.assertIs(monster.weapon, weapon_ok)
        self.assertEqual(loot.pile, [weapon_other])

    def test_take_weapon_from_loot_no_preferred(self):
        monster = make_monster()
        weapon = make_weapon(game=monster.game, empty=False)
        loot = Loot(monster.game)
        loot.add(weapon)
        result = monster.take_weapon_from_loot(loot)
        self.assertTrue(result)
        self.assertIs(monster.weapon, weapon)
        self.assertEqual(loot.pile, [])

    def test_take_weapon_from_loot_already_equipped(self):
        monster = make_monster()
        monster.weapon = make_weapon(game=monster.game, empty=False)
        loot = Loot(monster.game)
        loot.add(make_weapon(game=monster.game, empty=False))
        self.assertFalse(monster.take_weapon_from_loot(loot))

    def test_take_weapon_from_loot_no_carry(self):
        monster = make_monster(carry_weapon=False)
        loot = Loot(monster.game)
        loot.add(make_weapon(game=monster.game, empty=False))
        self.assertFalse(monster.take_weapon_from_loot(loot))

    def test_take_weapon_from_loot_no_weapons(self):
        monster = make_monster()
        loot = Loot(monster.game)
        self.assertFalse(monster.take_weapon_from_loot(loot))

    def test_equip_weapon_simple(self):
        monster = make_monster()
        weapon = make_weapon(game=monster.game, empty=False)
        monster.equip_weapon(weapon)
        self.assertIs(monster.weapon, weapon)

    def test_equip_weapon_twohanded_drops_shield(self):
        monster = make_monster()
        old_shield = make_shield(game=monster.game, empty=False)
        monster.shield = old_shield
        room = FakeRoom(floor=FakeFloor())
        monster.current_position = room
        weapon = make_weapon(game=monster.game, empty=False, twohanded=True)
        monster.equip_weapon(weapon)
        self.assertIs(monster.weapon, weapon)
        self.assertIs(monster.shield, monster.game.no_shield)
        self.assertIn(old_shield, room.loot.pile)

    def test_take_shield_already_has(self):
        monster = make_monster()
        monster.shield = make_shield(game=monster.game, empty=False)
        self.assertFalse(monster.take_shield(make_shield(game=monster.game)))

    def test_take_shield_no_carry(self):
        monster = make_monster(carry_shield=False)
        self.assertFalse(monster.take_shield(make_shield(game=monster.game)))

    def test_take_shield_with_twohanded_weapon(self):
        monster = make_monster()
        monster.weapon = make_weapon(game=monster.game, empty=False, twohanded=True)
        item = make_shield(game=monster.game, empty=False)
        result = monster.take_shield(item)
        self.assertTrue(result)
        self.assertTrue(monster.shield.empty)
        self.assertIn(item, monster.loot.pile)

    def test_take_shield_ok(self):
        monster = make_monster()
        item = make_shield(game=monster.game, empty=False)
        result = monster.take_shield(item)
        self.assertTrue(result)
        self.assertIs(monster.shield, item)

    def test_take_shield_from_loot_no_carry(self):
        monster = make_monster(carry_shield=False)
        loot = Loot(monster.game)
        loot.add(make_shield(game=monster.game, empty=False))
        self.assertFalse(monster.take_shield_from_loot(loot))

    def test_take_shield_from_loot_twohanded(self):
        monster = make_monster()
        monster.weapon = make_weapon(game=monster.game, empty=False, twohanded=True)
        loot = Loot(monster.game)
        loot.add(make_shield(game=monster.game, empty=False))
        self.assertFalse(monster.take_shield_from_loot(loot))

    def test_take_shield_from_loot_no_shields(self):
        monster = make_monster()
        loot = Loot(monster.game)
        self.assertFalse(monster.take_shield_from_loot(loot))

    def test_take_shield_from_loot_ok(self):
        monster = make_monster()
        shield = make_shield(game=monster.game, empty=False)
        loot = Loot(monster.game)
        loot.add(shield)
        result = monster.take_shield_from_loot(loot)
        self.assertTrue(result)
        self.assertIs(monster.shield, shield)
        self.assertEqual(loot.pile, [])

    def test_take_armor_already_has(self):
        monster = make_monster()
        monster.armor = make_armor(game=monster.game, empty=False)
        self.assertFalse(monster.take_armor(make_armor(game=monster.game)))

    def test_take_armor_no_wear(self):
        monster = make_monster(wear_armor=False)
        self.assertFalse(monster.take_armor(make_armor(game=monster.game)))

    def test_take_armor_ok(self):
        monster = make_monster()
        item = make_armor(game=monster.game, empty=False)
        result = monster.take_armor(item)
        self.assertTrue(result)
        self.assertIs(monster.armor, item)

    def test_take_armor_from_loot_already_has(self):
        monster = make_monster()
        monster.armor = make_armor(game=monster.game, empty=False)
        loot = Loot(monster.game)
        loot.add(make_armor(game=monster.game, empty=False))
        self.assertFalse(monster.take_armor_from_loot(loot))

    def test_take_armor_from_loot_no_wear(self):
        monster = make_monster(wear_armor=False)
        loot = Loot(monster.game)
        loot.add(make_armor(game=monster.game, empty=False))
        self.assertFalse(monster.take_armor_from_loot(loot))

    def test_take_armor_from_loot_no_armor(self):
        monster = make_monster()
        loot = Loot(monster.game)
        self.assertFalse(monster.take_armor_from_loot(loot))

    def test_take_armor_from_loot_ok(self):
        monster = make_monster()
        armor = make_armor(game=monster.game, empty=False)
        loot = Loot(monster.game)
        loot.add(armor)
        result = monster.take_armor_from_loot(loot)
        self.assertTrue(result)
        self.assertIs(monster.armor, armor)
        self.assertEqual(loot.pile, [])

    def test_take_loot_moves_equipment(self):
        monster = make_monster()
        loot = Loot(monster.game)
        weapon = make_weapon(game=monster.game, empty=False, weapon_type='ударное')
        shield = make_shield(game=monster.game, empty=False)
        armor = make_armor(game=monster.game, empty=False)
        loot.add(weapon)
        loot.add(shield)
        loot.add(armor)
        monster.take_loot(loot)
        self.assertIs(monster.weapon, weapon)
        self.assertIs(monster.shield, shield)
        self.assertIs(monster.armor, armor)
        self.assertEqual(loot.pile, [])

    def test_take_loot_keeps_rest_when_equipped(self):
        monster = make_monster()
        monster.weapon = make_weapon(game=monster.game, empty=False)
        loot = Loot(monster.game)
        shield = make_shield(game=monster.game, empty=False)
        loot.add(shield)
        monster.take_loot(loot)
        self.assertIs(monster.shield, shield)
        self.assertEqual(loot.pile, [])

    def test_take_weapon_dispatch(self):
        monster = make_monster()
        weapon = make_weapon(game=monster.game, empty=False)
        self.assertTrue(monster.take(weapon))
        self.assertIs(monster.weapon, weapon)

    def test_take_shield_dispatch(self):
        monster = make_monster()
        shield = make_shield(game=monster.game, empty=False)
        self.assertTrue(monster.take(shield))
        self.assertIs(monster.shield, shield)

    def test_take_armor_dispatch(self):
        monster = make_monster()
        armor = make_armor(game=monster.game, empty=False)
        self.assertTrue(monster.take(armor))
        self.assertIs(monster.armor, armor)

    def test_take_rune_dispatch(self):
        monster = make_monster()
        monster.weapon = make_weapon(game=monster.game, empty=False)
        rune = Rune(monster.game)
        rune.damage = 2
        rune.defence = 1
        self.assertTrue(monster.take(rune))
        self.assertIn(rune, monster.weapon.runes)

    def test_take_money_dispatch(self):
        monster = make_monster(carry_money=True)
        money = Money(monster.game, how_much_money=5)
        self.assertTrue(monster.take(money))
        self.assertEqual(monster.loot.pile, [money])

    def test_take_other_dispatch(self):
        monster = make_monster()
        item = object()
        self.assertTrue(monster.take(item))
        self.assertIn(item, monster.loot.pile)


class TestMonsterDeathAndResurrect(unittest.TestCase):
    """Смерть, зомбирование, воскрешение и превращение в труп."""

    def test_finally_die(self):
        monster = make_monster()
        floor, room, rooms = setup_world(monster, n_rooms=1)
        result = monster.finally_die(MagicMock())
        self.assertEqual(result, 'монстр падает замертво на пол комнаты.')
        self.assertFalse(monster.alive)
        self.assertEqual(floor.all_monsters, [])
        self.assertEqual(floor.monsters_in_rooms[room], [])
        self.assertEqual(len(monster.game.all_corpses), 1)

    def test_finally_die_when_not_in_lists(self):
        monster = make_monster()
        floor, room, rooms = setup_world(monster, n_rooms=1)
        floor.all_monsters = []
        floor.monsters_in_rooms[room] = []
        result = monster.finally_die(MagicMock())
        self.assertFalse(monster.alive)
        self.assertEqual(result, 'монстр падает замертво на пол комнаты.')

    def test_become_a_zombie(self):
        monster = make_monster()
        floor, room, rooms = setup_world(monster, n_rooms=1)
        result = monster.become_a_zombie(MagicMock())
        self.assertTrue(result)
        self.assertFalse(monster.alive)
        self.assertEqual(floor.all_monsters, [])
        self.assertEqual(len(monster.game.all_corpses), 1)
        self.assertTrue(monster.game.all_corpses[0].can_resurrect)

    def test_become_a_zombie_when_not_in_lists(self):
        monster = make_monster()
        floor, room, rooms = setup_world(monster, n_rooms=1)
        floor.all_monsters = []
        floor.monsters_in_rooms[room] = []
        result = monster.become_a_zombie(MagicMock())
        self.assertTrue(result)
        self.assertFalse(monster.alive)
        self.assertEqual(len(monster.game.all_corpses), 1)

    def test_resurrect(self):
        monster = make_monster()
        floor, room, rooms = setup_world(monster, n_rooms=1)
        monster.alive = False
        floor.all_monsters = []
        floor.monsters_in_rooms[room] = []
        game = monster.game
        game.monsters_controller.all_objects = []
        game.monsters_controller.how_many = 0
        result = monster.resurrect()
        self.assertTrue(result)
        self.assertTrue(monster.alive)
        self.assertIn(monster, floor.all_monsters)
        self.assertIn(monster, floor.monsters_in_rooms[room])
        self.assertEqual(game.monsters_controller.how_many, 1)
        self.assertIn(monster, room.action_controller.actions)
        self.assertLess(monster.health, 10)

    def test_become_a_corpse_not_corpse(self):
        monster = make_monster(corpse=False)
        monster.current_position = FakeRoom()
        self.assertFalse(monster.become_a_corpse(for_good=True))

    def test_become_a_corpse_for_good(self):
        monster = make_monster()
        monster.shield = make_shield(game=monster.game, empty=False)
        room = FakeRoom(floor=FakeFloor())
        monster.current_position = room
        room.action_controller.add_actions(monster)
        result = monster.become_a_corpse(for_good=True)
        self.assertTrue(result)
        self.assertIn(monster.shield, monster.loot.pile)
        self.assertEqual(len(monster.game.all_corpses), 1)
        self.assertFalse(monster.game.all_corpses[0].can_resurrect)
        self.assertNotIn(monster, room.action_controller.actions)

    def test_gather_loot(self):
        monster = make_monster()
        monster.shield = make_shield(game=monster.game, empty=False)
        monster.armor = make_armor(game=monster.game, empty=False)
        monster.weapon = make_weapon(game=monster.game, empty=False)
        monster.gather_loot()
        self.assertEqual(len(monster.loot.pile), 3)

    def test_win(self):
        monster = make_monster(health=3, disturbed=True)
        monster.win()
        self.assertEqual(monster.health, 10)
        self.assertFalse(monster.disturbed)


class TestMonsterWounds(unittest.TestCase):
    """Ранения и попытки убежать."""

    def test_hand_wound_drops_weapon(self):
        monster = make_monster()
        weapon = make_weapon(game=monster.game, empty=False, name='меч')
        monster.weapon = weapon
        floor, room, rooms = setup_world(monster, n_rooms=2)
        messages = monster.hand_wound(MagicMock())
        self.assertIs(monster.weapon, monster.game.no_weapon)
        self.assertIn(weapon, room.loot.pile)
        self.assertTrue(any('убегает' in m for m in messages))

    def test_hand_wound_drops_shield(self):
        monster = make_monster()
        shield = make_shield(game=monster.game, empty=False)
        monster.shield = shield
        floor, room, rooms = setup_world(monster, n_rooms=2)
        messages = monster.hand_wound(MagicMock())
        self.assertIs(monster.shield, monster.game.no_shield)
        self.assertIn(shield, room.loot.pile)
        self.assertTrue(any('убегает' in m for m in messages))

    def test_bleed(self):
        monster = make_monster()
        monster.stren.modifier = 2
        floor, room, rooms = setup_world(monster, n_rooms=2)
        messages = monster.bleed(MagicMock())
        self.assertEqual(monster.health, monster.start_health)
        self.assertLess(monster.stren.modifier, 2)
        self.assertTrue(any('истекает кровью' in m for m in messages))

    def test_rage(self):
        monster = make_monster()
        floor, room, rooms = setup_world(monster, n_rooms=2)
        messages = monster.rage(MagicMock())
        self.assertEqual(monster.health, 6)
        self.assertGreater(monster.stren.modifier, 0)
        self.assertTrue(any('приходит в ярость' in m for m in messages))

    def test_rage_floor_health(self):
        monster = make_monster(start_health=1, health=1)
        monster.current_position = FakeRoom(light=True)
        floor, room, rooms = setup_world(monster, n_rooms=2)
        messages = monster.rage(MagicMock())
        self.assertGreaterEqual(monster.health, 1)

    def test_contusion(self):
        monster = make_monster()
        monster.stren.modifier = 2
        floor, room, rooms = setup_world(monster, n_rooms=2)
        messages = monster.contusion(MagicMock())
        self.assertEqual(monster.health, 14)
        self.assertLess(monster.stren.modifier, 2)
        self.assertTrue(any('получает контузию' in m for m in messages))

    def test_leg_wound(self):
        monster = make_monster()
        floor, room, rooms = setup_world(monster, n_rooms=2)
        messages = monster.leg_wound(MagicMock())
        self.assertEqual(monster.health, 6)
        self.assertTrue(any('ранение в ногу' in m for m in messages))

    def test_get_wounded(self):
        monster = make_monster()
        floor, room, rooms = setup_world(monster, n_rooms=2)
        with patch('src.class_monsters.randomitem',
                   side_effect=[monster.contusion, rooms[1]]):
            result = monster.get_wounded(MagicMock())
        self.assertTrue(monster.wounded)
        self.assertTrue(any('контузию' in m for m in result))

    def test_lose_finally_die(self):
        monster = make_monster()
        floor, room, rooms = setup_world(monster, n_rooms=2)
        with patch('src.class_monsters.roll', return_value=5):
            result = monster.lose(MagicMock())
        self.assertFalse(monster.alive)
        self.assertIn('падает замертво', result)

    def test_lose_wounded_finally_die(self):
        monster = make_monster(wounded=True)
        floor, room, rooms = setup_world(monster, n_rooms=2)
        with patch('src.class_monsters.roll', return_value=8):
            result = monster.lose(MagicMock())
        self.assertFalse(monster.alive)

    def test_lose_cannot_run_finally_die(self):
        monster = make_monster(can_run=False)
        floor, room, rooms = setup_world(monster, n_rooms=2)
        with patch('src.class_monsters.roll', return_value=8):
            result = monster.lose(MagicMock())
        self.assertFalse(monster.alive)

    def test_lose_get_wounded(self):
        monster = make_monster()
        floor, room, rooms = setup_world(monster, n_rooms=2)
        with patch('src.class_monsters.roll', return_value=8), \
                patch('src.class_monsters.randomitem',
                      side_effect=[monster.contusion, rooms[1]]):
            result = monster.lose(MagicMock())
        self.assertTrue(monster.wounded)
        self.assertTrue(any('контузию' in m for m in result))

    def test_lose_can_resurrect_uses_larger_die(self):
        monster = make_monster(can_resurrect=True)
        floor, room, rooms = setup_world(monster, n_rooms=2)
        with patch('src.class_monsters.roll', return_value=12) as roll_mock:
            monster.lose(MagicMock())
        roll_mock.assert_called_once_with([15])

    def test_lose_weapon_text_light(self):
        monster = make_monster()
        monster.weapon = make_weapon(game=monster.game, empty=False, name='меч')
        monster.current_position = FakeRoom(light=True)
        self.assertEqual(monster.lose_weapon_text(), 'На пол падает меч. ')

    def test_lose_weapon_text_dark(self):
        monster = make_monster()
        monster.current_position = FakeRoom(light=False)
        self.assertEqual(monster.lose_weapon_text(),
                         'Слышно, что какое-то оружие ударилось об пол комнаты. ')

    def test_lose_shield_text_light(self):
        monster = make_monster()
        monster.shield = make_shield(game=monster.game, empty=False, name='щит')
        monster.current_position = FakeRoom(light=True)
        self.assertEqual(monster.lose_shield_text(), 'На пол падает щит. ')

    def test_lose_shield_text_dark(self):
        monster = make_monster()
        monster.current_position = FakeRoom(light=False)
        self.assertEqual(monster.lose_shield_text(),
                         'В темноте можно услышать, что что-то большое упало в углу. ')

    def test_get_self_name_in_room_light(self):
        monster = make_monster()
        monster.current_position = FakeRoom(light=True)
        self.assertEqual(monster.get_self_name_in_room(), 'монстр')

    def test_get_self_name_in_room_dark(self):
        monster = make_monster()
        monster.current_position = FakeRoom(light=False)
        self.assertEqual(monster.get_self_name_in_room(), 'Противник')

    def test_try_to_run_away_success(self):
        monster = make_monster()
        floor, room, rooms = setup_world(monster, n_rooms=2)
        result = monster.try_to_run_away(MagicMock())
        self.assertEqual(result, 'монстр убегает из комнаты.')

    def test_try_to_run_away_death(self):
        monster = make_monster()
        floor, room, rooms = setup_world(monster, n_rooms=1)
        result = monster.try_to_run_away(MagicMock())
        self.assertIn('врезается в стену', result)
        self.assertFalse(monster.alive)


class TestMonsterPlace(unittest.TestCase):
    """Перемещение монстра между комнатами."""

    def test_place_to_given_room(self):
        monster = make_monster()
        floor, room, rooms = setup_world(monster, n_rooms=2)
        target = rooms[1]
        result = monster.place(floor, room_to_place=target)
        self.assertTrue(result)
        self.assertIs(monster.current_position, target)
        self.assertIn(monster, floor.monsters_in_rooms[target])
        self.assertIs(monster.floor, floor)

    def test_place_with_old_place(self):
        monster = make_monster()
        floor, room, rooms = setup_world(monster, n_rooms=3)
        result = monster.place(floor, old_place=room)
        self.assertTrue(result)
        self.assertNotIn(monster, floor.monsters_in_rooms[room])
        self.assertTrue(any(monster in floor.monsters_in_rooms[r]
                            for r in rooms[1:]))

    def test_place_no_rooms_for_old_place(self):
        monster = make_monster()
        floor, room, rooms = setup_world(monster, n_rooms=1)
        self.assertFalse(monster.place(floor, old_place=room))

    def test_place_random_empty_room(self):
        monster = make_monster()
        floor, room, rooms = setup_world(monster, n_rooms=2)
        room.monsters_list = [monster]
        with patch('src.class_monsters.randomitem', return_value=rooms[1]):
            result = monster.place(floor)
        self.assertTrue(result)
        self.assertIs(monster.current_position, rooms[1])

    def test_place_no_empty_rooms(self):
        monster = make_monster()
        floor, room, rooms = setup_world(monster, n_rooms=2)
        for r in rooms:
            r.monsters_list = [make_monster(game=monster.game)]
        self.assertFalse(monster.place(floor))

    def test_place_can_hide(self):
        monster = make_monster(can_hide=True)
        floor, room, rooms = setup_world(monster, n_rooms=1)
        furniture = FakeFurniture(can_hide=True)
        room.furniture = [furniture]
        with patch('src.class_monsters.randomitem', return_value=furniture), \
                patch.object(Monster, '_hide_possibility', Dice([1])):
            monster.place(floor, room_to_place=room)
        self.assertIs(monster.hiding_place, furniture)

    def test_place_stink(self):
        monster = make_monster(stink=True)
        floor, room, rooms = setup_world(monster, n_rooms=1)
        monster.place(floor, room_to_place=room)
        self.assertEqual(room.stink, 3)
        self.assertTrue(floor.stink_mapped)


class TestPlant(unittest.TestCase):
    """Класс Plant."""

    def test_want_to_fight_never(self):
        plant = make_monster(Plant)
        self.assertFalse(plant.want_to_fight(MagicMock()))

    def test_grow_in_room(self):
        plant = make_monster(Plant)
        game = plant.game
        game.monsters_controller = MagicMock()
        new_plant = MagicMock()
        game.monsters_controller.create_monster_by_name.return_value = new_plant
        room = FakeRoom(floor=FakeFloor())
        plant.grow_in_room(room)
        game.monsters_controller.create_monster_by_name.assert_called_once_with(plant.name)
        new_plant.place.assert_called_once_with(floor=room.floor, room_to_place=room)

    def test_win(self):
        plant = make_monster(Plant, health=5, disturbed=True)
        plant.grow = MagicMock()
        plant.win()
        self.assertEqual(plant.health, 10)
        self.assertFalse(plant.disturbed)
        plant.grow.assert_called_once_with()

    def test_grow(self):
        plant = make_monster(Plant)
        room1 = FakeRoom(floor=FakeFloor())
        room2 = FakeRoom(floor=FakeFloor())
        room3 = FakeRoom(floor=FakeFloor())
        plant.floor = MagicMock()
        plant.floor.get_rooms_around.return_value = [room1, room2, room3]
        plant.current_position = room1
        plant.grow_in_room = MagicMock()
        plant.grow()
        self.assertEqual(plant.grow_in_room.call_count, 2)

    def test_grow_single_room(self):
        plant = make_monster(Plant)
        room = FakeRoom(floor=FakeFloor())
        plant.floor = MagicMock()
        plant.floor.get_rooms_around.return_value = [room]
        plant.current_position = room
        plant.grow_in_room = MagicMock()
        plant.grow()
        self.assertEqual(plant.grow_in_room.call_count, 0)

    def test_choose_target_last_attacker(self):
        plant = make_monster(Plant)
        target = make_monster()
        plant.last_attacker = target
        fight = MagicMock()
        fight.get_targets.return_value = [target]
        self.assertIs(plant.choose_target(fight), target)

    def test_choose_target_no_attacker(self):
        plant = make_monster(Plant)
        fight = MagicMock()
        fight.get_targets.return_value = [make_monster()]
        self.assertFalse(plant.choose_target(fight))

    def test_place_to_given_room(self):
        plant = make_monster(Plant)
        floor, room, rooms = setup_world(plant, n_rooms=2)
        plant.place(floor, room_to_place=rooms[1])
        self.assertIs(plant.current_position, rooms[1])
        self.assertIn(plant, floor.monsters_in_rooms[rooms[1]])

    def test_place_random_room(self):
        plant = make_monster(Plant)
        floor, room, rooms = setup_world(plant, n_rooms=2)
        room.monsters_list = [make_monster(game=plant.game)]
        with patch('src.class_monsters.randomitem', return_value=rooms[1]):
            plant.place(floor)
        self.assertIs(plant.current_position, rooms[1])

    def test_generate_mele_attack_normal(self):
        plant = make_monster(Plant, stren=Dice([6]))
        target = MagicMock()
        target.check_light.return_value = True
        self.assertIn(plant.generate_mele_attack(target), range(1, 7))

    def test_generate_mele_attack_poisoned_and_dark(self):
        plant = make_monster(Plant, stren=Dice([6]), poisoned=True)
        target = MagicMock()
        target.check_light.return_value = False
        self.assertIn(plant.generate_mele_attack(target), range(0, 7))


class TestBerserk(unittest.TestCase):
    """Класс Berserk."""

    def test_want_to_fight_always(self):
        berserk = make_monster(Berserk)
        self.assertTrue(berserk.want_to_fight(MagicMock()))

    def test_generate_mele_attack_with_rage(self):
        berserk = make_monster(Berserk, start_health=10, health=7)
        result = berserk.generate_mele_attack(MagicMock())
        self.assertEqual(berserk.rage, 1)
        self.assertGreaterEqual(result, 2)

    def test_generate_mele_attack_poisoned(self):
        berserk = make_monster(Berserk, start_health=10, health=7, poisoned=True)
        result = berserk.generate_mele_attack(MagicMock())
        self.assertEqual(berserk.rage, 1)
        self.assertIn(result, range(0, 7))

    def test_choose_target(self):
        berserk = make_monster(Berserk)
        target = make_monster()
        fight = MagicMock()
        fight.get_targets.return_value = [target]
        self.assertIs(berserk.choose_target(fight), target)

    def test_choose_target_no_targets(self):
        berserk = make_monster(Berserk)
        fight = MagicMock()
        fight.get_targets.return_value = []
        self.assertFalse(berserk.choose_target(fight))


class TestVampire(unittest.TestCase):
    """Класс Vampire."""

    def make_fight_with_hero(self, hero):
        fight = MagicMock()
        fight.hero = hero
        return fight

    def test_want_to_fight_hero_with_light(self):
        hero = MagicMock()
        hero.weapon = MagicMock()
        hero.check_light.return_value = True
        vampire = make_monster(Vampire)
        self.assertFalse(vampire.want_to_fight(self.make_fight_with_hero(hero)))

    def test_want_to_fight_hero_with_water_weapon(self):
        hero = MagicMock()
        hero.weapon = MagicMock()
        hero.check_light.return_value = False
        hero.weapon.element.return_value = 12
        vampire = make_monster(Vampire)
        self.assertFalse(vampire.want_to_fight(self.make_fight_with_hero(hero)))

    def test_want_to_fight_in_dark(self):
        hero = MagicMock()
        hero.weapon = MagicMock()
        hero.check_light.return_value = False
        hero.weapon.element.return_value = 3
        vampire = make_monster(Vampire)
        self.assertTrue(vampire.want_to_fight(self.make_fight_with_hero(hero)))

    def test_choose_target(self):
        vampire = make_monster(Vampire)
        target = make_monster()
        fight = MagicMock()
        fight.get_fighter_by_health.return_value = target
        self.assertIs(vampire.choose_target(fight), target)
        fight.get_fighter_by_health.assert_called_once_with(
            vampire, ['Vampire', 'Plant', 'Skeleton', 'WalkingDead'], 'Min')

    def test_vampire_suck(self):
        vampire = make_monster(Vampire, health=10)
        message = vampire.vampire_suck(5)
        self.assertEqual(vampire.health, 12)
        self.assertIn('высасывает', message)

    def test_place_with_hiding_place(self):
        vampire = make_monster(Vampire)
        floor, room, rooms = setup_world(vampire, n_rooms=1)
        furniture = FakeFurniture(can_hide=True)
        room.furniture = [furniture]
        with patch('src.class_monsters.randomitem', return_value=room):
            result = vampire.place(floor, room_to_place=room)
        self.assertTrue(result)
        self.assertIs(vampire.current_position, room)
        self.assertIs(vampire.hiding_place, room)

    def test_place_random(self):
        vampire = make_monster(Vampire)
        floor, room, rooms = setup_world(vampire, n_rooms=2)
        with patch('src.class_monsters.randomitem', return_value=rooms[1]):
            result = vampire.place(floor)
        self.assertTrue(result)
        self.assertIs(vampire.current_position, rooms[1])
        self.assertIn(vampire, floor.monsters_in_rooms[rooms[1]])

    def test_place_with_old_place(self):
        vampire = make_monster(Vampire)
        floor, old_room, rooms = setup_world(vampire, n_rooms=3)
        new_room = rooms[2]
        new_room.furniture = []
        floor.monsters_in_rooms[new_room] = []
        self.assertIn(vampire, floor.monsters_in_rooms[old_room])
        with patch('src.class_monsters.randomitem', return_value=new_room):
            result = vampire.place(floor, old_place=old_room)
        self.assertTrue(result)
        self.assertIs(vampire.current_position, new_room)
        self.assertNotIn(vampire, floor.monsters_in_rooms[old_room])

    def test_place_stink(self):
        vampire = make_monster(Vampire, stink=True)
        floor, room, rooms = setup_world(vampire, n_rooms=2)
        room.floor = floor
        room.furniture = []
        with patch('src.class_monsters.randomitem', return_value=rooms[1]):
            result = vampire.place(floor)
        self.assertTrue(result)
        self.assertTrue(rooms[1].stink == 3)
        self.assertTrue(floor.stink_mapped)


class TestHumanDemonWalkingDead(unittest.TestCase):
    """Классы Human, Demon, WalkingDead."""

    def test_human_fights_when_disturbed(self):
        human = make_monster(Human, disturbed=True)
        self.assertTrue(human.want_to_fight(MagicMock()))

    def test_human_fights_with_other_human(self):
        human = make_monster(Human)
        other = make_monster(Human)
        fight = MagicMock()
        fight.fighters = [other]
        self.assertTrue(human.want_to_fight(fight))

    def test_human_does_not_fight(self):
        human = make_monster(Human)
        other = make_monster(Monster)
        fight = MagicMock()
        fight.fighters = [other]
        self.assertFalse(human.want_to_fight(fight))

    def test_demon_always_fights(self):
        demon = make_monster(Demon)
        self.assertTrue(demon.want_to_fight(MagicMock()))

    def test_walking_dead_always_fights(self):
        walking_dead = make_monster(WalkingDead)
        self.assertTrue(walking_dead.want_to_fight(MagicMock()))

    def test_walking_dead_wounds_include_zombie(self):
        walking_dead = make_monster(WalkingDead)
        self.assertEqual(walking_dead.wounds_list.count(walking_dead.become_a_zombie), 3)


class TestSkeletonMethods(unittest.TestCase):
    """Остальные методы Skeleton."""

    def test_make_noise_when_dead(self):
        skeleton = make_monster(Skeleton)
        self.assertEqual(skeleton.make_noise_when_dead(), 1)

    def test_get_poison_protection(self):
        skeleton = make_monster(Skeleton)
        self.assertEqual(skeleton.get_poison_protection(), 100)

    def test_choose_target_living(self):
        skeleton = make_monster(Skeleton)
        target = make_monster()
        fight = MagicMock()
        fight.get_fighter_by_health.return_value = target
        self.assertIs(skeleton.choose_target(fight), target)
        fight.get_fighter_by_health.assert_called_once_with(
            skeleton, exclude=['Skeleton', 'WalkingDead'], mode='Min')

    def test_choose_target_only_undead(self):
        skeleton = make_monster(Skeleton)
        target = make_monster(WalkingDead)
        fight = MagicMock()
        fight.get_fighter_by_health.side_effect = [None, target]
        self.assertIs(skeleton.choose_target(fight), target)
        fight.get_fighter_by_health.assert_called_with(
            skeleton, exclude=['Skeleton'], mode='Min')


class TestCorpse(unittest.TestCase):
    """Класс Corpse."""

    def setUp(self):
        self.game = FakeGame()
        self.room = FakeRoom()
        self.loot = Loot(self.game)
        self.creature = make_monster(WalkingDead)
        self.creature.monster_type = 'basic'
        self.creature.resurrect = MagicMock()
        self.creature.take_loot = MagicMock()
        self.corpse = Corpse(
            game=self.game, name='труп орка', loot=self.loot,
            room=self.room, creature=self.creature, can_resurrect=True)

    def test_after_search(self):
        self.assertIsNone(self.corpse.after_search(make_monster()))

    def test_place_adds_to_room_and_game(self):
        self.assertIn(self.corpse, self.room.morgue)
        self.assertIn(self.corpse, self.game.all_corpses)
        self.assertIn(self.corpse, self.room.action_controller.actions)

    def test_generate_description(self):
        self.assertIn(self.corpse.name, self.corpse.description)

    def test_check_name_matches(self):
        self.assertTrue(self.corpse.check_name('ТРУП ОРКА'))
        self.assertFalse(self.corpse.check_name('что-то другое'))

    def test_get_names_list(self):
        self.assertEqual(self.corpse.get_names_list(), ['труп', 'труп орка'])

    def test_try_to_rise_no_creature(self):
        corpse = Corpse(game=self.game, name='труп', loot=Loot(self.game),
                        room=FakeRoom(), creature=None, can_resurrect=True)
        self.assertFalse(corpse.try_to_rise())

    def test_try_to_rise_not_allowed(self):
        corpse = Corpse(game=self.game, name='труп', loot=Loot(self.game),
                        room=FakeRoom(), creature=self.creature, can_resurrect=False)
        self.assertFalse(corpse.try_to_rise())

    def test_try_to_rise_die_not_one(self):
        with patch('src.class_monsters.roll', return_value=2):
            self.assertFalse(self.corpse.try_to_rise())

    def test_try_to_rise_success(self):
        with patch('src.class_monsters.roll', return_value=1):
            self.assertTrue(self.corpse.try_to_rise())
        self.creature.resurrect.assert_called_once_with()
        self.assertNotIn(self.corpse, self.room.morgue)
        self.assertNotIn(self.corpse, self.game.all_corpses)

    def test_rise_from_dead(self):
        result = self.corpse.rise_from_dead()
        self.assertTrue(result)
        self.creature.resurrect.assert_called_once_with()
        self.creature.take_loot.assert_called_once_with(self.loot)
        self.assertNotIn(self.corpse, self.room.morgue)
        self.assertNotIn(self.corpse, self.game.all_corpses)
        self.assertNotIn(self.corpse, self.room.action_controller.actions)

    def test_examine_already_examined(self):
        self.corpse.examined = True
        result = self.corpse.examine(make_monster())
        self.assertIn('уже осматривал', result)

    def test_examine_rise(self):
        with patch('src.class_monsters.roll', return_value=1):
            result = self.corpse.examine(make_monster())
        self.assertIn('возвращается к жизни', result)

    def test_examine_increases_knowledge(self):
        self.corpse.can_resurrect = False
        who = make_monster()
        who.increase_monster_knowledge = MagicMock(return_value='новое знание')
        result = self.corpse.examine(who)
        self.assertEqual(result, 'новое знание')
        who.increase_monster_knowledge.assert_called_once_with('basic')

    def test_search_empty(self):
        corpse = Corpse(game=self.game, name='труп', loot=Loot(self.game),
                        room=FakeRoom(), creature=None)
        result = corpse.search(make_monster())
        self.assertIn('ничего не находит', result)

    def test_search_with_loot(self):
        corpse = Corpse(game=self.game, name='труп', loot=self.loot,
                        room=FakeRoom(), creature=None)
        corpse.loot.add(Money(game=self.game, how_much_money=5))
        corpse.loot.add(make_weapon(game=self.game, name='меч'))
        who = make_monster()
        result = corpse.search(who)
        self.assertIn('находит:', result[0])
        self.assertIn('разбросано по полу', result[-1])
        self.assertEqual(corpse.loot.pile, [])
        self.assertEqual(len(corpse.room.loot.pile), 2)


class TestMonstersControllerErrors(unittest.TestCase):
    """Ветки исключений и денег в MonstersController."""

    def setUp(self):
        self.controller = MonstersController(game=None)

    def make_template(self, boss=False):
        return self.controller.Template(
            class_name='Monster', name='Тест', lexemes={}, stren={}, health={},
            hit_chance={}, parry_chance={}, can_hide=False, can_run=True,
            actions=[], state='', frightening=False, aggressive=False,
            carry_weapon=False, carry_shield=False, poison_level={},
            poison_protection={}, gender=0, size={}, corpse=True,
            monster_type='basic', initiative={}, min_floor=1, max_floor=1,
            specific_floors=[], wear_armor=False, preferred_weapon='',
            stink=False, can_resurrect=False, weakness={}, carry_money=False,
            money=0, boss=boss)

    def test_generate_money_non_monster_raises(self):
        with self.assertRaises(TypeError):
            self.controller.generate_money('not_a_monster')

    def test_generate_money_carry_money(self):
        monster = make_monster(carry_money=True, money=15)
        result = self.controller.generate_money(monster)
        self.assertTrue(result)
        self.assertIsNone(monster.money)
        self.assertEqual(len(monster.loot.pile), 1)

    def test_generate_money_no_carry(self):
        monster = make_monster(carry_money=False, money=15)
        self.controller.generate_money(monster)
        self.assertIsNone(monster.money)
        self.assertEqual(monster.loot.pile, [])

    def test_get_templates_by_floor_type_error(self):
        with self.assertRaises(TypeError):
            self.controller.get_templates_by_floor('1')

    def test_get_templates_by_floor_matching(self):
        templates = self.controller.get_templates_by_floor(1)
        self.assertTrue(templates)
        for template in templates:
            self.assertFalse(template.boss)
            self.assertTrue(template.min_floor <= 1 <= template.max_floor
                            or 1 in template.specific_floors)

    def test_get_templates_by_floor_no_bosses(self):
        templates = self.controller.get_templates_by_floor(1000)
        for template in templates:
            self.assertFalse(template.boss)

    def test_get_random_boss_template_returns_boss(self):
        boss = self.controller.get_random_boss_template()
        self.assertTrue(boss.boss)

    def test_get_random_boss_template_no_bosses_raises(self):
        self.controller.templates = [self.make_template(boss=False)]
        with self.assertRaises(ValueError):
            self.controller.get_random_boss_template()

    def test_get_random_templates_by_floor_type_error(self):
        with self.assertRaises(TypeError):
            self.controller.get_random_templates_by_floor('1')

    def test_get_random_templates_by_floor_returns_list(self):
        templates = self.controller.get_random_templates_by_floor(1, how_many=3)
        self.assertEqual(len(templates), 3)
        for template in templates:
            self.assertFalse(template.boss)

    def test_get_random_templates_by_floor_single(self):
        templates = self.controller.get_random_templates_by_floor(1)
        self.assertEqual(len(templates), 1)


if __name__ == '__main__':
    unittest.main()
