# Атака монстра
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