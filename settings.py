# Игра

s_how_many = {'монстры': 10,
              'оружие': 10,
              'щит': 5,
              'доспех': 5,
              'зелье': 10,
              'мебель': 10,
              'книга': 5,
              'очаг': 2,
              'руна': 10}
"""Количество всяких штук, которые разбрасываются по замку."""

s_game_common_commands = ['?',
                        'осмотреть',
                        'идти',
                        'атаковать',
                        'напасть',
                        'взять',
                        'забрать',
                        'подобрать',
                        'обыскать',
                        'открыть',
                        'использовать',
                        'применить',
                        'читать',
                        'прочитать',
                        'чинить',
                        'починить',
                        'убрать',
                        'улучшить',
                        'отдохнуть',
                        'отдыхать',
                        'бросить',
                        'сменить',
                        'поменять',
                        'выбросить']
"""Список комманд, которые может выполнять персонаж игры."""

s_game_level_up_commands = ['здоровье',
                            '?',
                            'силу',
                            'ловкость',
                            'интеллект']
"""Список дополнительных комманд при прокачке уровня персонажа."""

s_game_fight_commands = ['ударить',
                        '?',
                        'защититься',
                        'бежать',
                        'сменить оружие',
                        'сменить',
                        'поменять',
                        'использовать']
"""Список комманд во время схватки."""

# Герой
# Параметры героя по умолчанию

s_hero_name = 'Клава'
"""Имя героя по умолчанию."""

s_hero_name1 = 'Клаву'
"""Имя героя в винительном падеже по умолчанию."""

s_hero_gender = 1
"""
Пол героя: 
- 0 - мужской, 
- 1 - женский (сделано так для удобства работы с этой информацией)

TODO - перевести эту переменную на ENUM
"""

s_hero_strength = 10
"""Начальная сила героя по умолчанию."""

s_hero_dexterity = 2
"""Начальная ловкость героя по умолчанию."""

s_hero_intelligence = 1
"""Начальный интеллект героя по умолчанию."""

s_hero_health = 25
"""Начальное здоровье героя по умолчанию."""

s_nightmare_probability = 3
"""
Вероятность того, что герой увидит кошмар во время отдыха. 
Рассчитывается как 1/n, где n - это значение параметра.

"""

s_nightmare_divider = 2
"""Коэффициент, на который делится страх если приснился кошмар."""

s_steal_probability = 2 
"""
Вероятность того, что героя обворуют во время отдыха. 
Рассчитывается как 1/n, где n - это значение параметра.

"""
 
s_fear_limit = 5
"""Значение уровня страха героя, при котором он начинает отказываться делать определенные вещи."""
 
s_critical_step = 5
"""На сколько увеличивается вероятность критического удара оружием при увеличении мастерства на 1."""

s_critical_multiplier = 2
"""Коэффициент увеличения урона при критическом ударе."""
 
s_dark_damage_divider_dice = 3
"""Кубик, который кидается, чтобы выяснить, во сколько раз уменьшится урон от атаки в темноте."""
 
s_hero_add_poison_level = 3
"""Значение, которое прибавляется к уровню отравления чтобы рассчитать кубик отравления."""
 
s_hero_default_poison_die = 10
"""Кубик отравления у монстра по умолчанию."""

s_hero_actions = ['бьет',
                  'калечит',
                  'терзает',
                  'протыкает']
"""Действия, которые герой может делать своим оружием в бою."""

