import unittest
from unittest.mock import MagicMock, patch

from src.processes.process import Process
from src.processes.process_trade import TradeProcess, BuyProcess, SellProcess
from src.processes.process_enchantment import EnchantmentProcess
from src.controllers.controller_processes import ProcessesController


class Weapon:
    def __init__(self, name='Меч', weapon_type='рубящее'):
        self.name = name
        self.weapon_type = weapon_type
        self.empty = False
    def show(self):
        return self.name
    def __format__(self, fmt):
        return self.name


class Shield:
    def __init__(self, name='Щит'):
        self.name = name
        self.empty = False
    def show(self):
        return self.name
    def __format__(self, fmt):
        return self.name


class Rune:
    def __init__(self, name='Руна огня'):
        self.name = name
    def show(self):
        return self.name
    def check_name(self, text):
        return text.lower() in self.name.lower()
    def __format__(self, fmt):
        return self.name
    def enchant(self):
        return True


def make_game():
    game = MagicMock()
    game.bot = MagicMock()
    game.chat_id = 'test_chat'
    game.processes_controller = ProcessesController(game)
    return game


def make_hero(name='Герой', gender=0, light=True, fear=False):
    hero = MagicMock()
    hero.name = name
    hero.gender = gender
    hero.g = lambda m, f: m if gender == 0 else f
    hero.__format__ = lambda self, fmt: name
    hero.check_light.return_value = light
    hero.check_fear.return_value = fear
    hero.weapon = MagicMock()
    hero.weapon.can_be_enchanted.return_value = False
    hero.shield = MagicMock()
    hero.shield.can_be_enchanted.return_value = False
    hero.removed_shield = MagicMock()
    hero.removed_shield.can_be_enchanted.return_value = False
    hero.armor = MagicMock()
    hero.armor.can_be_enchanted.return_value = False
    hero.backpack = MagicMock()
    hero.check_backpack.return_value = False
    hero.money = MagicMock()
    return hero


def make_trader(name='Торговец'):
    trader = MagicMock()
    trader.name = name
    trader.shop = []
    trader.goods_to_buy = []
    trader.__format__ = lambda self, fmt: name
    return trader


class _FakeProcess(Process):
    status_enum = TradeProcess.status_enum


class TestProcessBase(unittest.TestCase):

    def test_init(self):
        game = make_game()
        owner = make_hero()
        p = Process(game, owner, init_text='test')
        self.assertIs(p.game, game)
        self.assertIs(p.owner, owner)
        self.assertEqual(p.init_text, 'test')

    def test_termination_commands(self):
        for cmd in ['отмена', 'выход', 'закончить']:
            self.assertIn(cmd, Process._termination_commands)

    def test_check_termination_true(self):
        p = Process(make_game(), make_hero())
        for cmd in Process._termination_commands:
            self.assertTrue(p.check_termination(cmd))

    def test_check_termination_false(self):
        p = Process(make_game(), make_hero())
        self.assertFalse(p.check_termination('атаковать'))
        self.assertFalse(p.check_termination(''))

    def test_set_status(self):
        p = Process(make_game(), make_hero())
        p.set_status('new_status')
        self.assertEqual(p.status, 'new_status')

    def test_set_owner_status_light_no_fear(self):
        p = Process(make_game(), make_hero(light=True, fear=False))
        self.assertTrue(p.set_owner_status())

    def test_set_owner_status_too_dark(self):
        owner = make_hero(light=False, fear=False)
        p = _FakeProcess(make_game(), owner)
        result = p.set_owner_status()
        self.assertFalse(result)
        self.assertEqual(p.status, TradeProcess.status_enum.TOO_DARK)

    def test_set_owner_status_fear(self):
        owner = make_hero(light=True, fear=True)
        p = _FakeProcess(make_game(), owner)
        result = p.set_owner_status()
        self.assertFalse(result)
        self.assertEqual(p.status, TradeProcess.status_enum.FEAR)

    def test_terminate_calls_controller(self):
        game = make_game()
        p = Process(game, make_hero())
        game.processes_controller.register_process(p)
        with patch('src.processes.process.tprint'):
            p.terminate('goodbye')
        self.assertNotIn(p, game.processes_controller.queue)

    def test_send_message_termination(self):
        game = make_game()
        p = Process(game, make_hero())
        p._termination_statuses = ['TERMINAL']
        p._message_generators = {'TERMINAL': 'generate_test'}
        p.generate_test = MagicMock(return_value=['msg'])
        p.status = 'TERMINAL'
        game.processes_controller.register_process(p)
        with patch('src.processes.process.tprint') as mock_tprint:
            p.send_message()
        mock_tprint.assert_called_once()

    def test_send_message_non_termination(self):
        game = make_game()
        p = Process(game, make_hero())
        p._termination_statuses = []
        p._message_generators = {'ACTIVE': 'generate_test'}
        p.generate_test = MagicMock(return_value=['msg'])
        p.status = 'ACTIVE'
        with patch('src.processes.process.tprint') as mock_tprint:
            p.send_message()
        mock_tprint.assert_called_once()

    def test_generate_message(self):
        p = Process(make_game(), make_hero())
        p._message_generators = {'MY_STATUS': 'my_gen'}
        p.my_gen = MagicMock(return_value=['hello'])
        p.status = 'MY_STATUS'
        result = p.generate_message()
        self.assertEqual(result, ['hello'])


