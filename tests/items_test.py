import unittest
from unittest.mock import MagicMock, patch

from src.class_items import Spell, Matches, Map, Key


def make_game():
    game = MagicMock()
    game.player = MagicMock()
    return game


def make_floor(floor_number=1, rows=2, rooms=2):
    floor = MagicMock()
    floor.floor_number = floor_number
    floor.rows = rows
    floor.rooms = rooms
    floor.plan = []
    for i in range(rows * rooms):
        room = MagicMock()
        room.light = True
        room.locked = False
        room.furniture = []
        room.loot = MagicMock()
        room.doors = [MagicMock() for _ in range(4)]
        room.get_symbol_for_map.return_value = 'K'
        floor.plan.append(room)
    return floor


def make_hero(name='Герой', no_backpack=False, fear=0):
    hero = MagicMock()
    hero.name = name
    hero.g = lambda m, f: m
    hero.backpack = MagicMock()
    hero.backpack.no_backpack = no_backpack
    hero.current_position = MagicMock()
    hero.current_position.light = True
    hero.fear = fear
    hero.action_controller = MagicMock()
    return hero


# ==================== SPELL ====================


class TestSpell(unittest.TestCase):

    def test_init_defaults(self):
        game = make_game()
        s = Spell(game)
        self.assertIs(s.game, game)
        self.assertEqual(s.name, 'Обычное заклинание')
        self.assertEqual(s.element, 'магия')
        self.assertEqual(s.min_damage, 1)
        self.assertEqual(s.max_damage, 5)
        self.assertEqual(s.min_damage_mult, 1)
        self.assertEqual(s.max_damage_mult, 1)
        self.assertEqual(s.actions, 'кастует')
        self.assertFalse(s.empty)

    def test_init_custom(self):
        game = make_game()
        s = Spell(game, name='Огненный шар', element='огонь',
                  min_damage=2, max_damage=10, min_damage_mult=2,
                  max_damage_mult=3, actions='бросает')
        self.assertEqual(s.name, 'Огненный шар')
        self.assertEqual(s.element, 'огонь')
        self.assertEqual(s.min_damage, 2)
        self.assertEqual(s.max_damage, 10)
        self.assertEqual(s.min_damage_mult, 2)
        self.assertEqual(s.max_damage_mult, 3)
        self.assertEqual(s.actions, 'бросает')

    def test_description_equals_name(self):
        s = Spell(make_game(), name='Молния')
        self.assertEqual(s.description, 'Молния')

    def test_str(self):
        s = Spell(make_game(), name='Молния')
        self.assertEqual(str(s), 'Молния')

    def test_format_known_case(self):
        s = Spell(make_game())
        s.lexemes = {'nom': 'заклинание', 'accus': 'заклинание'}
        self.assertEqual(f'{s:nom}', 'заклинание')
        self.assertEqual(f'{s:accus}', 'заклинание')

    def test_format_unknown_case(self):
        s = Spell(make_game())
        s.lexemes = {'nom': 'заклинание'}
        self.assertEqual(f'{s:unknown}', '')

    def test_take_empty_who(self):
        s = Spell(make_game())
        self.assertFalse(s.take(''))

    def test_take_put_in_backpack(self):
        game = make_game()
        s = Spell(game)
        who = make_hero()
        who.backpack.no_backpack = False
        with patch('src.class_items.tprint'):
            s.take(who)
        who.backpack.add.assert_called_once_with(s)

    def test_take_no_backpack(self):
        game = make_game()
        s = Spell(game)
        who = make_hero(no_backpack=True)
        with patch('src.class_items.tprint'):
            s.take(who)
        who.backpack.add.assert_not_called()

    def test_check_name(self):
        s = Spell(make_game())
        s.lexemes = {'nom': 'заклинание', 'accus': 'заклинание'}
        self.assertTrue(s.check_name('заклинание'))
        self.assertTrue(s.check_name('ЗАКЛИНАНИЕ'))

    def test_check_name_wrong(self):
        s = Spell(make_game())
        s.lexemes = {'nom': 'заклинание'}
        self.assertFalse(s.check_name('меч'))

    def test_get_names_list(self):
        s = Spell(make_game())
        s.lexemes = {'nom': 'заклинание', 'accus': 'заклинание', 'gen': 'заклинания'}
        result = s.get_names_list(['nom', 'accus'])
        self.assertEqual(result, ['заклинание', 'заклинание', 'заклинание'])

    def test_get_names_list_no_cases(self):
        s = Spell(make_game())
        result = s.get_names_list(cases=[])
        self.assertEqual(result, ['заклинание'])

    def test_use_tprint_message(self):
        game = make_game()
        s = Spell(game)
        who = make_hero()
        with patch('src.class_items.tprint') as mock_tprint:
            s.use(who)
        mock_tprint.assert_called_once()
        self.assertIn('не знает', mock_tprint.call_args[0][1])