s_hero_doors_dict = {'наверх': 0,
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
"""Словарь направлений, в которых может пойти герой."""

# Монстры
# Параметры монстра по умолчанию
s_monster_name = ''
"""Имя монстра по умолчанию."""

s_monster_lexemes = {}
"""Лексемы имени монстра по умолчанию."""

s_monster_name1 = ''
"""Имя монстра в винительном падеже по умолчанию."""

s_monster_strength = 10
"""Сила монстра по умолчанию."""

s_monster_health = 20
"""Здоровье монстра по умолчанию."""

s_monster_actions = 'бьет'
"""Действие монстра в бою по умолчанию."""

s_monster_state = 'стоит'
"""Состояние монстра в комнате по умолчанию."""

s_is_monster_agressive = False
"""Агрессивность монстра по умолчанию."""

s_is_monster_carry_weapon = True
"""Способен ли монстр носить оружие, по умолчанию."""

s_is_monster_carry_shield = True
"""Способен ли монстр носить щит, по умолчанию."""

s_is_monster_wear_armor = True
"""Носит ли монстр доспехи, по умолчанию."""

s_monster_money = 5
"""Сколько у монстра по умолчанию денег."""

s_monster_see_through_keyhole = 'видит какую-то неясную фигуру.'
"""Что отображается если монстра увидеть через замочную скважину."""

s_monster_hit_chance = 5
"""Шанс попадания монстра по умолчанию."""

s_monster_parry_chance = 2
"""Шанс парирования монстра по умолчанию."""

s_monster_add_poison_level = 3
"""Значение, которое прибавляется к уровню отравления чтобы рассчитать кубик отравления"""
 
s_monster_default_poison_die = 10
"""Кубик отравления у монстра по умолчанию"""

# Прочие параметры логики монстров

s_monster_exp_multiplier_limit = 10
"""
Верхняя граница значения множителя, на который 
умножается сила монстра при рассчете полученного за него опыта.

"""

s_monster_name_in_darkness = 'Кто-то страшный'
"""Имя, которое отображается для монстра в темноте."""

s_monster_name1_in_darkness = 'черт знает кого'
"""Имя, которое отображается для монстра в темноте, в винительном падеже."""

s_wounded_monster_strength_coefficient = 0.4
"""Коэффициент, на который умножается сила монстра если он ранен."""
 
s_wounded_monster_health_coefficient = 0.4
"""Коэффициент, на который умножается здоровье монстра если он ранен."""
 
s_monster_hide_possibility = 5
"""Вероятность, с которой монстр садится в засаду (если 5, то вероятность 1/5)."""
 
s_berserk_rage_coefficient = 3
"""Какая часть потерянного здоровья берсерка уходит в его ярость (если 3, то 1/3)."""
 
s_vampire_suck_coefficient = 2
"""Какую часть урона вампир высасывает себе (если 2, то 1/2)."""

s_poison_base_protection_die = 5
"""Кубик, который кидается чтобы определить базовую защиту от отравления."""

s_poison_additional_protection_die = 5
"""
Кубик, который кидается чтобы определить дополнительную защиту от яда
когда у героя или монстра ядовитые доспехи или щит.

"""

# Трупы

s_corpse_places = [
    'В центре комнаты',
    'У стены',
    'Под окном',
    'У двери',
    'В тени'
]
"""Массив возможных мест, где могут валяться трупы"""

s_corpse_states = [
    'лежит',
    'гниет',
    'воняет',
    'валяется'
]
"""Массив возможных состояний трупов"""

s_corpse_depiction = [
    'изуродованный',
    'полуразложившийся',
    'окровавленный',
    'обезображенный',
    'почти не тронутый',
    'холодный',
    'скрюченный'
]
"""Массив возможный прилагательных для трупа"""

# Деньги

s_money_groups = [10, 20, 30]
"""Значения для разделения денег на кучки."""

s_money_piles = [
    [
        'Несколько монет',
        'Несколько монет'
    ],
    [
        'Кучка монет',
        'Кучку монет'
    ],
    [
        'Груда монет',
        'Груду монет'
    ],
    [
        'Много монет',
        'Много монет'
    ],
]
"""Текстовые обозначения для кучек с разным количеством монет"""
# Замок

s_dark_rooms_ratio = 8
"""Какая часть комнат замка будет темными (если 5, то будет каждая пятая комната)."""
 
s_locked_rooms_ratio = 8
"""Какая часть комнат замка будет заперта (если 5, то будет каждая пятая комната)."""
 
s_min_money_in_locked_room = 15
"""Минимальное количество денег в запертой комнате."""
 
s_max_money_in_locked_room = 40
"""Максимальное количество денег в запертой комнате."""
 
s_map_width_coefficient = 72
"""Коэффициент для расчета ширины карты."""
 
s_map_height_coefficient = 90
"""Коэффициент для расчета высоты карты."""
 
s_castle_floors_sizes = [
    [5, 
     5, 
     {'монстры': 10,
      'оружие': 10,
      'щит': 5,
      'доспех': 5,
      'зелье': 10,
      'мебель': 10,
      'книга': 5,
      'очаг': 2,
      'руна': 10}]
]
"""Размеры этажей замка. Каждый подмассив - это этаж замка."""

# Комната
# 
s_room_stink_levels = {1: 'Немного', 2: 'Сильно', 3: 'Невыносимо'}
"""Уровни вони."""
# 
s_room_secrets_dictionary = ['унитаз',
                             'аквариум',
                             'бак',
                             'камин',
                             'хлам']
"""
Словарь секретных мест, которые могут встречаться в комнатах.
Если в тексте описания комнаты есть эти слова, 
то в ней может быть серкретный клад, который можно найти обыскав эти предметы.

"""
 
s_room_torch_is_on_dice = 5
"""
Кубик, который кидается чтобы определить, горит в комнате факел, или нет 
(берется выпадение одного конкретного значения).

"""
 
s_room_plan_picture_width = 100
"""Ширина картинки плана комнаты."""

s_room_plan_picture_height = 120
"""Высота картинки плана комнаты."""

# Мебель

s_furniture_locked_possibility = 4
"""Вероятность того, что мебель будет заперта (если 4, то 1/4)."""

s_furniture_initial_money_maximum = 50
"""Верхний лимит денег в мебели при генерации."""

# Зелья

s_potion_types = [['Зелье исцеления', 10, 0, True,
                    'Лечебное зелье восстанавливает некоторое количество единиц здоровья.'],
                   ['Зелье здоровья', 1, 1, False,
                    'Зелье здоровья увеличивает максимальный запас здоровья персонажа.'],
                   ['Зелье силы', 1, 2, False,
                    'Зелье силы увеличивает максимальное значение силы персонажа.'],
                   ['Зелье усиления', 5, 3, True,
                    'Зелье усиления временно добавляет персонажу силы.'],
                   ['Зелье ловкости', 1, 4, False,
                    'Зелье ловкости увеличивает максимальное значение ловкости персонажа.'],
                   ['Зелье увертливости', 5, 5, True,
                    'Зелье увертливости временно добавляет персонажу ловкости.'],
                   ['Зелье ума', 1, 6, False,
                    'Зелье ума увеличивает максимальное значение силы интеллекта.'],
                   ['Зелье просветления', 5, 7, True,
                    'Зелье просветления временно добавляет персонажу интеллекта.']]
"""Массив настроек типов зелий."""

#Защита
 
s_protection_weak_weapon_multiplier = 0.67
"""Множитель защиты когда бьют оружием со слабыми рунами."""
 
s_protection_strong_weapon_multiplier = 1.5
"""Множитель защиты когда бьют оружием с сильными рунами."""

s_weakness_dictionary = {1: [3, 3],
                         2: [3, 6],
                         3: [7, 7],
                         4: [3, 7],
                         6: [7, 14],
                         7: [12, 12],
                         8: [3, 12],
                         10: [7, 12],
                         12: [1, 1],
                         13: [1, 3],
                         14: [12, 24],
                         15: [1, 7],
                         19: [1, 12],
                         24: [1, 2]}
"""Словарь слабостей. Каждой стихии соответствует список слабых стихий."""

# Щит

s_shield_crushed_upper_limit = 10
"""Верхняя планка случайных значений при проверке того, что щит сломан."""
 
s_shield_damage_when_hiding_min = 50
"""Нижняя планка случайных значений при генерации ущерба щиту когда персонаж спрятался."""
 
s_shield_damage_when_hiding_max = 75
"""Верхняя планка случайных значений при генерации ущерба щиту когда персонаж спрятался."""
 
s_shield_damage_min = 10
"""Нижняя планка случайных значений при генерации ущерба щиту в обычных условиях."""
 
s_shield_damage_max = 25
"""Верхняя планка случайных значений при генерации ущерба щиту в обычных условиях."""
 
s_shield_repair_multiplier = 10 
"""Множитель, на который умножается накопленный урон щита чтобы определить стоимость его починки."""
 
s_shield_states_dictionary = {1: 'поцарапанный',
                              2: 'потрепанный',
                              3: 'почти сломанный',
                              4: 'еле живой'}
"""Словарь состояний щита."""

# Оружие

s_weapon_poison_level = 10
"""Кубик, который кидается при проверке отравления оружием."""
 
s_weapon_first_words_dictionary = [[['Большой', 'Большой'], ['Большая', 'Большую'], ['Большое', 'Большое']],
                                   [['Малый', 'Малый'], ['Малая', 'Малую'], ['Малое', 'Малое']],
                                   [['Старый', 'Старый'], ['Старая', 'Старую'], ['Старое', 'Старое']],
                                   [['Тяжелый', 'Тяжелый'], ['Тяжелая', 'Тяжелую'], ['Тяжелое', 'Тяжелое']],
                                   [['Новый', 'Новый'], ['Новая', 'Новую'], ['Новое', 'Новое']]]
"""Словарь первых слов в описании оружия."""
 
s_weapon_types_dictionary = [['меч', 0, 'меч', 'рубящее', False, 6],
                             ['сабля', 1, 'саблю', 'рубящее', False, 7],
                             ['катана', 1, 'катану', 'рубящее', False, 7],
                             ['рапира', 1, 'рапиру', 'колющее', False, 6],
                             ['пика', 1, 'пику', 'колющее', True, 4],
                             ['копье', 2, 'копье', 'колющее', True, 4],
                             ['топор', 0, 'топор', 'рубящее', False, 5],
                             ['кинжал', 0, 'кинжал', 'колющее', False, 5],
                             ['дубина', 1, 'дубину', 'ударное', False, 4],
                             ['палица', 1, 'палицу', 'ударное', False, 5],
                             ['булава', 1, 'булаву', 'ударное', False, 5],
                             ['молот', 0, 'молот', 'ударное', True, 5],
                             ['шпага', 1, 'шпагу', 'колющее', False, 6]]
"""Словарь типов оружия."""
 
s_weapon_twohanded_dictionary = ['двуручный', 'двуручная', 'двуручное']
"""Словарь двуручного оружия."""

s_enchantable_die = 4
"""
Какой кубик нужно кинуть чтобы определить, что оружие нельзя улучшать. 
Оружие нельзя улучшать если выпадает единица.
Так, если указано значение 4, то вероятность будет 1 к 3.

"""

# Руны

s_rune_poison_probability = 3
"""
Вероятность того, что руна будет отравленной. 
Цифра указывает на количество граней кубика, который надо кинуть. 
Если 1 - руна отравлена.

"""

s_elements_dictionary = {1: 'огня',
                     2: 'пламени',
                     3: 'воздуха',
                     4: 'света',
                     6: 'ветра',
                     7: 'земли',
                     8: 'лавы',
                     10: 'пыли',
                     12: 'воды',
                     13: 'пара',
                     14: 'камня',
                     15: 'дождя',
                     19: 'грязи',
                     24: 'потопа'}
"""Словарь стихий."""

s_glowing_elements = [1, 2, 4]
"""Массив стихий, которые заставляют оружие светиться в темноте"""

# Торговец

s_how_many_traders = 1
"""Сколько торговцев в игре"""

s_how_many_books_trader_can_have = 5
"""Кубик, который надо кинуть чтобы определить количество книг у торговца"""

s_how_many_runes_trader_can_have = 4
"""Кубик, который надо кинуть чтобы определить количество рун у торговца"""

s_how_many_potions_trader_can_have = 6
"""Кубик, который надо кинуть чтобы определить количество зелий у торговца"""

s_traider_maximum_money = 50
"""Максимальное количество денег у торговца"""

s_traider_minimum_money = 20
"""Минимальное количество денег у торговца"""