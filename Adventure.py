import os
import random
import time
import json

ITEMS_JSON = 'items.json'
ENEMIES_JSON = 'enemies.json'
LOCATIONS_JSON = 'locations.json'

class Player:
    def __init__(self, player_class):
        self.player_class = player_class
        self.inventory_file = f'{player_class}_inventory.json'
        self.equipped_file = f'{player_class}_equipped.json'
        self.inventory = []
        self.equipped_items = {
            'trap_detection_item': None,
            'trap_disarmament_item': None,
            'orb_mystic': None,
            'chest': None,
            'two-handed weapon': None,
            'armguards_upper': None,
            'tome_knowledge': None,
            'head': None,
            'tome_power': None,
            'scroll_lighting': None,
            'stam_potion': None,
            'tome_mystic': None,
            'elixir_power': None,
            'scroll_fire': None,
            'int_potion': None,
            'necklace': None,
            'legs': None,
            'scroll_telly': None, 
            'elixir_life': None,
            'strength_potion': None,
            'elixir_speed': None,
            'elixir_mystic': None,
            'orb_protection': None,
            'ring_right': None,
            'one-handed weapon': None,
            'shield': None, 
            'ring_left': None,
            'orb_summon': None,
            'elixir_wisdom': None,
            'gloves': None,
            'scroll_mystic': None,
            'boots': None, 
            'health_potion': None,
            'tome_secrets': None,
            'armguards_lower': None,
            'back': None, 
            'orb_telly': None,
            'orb_enlight': None,
            'agility_potion': None,
            'scroll_invis': None,
            'scroll_heal': None,
            'tome_spells': None,
            'mana_potion': None,
        }

        self.load_inventory_from_file()
        self.load_equipped_from_file()
        self.poisoned = False
        self.poison_duration = 0
        self.action_performed = False
        self.current_location = 'Town'
        self.visited_locations = ['start']
        self.game_over = False
        self.health = 100
        self.damage_modifier = 1  # Base damage modifier
        self.max_health = 100
        self.max_mana = 120 if self.player_class == "Mage" else 0
        self.mana = self.max_mana
        self.armor_rating = 0  
        self.damage_rating = 10 
        
        if self.player_class == "Warrior":
            self.max_health = 120
            self.health = 120
            self.damage_rating = 15
            self.armor_rating = 10
        elif self.player_class == "Mage":
            self.max_mana = 120
            self.mana = 120
            self.damage_rating = 12
            self.armor_rating = 5
            self.max_health = 80
            self.health = 80
        elif self.player_class == "Rogue":
            self.max_health = 100
            self.health = 100
            self.damage_rating = 13
            self.armor_rating = 3
        self.assign_starting_items()
        
        pass

    def start_game(self):
        self.current_location = 'start'
        self.visited_locations = ['start']
        self.describe_location()

    def load_inventory_from_file(self):
        try:
            with open(self.inventory_file, 'r') as f:
                self.inventory = json.load(f)
        except FileNotFoundError:
            pass

    def load_equipped_from_file(self):
        try:
            with open(self.equipped_file, 'r') as f:
                self.equipped_items = json.load(f)
        except FileNotFoundError:
            pass 

    def save_inventory_to_file(self):
        with open(self.inventory_file, 'w') as f:
            json.dump(self.inventory, f)

    def save_equipped_to_file(self):
        with open(self.equipped_file, 'w') as f:
            json.dump(self.equipped_items, f)

    def load_items(self):
        with open('items.json', 'r') as f:
            return json.load(f)
    
    def load_enemies(self):
        with open('enemies.json', 'r') as f:
            return json.load(f)

    def load_locations(self):
        with open(LOCATIONS_JSON, 'r') as file:
            locations = json.load(file)
        return locations
        
    def assign_starting_items(self):
        items = self.load_items() 
        starting_items = {
            'Warrior': ['Sword', 'Shield', 'Chestplate', 'Boots', 'Leggings', 'Health Potion'],
            'Mage': ['Staff', 'Robe','Magic Amulet', 'Leggings', 'Boots', 'Gloves' 'Health Potion', 'Mana Potion'],
            'Rogue': ['Dagger', 'Dagger', 'Cloak', 'Boots', 'Gloves', 'Bracers', 'Health Potion']
        }
        items_to_add = starting_items.get(self.player_class, [])
        for item_name in items_to_add:
            if item_name in items:
                self.add_to_inventory(item_name)
            else:
                print(f"Item {item_name} not found in items.json.")

    def add_to_inventory(self, item_name):
        items = self.load_items()
        if item_name in items:
            self.inventory.append(item_name)
            print(f"Added {item_name} to inventory.")
            self.save_inventory_to_file()
        else:
            print(f"Item {item_name} not found in items.json.")

    def equip_item(self, item_name):
        items = self.load_items()
        if item_name in items:
            item_type = items[item_name]['type']
            self.equipped_items[item_type] = item_name
            print(f"You equipped {item_name}.")
            self.save_equipped_to_file()
        else:
            print("Item not found in items.json.")


    def unequip_item(self, item_type):
        if item_type in self.equipped_items:
            if self.equipped_items[item_type]:
                self.inventory.append(self.equipped_items[item_type])
                print(f"You unequipped {self.equipped_items[item_type]}.")
                self.equipped_items[item_type] = None
                self.save_inventory_to_file()
                self.save_equipped_to_file()
            else:
                print(f"No {item_type} equipped.")
        else:
            print("Invalid equipment type.")

    def move(self, direction):
        destinations = self.load_locations_from_json()
        if direction == "random":
            random_moves = destinations[self.current_location]['random_moves']
            self.current_location = random.choice(random_moves)
        elif direction in destinations[self.current_location]:
            new_location = destinations[self.current_location][direction]
            self.current_location = new_location
            if new_location not in self.visited_locations:
                self.visited_locations.append(new_location)
            self.describe_location()
            self.encounter_enemy()
            self.detect_trap()
        else:
            print("You can't go that way.")

    def load_locations_from_json(self):
        with open(LOCATIONS_JSON, 'r') as file:
            locations = json.load(file)
        return locations

    def describe_location(self):
        with open(LOCATIONS_JSON, 'r') as file:
            locations_data = json.load(file)
        
        descriptions = locations_data[self.current_location]['description']
        print(descriptions)

    def show_inventory(self):
        if self.inventory:
            print("You are carrying:")
            for item in self.inventory:
                print(f"- {item}")
        else:
            print("Your inventory is empty.")
    
    def use_consumable(self, item):
        items = self.load_items()
        if item in items:
            item_type = items[item]['type']
            if item_type == 'consumable':
                print(f"You used {item}.")
                self.inventory.remove(item)
                self.save_inventory_to_file()
                if item_type == 'Health Potion':
                    self.health += random.randint(20, 30)
                    if self.health > self.max_health:
                        self.health = self.max_health
                    print(f"Your health is now {self.health}.")
                elif item_type == 'Mana Potion':
                    self.mana += random.randint(20, 30)
                    if self.mana > self.max_mana:
                        self.mana = self.max_mana
                    print(f"Your mana is now {self.mana}.")
            else:
                print(f"{item} is not a consumable.")
        else:
            print(f"You don't have {item} in your inventory.")
    
    def use_tome(self):
        print("You used a Tome. It reveals hidden knowledge.")

    def use_scroll(self):
        print("You used a Scroll. It casts a spell or reveals a message.")

    def use_orb(self):
        print("You used an Orb. It enhances your magical abilities.")

    def use_amulet(self):
        print("You used an Amulet. It provides mystical protection.")

    def describe_enemies(self):
        enemies = self.load_enemies()
        print("Enemies in this area:")
        for enemy, stats in enemies.items():
            print(f"{enemy}: {stats['description']}")

    def encounter_enemy(self):
        encounter_chance = random.random()
        if encounter_chance < 0.4: 
            enemies = self.load_enemies()
            num_enemies = random.randint(1, 4)  
            encountered_enemies = random.sample(list(enemies.items()), num_enemies)
            print(f"Encountered {num_enemies} enemies!")
            for enemy_name, stats in encountered_enemies:
                print(f"An enemy approaches: {enemy_name}")
                self.battle_enemy(enemy_name, stats)

    def save_game(self):
        save_name = input("Enter a name for your save: ").strip()
        save_file = f'{save_name}_save.json'
        save_data = {
                'player_class': self.player_class,
                'inventory': self.inventory,
                'equipped_items': self.equipped_items,
                'health': self.health,
                'max_health': self.max_health,
                'mana': self.mana,
                'max_mana': self.max_mana,
                'damage_rating': self.damage_rating,
                'armor_rating': self.armor_rating,
                'current_location': self.current_location,
                'visited_locations': self.visited_locations
        }
        with open(save_file, 'w') as f:
            json.dump(save_data, f)
        print(f"Game saved as '{save_name}_save.json'.")

    def load_game(self):
        saved_games = self.get_saved_games()
        if not saved_games:
            print("No saved games found.")
            return
        
        print("Saved games:")
        for idx, save in enumerate(saved_games, start=1):
            print(f"{idx}. {save}")

        choice = input("Enter the number of the save you want to load: ").strip()
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(saved_games):
            print("Invalid choice.")
            return
        
        save_name = saved_games[int(choice) - 1]
        save_file = f'{save_name}_save.json'

        try:
            with open(save_file, 'r') as f:
                save_data = json.load(f)
                self.current_location = save_data['current_location']
                self.health = save_data['health']
                self.mana = save_data['mana']
                self.inventory = save_data['inventory']
                self.equipped_items = save_data['equipped_items']
            print(f"Game '{save_name}_save.json' loaded.")
            self.describe_location()
            self.show_health_and_stats()
        except FileNotFoundError:
            print("Error loading saved game.")

    def get_saved_games(self):
        saved_games = [filename.split('_save.json')[0] for filename in os.listdir('.') if filename.endswith('_save.json')]
        return saved_games

    def show_health_and_stats(self):
        print(f"Health: {self.health}/{self.max_health}")
        print(f"Damage Modifier: {self.damage_modifier}")
        print(f"Armor: {self.armor}")
        if self.player_class == "Mage":
            print(f"Mana: {self.mana}/{self.max_mana}")

    def fight(self, enemy_name, enemy_stats):
        print(f"A {enemy_name} blocks your path.")
        while True:
            action = input("Do you want to [fight], [evade], or [negotiate]? ").lower()
            if action == "fight":
                if self.battle_enemy(enemy_name, enemy_stats):
                    print(f"You defeated the {enemy_name}. Continue your journey.")
                    self.reward_quest()
                    break
                else:
                    print(f"You were defeated by the {enemy_name}. Game over.")
                    self.game_over = True
                    break
            elif action == "evade":
                if random.random() < 0.5:  
                    print(f"You successfully evaded the {enemy_name}.")
                    break
                else:
                    print(f"You failed to evade the {enemy_name} and must face it.")
                    if self.battle_enemy(enemy_name, enemy_stats):
                        print(f"You defeated the {enemy_name}. Continue your journey.")
                        self.reward_quest()
                    else:
                        print(f"You were defeated by the {enemy_name}. Game over.")
                        self.game_over = True
                    break
            elif action == "negotiate":
                print(f"You attempt to negotiate with the {enemy_name}.")
                if random.random() < 0.5:  
                    print(f"You successfully negotiate with the {enemy_name} and continue your journey.")
                    self.reward_quest()
                    break
                else:
                    print(f"The {enemy_name} is not interested in negotiation and attacks!")
                    if self.battle_enemy(enemy_name, enemy_stats):
                        print(f"You defeated the {enemy_name}. Continue your journey.")
                    else:
                        print(f"You were defeated by the {enemy_name}. Game over.")
                        self.game_over = True
                    break
            else:
                print("Invalid action. Please choose [fight], [evade], or [negotiate].")

    def battle_enemy(self, enemy_name, enemy_stats):
        print(f"Battle begins! You are fighting {enemy_name}.")
        while self.health > 0 and enemy_stats['health'] > 0:
            print(f"Your Health: {self.health}, Enemy Health: {enemy_stats['health']}")
            action = input("What will you do? (attack, block, heal) ").lower()

            if action == "attack":
                self.attack(enemy_name, enemy_stats)
                if enemy_stats['health'] > 0:
                    self.defend(enemy_name, enemy_stats)
            elif action == "block":
                self.block(enemy_name, enemy_stats)
                self.defend(enemy_name, enemy_stats)
            elif action == "heal":
                self.heal()
                self.defend(enemy_name, enemy_stats)
            else:
                print("Invalid action. Choose 'attack', 'block', or 'heal'.")

            if self.health <= 0:
                print("Game Over. You have been defeated.")
                self.game_over = True
                return False
            elif enemy_stats['health'] <= 0:
                print(f"You defeated the {enemy_name}!")
                self.reward_quest()
                return True

        print(f"You and {enemy_name} are too tired to fight.")
        return True
    
    def attack(self, enemy_name, enemy_stats):
        print(f"You attack the {enemy_name}!")
        attack_damage = random.randint(5, 15) * self.damage_modifier + self.damage_rating
        enemy_damage = random.randint(5, 15) * (1 - self.armor_rating / 100) - self.armor_rating
        enemy_stats['health'] -= max(0, attack_damage)
        self.health -= max(0, enemy_damage)
        print(f"You dealt {max(0, attack_damage)} damage to {enemy_name}.")
        print(f"{enemy_name} dealt {max(0, enemy_damage)} damage to you.")

    def block(self, enemy_name, enemy_stats):
        print(f"You block the {enemy_name}'s attack!")
        block_amount = random.randint(0, 5)
        self.health -= block_amount
        print(f"You blocked {block_amount} damage.")

    def heal(self):
        if 'Health Potion' in self.inventory:
            potion_health = random.randint(10, 20)
            self.health = min(self.max_health, self.health + potion_health)
            print(f"You used a Health Potion and healed {potion_health} health points.")
            self.inventory.remove('Health Potion')
        else:
            print("You don't have any Health Potions to use.")

    def defend(self, enemy_name, enemy_stats):
        print(f"{enemy_name} attacks you!")
        enemy_damage = random.randint(5, 15) * enemy_stats['damage']
        self.health -= max(0, enemy_damage)
        print(f"You received {max(0, enemy_damage)} damage.")

    def reward_quest(self):
        reward_types = ['gold', 'item', 'experience']
        reward = random.choice(reward_types)
        if reward == 'gold':
            print("You found some gold!")
        elif reward == 'item':
            item_reward = random.choice(list(self.load_items().keys()))
            self.add_to_inventory(item_reward)
            print(f"You found a {item_reward}!")
        elif reward == 'experience':
            print("You gained experience!")
        self.damage_modifier += 0.2

    def use_healing_item(self):
        if self.equipped_items['healing_item']:
            self.health += random.randint(20, 30)
            print(f"You used {self.equipped_items['healing_item']} to heal.")
            if self.health > self.max_health:
                self.health = self.max_health
            print(f"Your health is now {self.health}.")
        else:
            print("No healing item equipped.")

    
    def detect_trap(self):
        trap_types = ['spike', 'pitfall', 'net', 'poison dart']
        if random.random() < 0.3:
            trap = random.choice(trap_types)  
        if self.player_class == 'Rogue':
            print(f"You detected a {trap} trap!")
        elif 'trap_detection_item' in self.inventory:
            if random.random() < 0.5:  
                print(f"You noticed the {trap} trap before it triggered. Your Trap Detection Kit Broke")
                self.inventory.remove('trap_detection_item')
            else:
                print(f"You encountered a {trap} trap and triggered it!")
                self.trigger_trap(trap)
                return
        else:
            print(f"You encountered a {trap} trap and triggered it!")
            self.trigger_trap(trap)
            return
    
        action = input("Do you want to [disarm] or [avoid] the trap? ").lower()
        
        if action == "disarm":
            if 'trap_disarmament_item' in self.inventory:
                disarm_tool_success = random.random() < 0.9 if self.player_class == 'rogue' else random.random() < 0.5
                if disarm_tool_success:
                    print(f"You successfully disarmed the {trap} trap with your {self.inventory['trap_disarmament_item']}.")
                    keep_tool_chance = 0.7 if self.player_class == 'rogue' else 0
                    if random.random() < keep_tool_chance:
                        print(f"You managed to keep your {self.inventory['trap_disarmament_item']} after disarming the trap.")
                    else:
                        print(f"Your {self.inventory['trap_disarmament_item']} broke during the disarmament process.")
                        self.inventory.remove('trap_disarmament_item')
                else:
                    print(f"You failed to disarm the {trap} trap with your {self.inventory['trap_disarmament_item']}.")
                    self.inventory.remove('trap_disarmament_item')
                    if self.player_class == 'rogue':
                        print(f"The trap activates and you take half damage!")
                        self.take_damage(trap, damage_multiplier=0.5)
                        if trap == 'net':
                            self.encounter_enemy()
                    else:
                        print(f"The trap activates!")
                        self.trigger_trap(trap)
            else:
                disarm_success = random.random() < 0.5 if self.player_class != 'rogue' else random.random() < 0.2
                if disarm_success:
                    print(f"You successfully disarmed the {trap} trap.")
                else:
                    print(f"You failed to disarm the {trap} trap and it activates!")
                    self.trigger_trap(trap)
        elif action == "avoid":
            avoid_chance = 0.6 if self.player_class == 'rogue' else 0.4
            if random.random() < avoid_chance:
                print(f"You successfully avoided the {trap} trap.")
            else:
                print(f"You failed to avoid the {trap} trap and it activates!")
                self.trigger_trap(trap)
        else:
            print(f"You triggered the {trap} trap!")
            self.trigger_trap(trap)   
        
    
    def trigger_trap(self, trap):
        if trap == 'spike':
            self.take_damage(trap, amount=20)
        elif trap == 'pitfall':
            self.take_damage(trap, amount=30)
        elif trap == 'net':
            print("You are temporarily caught in the net.")
            self.take_damage(trap, amount=0)  
            self.encounter_enemy()  
        elif trap == 'poison dart':
            self.poisoned = True
            self.poison_duration = random.randint(2, 5)  
            print("You are poisoned and will lose additional health over time.")
            if self.player_class == 'rogue':
                self.poison_duration += random.randint(1, 2)  
            self.apply_poison_effect()

        if self.health <= 0:
            print("You succumbed to your injuries. Game over.")
            self.game_over = True

    def apply_poison_effect(self):
        if self.poisoned:
            while self.poison_duration > 0:
                if self.action_performed:  
                    print(f"You are poisoned! {self.poison_duration} turns remaining.")
                    self.take_damage('poison', amount=10)
                    self.poison_duration -= 1
                else:
                    print("You are poisoned, but you rest this turn.")
                    break
                time.sleep(1)
            if self.poison_duration <= 0:
                print("You recovered from the poison.")
                self.poisoned = False
            self.action_performed = False  
    
    def take_damage(self, trap, amount, damage_multiplier=1.0):
        if self.player_class == 'rogue' and damage_multiplier < 1.0:
            print(f"You resisted some of the damage from the {trap} trap!")
            damage_multiplier *= 0.5  
        
        damage_taken = int(amount * damage_multiplier)
        self.health -= damage_taken
        print(f"You took {damage_taken} damage!")
        
        if self.poisoned:
            print(f"You are poisoned and lose {amount} health over time.")
            self.health -= amount
            self.poison_duration -= 1
            if self.poison_duration <= 0:
                print("You recovered from the poison.")
                self.poisoned = False
        
        if self.health <= 0:
            print("You succumbed to your injuries. Game over.")
            self.game_over = True