class TestMatchesInit(unittest.TestCase):

    def test_init_sets_attributes(self):
        game = make_game()
        m = Matches(game)
        self.assertIs(m.game, game)
        self.assertFalse(m.can_use_in_fight)
        self.assertEqual(m.name, 'спички')
        self.assertFalse(m.empty)
        self.assertIsNone(m.room)
        self.assertIsInstance(m.quantity, int)
        self.assertGreater(m.quantity, 0)
        self.assertLessEqual(m.quantity, 10)

    def test_quantity_die_is_d10(self):
        self.assertEqual(Matches._quantity_die.dice, [10])

    def test_hero_actions_keys(self):
        m = Matches(make_game())
        expected = {'осмотреть', 'пересчитать', 'посчитать', 'бросить', 'выбросить', 'оставить'}
        self.assertEqual(set(m.hero_actions.keys()), expected)

    def test_room_actions_keys(self):
        m = Matches(make_game())
        expected = {'взять', 'брать', 'собрать'}
        self.assertEqual(set(m.room_actions.keys()), expected)

    def test_drop_actions_method(self):
        m = Matches(make_game())
        for key in ['бросить', 'выбросить', 'оставить']:
            self.assertEqual(m.hero_actions[key]['method'], 'drop')

    def test_show_actions_method(self):
        m = Matches(make_game())
        for key in ['осмотреть', 'пересчитать', 'посчитать']:
            self.assertEqual(m.hero_actions[key]['method'], 'show')

    def test_room_actions_all_take(self):
        m = Matches(make_game())
        for key in m.room_actions:
            self.assertEqual(m.room_actions[key]['method'], 'take')

    def test_drop_actions_allow_darkness(self):
        m = Matches(make_game())
        for key in ['бросить', 'выбросить', 'оставить']:
            self.assertTrue(m.hero_actions[key]['in_darkness'])

    def test_show_actions_not_in_combat(self):
        m = Matches(make_game())
        for key in ['осмотреть', 'пересчитать', 'посчитать']:
            self.assertFalse(m.hero_actions[key]['in_combat'])


class TestMatchesFormat(unittest.TestCase):

    def test_format_known_cases(self):
        m = Matches(make_game())
        self.assertEqual(f'{m:accus}', 'спички')
        self.assertEqual(f'{m:gen}', 'спичек')
        self.assertEqual(f'{m:nom}', 'спички')
        self.assertEqual(f'{m:dat}', 'спичкам')
        self.assertEqual(f'{m:prep}', 'спичках')
        self.assertEqual(f'{m:inst}', 'спичками')

    def test_format_unknown_case(self):
        m = Matches(make_game())
        self.assertEqual(f'{m:unknown}', '')


class TestMatchesCheckName(unittest.TestCase):

    def test_matches_name(self):
        self.assertTrue(Matches(make_game()).check_name('спички'))

    def test_korobok_name(self):
        self.assertTrue(Matches(make_game()).check_name('коробок'))

    def test_wrong_name(self):
        self.assertFalse(Matches(make_game()).check_name('факел'))

    def test_case_insensitive(self):
        self.assertTrue(Matches(make_game()).check_name('СПИЧКИ'))


