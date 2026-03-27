"""
TODO:
- Rework everything in here so it becomes usable again; expand functionality to cover more aspects 
  of the game.
  - In the future, the plan is to pass the data from other areas into this one and have shuffling, 
    etc. occur here. 
  - If all goes well, the Randomiser itself can be expanded to affect other aspects of gameplay 
    (e.g. items) without having functionality split across every relevant manager class/file.

"""

import sys
import random
import locations
import globals

import controllers.monsterman as monsterman
import controllers.itemman as itemman

class EnemyRandomiser:
    pass
    # def __init__(self, enemy_manager: enemyman.EnemyManager, item_manager: itemman.ItemManager):
    #     self.enemy_manager = enemy_manager
    
    '''
    Salanewt's note: The functions below were originally in enemyman.py.
    '''

    # # I am passing the enemy name into each enemy object, but when writing enemy back,
    # # i don't do anything with the name that may have changed
    # def shuffle_enemies_deep(self):
    #     random.shuffle(self.main_enemy_list)

    # # shuffles sets of enemy names+ids+abilities+types+exp+money (not money yet!)
    # # for example, lime slime could replace rabite, but keeping the rabite stats
    # def shuffle_enemies_light(self):
    #     multi_list = [(e.name, e.id, e.type_, e.ability_prime, e.ability_sub) for e in self.main_enemy_list]
    #     shuffled_list = random.sample(multi_list, len(multi_list))
    #     for i, e in enumerate(self.main_enemy_list):
    #         e.name, e.id, e.type_, e.ability_prime, e.ability_sub = shuffled_list[i]

    # # all these 3 functions are basically identical...
    # def shuffle_stats_only(self):
    #     stat_list = [enemy.stats for enemy in self.main_enemy_list]
    #     # same as random.shuffle but not inplace
    #     shuffled_stat_list = random.sample(stat_list, len(stat_list))
    #     for i, enemy in enumerate(self.main_enemy_list):
    #         enemy.stats = shuffled_stat_list[i]

    # def shuffle_magic_resistances_only(self):
    #     magic_res_list = [enemy.magic_res for enemy in self.main_enemy_list]
    #     shuffled_magic_res_list = random.sample(magic_res_list, len(magic_res_list))
    #     for i, enemy in enumerate(self.main_enemy_list):
    #         enemy.magic_res = shuffled_magic_res_list[i]

    # def shuffle_weapon_resistances_only(self):
    #     weapon_res_list = [enemy.weapon_res for enemy in self.main_enemy_list]
    #     shuffled_weapon_res_list = random.sample(weapon_res_list, len(weapon_res_list))
    #     for i, enemy in enumerate(self.main_enemy_list):
    #         enemy.weapon_res = shuffled_weapon_res_list[i]


    '''
    Salanewt's note: The functions below were originally in main.pyw.
    '''
  
    # def shuffle_monsters(self):
    #     if self.shuffle_main.isChecked():
    #         main_enemy_list = self.monster_model.monsters[1:123]
    #         random.shuffle(main_enemy_list)
    #         self.monster_model.monsters[1:123] = main_enemy_list
    #     else:
    #         random.shuffle(globals.my_enemyman.full_enemy_list)
    #     self.monster_model.layoutChanged.emit()

    # def toggleCombo(self, state):
    #     if state > 0:
    #         self.weaknesses_prevent_combo.setEnabled(True)
    #     else:
    #         self.weaknesses_prevent_combo.setEnabled(False)

    # def randomize_weaknesses(self):
    #     chosen_weights = []
    #     chosen_weights.append(self.weight_spin_circle.value())
    #     chosen_weights.append(self.weight_spin_dblcircle.value())
    #     chosen_weights.append(self.weight_spin_tri.value())
    #     chosen_weights.append(self.weight_spin_x.value())
    #     # make sure that weights are not all 0
    #     if all([w == 0 for w in chosen_weights]):
    #         msg = QMessageBox()
    #         msg.setWindowTitle('Error')
    #         msg.setText('Not all weights can be 0.')
    #         msg.setStandardButtons(QMessageBox.Ok)
    #         msg.exec()
    #     else:
    #         for i, enemy in enumerate(globals.my_enemyman.full_enemy_list):

    #             weapon_weaknesses = random.choices(population=[0, 1, 2, 3], weights=chosen_weights, k=3)
    #             magic_weaknesses = random.choices(population=[0, 1, 2, 3], weights=chosen_weights, k=8)
    #             if self.weaknesses_prevent_combo.isEnabled():
    #                 weapon_weaknesses_all_none = all([w == 3 for w in weapon_weaknesses])
    #                 magic_weaknesses_all_none = all([w == 3 for w in magic_weaknesses])

    #                 combo_type = self.weaknesses_prevent_combo.currentIndex()

    #                 if combo_type == 0:
    #                     # ensure weapon and magic weaknesses both have 1 not none
    #                     if weapon_weaknesses_all_none:
    #                         weapon_weaknesses[random.choice(range(3))] = 2
    #                     if magic_weaknesses_all_none:
    #                         magic_weaknesses[random.choice(range(8))] = 2
    #                 elif combo_type == 1:
    #                     # ensure weapon OR magic weaknesses have 1 not none
    #                     if weapon_weaknesses_all_none and magic_weaknesses_all_none:
    #                         if random.choice([0, 1]) == 0:
    #                             weapon_weaknesses[random.choice(range(3))] = 2
    #                         else:
    #                             magic_weaknesses[random.choice(range(8))] = 2
    #                 elif combo_type == 2:
    #                     # ensure weapon weaknesses have 1 not none
    #                     if weapon_weaknesses_all_none:
    #                         weapon_weaknesses[random.choice(range(3))] = 2
    #                 elif combo_type == 3:
    #                     # ensure magic weaknesses have 1 not none
    #                     if magic_weaknesses_all_none:
    #                         magic_weaknesses[random.choice(range(3))] = 2

    #             globals.my_enemyman.full_enemy_list[i].slash = weapon_weaknesses[0]
    #             globals.my_enemyman.full_enemy_list[i].bash = weapon_weaknesses[1]
    #             globals.my_enemyman.full_enemy_list[i].jab = weapon_weaknesses[2]

    #             globals.my_enemyman.full_enemy_list[i].light = magic_weaknesses[0]
    #             globals.my_enemyman.full_enemy_list[i].dark = magic_weaknesses[1]
    #             globals.my_enemyman.full_enemy_list[i].moon = magic_weaknesses[2]
    #             globals.my_enemyman.full_enemy_list[i].fire = magic_weaknesses[3]
    #             globals.my_enemyman.full_enemy_list[i].water = magic_weaknesses[4]
    #             globals.my_enemyman.full_enemy_list[i].wood = magic_weaknesses[5]
    #             globals.my_enemyman.full_enemy_list[i].wind = magic_weaknesses[6]
    #             globals.my_enemyman.full_enemy_list[i].earth = magic_weaknesses[7]