class TestTradeProcess(unittest.TestCase):

    def _make_trade(self, light=True, fear=False):
        game = make_game()
        owner = make_hero(light=light, fear=fear)
        trader = make_trader()
        with patch('src.processes.process.tprint'):
            tp = TradeProcess(game, owner, trader)
        return tp, game, owner, trader

    def test_init_sets_status(self):
        tp, *_ = self._make_trade()
        self.assertEqual(tp.status, TradeProcess.status_enum.WAITING_FOR_ACTION)

    def test_init_too_dark(self):
        tp, *_ = self._make_trade(light=False)
        self.assertEqual(tp.status, TradeProcess.status_enum.TOO_DARK)

    def test_init_fear(self):
        tp, *_ = self._make_trade(fear=True)
        self.assertEqual(tp.status, TradeProcess.status_enum.FEAR)

    def test_proceed_termination(self):
        tp, *_ = self._make_trade()
        with patch('src.processes.process.tprint') as mock_tprint:
            tp.proceed('отмена')
        mock_tprint.assert_called()

    def _make_trade_with_shop(self, light=True):
        game = make_game()
        owner = make_hero(light=light)
        trader = make_trader()
        trader.shop = [MagicMock()]
        with patch('src.processes.process.tprint'):
            tp = TradeProcess(game, owner, trader)
        return tp, game, owner, trader

    def _make_trade_with_goods(self, light=True):
        game = make_game()
        owner = make_hero(light=light)
        trader = make_trader()
        trader.goods_to_buy = [MagicMock()]
        with patch('src.processes.process.tprint'):
            tp = TradeProcess(game, owner, trader)
        return tp, game, owner, trader

    def test_proceed_buy_action(self):
        tp, game, *_ = self._make_trade_with_shop()
        with patch('src.processes.process.tprint'):
            tp.proceed('купить')
        self.assertEqual(len(game.processes_controller.queue), 1)
        self.assertIsInstance(game.processes_controller.queue[0], BuyProcess)

    def test_proceed_buy_action_variant(self):
        tp, game, *_ = self._make_trade_with_shop()
        with patch('src.processes.process.tprint'):
            tp.proceed('покупать')
        self.assertEqual(len(game.processes_controller.queue), 1)
        self.assertIsInstance(game.processes_controller.queue[0], BuyProcess)

    def test_proceed_buy_action_number(self):
        tp, game, *_ = self._make_trade_with_shop()
        with patch('src.processes.process.tprint'):
            tp.proceed('1')
        self.assertEqual(len(game.processes_controller.queue), 1)
        self.assertIsInstance(game.processes_controller.queue[0], BuyProcess)

    def test_proceed_sell_action(self):
        tp, game, *_ = self._make_trade_with_goods()
        with patch('src.processes.process.tprint'):
            tp.proceed('продать')
        self.assertEqual(len(game.processes_controller.queue), 1)
        self.assertIsInstance(game.processes_controller.queue[0], SellProcess)

    def test_proceed_sell_action_variant(self):
        tp, game, *_ = self._make_trade_with_goods()
        with patch('src.processes.process.tprint'):
            tp.proceed('продавать')
        self.assertEqual(len(game.processes_controller.queue), 1)
        self.assertIsInstance(game.processes_controller.queue[0], SellProcess)

    def test_proceed_sell_action_number(self):
        tp, game, *_ = self._make_trade_with_goods()
        with patch('src.processes.process.tprint'):
            tp.proceed('2')
        self.assertEqual(len(game.processes_controller.queue), 1)
        self.assertIsInstance(game.processes_controller.queue[0], SellProcess)

    def test_proceed_unknown_action(self):
        tp, *_ = self._make_trade()
        with patch('src.processes.process.tprint') as mock_tprint:
            tp.proceed('непонятное')
        mock_tprint.assert_called()

    def test_proceed_no_text(self):
        tp, *_ = self._make_trade()
        with patch('src.processes.process.tprint') as mock_tprint:
            tp.proceed()
        mock_tprint.assert_called()

    def test_start_buy(self):
        tp, game, *_ = self._make_trade_with_shop()
        with patch('src.processes.process.tprint'):
            result = tp.start_buy('меч')
        self.assertTrue(result)
        self.assertEqual(len(game.processes_controller.queue), 1)
        self.assertIsInstance(game.processes_controller.queue[0], BuyProcess)

    def test_start_sell(self):
        tp, game, *_ = self._make_trade_with_goods()
        with patch('src.processes.process.tprint'):
            result = tp.start_sell('меч')
        self.assertTrue(result)
        self.assertEqual(len(game.processes_controller.queue), 1)
        self.assertIsInstance(game.processes_controller.queue[0], SellProcess)

    def test_generate_actions_message(self):
        tp, *_ = self._make_trade()
        msg = tp.generate_actions_message()
        self.assertIsInstance(msg, list)
        self.assertTrue(len(msg) > 0)

    def test_generate_too_dark_message(self):
        tp, *_ = self._make_trade()
        msg = tp.generate_too_dark_message()
        self.assertIsInstance(msg, list)
        self.assertTrue(any('темноте' in m for m in msg))

    def test_generate_fear_message(self):
        tp, *_ = self._make_trade()
        msg = tp.generate_fear_message()
        self.assertIsInstance(msg, list)
        self.assertTrue(any('борьбы' in m for m in msg))

    def test_termination_statuses(self):
        self.assertIn(TradeProcess.status_enum.TOO_DARK, TradeProcess._termination_statuses)
        self.assertIn(TradeProcess.status_enum.FEAR, TradeProcess._termination_statuses)

    def test_message_generators_keys(self):
        for status in TradeProcess.status_enum:
            self.assertIn(status, TradeProcess._message_generators)


