import os
import pygame
import random


class Player:
    """Player with sprite-based animations.

    Animations are loaded from src/assets/images/player and scaled to 38x20.
    State machine handles smooth transitions between idle/run/turn/attack/jump/fall/hit/death.
    """

    def __init__(self, x, y):
        self.width = 304
        self.height = 160
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Hitbox (same as enemy for consistency)
        self.hitbox_width = 74
        self.hitbox_height = 74

        # Movement
        self.speed = 5
        self.vel_x = 0
        self.vel_y = 0
        self.jump_power = -12
        self.gravity = 0.6
        self.on_ground = False
        self.facing = 1  # 1 = right, -1 = left

        # Knockback
        self.knockback_vel_x = 0
        self.knockback_decay = 0.85

        # Animation state
        self.animations = {}  # name -> list of Surfaces
        self.state = 'idle'
        self.anim_index = 0
        self.last_anim_time = pygame.time.get_ticks()
        # milliseconds per frame (can be tuned per animation)
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

        # Attack toggle to alternate between attack1 and attack2
        self._next_attack_is_two = False
        # Lock movement while certain animations play
        self.locked = False

        # HP system (5 hits max)
        self.max_hp = 5
        self.current_hp = 5
        self.hit_cooldown = 0  # Cooldown between hits in milliseconds
        self.hit_cooldown_duration = 1000  # 1 second invulnerability after hit

        # load sprites
        self._load_sprites()

    def _load_sprites(self):
        """Load and slice spritesheets from assets/images/player.

        Assumes files are named like `_Idle.png`, `_Run.png`, etc. Frame counts follow the spec.
        """
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        assets_dir = os.path.join(base, 'assets', 'images', 'player')

        # mapping animation name -> (filename without leading underscore, frame_count)
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
                # fallback: create a simple colored surface so game won't crash
                surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                surf.fill((255, 0, 255))
                self.animations[state] = [surf]
                continue

            sheet = pygame.image.load(path).convert_alpha()
            sheet_w, sheet_h = sheet.get_size()

            # If frames fits horizontally
            frame_w = max(1, sheet_w // frames)
            frames_list = []
            for i in range(frames):
                rect = pygame.Rect(i * frame_w, 0, frame_w, sheet_h)
                frame = pygame.Surface(rect.size, pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), rect)
                # scale to target size
                frame = pygame.transform.smoothscale(frame, (self.width, self.height))
                frames_list.append(frame)

            self.animations[state] = frames_list

    def handle_input(self, keys):
        # If locked (e.g., during attack animations) or dead, don't accept movement input
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
        # lock movement briefly while attacking
        self.locked = True

    def take_damage(self, amount=1):
        """Player receives damage. Activates hit animation and cooldown.
        
        Args:
            amount: Amount of damage to take (default 1)
            
        Returns:
            True if player dies (HP <= 0), False otherwise
        """
        # Check if still in cooldown (invulnerable)
        now = pygame.time.get_ticks()
        if self.hit_cooldown > 0 and now - self.hit_cooldown < self.hit_cooldown_duration:
            return False
        
        self.current_hp -= amount
        self.hit_cooldown = now
        
        # Play hit animation
        if self.current_hp > 0:
            self._set_state('hit')
            self.locked = True
        else:
            # Player dies
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
        # Apply gravity
        self.vel_y += self.gravity

        # Apply knockback decay
        self.knockback_vel_x *= self.knockback_decay
        if abs(self.knockback_vel_x) < 0.1:
            self.knockback_vel_x = 0

        # Move with knockback
        self.rect.x += int(self.vel_x + self.knockback_vel_x)
        self.rect.y += int(self.vel_y)

        # Ensure horizontal/world bounds based on hitbox (not sprite image)
        # If the hitbox is going out of bounds, shift the full sprite rect so the hitbox stays inside.
        hb = self.get_hitbox()
        if hb.left < 0:
            # shift right by the overlap amount
            overlap = 0 - hb.left
            self.rect.x += overlap
        if hb.right > screen_width:
            overlap = hb.right - screen_width
            self.rect.x -= overlap

        # Floor collision
        if self.rect.bottom >= ground_y:
            self.rect.bottom = ground_y
            self.vel_y = 0
            # If was falling or jumping, land
            self.on_ground = True
        else:
            self.on_ground = False

        # Decide animation state based on velocities and flags
        # Death/hit take precedence (not implemented death trigger here)
        if self.state == 'death':
            # play death until finished (no transitions)
            self._update_animation(loop=False)
            return

        # If in hit state, advance animation and unlock when finished
        if self.state == 'hit':
            finished = self._update_animation(loop=False)
            if finished:
                # return to run or idle depending on vel_x
                self.locked = False
                if abs(self.vel_x) > 0:
                    self._set_state('run')
                else:
                    self._set_state('idle')
            return

        # If attacking, advance attack animation and unlock when finished
        if self.state.startswith('attack'):
            finished = self._update_animation(loop=False)
            if finished:
                # return to run or idle depending on vel_x
                self.locked = False
                if abs(self.vel_x) > 0:
                    self._set_state('run')
                else:
                    self._set_state('idle')
            return

        # In air -> jump or fall
        if not self.on_ground:
            if self.vel_y < 0:
                # going up -> jump
                # If we just switched from falling, play jump_trans first
                if self.state == 'fall' and 'jump_trans' in self.animations:
                    self._set_state('jump_trans')
                else:
                    self._set_state('jump')
            else:
                # going down -> fall. If we were in jump, insert transition
                if self.state == 'jump' and 'jump_trans' in self.animations:
                    self._set_state('jump_trans')
                else:
                    self._set_state('fall')
        else:
            # On ground: run or idle
            if abs(self.vel_x) > 0:
                # turning quickly? use turn animation when velocity reverses
                if (self.vel_x > 0 and self.facing < 0) or (self.vel_x < 0 and self.facing > 0):
                    self._set_state('turn')
                else:
                    self._set_state('run')
            else:
                self._set_state('idle')

        # advance animation normally
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
                    # clamp to last frame and report finished
                    self.anim_index = len(frames) - 1
                    return True
        return False

    def draw(self, surface):
        frames = self.animations.get(self.state, None)
        if not frames:
            # fallback visual
            pygame.draw.rect(surface, (0, 200, 0), self.rect)
            return

        frame = frames[self.anim_index % len(frames)]
        # flip if facing left
        if self.facing < 0:
            frame = pygame.transform.flip(frame, True, False)

        surface.blit(frame, self.rect.topleft)

    def draw_at(self, surface, pos):
        """Draw player sprite at a specific screen position (used by camera system).
        
        Args:
            surface: pygame surface to draw on
            pos: tuple (x, y) position on screen in pixels
        """
        frames = self.animations.get(self.state, None)
        if not frames:
            # fallback visual
            pygame.draw.rect(surface, (0, 200, 0), (*pos, self.width, self.height))
            return

        frame = frames[self.anim_index % len(frames)]
        # flip if facing left
        if self.facing < 0:
            frame = pygame.transform.flip(frame, True, False)

        surface.blit(frame, pos)

    def get_rect(self):
        return self.rect
    
    def get_hitbox(self):
        """Get the actual hitbox for body collision detection.
        
        Returns a rect centered on the player body for realistic collision.
        Same dimensions as enemy hitbox for consistency.
        """
        # Center the hitbox horizontally
        hitbox_x = self.rect.centerx - self.hitbox_width // 2
        # Align to lower part of sprite (where character actually is)
        hitbox_y = self.rect.bottom - self.hitbox_height
        
        return pygame.Rect(hitbox_x, hitbox_y, self.hitbox_width, self.hitbox_height)