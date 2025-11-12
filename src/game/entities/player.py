import os
import pygame
from ..settings import HITBOX_WIDTH, HITBOX_HEIGHT

class Player:
    """Player with sprite-based animations.

    Animations are loaded from src/assets/images/player and scaled to 38x20.
    State machine handles smooth transitions between idle/run/turn/attack/jump/fall/hit/death.
    """

    def __init__(self, x, y):
        self.width = 304
        self.height = 160
        self.rect = pygame.Rect(x, y, self.width, self.height)

        self.hitbox_width = HITBOX_WIDTH
        self.hitbox_height = HITBOX_HEIGHT
        self.hitbox_offset_x = (self.width - self.hitbox_width) // 2

        self.hitbox_offset_y = (self.height - self.hitbox_height) // 2

        self.speed = 5
        self.vel_x = 0
        self.vel_y = 0
        self.jump_power = -12
        self.gravity = 0.6
        self.on_ground = False
        self.facing = 1  

        self.knockback_vel_x = 0
        self.knockback_decay = 0.85

        self.animations = {}  
        self.state = 'idle'
        self.anim_index = 0
        self.last_anim_time = pygame.time.get_ticks()

        self.frame_durations = {
            'idle': 100,
            'run': 80,
            'turn': 80,
            'attack1': 80,
            'attack2': 70,
            'jump': 120,
            'jump_trans': 80,
            'fall': 120,
            'fall_trans': 80,
            'hit': 250,
            'death': 100,
        }

        self._next_attack_is_two = False

        self.locked = False

        self.max_hp = 5
        self.current_hp = 5
        self.hit_cooldown = 0  
        self.hit_cooldown_duration = 1000  

        self.flash_timer = 0
        self.flash_duration = 180  

        self._load_sprites()

    def _load_sprites(self):
        """Load and slice spritesheets from assets/images/player.

        Assumes files are named like `_Idle.png`, `_Run.png`, etc. Frame counts follow the spec.
        """
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        assets_dir = os.path.join(base, 'assets', 'images', 'player')

        mapping = {
            'idle': ('Idle', 10),
            'run': ('Run', 10),
            'turn': ('TurnAround', 3),
            'attack1': ('Attack', 4),
            'attack2': ('Attack2', 6),
            'jump': ('Jump', 3),
            'jump_trans': ('JumpFallInbetween', 2),
            'fall': ('Fall', 3),
            'hit': ('Hit', 1),
            'death': ('Death', 10),
        }

        for state, (name, frames) in mapping.items():
            fname = f'_{name}.png'
            path = os.path.join(assets_dir, fname)
            if not os.path.exists(path):

                surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                surf.fill((255, 0, 255))
                self.animations[state] = [surf]
                continue

            try:
                if pygame.display.get_init():
                    sheet = pygame.image.load(path).convert_alpha()
                else:
                    sheet = pygame.image.load(path)
            except Exception:

                sheet = None

            if sheet is None:
                surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                surf.fill((255, 0, 255))
                self.animations[state] = [surf]
                continue
            sheet_w, sheet_h = sheet.get_size()

            frame_w = max(1, sheet_w // frames)
            frames_list = []
            for i in range(frames):
                rect = pygame.Rect(i * frame_w, 0, frame_w, sheet_h)
                frame = pygame.Surface(rect.size, pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), rect)

                frame = pygame.transform.smoothscale(frame, (self.width, self.height))
                frames_list.append(frame)

            self.animations[state] = frames_list

    def handle_input(self, keys):

        if self.locked or self.state == 'death':
            self.vel_x = 0
            return

        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -self.speed
            self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = self.speed
            self.facing = 1
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

    def attack(self):
        """Trigger an attack. Alternates between attack1 and attack2 for variety."""
        if self.state.startswith('attack') or self.state == 'death':
            return
        self._next_attack_is_two = not self._next_attack_is_two
        self.state = 'attack2' if self._next_attack_is_two else 'attack1'
        self.anim_index = 0
        self.last_anim_time = pygame.time.get_ticks()

        self.locked = True

    def take_damage(self, amount=1):
        """Player receives damage. Activates hit animation and cooldown.

        Args:
            amount: Amount of damage to take (default 1)

        Returns:
            True if player dies (HP <= 0), False otherwise
        """

        now = pygame.time.get_ticks()
        if self.hit_cooldown > 0 and now - self.hit_cooldown < self.hit_cooldown_duration:
            return False

        self.current_hp -= amount
        self.hit_cooldown = now

        self.flash_timer = now

        if self.current_hp > 0:
            self._set_state('hit')
            self.locked = True
        else:

            self._set_state('death')
            self.current_hp = 0
            return True

        return False

    def _set_state(self, new_state):
        if new_state == self.state:
            return
        self.state = new_state
        self.anim_index = 0
        self.last_anim_time = pygame.time.get_ticks()

    def update(self, screen_width, screen_height, ground_y):

        self.vel_y += self.gravity

        self.knockback_vel_x *= self.knockback_decay
        if abs(self.knockback_vel_x) < 0.1:
            self.knockback_vel_x = 0

        self.rect.x += int(self.vel_x + self.knockback_vel_x)
        self.rect.y += int(self.vel_y)

        hb = self.get_hitbox()
        if hb.left < 0:

            overlap = 0 - hb.left
            self.rect.x += overlap
        if hb.right > screen_width:
            overlap = hb.right - screen_width
            self.rect.x -= overlap

        if self.rect.bottom >= ground_y:
            self.rect.bottom = ground_y
            self.vel_y = 0

            self.on_ground = True
        else:
            self.on_ground = False

        if self.state == 'death':

            self._update_animation(loop=False)
            return

        if self.state == 'hit':
            finished = self._update_animation(loop=False)
            if finished:

                self.locked = False
                if abs(self.vel_x) > 0:
                    self._set_state('run')
                else:
                    self._set_state('idle')
            return

        if self.state.startswith('attack'):
            finished = self._update_animation(loop=False)
            if finished:

                self.locked = False
                if abs(self.vel_x) > 0:
                    self._set_state('run')
                else:
                    self._set_state('idle')
            return

        if not self.on_ground:
            if self.vel_y < 0:

                if self.state == 'fall' and 'jump_trans' in self.animations:
                    self._set_state('jump_trans')
                else:
                    self._set_state('jump')
            else:

                if self.state == 'jump' and 'jump_trans' in self.animations:
                    self._set_state('jump_trans')
                else:
                    self._set_state('fall')
        else:

            if abs(self.vel_x) > 0:

                if (self.vel_x > 0 and self.facing < 0) or (self.vel_x < 0 and self.facing > 0):
                    self._set_state('turn')
                else:
                    self._set_state('run')
            else:
                self._set_state('idle')

        self._update_animation(loop=True)

    def _update_animation(self, loop=True):
        """Advance animation frames based on time.

        Returns True if a non-looping animation finished on this update.
        """
        now = pygame.time.get_ticks()
        key = self.state
        frames = self.animations.get(key, None)
        if not frames:
            return True

        dur = self.frame_durations.get(key, 100)
        if now - self.last_anim_time >= dur:
            self.anim_index += 1
            self.last_anim_time = now
            if self.anim_index >= len(frames):
                if loop:
                    self.anim_index = 0
                else:

                    self.anim_index = len(frames) - 1
                    return True
        return False

    def draw(self, surface):
        frames = self.animations.get(self.state, None)
        if not frames:

            pygame.draw.rect(surface, (0, 200, 0), self.rect)
            return

        frame = frames[self.anim_index % len(frames)]

        if self.facing < 0:
            frame = pygame.transform.flip(frame, True, False)

        surface.blit(frame, self.rect.topleft)

        now = pygame.time.get_ticks()
        if getattr(self, 'flash_timer', 0) and now - self.flash_timer < self.flash_duration:

            try:
                white_frame = frame.copy()

                white_frame.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
                surface.blit(white_frame, self.rect.topleft)
            except Exception:

                overlay = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 180))
                surface.blit(overlay, self.rect.topleft)

    def draw_at(self, surface, pos):
        """Draw player sprite at a specific screen position (used by camera system).

        Args:
            surface: pygame surface to draw on
            pos: tuple (x, y) position on screen in pixels
        """
        frames = self.animations.get(self.state, None)
        if not frames:

            pygame.draw.rect(surface, (0, 200, 0), (*pos, self.width, self.height))
            return

        frame = frames[self.anim_index % len(frames)]

        if self.facing < 0:
            frame = pygame.transform.flip(frame, True, False)

        surface.blit(frame, pos)

        now = pygame.time.get_ticks()
        if getattr(self, 'flash_timer', 0) and now - self.flash_timer < self.flash_duration:
            try:
                white_frame = frame.copy()

                white_frame.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
                surface.blit(white_frame, pos)
            except Exception:
                overlay = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 180))
                surface.blit(overlay, pos)

    def get_hitbox(self):
        """Get the actual hitbox for body collision detection.

        Returns a rect centered on the player body for realistic collision.
        Same dimensions as enemy hitbox for consistency.
        """

        hitbox_x = int(self.rect.x + self.hitbox_offset_x)
        hitbox_y = int(self.rect.y + self.hitbox_offset_y)

        return pygame.Rect(hitbox_x, hitbox_y, int(self.hitbox_width), int(self.hitbox_height))