class TestBuyProcess(unittest.TestCase):

    def _make_buy(self, shop_items=None, light=True, fear=False, init_text=None):
        game = make_game()
        owner = make_hero(light=light, fear=fear)
        trader = make_trader()
        trader.shop = shop_items if shop_items is not None else []
        with patch('src.processes.process.tprint'):
            bp = BuyProcess(game, owner, trader, init_text=init_text)
        return bp, game, owner, trader

    def test_init_with_items(self):
        bp, *_ = self._make_buy(shop_items=[MagicMock()])
        self.assertEqual(bp.status, BuyProcess.status_enum.WAITING_FOR_ITEM)
        self.assertEqual(len(bp.items_list), 1)

    def test_init_empty_shop(self):
        bp, *_ = self._make_buy(shop_items=[])
        self.assertEqual(bp.status, BuyProcess.status_enum.NO_AVAILABLE_ITEMS)

    def test_init_too_dark(self):
        bp, *_ = self._make_buy(shop_items=[MagicMock()], light=False)
        self.assertEqual(bp.status, BuyProcess.status_enum.TOO_DARK)

    def test_init_fear(self):
        bp, *_ = self._make_buy(shop_items=[MagicMock()], fear=True)
        self.assertEqual(bp.status, BuyProcess.status_enum.FEAR)

    def test_init_terminated_on_fear(self):
        game = make_game()
        game.processes_controller.queue = []
        owner = make_hero(fear=True)
        trader = make_trader()
        trader.shop = [MagicMock()]
        with patch('src.processes.process.tprint'):
            BuyProcess(game, owner, trader)
        self.assertEqual(len(game.processes_controller.queue), 0)

    def test_init_terminated_on_dark(self):
        game = make_game()
        game.processes_controller.queue = []
        owner = make_hero(light=False)
        trader = make_trader()
        trader.shop = [MagicMock()]
        with patch('src.processes.process.tprint'):
            BuyProcess(game, owner, trader)
        self.assertEqual(len(game.processes_controller.queue), 0)

    def test_init_terminated_on_no_items(self):
        game = make_game()
        game.processes_controller.queue = []
        trader = make_trader()
        trader.shop = []
        with patch('src.processes.process.tprint'):
            BuyProcess(game, make_hero(), trader)
        self.assertEqual(len(game.processes_controller.queue), 0)

    def test_get_items_list_with_items(self):
        bp, *_ = self._make_buy(shop_items=[MagicMock()])
        items = bp.get_items_list()
        self.assertEqual(len(items), 1)

    def test_get_items_list_empty(self):
        bp, *_ = self._make_buy(shop_items=[])
        items = bp.get_items_list()
        self.assertEqual(items, [])
        self.assertEqual(bp.status, BuyProcess.status_enum.NO_AVAILABLE_ITEMS)

    def test_proceed_termination(self):
        bp, *_ = self._make_buy(shop_items=[MagicMock()])
        with patch('src.processes.process.tprint') as mock_tprint:
            bp.proceed('выход')
        mock_tprint.assert_called()

    def test_proceed_with_item_text(self):
        trader = make_trader()
        trader.sell.return_value = True
        trader.shop = [MagicMock()]
        game = make_game()
        owner = make_hero()
        with patch('src.processes.process.tprint'):
            bp = BuyProcess(game, owner, trader)
        with patch('src.processes.process.tprint'):
            bp.proceed('1')
        trader.sell.assert_called_once_with('1', owner)

    def test_proceed_no_text(self):
        bp, *_ = self._make_buy(shop_items=[MagicMock()])
        with patch('src.processes.process.tprint') as mock_tprint:
            bp.proceed()
        mock_tprint.assert_called()

    def test_buy_item_success(self):
        trader = make_trader()
        trader.sell.return_value = True
        trader.shop = [MagicMock()]
        game = make_game()
        with patch('src.processes.process.tprint'):
            bp = BuyProcess(game, make_hero(), trader)
        with patch('src.processes.process.tprint'):
            self.assertTrue(bp.buy_item('1'))

    def test_buy_item_failure(self):
        trader = make_trader()
        trader.sell.return_value = False
        trader.shop = [MagicMock()]
        game = make_game()
        with patch('src.processes.process.tprint'):
            bp = BuyProcess(game, make_hero(), trader)
        with patch('src.processes.process.tprint'):
            self.assertFalse(bp.buy_item('999'))

    def test_generate_item_message(self):
        bp, *_ = self._make_buy(shop_items=[MagicMock()])
        msg = bp.generate_item_message()
        self.assertIsInstance(msg, list)
        self.assertTrue(len(msg) > 0)

    def test_generate_no_items_message(self):
        bp, *_ = self._make_buy(shop_items=[])
        msg = bp.generate_no_items_message()
        self.assertIsInstance(msg, list)
        self.assertTrue(any('пусто' in m for m in msg))

    def test_generate_too_dark_message(self):
        bp, *_ = self._make_buy()
        msg = bp.generate_too_dark_message()
        self.assertIsInstance(msg, list)
        self.assertTrue(any('темноте' in m for m in msg))

    def test_generate_fear_message(self):
        bp, *_ = self._make_buy()
        msg = bp.generate_fear_message()
        self.assertIsInstance(msg, list)
        self.assertTrue(any('покупок' in m for m in msg))

    def test_termination_statuses(self):
        self.assertIn(BuyProcess.status_enum.NO_AVAILABLE_ITEMS, BuyProcess._termination_statuses)
        self.assertIn(BuyProcess.status_enum.TOO_DARK, BuyProcess._termination_statuses)
        self.assertIn(BuyProcess.status_enum.FEAR, BuyProcess._termination_statuses)

    def test_message_generators_all_statuses(self):
        for status in BuyProcess.status_enum:
            self.assertIn(status, BuyProcess._message_generators)