class TestMatchesGetQuantity(unittest.TestCase):

    def test_quantity_in_valid_range(self):
        game = make_game()
        for _ in range(200):
            m = Matches(game)
            self.assertGreaterEqual(m.quantity, 1)
            self.assertLessEqual(m.quantity, 10)


class TestMatchesGetQuantityText(unittest.TestCase):

    def setUp(self):
        self.m = Matches(make_game())

    def test_zero(self):
        self.assertEqual(self.m.get_quantity_text(0), 'Пустой спичечный коробок')

    def test_one(self):
        self.assertEqual(self.m.get_quantity_text(1), 'Коробок со всего одной спичкой')

    def test_two(self):
        self.assertEqual(self.m.get_quantity_text(2), 'Коробок, в котором болтается пара спичек')

    def test_three(self):
        self.assertEqual(self.m.get_quantity_text(3), 'Коробок, в котором есть немного спичек')

    def test_five(self):
        self.assertEqual(self.m.get_quantity_text(5), 'Коробок, в котором есть немного спичек')

    def test_six(self):
        self.assertEqual(self.m.get_quantity_text(6), 'Коробок, в котором много спичек')

    def test_nine(self):
        self.assertEqual(self.m.get_quantity_text(9), 'Коробок, в котором много спичек')

    def test_ten(self):
        self.assertEqual(self.m.get_quantity_text(10), 'Полный спичек коробок')


class TestMatchesAdd(unittest.TestCase):

    def test_add_matches(self):
        game = make_game()
        m1 = Matches(game)
        m2 = Matches(game)
        q1, q2 = m1.quantity, m2.quantity
        result = m1 + m2
        self.assertTrue(result)
        self.assertEqual(m1.quantity, q1 + q2)

    def test_add_non_matches_returns_false(self):
        m = Matches(make_game())
        self.assertFalse((m + 'str'))

    def test_add_non_matches_does_not_change_quantity(self):
        m = Matches(make_game())
        q = m.quantity
        m + 42
        self.assertEqual(m.quantity, q)


class TestMatchesStr(unittest.TestCase):

    def test_str(self):
        m = Matches(make_game())
        self.assertEqual(str(m), f'Коробок спичек, {m.quantity}')


class TestMatchesShow(unittest.TestCase):

    def test_show_returns_quantity_text(self):
        m = Matches(make_game())
        self.assertEqual(m.show(), m.get_quantity_text(m.quantity))


class TestMatchesPlace(unittest.TestCase):

    def test_place_in_specified_place(self):
        m = Matches(make_game())
        place = MagicMock()
        self.assertTrue(m.place(None, place=place))
        place.add.assert_called_once_with(m)

    def test_place_random_room_with_furniture(self):
        m = Matches(make_game())
        castle = MagicMock()
        room = MagicMock()
        room.locked = False
        room.light = True
        furn = MagicMock()
        room.furniture = [furn]
        castle.plan = [room]
        self.assertTrue(m.place(castle))
        self.assertIs(m.room, room)
        furn.add.assert_called_once_with(m)

    def test_place_random_room_without_furniture(self):
        m = Matches(make_game())
        castle = MagicMock()
        room = MagicMock()
        room.locked = False
        room.light = True
        room.furniture = []
        castle.plan = [room]
        self.assertTrue(m.place(castle))
        room.loot.add.assert_called_once_with(m)

    def test_place_all_locked_returns_false(self):
        m = Matches(make_game())
        castle = MagicMock()
        room = MagicMock()
        room.locked = True
        castle.plan = [room]
        self.assertFalse(m.place(castle))

    def test_place_all_dark_returns_false(self):
        m = Matches(make_game())
        castle = MagicMock()
        room = MagicMock()
        room.locked = False
        room.light = False
        castle.plan = [room]
        self.assertFalse(m.place(castle))

    def test_place_empty_plan_returns_false(self):
        m = Matches(make_game())
        castle = MagicMock()
        castle.plan = []
        self.assertFalse(m.place(castle))


