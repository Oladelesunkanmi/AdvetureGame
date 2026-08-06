"""
Quest System Module
===================
Manages active and completed quests, progress tracking, and reward XP.
"""

class Quest:
    def __init__(self, title, description, objective_type, target_count, reward_xp=50):
        self.title = title
        self.description = description
        self.objective_type = objective_type
        self.target_count = target_count
        self.current_count = 0
        self.completed = False
        self.reward_xp = reward_xp
        self.claimed = False

    def progress(self, amount=1):
        if not self.completed:
            self.current_count = min(self.target_count, self.current_count + amount)
            if self.current_count >= self.target_count:
                self.completed = True

active_quests = []
completed_quests = []

def add_quest(quest):
    """Adds a new quest to the active quests list."""
    active_quests.append(quest)

def update_quests(objective_type, amount=1):
    """Updates progress for all active quests matching objective_type."""
    for quest in active_quests:
        if quest.objective_type == objective_type and not quest.completed:
            quest.progress(amount)