class TestSellProcess(unittest.TestCase):

    def _make_sell(self, goods_items=None, light=True, fear=False):
        game = make_game()
        owner = make_hero(light=light, fear=fear)
        trader = make_trader()
        trader.goods_to_buy = goods_items if goods_items is not None else []
        with patch('src.processes.process.tprint'):
            sp = SellProcess(game, owner, trader)
        return sp, game, owner, trader

    def test_init_with_items(self):
        sp, *_ = self._make_sell(goods_items=[MagicMock()])
        self.assertEqual(sp.status, SellProcess.status_enum.WAITING_FOR_ITEM)

    def test_init_empty_goods(self):
        sp, *_ = self._make_sell(goods_items=[])
        self.assertEqual(sp.status, SellProcess.status_enum.NO_AVAILABLE_ITEMS)

    def test_init_too_dark(self):
        sp, *_ = self._make_sell(goods_items=[MagicMock()], light=False)
        self.assertEqual(sp.status, SellProcess.status_enum.TOO_DARK)

    def test_init_fear(self):
        sp, *_ = self._make_sell(goods_items=[MagicMock()], fear=True)
        self.assertEqual(sp.status, SellProcess.status_enum.FEAR)

    def test_init_terminated_on_fear(self):
        game = make_game()
        game.processes_controller.queue = []
        owner = make_hero(fear=True)
        trader = make_trader()
        trader.goods_to_buy = [MagicMock()]
        with patch('src.processes.process.tprint'):
            SellProcess(game, owner, trader)
        self.assertEqual(len(game.processes_controller.queue), 0)

    def test_init_terminated_on_dark(self):
        game = make_game()
        game.processes_controller.queue = []
        owner = make_hero(light=False)
        trader = make_trader()
        trader.goods_to_buy = [MagicMock()]
        with patch('src.processes.process.tprint'):
            SellProcess(game, owner, trader)
        self.assertEqual(len(game.processes_controller.queue), 0)

    def test_init_terminated_on_no_items(self):
        game = make_game()
        game.processes_controller.queue = []
        trader = make_trader()
        trader.goods_to_buy = []
        with patch('src.processes.process.tprint'):
            SellProcess(game, make_hero(), trader)
        self.assertEqual(len(game.processes_controller.queue), 0)

    def test_get_items_list_empty(self):
        sp, *_ = self._make_sell(goods_items=[])
        items = sp.get_items_list()
        self.assertEqual(items, [])
        self.assertEqual(sp.status, SellProcess.status_enum.NO_AVAILABLE_ITEMS)

    def test_proceed_termination(self):
        sp, *_ = self._make_sell(goods_items=[MagicMock()])
        with patch('src.processes.process.tprint') as mock_tprint:
            sp.proceed('закончить')
        mock_tprint.assert_called()

    def test_proceed_with_item_text(self):
        trader = make_trader()
        trader.buy.return_value = True
        trader.goods_to_buy = [MagicMock()]
        game = make_game()
        with patch('src.processes.process.tprint'):
            sp = SellProcess(game, make_hero(), trader)
        with patch('src.processes.process.tprint'):
            sp.proceed('1')
        trader.buy.assert_called_once_with('1', sp.owner)

    def test_proceed_no_text(self):
        sp, *_ = self._make_sell(goods_items=[MagicMock()])
        with patch('src.processes.process.tprint') as mock_tprint:
            sp.proceed()
        mock_tprint.assert_called()

    def test_sell_item_success(self):
        trader = make_trader()
        trader.buy.return_value = True
        trader.goods_to_buy = [MagicMock()]
        game = make_game()
        with patch('src.processes.process.tprint'):
            sp = SellProcess(game, make_hero(), trader)
        with patch('src.processes.process.tprint'):
            self.assertTrue(sp.sell_item('1'))

    def test_sell_item_failure(self):
        trader = make_trader()
        trader.buy.return_value = False
        trader.goods_to_buy = [MagicMock()]
        game = make_game()
        with patch('src.processes.process.tprint'):
            sp = SellProcess(game, make_hero(), trader)
        with patch('src.processes.process.tprint'):
            self.assertFalse(sp.sell_item('999'))

    def test_generate_item_message(self):
        sp, *_ = self._make_sell(goods_items=[MagicMock()])
        msg = sp.generate_item_message()
        self.assertIsInstance(msg, list)
        self.assertTrue(len(msg) > 0)

    def test_generate_no_items_message(self):
        sp, *_ = self._make_sell(goods_items=[])
        msg = sp.generate_no_items_message()
        self.assertIsInstance(msg, list)
        self.assertTrue(any('руками' in m for m in msg))

    def test_generate_too_dark_message(self):
        sp, *_ = self._make_sell()
        msg = sp.generate_too_dark_message()
        self.assertIsInstance(msg, list)
        self.assertTrue(any('темноте' in m for m in msg))

    def test_generate_fear_message(self):
        sp, *_ = self._make_sell()
        msg = sp.generate_fear_message()
        self.assertIsInstance(msg, list)
        self.assertTrue(any('продаж' in m for m in msg))

    def test_termination_statuses(self):
        self.assertIn(SellProcess.status_enum.NO_AVAILABLE_ITEMS, SellProcess._termination_statuses)
        self.assertIn(SellProcess.status_enum.TOO_DARK, SellProcess._termination_statuses)
        self.assertIn(SellProcess.status_enum.FEAR, SellProcess._termination_statuses)

    def test_message_generators_all_statuses(self):
        for status in SellProcess.status_enum:
            self.assertIn(status, SellProcess._message_generators)


def _make_ep_manual(game=None, light=True, fear=False):
    game = game or make_game()
    owner = make_hero(light=light, fear=fear)
    ep = EnchantmentProcess.__new__(EnchantmentProcess)
    ep.game = game
    ep.owner = owner
    ep.init_text = None
    ep.status = EnchantmentProcess.status_enum.WAITING_FOR_ITEM
    ep.items_list = []
    ep.runes_list = []
    ep.item = None
    ep.rune = None
    ep._termination_statuses = EnchantmentProcess._termination_statuses
    ep._message_generators = EnchantmentProcess._message_generators
    return ep, game, owner