class TestMatchesTake(unittest.TestCase):

    def test_take_none_returns_false(self):
        self.assertFalse(Matches(make_game()).take(None))

    def test_take_no_existing_matches_put_in_backpack(self):
        m = Matches(make_game())
        who = make_hero()
        who.backpack.get_first_item_by_class.return_value = False
        result = m.take(who)
        self.assertIn('забирает', result)
        who.put_in_backpack.assert_called_once_with(m)

    def test_take_merges_with_existing_matches(self):
        m_new = Matches(make_game())
        m_new.quantity = 5
        room = MagicMock()
        m_new.room = room
        m_existing = Matches(make_game())
        m_existing.quantity = 3
        who = make_hero()
        who.backpack.get_first_item_by_class.return_value = m_existing
        result = m_new.take(who)
        self.assertEqual(m_existing.quantity, 8)
        who.put_in_backpack.assert_not_called()
        room.loot.remove.assert_called_once_with(m_new)
        self.assertIsNone(m_new.room)
        self.assertIn('забирает', result)

    def test_take_no_backpack(self):
        m = Matches(make_game())
        who = make_hero(no_backpack=True)
        result = m.take(who)
        self.assertIn('не может забрать', result)


class TestMatchesUse(unittest.TestCase):

    def test_use_default_player_light_room(self):
        game = make_game()
        m = Matches(game)
        game.player.current_position.light = True
        result = m.use()
        self.assertEqual(result, 'Незачем тратить спички, здесь и так светло.')

    def test_use_light_room(self):
        m = Matches(make_game())
        who = make_hero()
        who.current_position.light = True
        self.assertEqual(m.use(who), 'Незачем тратить спички, здесь и так светло.')

    def test_use_fear_breaks_match(self):
        m = Matches(make_game())
        who = make_hero()
        who.current_position.light = False
        who.check_fear.return_value = True
        with patch('src.class_items.roll', return_value=1):
            result = m.use(who)
        self.assertIn('не слушаются', result)

    def test_use_fear_not_triggered_when_roll_not_one(self):
        m = Matches(make_game())
        m.quantity = 5
        who = make_hero()
        who.current_position.light = False
        who.check_fear.return_value = True
        with patch('src.class_items.roll', return_value=2):
            who.current_position.turn_on_light.return_value = ['Факел зажжён']
            result = m.use(who)
        self.assertIsInstance(result, list)
        self.assertEqual(m.quantity, 4)

    def test_use_dark_room_success(self):
        m = Matches(make_game())
        m.quantity = 5
        who = make_hero()
        who.current_position.light = False
        who.check_fear.return_value = False
        who.current_position.turn_on_light.return_value = ['Факел зажжён']
        result = m.use(who)
        self.assertIsInstance(result, list)
        self.assertEqual(m.quantity, 4)
        who.current_position.turn_on_light.assert_called_once_with(who)

    def test_use_last_match_removes_from_backpack(self):
        m = Matches(make_game())
        m.quantity = 1
        who = make_hero()
        who.current_position.light = False
        who.check_fear.return_value = False
        who.current_position.turn_on_light.return_value = ['Факел зажжён']
        result = m.use(who)
        self.assertEqual(m.quantity, 0)
        who.backpack.remove.assert_called_with(m)
        self.assertTrue(any('зашвыривает' in msg for msg in result))


class TestMatchesCheckIfEmpty(unittest.TestCase):

    def test_empty_removes_from_backpack(self):
        m = Matches(make_game())
        m.quantity = 0
        who = make_hero()
        result = m.check_if_empty(who)
        who.backpack.remove.assert_called_once_with(m)
        self.assertIn('зашвыривает', result)

    def test_not_empty_returns_careful_message(self):
        m = Matches(make_game())
        m.quantity = 3
        who = make_hero()
        result = m.check_if_empty(who)
        who.backpack.remove.assert_not_called()
        self.assertIn('бережно', result)


