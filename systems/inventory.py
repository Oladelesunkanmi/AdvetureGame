"""
Inventory System Module
======================
Manages player item inventory, addition, removal, and consumable usage.
"""

from particles import spawn_particles

class Inventory:
    def __init__(self):
        self.items = {}
        self.max_slots = 8

    def add(self, item_name, count=1):
        if item_name in self.items:
            self.items[item_name] += count
        else:
            if len(self.items) < self.max_slots:
                self.items[item_name] = count

    def has(self, item_name, count=1):
        return self.items.get(item_name, 0) >= count

    def remove(self, item_name, count=1):
        if item_name in self.items:
            self.items[item_name] -= count
            if self.items[item_name] <= 0:
                del self.items[item_name]

    def use(self, item_name, player):
        if item_name == "Health Potion" and self.has(item_name):
            player.health = min(player.max_health, player.health + 15)
            self.remove(item_name)
            spawn_particles(player.centerx, player.centery, (0, 255, 100), 12, 4)
            return True
        return False