def _make_hero_enchant(light=True, fear=False, weapon_can=False, shield_can=False,
                       removed_shield_can=False, armor_can=False,
                       has_backpack=False, runes=None, bp_enchant_items=None):
    hero = make_hero(light=light, fear=fear)
    hero.weapon.can_be_enchanted.return_value = weapon_can
    hero.shield.can_be_enchanted.return_value = shield_can
    hero.removed_shield.can_be_enchanted.return_value = removed_shield_can
    hero.armor.can_be_enchanted.return_value = armor_can
    hero.check_backpack.return_value = has_backpack
    hero.backpack.get_items_by_class.return_value = runes or []
    hero.backpack.get_items_to_enchant.return_value = bp_enchant_items or []
    return hero


class TestEnchantmentProcess(unittest.TestCase):

    def _init_ep(self, light=True, fear=False, weapon_can=False, shield_can=False,
                 removed_shield_can=False, armor_can=False,
                 has_backpack=False, runes=None, bp_enchant_items=None):
        game = make_game()
        hero = _make_hero_enchant(light=light, fear=fear, weapon_can=weapon_can,
                                  shield_can=shield_can, removed_shield_can=removed_shield_can,
                                  armor_can=armor_can, has_backpack=has_backpack,
                                  runes=runes, bp_enchant_items=bp_enchant_items)
        with patch('src.processes.process.tprint'):
            ep = EnchantmentProcess(game, hero, init_text='')
        return ep, game, hero

    def test_init_no_items_no_runes(self):
        ep, *_ = self._init_ep()
        self.assertEqual(ep.status, EnchantmentProcess.status_enum.NO_AVAILABLE_RUNES)

    def test_init_too_dark(self):
        ep, *_ = self._init_ep(light=False)
        self.assertEqual(ep.status, EnchantmentProcess.status_enum.TOO_DARK)

    def test_init_fear(self):
        ep, *_ = self._init_ep(fear=True)
        self.assertEqual(ep.status, EnchantmentProcess.status_enum.FEAR)

    def test_init_with_weapon(self):
        ep, game, hero = self._init_ep(weapon_can=True)
        self.assertEqual(len(ep.items_list), 1)
        self.assertIs(ep.items_list[0], hero.weapon)

    def test_init_with_shield(self):
        ep, game, hero = self._init_ep(shield_can=True)
        self.assertEqual(len(ep.items_list), 1)
        self.assertIs(ep.items_list[0], hero.shield)

    def test_init_with_removed_shield(self):
        ep, game, hero = self._init_ep(removed_shield_can=True)
        self.assertEqual(len(ep.items_list), 1)
        self.assertIs(ep.items_list[0], hero.removed_shield)

    def test_init_with_armor(self):
        ep, game, hero = self._init_ep(armor_can=True)
        self.assertEqual(len(ep.items_list), 1)
        self.assertIs(ep.items_list[0], hero.armor)

    def test_init_with_runes(self):
        rune = MagicMock()
        ep, game, hero = self._init_ep(has_backpack=True, runes=[rune])
        self.assertEqual(len(ep.runes_list), 1)

    def test_init_no_runes_status(self):
        ep, *_ = self._init_ep(has_backpack=False)
        self.assertEqual(ep.status, EnchantmentProcess.status_enum.NO_AVAILABLE_RUNES)

    def test_init_terminated_on_too_dark(self):
        game = make_game()
        game.processes_controller.queue = []
        hero = _make_hero_enchant(light=False)
        with patch('src.processes.process.tprint'):
            EnchantmentProcess(game, hero, init_text='')
        self.assertEqual(len(game.processes_controller.queue), 0)

    def test_init_terminated_on_fear(self):
        game = make_game()
        game.processes_controller.queue = []
        hero = _make_hero_enchant(fear=True)
        with patch('src.processes.process.tprint'):
            EnchantmentProcess(game, hero, init_text='')
        self.assertEqual(len(game.processes_controller.queue), 0)

    def test_init_terminated_on_no_items(self):
        game = make_game()
        game.processes_controller.queue = []
        hero = _make_hero_enchant()
        with patch('src.processes.process.tprint'):
            EnchantmentProcess(game, hero, init_text='')
        self.assertEqual(len(game.processes_controller.queue), 0)

    def test_init_terminated_on_no_runes(self):
        game = make_game()
        game.processes_controller.queue = []
        hero = _make_hero_enchant(weapon_can=True, has_backpack=False)
        with patch('src.processes.process.tprint'):
            EnchantmentProcess(game, hero, init_text='')
        self.assertEqual(len(game.processes_controller.queue), 0)

    def test_get_items_list_weapon(self):
        ep, *_ = _make_ep_manual()
        ep.owner.weapon.can_be_enchanted.return_value = True
        items = ep.get_items_list()
        self.assertEqual(len(items), 1)
        self.assertIs(items[0], ep.owner.weapon)

    def test_get_items_list_shield(self):
        ep, *_ = _make_ep_manual()
        ep.owner.weapon.can_be_enchanted.return_value = False
        ep.owner.shield.can_be_enchanted.return_value = True
        items = ep.get_items_list()
        self.assertEqual(len(items), 1)
        self.assertIs(items[0], ep.owner.shield)

    def test_get_items_list_removed_shield(self):
        ep, *_ = _make_ep_manual()
        ep.owner.weapon.can_be_enchanted.return_value = False
        ep.owner.shield.can_be_enchanted.return_value = False
        ep.owner.removed_shield.can_be_enchanted.return_value = True
        items = ep.get_items_list()
        self.assertEqual(len(items), 1)
        self.assertIs(items[0], ep.owner.removed_shield)

    def test_get_items_list_armor(self):
        ep, *_ = _make_ep_manual()
        ep.owner.weapon.can_be_enchanted.return_value = False
        ep.owner.shield.can_be_enchanted.return_value = False
        ep.owner.removed_shield.can_be_enchanted.return_value = False
        ep.owner.armor.can_be_enchanted.return_value = True
        items = ep.get_items_list()
        self.assertEqual(len(items), 1)
        self.assertIs(items[0], ep.owner.armor)

    def test_get_items_list_backpack_items(self):
        ep, *_ = _make_ep_manual()
        bp_item = MagicMock()
        ep.owner.check_backpack.return_value = True
        ep.owner.backpack.get_items_to_enchant.return_value = [bp_item]
        items = ep.get_items_list()
        self.assertEqual(len(items), 1)
        self.assertIs(items[0], bp_item)

    def test_get_items_list_empty(self):
        ep, *_ = _make_ep_manual()
        items = ep.get_items_list()
        self.assertEqual(items, [])
        self.assertEqual(ep.status, EnchantmentProcess.status_enum.NO_AVAILABLE_ITEMS)

    def test_get_items_list_all_combined(self):
        ep, *_ = _make_ep_manual()
        ep.owner.weapon.can_be_enchanted.return_value = True
        ep.owner.armor.can_be_enchanted.return_value = True
        bp_item = MagicMock()
        ep.owner.check_backpack.return_value = True
        ep.owner.backpack.get_items_to_enchant.return_value = [bp_item]
        items = ep.get_items_list()
        self.assertEqual(len(items), 3)

    def test_get_runes_list_with_runes(self):
        ep, *_ = _make_ep_manual()
        rune = MagicMock()
        ep.owner.check_backpack.return_value = True
        ep.owner.backpack.get_items_by_class.return_value = [rune]
        runes = ep.get_runes_list()
        self.assertEqual(len(runes), 1)

    def test_get_runes_list_empty(self):
        ep, *_ = _make_ep_manual()
        runes = ep.get_runes_list()
        self.assertEqual(runes, [])
        self.assertEqual(ep.status, EnchantmentProcess.status_enum.NO_AVAILABLE_RUNES)

    def test_try_to_find_item_weapon(self):
        ep, *_ = _make_ep_manual()
        ep.owner.weapon.empty = False
        found = ep.try_to_find_item('оружие')
        self.assertIs(found, ep.owner.weapon)
        self.assertEqual(ep.status, EnchantmentProcess.status_enum.WAITING_FOR_RUNE)

    def test_try_to_find_item_shield(self):
        ep, *_ = _make_ep_manual()
        ep.owner.shield.empty = False
        found = ep.try_to_find_item('щит')
        self.assertIs(found, ep.owner.shield)

    def test_try_to_find_item_removed_shield(self):
        ep, *_ = _make_ep_manual()
        ep.owner.shield.empty = True
        ep.owner.removed_shield.empty = False
        found = ep.try_to_find_item('щит')
        self.assertIs(found, ep.owner.removed_shield)

    def test_try_to_find_item_armor(self):
        ep, *_ = _make_ep_manual()
        ep.owner.armor.empty = False
        found = ep.try_to_find_item('доспех')
        self.assertIs(found, ep.owner.armor)

    def test_try_to_find_item_armor_plural(self):
        ep, *_ = _make_ep_manual()
        ep.owner.armor.empty = False
        found = ep.try_to_find_item('доспехи')
        self.assertIs(found, ep.owner.armor)

    def test_try_to_find_item_by_number(self):
        ep, *_ = _make_ep_manual()
        item1, item2 = MagicMock(), MagicMock()
        ep.items_list = [item1, item2]
        found = ep.try_to_find_item('2')
        self.assertIs(found, item2)

    def test_try_to_find_item_by_name(self):
        ep, *_ = _make_ep_manual()
        item = MagicMock()
        item.check_name.return_value = True
        ep.items_list = [item]
        found = ep.try_to_find_item('огненный меч')
        self.assertIs(found, item)

    def test_try_to_find_item_not_found_empty_list(self):
        ep, *_ = _make_ep_manual()
        ep.items_list = []
        found = ep.try_to_find_item('несуществующее')
        self.assertIsNone(found)

    def test_try_to_find_item_number_out_of_range(self):
        ep, *_ = _make_ep_manual()
        item = MagicMock()
        item.check_name.return_value = False
        ep.items_list = [item]
        found = ep.try_to_find_item('999')
        self.assertIsNone(found)

    def test_try_to_find_item_weapon_empty(self):
        ep, *_ = _make_ep_manual()
        ep.owner.weapon.empty = True
        found = ep.try_to_find_item('оружие')
        self.assertIsNone(found)

    def test_try_to_find_item_shield_and_removed_empty(self):
        ep, *_ = _make_ep_manual()
        ep.owner.shield.empty = True
        ep.owner.removed_shield.empty = True
        found = ep.try_to_find_item('щит')
        self.assertIsNone(found)

    def test_try_to_find_rune_by_number(self):
        ep, *_ = _make_ep_manual()
        rune1, rune2 = MagicMock(), MagicMock()
        ep.runes_list = [rune1, rune2]
        found = ep.try_to_find_rune('1')
        self.assertIs(found, rune1)
        self.assertEqual(ep.status, EnchantmentProcess.status_enum.READY_TO_ENCHANT)

    def test_try_to_find_rune_by_name(self):
        ep, *_ = _make_ep_manual()
        rune = MagicMock()
        rune.check_name.return_value = True
        ep.runes_list = [rune]
        found = ep.try_to_find_rune('огонь')
        self.assertIs(found, rune)
        self.assertEqual(ep.status, EnchantmentProcess.status_enum.READY_TO_ENCHANT)

    def test_try_to_find_rune_not_found(self):
        ep, *_ = _make_ep_manual()
        ep.runes_list = []
        found = ep.try_to_find_rune('несуществующее')
        self.assertIsNone(found)

    def test_proceed_termination(self):
        ep, *_ = _make_ep_manual()
        with patch('src.processes.process.tprint') as mock_tprint:
            ep.proceed('отмена')
        mock_tprint.assert_called()

    def test_proceed_wait_item_and_text(self):
        ep, *_ = _make_ep_manual()
        item = MagicMock()
        item.check_name.return_value = True
        ep.items_list = [item]
        with patch('src.processes.process.tprint'):
            ep.proceed('предмет1')
        self.assertIsNotNone(ep.item)

    def test_proceed_wait_rune_and_text(self):
        ep, *_ = _make_ep_manual()
        rune = Rune('Руна')
        ep.runes_list = [rune]
        item = MagicMock()
        item.__format__ = lambda self, fmt: 'Меч'
        item.enchant.return_value = True
        ep.item = item
        ep.status = EnchantmentProcess.status_enum.WAITING_FOR_RUNE
        with patch('src.processes.process.tprint'):
            ep.proceed('руна')
        self.assertIsNotNone(ep.rune)

    def test_proceed_ready_to_enchant(self):
        ep, *_ = _make_ep_manual()
        ep.status = EnchantmentProcess.status_enum.READY_TO_ENCHANT
        item = MagicMock()
        item.__format__ = lambda self, fmt: 'Меч'
        item.enchant.return_value = True
        ep.item = item
        ep.rune = Rune('Руна')
        with patch('src.processes.process.tprint'):
            ep.proceed()
        self.assertEqual(ep.status, EnchantmentProcess.status_enum.ENCHANTMENT_SUCCESS)

    def test_proceed_wait_item_no_text(self):
        ep, *_ = _make_ep_manual()
        with patch('src.processes.process.tprint') as mock_tprint:
            ep.proceed()
        mock_tprint.assert_called()

    def test_proceed_wait_rune_no_text(self):
        ep, *_ = _make_ep_manual()
        ep.item = Weapon('Меч')
        ep.status = EnchantmentProcess.status_enum.WAITING_FOR_RUNE
        with patch('src.processes.process.tprint') as mock_tprint:
            ep.proceed()
        mock_tprint.assert_called()

    def test_enchant_item_success(self):
        ep, *_ = _make_ep_manual()
        ep.item = MagicMock()
        ep.rune = MagicMock()
        ep.item.enchant.return_value = True
        self.assertTrue(ep.enchant_item())
        self.assertEqual(ep.status, EnchantmentProcess.status_enum.ENCHANTMENT_SUCCESS)

    def test_enchant_item_failure(self):
        ep, *_ = _make_ep_manual()
        ep.item = MagicMock()
        ep.rune = MagicMock()
        ep.item.enchant.return_value = False
        self.assertFalse(ep.enchant_item())
        self.assertEqual(ep.status, EnchantmentProcess.status_enum.ENCHANTMENT_ERROR)

    def test_generate_item_message_weapon_with_mastery(self):
        ep, *_ = _make_ep_manual()
        item = Weapon('Меч', 'рубящее')
        ep.items_list = [item]
        ep.owner.mastery = {'рубящее': {'level': 2}}
        msg = ep.generate_item_message()
        self.assertTrue(any('мастерство' in m for m in msg))

    def test_generate_item_message_weapon_zero_mastery(self):
        ep, *_ = _make_ep_manual()
        item = Weapon('Меч', 'рубящее')
        ep.items_list = [item]
        ep.owner.mastery = {'рубящее': {'level': 0}}
        msg = ep.generate_item_message()
        self.assertFalse(any('мастерство' in m for m in msg))

    def test_generate_item_message_weapon_no_mastery_entry(self):
        ep, *_ = _make_ep_manual()
        item = Weapon('Меч', 'рубящее')
        ep.items_list = [item]
        ep.owner.mastery = {'рубящее': {'level': 0}}
        msg = ep.generate_item_message()
        self.assertIsInstance(msg, list)

    def test_generate_item_message_non_weapon(self):
        ep, *_ = _make_ep_manual()
        item = Shield('Щит')
        ep.items_list = [item]
        msg = ep.generate_item_message()
        self.assertIsInstance(msg, list)

    def test_generate_item_message_item_without_mastery_attr(self):
        ep, *_ = _make_ep_manual()
        item = Weapon('Меч', 'рубящее')
        ep.items_list = [item]
        del ep.owner.mastery
        msg = ep.generate_item_message()
        self.assertIsInstance(msg, list)

    def test_generate_rune_message(self):
        ep, *_ = _make_ep_manual()
        ep.item = Weapon('Меч')
        ep.runes_list = [Rune('Руна')]
        msg = ep.generate_rune_message()
        self.assertIsInstance(msg, list)
        self.assertTrue(len(msg) > 1)

    def test_generate_error_message(self):
        ep, *_ = _make_ep_manual()
        msg = ep.generate_error_message()
        self.assertIsInstance(msg, list)
        self.assertTrue(any('сломалось' in m for m in msg))

    def test_generate_success_message(self):
        ep, *_ = _make_ep_manual()
        ep.item = Weapon('Меч')
        ep.rune = Rune('Руна')
        msg = ep.generate_success_message()
        self.assertIsInstance(msg, list)
        self.assertTrue(any('успешно' in m for m in msg))

    def test_generate_no_items_message(self):
        ep, *_ = _make_ep_manual()
        msg = ep.generate_no_items_message()
        self.assertIsInstance(msg, list)
        self.assertTrue(any('не нашел' in m for m in msg))

    def test_generate_no_runes_message(self):
        ep, *_ = _make_ep_manual()
        msg = ep.generate_no_runes_message()
        self.assertIsInstance(msg, list)
        self.assertTrue(any('рун' in m for m in msg))

    def test_generate_too_dark_message(self):
        ep, *_ = _make_ep_manual()
        msg = ep.generate_too_dark_message()
        self.assertIsInstance(msg, list)
        self.assertTrue(any('темноте' in m for m in msg))

    def test_generate_fear_message(self):
        ep, *_ = _make_ep_manual()
        msg = ep.generate_fear_message()
        self.assertIsInstance(msg, list)
        self.assertTrue(any('страха' in m for m in msg))

    def test_termination_statuses_complete(self):
        for status in [
            EnchantmentProcess.status_enum.NO_AVAILABLE_ITEMS,
            EnchantmentProcess.status_enum.NO_AVAILABLE_RUNES,
            EnchantmentProcess.status_enum.ENCHANTMENT_ERROR,
            EnchantmentProcess.status_enum.ENCHANTMENT_SUCCESS,
            EnchantmentProcess.status_enum.TOO_DARK,
            EnchantmentProcess.status_enum.FEAR,
        ]:
            self.assertIn(status, EnchantmentProcess._termination_statuses)

    def test_message_generators_all_statuses(self):
        non_generator_statuses = {EnchantmentProcess.status_enum.READY_TO_ENCHANT}
        for status in EnchantmentProcess.status_enum:
            if status not in non_generator_statuses:
                self.assertIn(status, EnchantmentProcess._message_generators)