class TestMatchesGetNamesList(unittest.TestCase):

    def test_default_names(self):
        m = Matches(make_game())
        result = m.get_names_list(cases=['nom', 'accus'])
        self.assertIn('спички', result)
        self.assertIn('спичку', result)
        self.assertIn('спичка', result)
        self.assertIn('спички', result)

    def test_empty_cases(self):
        m = Matches(make_game())
        result = m.get_names_list(cases=[])
        self.assertEqual(len(result), 3)


class TestMatchesDrop(unittest.TestCase):

    def test_drop(self):
        m = Matches(make_game())
        who = make_hero()
        result = m.drop(who)
        room = who.current_position
        room.loot.add.assert_called_once_with(m)
        who.backpack.remove.assert_called_once_with(item=m, place=room)
        room.action_controller.add_actions.assert_called_once_with(m)
        who.action_controller.delete_actions_by_item.assert_called_once_with(m)
        self.assertIn('бросает', result)


class TestMatchesUseOne(unittest.TestCase):

    def test_use_one_decreases_quantity(self):
        m = Matches(make_game())
        m.quantity = 5
        m.use_one()
        self.assertEqual(m.quantity, 4)

    def test_use_one_at_zero_does_nothing(self):
        m = Matches(make_game())
        m.quantity = 0
        m.use_one()
        self.assertEqual(m.quantity, 0)


# ==================== MAP ====================


class TestMapInit(unittest.TestCase):

    def test_init_sets_attributes(self):
        game = make_game()
        floor = make_floor()
        m = Map(game, floor)
        self.assertIs(m.game, game)
        self.assertIs(m.floor, floor)
        self.assertFalse(m.can_use_in_fight)
        self.assertEqual(m.name, 'карта')
        self.assertFalse(m.empty)

    def test_decorated_on_init(self):
        game = make_game()
        floor = make_floor(floor_number=2)
        m = Map(game, floor)
        self.assertTrue(m.decorated)
        self.assertIn('2 этажа', m.description)

    def test_lexemes_decorated(self):
        game = make_game()
        floor = make_floor(floor_number=3)
        m = Map(game, floor)
        self.assertIn('3 этажа', m.lexemes['nom'])
        self.assertIn('3 этажа', m.lexemes['accus'])

    def test_hero_actions_keys(self):
        m = Map(make_game(), make_floor())
        expected = {'смотреть', 'использовать', 'прочитать', 'читать', 'бросить', 'выбросить', 'оставить'}
        self.assertEqual(set(m.hero_actions.keys()), expected)

    def test_room_actions_keys(self):
        m = Map(make_game(), make_floor())
        expected = {'взять', 'брать', 'собрать'}
        self.assertEqual(set(m.room_actions.keys()), expected)


class TestMapDecorate(unittest.TestCase):

    def test_decorate_only_once(self):
        game = make_game()
        floor = make_floor(floor_number=5)
        m = Map(game, floor)
        first_desc = m.description
        m.decorate()
        self.assertEqual(m.description, first_desc)

    def test_decorate_adds_floor_number(self):
        floor = make_floor(floor_number=7)
        m = Map(make_game(), floor)
        self.assertIn('7 этажа', m.description)


class TestMapFormat(unittest.TestCase):

    def test_format_known_cases(self):
        m = Map(make_game(), make_floor(floor_number=1))
        self.assertIn('карту', f'{m:accus}')
        self.assertIn('карты', f'{m:gen}')
        self.assertIn('карт', f'{m:nom}')

    def test_format_unknown_case(self):
        m = Map(make_game(), make_floor())
        self.assertEqual(f'{m:unknown}', '')