def main():
    print("Welcome to the Text Adventure Game!")
    player_class = input("Choose your class (Warrior, Mage, Rogue): ").capitalize()
    while player_class not in ['Warrior', 'Mage', 'Rogue']:
        print("Invalid class. Please choose again.")
        player_class = input("Choose your class (Warrior, Mage, Rogue): ").capitalize()

    player = Player(player_class)

    while not player.game_over:
        player.show_health_and_stats()
        print("What would you like to do?")
        action = input("Options: move, show inventory, use item, save game, quit game\n").lower()

        if action == 'move':
            direction = input("Choose a direction (north, south, east, west) or random: ").lower()
            player.move(direction)
        elif action in ["inventory", "i"]:
            player.show_inventory()
        elif action.startswith("pick up"):
            item = action[7:].strip()
            player.add_to_inventory(item)
        elif action.startswith("equip"):
            item = action[6:].strip()
            player.equip_item(item)
        elif action.startswith("unequip"):
            item_type = action[8:].strip()
            player.unequip_item(item_type)
        elif action.startswith("use") or action.startswith("consume"):
            item = action.split(maxsplit=1)[1].strip()
            player.use_consumable(item)
        elif action in ["stats", "status"]:
            player.show_health_and_stats()
        elif action == "save":
            player.save_inventory_to_file()
            player.save_equipped_to_file()
            print("Game saved.")
        elif action == "load":
            player.load_inventory_from_file()
            player.load_equipped_from_file()
            print("Game loaded.")
        elif action == "fight":
            print("You can only fight if you encounter an enemy.")
        elif action == "quit":
            print("Exiting game.")
            break
        elif action == "help":
            display_help()
        else:
            print("Invalid command. Type 'help' for available commands.")
        
        def display_help():
            print("""
                Available commands:
                - move (m): Move in a direction (north, south, east, west)
                - inventory (i): Show your inventory
                - pick up [item]: Pick up an item
                - equip [item]: Equip an item
                - unequip [item type]: Unequip an item of a specific type
                - use [item] or consume [item]: Use a consumable item
                - stats or status: Show health and other stats
                - save: Save the game
                - load: Load the game
                - fight: Fight an enemy (only available if you encounter an enemy)
                - quit: Exit the game
                - help: Show this help message
            """)   
            
    if __name__ == "__main__":
        main()