class TestProcessesController(unittest.TestCase):

    def setUp(self):
        self.game = make_game()
        self.pc = ProcessesController(self.game)

    def test_init(self):
        self.assertIsInstance(self.pc.queue, list)
        self.assertEqual(len(self.pc.queue), 0)

    def test_register_process(self):
        p = MagicMock()
        self.pc.register_process(p)
        self.assertEqual(len(self.pc.queue), 1)
        self.assertIs(self.pc.queue[0], p)

    def test_get_current_process_empty(self):
        self.assertIsNone(self.pc.get_current_process())

    def test_get_current_process_with_items(self):
        p1, p2 = MagicMock(), MagicMock()
        self.pc.register_process(p1)
        self.pc.register_process(p2)
        self.assertIs(self.pc.get_current_process(), p2)

    def test_terminate_current_process_empty(self):
        self.assertFalse(self.pc.terminate_current_process())

    def test_terminate_current_process_with_items(self):
        p1, p2 = MagicMock(), MagicMock()
        self.pc.register_process(p1)
        self.pc.register_process(p2)
        self.assertTrue(self.pc.terminate_current_process())
        self.assertEqual(len(self.pc.queue), 1)
        self.assertIs(self.pc.queue[0], p1)

    def test_terminate_process_found(self):
        p = MagicMock()
        self.pc.register_process(p)
        self.assertTrue(self.pc.terminate_process(p))
        self.assertEqual(len(self.pc.queue), 0)

    def test_terminate_process_not_found(self):
        self.assertFalse(self.pc.terminate_process(MagicMock()))

    def test_terminate_process_removes_correct(self):
        p1, p2 = MagicMock(), MagicMock()
        self.pc.register_process(p1)
        self.pc.register_process(p2)
        self.assertTrue(self.pc.terminate_process(p1))
        self.assertEqual(len(self.pc.queue), 1)
        self.assertIs(self.pc.queue[0], p2)

    def test_create_process_trade(self):
        game = make_game()
        pc = ProcessesController(game)
        game.processes_controller = pc
        with patch('src.processes.process.tprint'):
            pc.create_process(owner=make_hero(), type='trade', trader=make_trader())
        self.assertEqual(len(pc.queue), 1)
        self.assertIsInstance(pc.queue[0], TradeProcess)

    def test_create_process_buy(self):
        game = make_game()
        pc = ProcessesController(game)
        game.processes_controller = pc
        trader = make_trader()
        trader.shop = [MagicMock()]
        with patch('src.processes.process.tprint'):
            pc.create_process(owner=make_hero(), type='buy', trader=trader)
        self.assertEqual(len(pc.queue), 1)
        self.assertIsInstance(pc.queue[0], BuyProcess)

    def test_create_process_sell(self):
        game = make_game()
        pc = ProcessesController(game)
        game.processes_controller = pc
        trader = make_trader()
        trader.goods_to_buy = [MagicMock()]
        with patch('src.processes.process.tprint'):
            pc.create_process(owner=make_hero(), type='sell', trader=trader)
        self.assertEqual(len(pc.queue), 1)
        self.assertIsInstance(pc.queue[0], SellProcess)

    def test_create_process_enchantment(self):
        game = make_game()
        pc = ProcessesController(game)
        game.processes_controller = pc
        owner = make_hero()
        owner.weapon.can_be_enchanted.return_value = True
        owner.shield.can_be_enchanted.return_value = False
        owner.removed_shield.can_be_enchanted.return_value = False
        owner.armor.can_be_enchanted.return_value = False
        owner.check_backpack.return_value = True
        owner.backpack.get_items_by_class.return_value = [Rune('Руна')]
        with patch('src.processes.process.tprint'):
            pc.create_process(owner=owner, type='enchantment', request_text='')
        self.assertEqual(len(pc.queue), 1)
        self.assertIsInstance(pc.queue[0], EnchantmentProcess)

    def test_create_process_exception_terminates(self):
        game = make_game()
        pc = ProcessesController(game)
        game.processes_controller = pc
        with patch('src.processes.process.tprint'):
            with patch.object(TradeProcess, '__init__', side_effect=RuntimeError('fail')):
                with self.assertRaises(RuntimeError):
                    pc.create_process(owner=make_hero(), type='trade', trader=MagicMock())
        self.assertEqual(len(pc.queue), 0)

    def test_create_process_invalid_type(self):
        with self.assertRaises(KeyError):
            self.pc.create_process(owner=make_hero(), type='invalid')


if __name__ == '__main__':
    unittest.main()