class TestMapCheckName(unittest.TestCase):

    def test_valid_names(self):
        m = Map(make_game(), make_floor())
        self.assertTrue(m.check_name('карта'))
        self.assertTrue(m.check_name('карту'))
        self.assertTrue(m.check_name('карты'))

    def test_invalid_name(self):
        m = Map(make_game(), make_floor())
        self.assertFalse(m.check_name('меч'))

    def test_case_insensitive(self):
        m = Map(make_game(), make_floor())
        self.assertTrue(m.check_name('КАРТА'))


class TestMapPlace(unittest.TestCase):

    def test_place_in_specified_place(self):
        m = Map(make_game(), make_floor())
        place = MagicMock()
        self.assertTrue(m.place(place=place))
        place.add.assert_called_once_with(m)

    @patch('src.class_items.randomitem')
    def test_place_random_room(self, mock_randomitem):
        m = Map(make_game(), make_floor())
        room = m.floor.plan[0]
        furn = MagicMock()
        room.furniture = [furn]
        mock_randomitem.side_effect = lambda lst: lst[0]
        m.place()
        furn.add.assert_called_once_with(m)

    @patch('src.class_items.randomitem')
    def test_place_no_furniture_uses_loot(self, mock_randomitem):
        floor = make_floor()
        floor.plan[0].furniture = []
        m = Map(make_game(), floor)
        room = m.floor.plan[0]
        mock_randomitem.return_value = room
        m.place()
        room.loot.add.assert_called_once_with(m)


class TestMapShow(unittest.TestCase):

    def test_show_returns_description(self):
        floor = make_floor(floor_number=1)
        m = Map(make_game(), floor)
        self.assertEqual(m.show(), m.description)


class TestMapGenerateMapText(unittest.TestCase):

    def test_in_action_returns_inappropriate(self):
        m = Map(make_game(), make_floor())
        who = make_hero()
        read_map, text = m.generate_map_text(who, in_action=True)
        self.assertFalse(read_map)
        self.assertIn('неуместно', text)

    def test_fear_blocks_reading(self):
        m = Map(make_game(), make_floor())
        who = make_hero()
        who.check_fear.return_value = False
        read_map, text = m.generate_map_text(who)
        self.assertFalse(read_map)
        self.assertIn('страха', text)

    def test_darkness_blocks_reading(self):
        m = Map(make_game(), make_floor())
        who = make_hero()
        who.check_fear.return_value = True
        who.current_position.light = False
        read_map, text = m.generate_map_text(who)
        self.assertFalse(read_map)
        self.assertIn('темно', text)

    def test_successful_reading(self):
        m = Map(make_game(), make_floor())
        who = make_hero()
        who.check_fear.return_value = True
        who.current_position.light = True
        read_map, text = m.generate_map_text(who)
        self.assertTrue(read_map)
        self.assertIn('смотрит на карту', text)


class TestMapUse(unittest.TestCase):

    def test_use_returns_text(self):
        m = Map(make_game(), make_floor())
        who = make_hero()
        who.check_fear.return_value = True
        who.current_position.light = True
        with patch.object(m, 'show_map'):
            result = m.use(who)
        self.assertIsInstance(result, str)

    def test_use_fear_returns_fear_message(self):
        m = Map(make_game(), make_floor())
        who = make_hero()
        who.check_fear.return_value = False
        result = m.use(who)
        self.assertIn('страха', result)

    def test_use_in_action_returns_battle_message(self):
        m = Map(make_game(), make_floor())
        who = make_hero()
        result = m.use(who, in_action=True)
        self.assertIn('неуместно', result)

    def test_use_success_calls_show_map(self):
        m = Map(make_game(), make_floor())
        who = make_hero()
        who.check_fear.return_value = True
        who.current_position.light = True
        with patch.object(m, 'show_map') as mock_sm:
            m.use(who)
            mock_sm.assert_called_once()


