class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 100
        self.speed = 2

    def move(self):
        # Logic for enemy movement
        pass

    def attack(self):
        # Logic for enemy attack
        pass

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        # Logic for enemy death
        pass