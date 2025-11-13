SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)

# Default hitbox size used by entities (width x height)
# Default hitbox size used by entities (width x height).
# These values are intentionally smaller than the full sprite so collisions
# only register when entities are close. Tune these if you want looser/tighter
# collisions project-wide.
HITBOX_WIDTH = 40
HITBOX_HEIGHT = 80

# Melee attack configuration used by gameplay collision checks. Lowering the
# range makes hits only register when the attacker is close to the target.
ATTACK_RANGE = 100
# Portion of the entity hitbox height covered by an attack (0-1). A lower
# value reduces vertical reach of attacks so they only hit the torso area.
ATTACK_HEIGHT_FACTOR = 0.5