class TestMapTake(unittest.TestCase):

    def test_take_with_backpack(self):
        m = Map(make_game(), make_floor())
        who = make_hero()
        result = m.take(who)
        who.put_in_backpack.assert_called_once_with(m)
        self.assertIn('забирает', result)

    def test_take_no_backpack(self):
        m = Map(make_game(), make_floor())
        who = make_hero(no_backpack=True)
        result = m.take(who)
        self.assertIn('не может забрать', result)


class TestMapGetNamesList(unittest.TestCase):

    def test_returns_lexemes_for_cases(self):
        floor = make_floor(floor_number=1)
        m = Map(make_game(), floor)
        result = m.get_names_list(cases=['nom', 'accus'])
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)

    def test_empty_cases(self):
        m = Map(make_game(), make_floor())
        result = m.get_names_list(cases=[])
        self.assertEqual(result, [])


class TestMapDrop(unittest.TestCase):

    def test_drop(self):
        m = Map(make_game(), make_floor())
        who = make_hero()
        result = m.drop(who)
        room = who.current_position
        room.loot.add.assert_called_once_with(m)
        who.backpack.remove.assert_called_once_with(item=m, place=room)
        room.action_controller.add_actions.assert_called_once_with(m)
        who.action_controller.delete_actions_by_item.assert_called_once_with(m)
        self.assertIn('оставляет', result)


class TestMapShowMap(unittest.TestCase):

    def _make_door(self, char='-'):
        door = MagicMock()
        door.__format__ = lambda self, spec: char
        return door

    @patch('src.class_items.pprint')
    def test_show_map_calls_pprint(self, mock_pprint):
        floor = make_floor(floor_number=1, rows=2, rooms=2)
        for room in floor.plan:
            room.doors = [self._make_door() for _ in range(4)]
        m = Map(make_game(), floor)
        m.show_map()
        mock_pprint.assert_called_once()

    @patch('src.class_items.pprint')
    def test_show_map_builds_correct_text(self, mock_pprint):
        floor = make_floor(floor_number=1, rows=1, rooms=1)
        for room in floor.plan:
            room.doors = [self._make_door() for _ in range(4)]
        m = Map(make_game(), floor)
        m.show_map()
        call_args = mock_pprint.call_args
        text = call_args[0][1]
        self.assertIsInstance(text, list)
        self.assertTrue(len(text) > 0)
        self.assertTrue(text[0].startswith('===='))


# ==================== KEY ====================


class TestKeyInit(unittest.TestCase):

    def test_init_sets_attributes(self):
        game = make_game()
        k = Key(game)
        self.assertIs(k.game, game)
        self.assertFalse(k.can_use_in_fight)
        self.assertEqual(k.name, 'ключ')
        self.assertEqual(k.description, 'Ключ, пригодный для дверей и сундуков')
        self.assertFalse(k.empty)

    def test_lexemes(self):
        k = Key(make_game())
        self.assertEqual(k.lexemes['nom'], 'ключ')
        self.assertEqual(k.lexemes['accus'], 'ключ')
        self.assertEqual(k.lexemes['gen'], 'ключа')
        self.assertEqual(k.lexemes['dat'], 'ключу')
        self.assertEqual(k.lexemes['prep'], 'ключе')
        self.assertEqual(k.lexemes['inst'], 'ключом')

    def test_hero_actions_keys(self):
        k = Key(make_game())
        self.assertEqual(set(k.hero_actions.keys()), {'бросить', 'выбросить', 'оставить'})

    def test_room_actions_keys(self):
        k = Key(make_game())
        self.assertEqual(set(k.room_actions.keys()), {'взять', 'брать', 'собрать'})

    def test_drop_actions_allow_darkness(self):
        k = Key(make_game())
        for key in k.hero_actions:
            self.assertTrue(k.hero_actions[key]['in_darkness'])

    def test_room_actions_all_take(self):
        k = Key(make_game())
        for key in k.room_actions:
            self.assertEqual(k.room_actions[key]['method'], 'take')


