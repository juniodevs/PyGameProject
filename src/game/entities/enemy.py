import os
import pygame
from ..settings import HITBOX_WIDTH, HITBOX_HEIGHT

class Enemy:
    """Enemy with sprite-based animations and AI behavior.

    Animations are loaded from src/assets/images/enemy spritesheets.
    Uses same sprite size as player (304x160) with 80x120 canvas animation frames.

    Animations:
    - Idle: 10 frames
    - Run: 10 frames
    - Turn Around: 3 frames
    - Attack 1: 4 frames
    - Attack 2: 6 frames
    - Hit: 1 frame
    - Death: 10 frames
    """

    def __init__(self, x, y):

        self.width = 304
        self.height = 160
        self.rect = pygame.Rect(x, y, self.width, self.height)

        self.hitbox_width = HITBOX_WIDTH
        self.hitbox_height = HITBOX_HEIGHT

        self.hitbox_offset_x = (self.width - self.hitbox_width) // 2
        self.hitbox_offset_y = (self.height - self.hitbox_height) // 2

        self.speed = 3.0
        self.vel_x = 0
        self.vel_y = 0
        self.gravity = 0.6
        self.on_ground = False
        self.facing = 1  

        self.animations = {}  
        self.state = 'idle'
        self.anim_index = 0
        self.last_anim_time = pygame.time.get_ticks()

        self.frame_durations = {
            'idle': 100,
            'run': 90,
            'turn': 120,
            'attack1': 80,
            'attack2': 80,
            'hit': 150,
            'death': 100,
        }

        self.max_hp = 4  
        self.current_hp = 4
        self.hit_cooldown = 0
        self.hit_cooldown_duration = 300  
        self.death_time = 0  

        self.flash_timer = 0
        self.flash_duration = 180

        self.detection_range = 500  
        self.attack_distance = 200  
        self.retreat_distance = 150  
        self.attack_cooldown = 0
        self.attack_cooldown_duration = 2000  
        self.locked = False  

        self.pursuing = False
        self.last_player_x = x
        self._next_attack_is_two = False  

        self.knockback_vel_x = 0
        self.knockback_decay = 0.85

        self._load_sprites()

    def _load_sprites(self):
        """Load sprites from spritesheet files in src/assets/images/enemy.

        Asset files (individual spritesheets):
        - _Idle.png: 10 frames
        - _Run.png: 10 frames
        - _TurnAround.png: 3 frames
        - _Attack.png: 4 frames (Attack 1)
        - _Attack2.png: 6 frames (Attack 2)
        - _Hit.png: 1 frame
        - _Death.png: 10 frames
        """
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        assets_dir = os.path.join(base, 'assets', 'images', 'enemy')

        mapping = {
            'idle': ('_Idle.png', 10),
            'run': ('_Run.png', 10),
            'turn': ('_TurnAround.png', 3),
            'attack1': ('_Attack.png', 4),
            'attack2': ('_Attack2.png', 6),
            'hit': ('_Hit.png', 1),
            'death': ('_Death.png', 10),
        }

        for state, (filename, frame_count) in mapping.items():
            path = os.path.join(assets_dir, filename)
            frames_list = []

            if os.path.exists(path):
                try:

                    if pygame.display.get_init():
                        sheet = pygame.image.load(path).convert_alpha()
                    else:
                        sheet = pygame.image.load(path)
                    sheet_w, sheet_h = sheet.get_size()

                    frame_w = sheet_w // frame_count

                    for i in range(frame_count):
                        rect = pygame.Rect(i * frame_w, 0, frame_w, sheet_h)
                        frame = pygame.Surface(rect.size, pygame.SRCALPHA)
                        frame.blit(sheet, (0, 0), rect)

                        frame = pygame.transform.smoothscale(frame, (self.width, self.height))
                        frames_list.append(frame)

                except Exception as e:
                    print(f"Error loading {path}: {e}")

                    surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    surf.fill((255, 0, 0, 128))
                    frames_list.append(surf)
            else:
                print(f"File not found: {path}")

                surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                surf.fill((255, 0, 0, 128))
                frames_list.append(surf)

            if frames_list:
                self.animations[state] = frames_list
            else:

                surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                surf.fill((255, 0, 0, 128))
                self.animations[state] = [surf]

    def update(self, player, world_width, world_height, ground_y):
        self.vel_y += self.gravity

        self.knockback_vel_x *= self.knockback_decay
        if abs(self.knockback_vel_x) < 0.1:
            self.knockback_vel_x = 0

        self.rect.x += int(self.vel_x + self.knockback_vel_x)
        self.rect.y += int(self.vel_y)

        my_hitbox = self.get_hitbox()
        player_hitbox = player.get_hitbox()
        if my_hitbox.colliderect(player_hitbox):
            self.vel_x = 0

        if self.rect.bottom >= ground_y:
            self.rect.bottom = ground_y
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        hb = self.get_hitbox()
        if hb.left < 0:
            overlap = 0 - hb.left
            self.rect.x += overlap
        if hb.right > world_width:
            overlap = hb.right - world_width
            self.rect.x -= overlap

        now = pygame.time.get_ticks()
        if self.hit_cooldown > 0 and now - self.hit_cooldown >= self.hit_cooldown_duration:
            self.hit_cooldown = 0

        if self.attack_cooldown > 0 and now - self.attack_cooldown >= self.attack_cooldown_duration:
            self.attack_cooldown = 0

        if self.state == 'death':
            self._update_animation(loop=False)
            return

        if self.state == 'hit':
            finished = self._update_animation(loop=False)
            if finished:
                self.locked = False
                self.vel_x = 0
                self._set_state('idle')
            return

        self._update_ai(player, now)

        if self.state.startswith('attack'):
            finished = self._update_animation(loop=False)
            if finished:
                self.locked = False
                self.vel_x = 0
                self._set_state('idle')
            return

        if self.on_ground:
            if abs(self.vel_x) > 0.5:
                self._set_state('run')
            else:
                self._set_state('idle')
        else:

            self._set_state('run')

        self._update_animation(loop=True)

    def _update_ai(self, player, now):
        """Update AI to pursue and attack player while maintaining safe distance."""

        dist = abs(player.rect.centerx - self.rect.centerx)

        if player.rect.centerx > self.rect.centerx:
            self.facing = 1
        else:
            self.facing = -1

        self.last_player_x = player.rect.centerx

        if self.state in ('hit', 'death'):
            self.vel_x = 0
            return

        if self.state.startswith('attack'):
            self.vel_x = 0
            return

        if dist < self.retreat_distance:
            if self.get_hitbox().colliderect(player.get_hitbox()):

                if player.rect.centerx > self.rect.centerx:
                    self.vel_x = -self.speed  
                else:
                    self.vel_x = self.speed   
                self.pursuing = True
                return

            if dist < self.attack_distance and self.attack_cooldown == 0:
                self.attack()
                self.vel_x = 0
                self.pursuing = True
                return

            self.vel_x = 0
            self.pursuing = True
            return

        if dist < self.attack_distance and self.attack_cooldown == 0:
            self.attack()
            self.vel_x = 0
            self.pursuing = True
            return

        if dist < self.attack_distance:

            self.vel_x = 0
            self.pursuing = True
            return

        if dist < self.detection_range:
            if player.rect.centerx > self.rect.centerx:
                self.vel_x = self.speed
            else:
                self.vel_x = -self.speed
            self.pursuing = True
            return

        self.vel_x = 0
        self.pursuing = False

    def attack(self):
        """Trigger an attack. Alternates between attack1 and attack2."""
        if self.state.startswith('attack') or self.state == 'death':
            return

        self._next_attack_is_two = not self._next_attack_is_two
        new_state = 'attack2' if self._next_attack_is_two else 'attack1'

        self._set_state(new_state)
        self.attack_cooldown = pygame.time.get_ticks()
        self.locked = True
        self.vel_x = 0

    def take_damage(self, amount=1, knockback_direction=1):
        """Enemy receives damage and gets knocked back.

        Args:
            amount: Amount of damage to take (default 1)
            knockback_direction: Direction of knockback (1 for right, -1 for left)

        Returns:
            True if enemy dies (HP <= 0), False otherwise
        """

        now = pygame.time.get_ticks()
        if self.hit_cooldown > 0 and now - self.hit_cooldown < self.hit_cooldown_duration:
            return False

        self.current_hp -= amount
        self.hit_cooldown = now

        self.flash_timer = now

        knockback_strength = 15
        self.knockback_vel_x = knockback_strength * knockback_direction

        if self.current_hp > 0:
            self._set_state('hit')
            self.locked = True
        else:
            self._set_state('death')
            self.death_time = now  
            self.current_hp = 0
            return True

        return False

    def _set_state(self, new_state):
        """Change animation state."""
        if new_state == self.state:
            return
        self.state = new_state
        self.anim_index = 0
        self.last_anim_time = pygame.time.get_ticks()

    def _update_animation(self, loop=True):
        """Advance animation frames based on time.

        Args:
            loop: If True, animation loops. If False, stays on last frame and returns True when done.

        Returns:
            True if a non-looping animation finished on this update.
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

    def draw(self, surface, camera_x=0, camera_y=0):
        """Draw enemy sprite with camera offset.

        Args:
            surface: pygame surface to draw on
            camera_x: Camera X position in world
            camera_y: Camera Y position in world
        """
        frames = self.animations.get(self.state, None)
        if not frames:

            pygame.draw.rect(surface, (200, 0, 0), self.rect)
            return

        frame = frames[self.anim_index % len(frames)]

        if self.facing < 0:
            frame = pygame.transform.flip(frame, True, False)

        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        surface.blit(frame, (screen_x, screen_y))

        now = pygame.time.get_ticks()
        if getattr(self, 'flash_timer', 0) and now - self.flash_timer < self.flash_duration:
            try:
                white_frame = frame.copy()

                white_frame.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
                surface.blit(white_frame, (screen_x, screen_y))
            except Exception:
                overlay = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 180))
                surface.blit(overlay, (screen_x, screen_y))

    def draw_at(self, surface, pos):
        """Draw enemy sprite at a specific screen position.

        Args:
            surface: pygame surface to draw on
            pos: tuple (x, y) position on screen in pixels
        """
        frames = self.animations.get(self.state, None)
        if not frames:

            pygame.draw.rect(surface, (200, 0, 0), (*pos, self.width, self.height))
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

        Returns a rect centered on the enemy body for realistic collision.
        """

        hitbox_x = int(self.rect.x + self.hitbox_offset_x)
        hitbox_y = int(self.rect.y + self.hitbox_offset_y)

        return pygame.Rect(hitbox_x, hitbox_y, int(self.hitbox_width), int(self.hitbox_height))


    def is_alive(self):
        """Check if enemy is alive."""
        return self.current_hp > 0