class TestKeyFormat(unittest.TestCase):

    def test_format_known_cases(self):
        k = Key(make_game())
        self.assertEqual(f'{k:nom}', 'ключ')
        self.assertEqual(f'{k:accus}', 'ключ')
        self.assertEqual(f'{k:gen}', 'ключа')
        self.assertEqual(f'{k:dat}', 'ключу')
        self.assertEqual(f'{k:prep}', 'ключе')
        self.assertEqual(f'{k:inst}', 'ключом')

    def test_format_unknown_case(self):
        k = Key(make_game())
        self.assertEqual(f'{k:unknown}', '')


class TestKeyCheckName(unittest.TestCase):

    def test_valid_name(self):
        self.assertTrue(Key(make_game()).check_name('ключ'))

    def test_invalid_name(self):
        self.assertFalse(Key(make_game()).check_name('дверь'))

    def test_case_insensitive(self):
        self.assertTrue(Key(make_game()).check_name('КЛЮЧ'))


class TestKeyStr(unittest.TestCase):

    def test_str_returns_description(self):
        k = Key(make_game())
        self.assertEqual(str(k), k.description)


class TestKeyShow(unittest.TestCase):

    def test_show_returns_description(self):
        k = Key(make_game())
        self.assertEqual(k.show(), k.description)


class TestKeyOnCreate(unittest.TestCase):

    def test_on_create_returns_true(self):
        self.assertTrue(Key(make_game()).on_create())


class TestKeyPlace(unittest.TestCase):

    def test_place_in_specified_place(self):
        k = Key(make_game())
        place = MagicMock()
        self.assertTrue(k.place(None, place=place))
        place.add.assert_called_once_with(k)

    def test_place_in_room_furniture(self):
        k = Key(make_game())
        floor = MagicMock()
        room = MagicMock()
        room.get_random_unlocked_furniture.return_value = MagicMock()
        floor.get_random_unlocked_room.return_value = room
        result = k.place(floor)
        self.assertTrue(result)
        room.get_random_unlocked_furniture.return_value.add.assert_called_once_with(k)

    def test_place_in_room_loot(self):
        k = Key(make_game())
        floor = MagicMock()
        room = MagicMock()
        room.get_random_unlocked_furniture.return_value = None
        room.loot = MagicMock()
        floor.get_random_unlocked_room.return_value = room
        result = k.place(floor)
        self.assertTrue(result)
        room.loot.add.assert_called_once_with(k)

    def test_place_no_unlocked_room_returns_false(self):
        k = Key(make_game())
        floor = MagicMock()
        floor.get_random_unlocked_room.return_value = None
        self.assertFalse(k.place(floor))


class TestKeyTake(unittest.TestCase):

    def test_take_with_backpack(self):
        k = Key(make_game())
        who = make_hero()
        result = k.take(who)
        who.put_in_backpack.assert_called_once_with(k)
        self.assertIn('забирает', result)

    def test_take_no_backpack(self):
        k = Key(make_game())
        who = make_hero(no_backpack=True)
        result = k.take(who)
        self.assertIn('не может забрать', result)


class TestKeyGetNamesList(unittest.TestCase):

    def test_returns_lexemes(self):
        k = Key(make_game())
        result = k.get_names_list(cases=['nom', 'gen'])
        self.assertIsInstance(result, list)
        self.assertIn('ключ', result)

    def test_empty_cases(self):
        k = Key(make_game())
        result = k.get_names_list(cases=[])
        self.assertEqual(result, [])


class TestKeyDrop(unittest.TestCase):

    def test_drop(self):
        k = Key(make_game())
        who = make_hero()
        result = k.drop(who)
        room = who.current_position
        room.loot.add.assert_called_once_with(k)
        who.backpack.remove.assert_called_once_with(item=k, place=room)
        room.action_controller.add_actions.assert_called_once_with(k)
        who.action_controller.delete_actions_by_item.assert_called_once_with(k)
        self.assertIn('бросает', result)
