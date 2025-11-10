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
        # Sprite size (same as player: 304x160)
        self.width = 304
        self.height = 160
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Much larger to match sprite size better
        # Hitbox size (use global constants)
        self.hitbox_width = HITBOX_WIDTH
        self.hitbox_height = HITBOX_HEIGHT
        # Hitbox offset from sprite rect.topleft. Keep symmetric with Player.
        self.hitbox_offset_x = (self.width - self.hitbox_width) // 2
        self.hitbox_offset_y = self.height - self.hitbox_height
        
        # Movement
        self.speed = 3.0
        self.vel_x = 0
        self.vel_y = 0
        self.gravity = 0.6
        self.on_ground = False
        self.facing = 1  # 1 = right, -1 = left

        # Animation state
        self.animations = {}  # name -> list of Surfaces
        self.state = 'idle'
        self.anim_index = 0
        self.last_anim_time = pygame.time.get_ticks()
        # milliseconds per frame for each animation
        self.frame_durations = {
            'idle': 100,
            'run': 90,
            'turn': 120,
            'attack1': 80,
            'attack2': 80,
            'hit': 150,
            'death': 100,
        }

        # HP system
        self.max_hp = 4  # 2 corações
        self.current_hp = 4
        self.hit_cooldown = 0
        self.hit_cooldown_duration = 600  # Invulnerability after hit
        self.death_time = 0  # Track when enemy died (for removal after animation)

        # Flash effect when receiving damage
        self.flash_timer = 0
        self.flash_duration = 180

        # AI behavior
        self.detection_range = 500  # How far can detect player
        self.attack_distance = 200  # Distance to start attacking
        self.retreat_distance = 150  # Distance to retreat/back away if too close
        self.attack_cooldown = 0
        self.attack_cooldown_duration = 2000  # Time between attacks
        self.locked = False  # Lock movement during certain animations
        
        # AI state tracking
        self.pursuing = False
        self.last_player_x = x
        self._next_attack_is_two = False  # Alternate between attack1 and attack2

        # Knockback
        self.knockback_vel_x = 0
        self.knockback_decay = 0.85

        # Load sprites
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

        # Mapping: state -> (filename, frame_count)
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
                    # Avoid convert_alpha in headless/test envs when display not init.
                    if pygame.display.get_init():
                        sheet = pygame.image.load(path).convert_alpha()
                    else:
                        sheet = pygame.image.load(path)
                    sheet_w, sheet_h = sheet.get_size()

                    # Calculate frame width from total width and frame count
                    frame_w = sheet_w // frame_count

                    # Extract each frame from the spritesheet
                    for i in range(frame_count):
                        rect = pygame.Rect(i * frame_w, 0, frame_w, sheet_h)
                        frame = pygame.Surface(rect.size, pygame.SRCALPHA)
                        frame.blit(sheet, (0, 0), rect)
                        # Scale to player size (304x160)
                        frame = pygame.transform.smoothscale(frame, (self.width, self.height))
                        frames_list.append(frame)

                except Exception as e:
                    print(f"Error loading {path}: {e}")
                    # Fallback: red placeholder
                    surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    surf.fill((255, 0, 0, 128))
                    frames_list.append(surf)
            else:
                print(f"File not found: {path}")
                # Fallback: red placeholder
                surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                surf.fill((255, 0, 0, 128))
                frames_list.append(surf)

            if frames_list:
                self.animations[state] = frames_list
            else:
                # Fallback if no frames found
                surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                surf.fill((255, 0, 0, 128))
                self.animations[state] = [surf]

    def update(self, player, world_width, world_height, ground_y):
        """Update enemy AI, movement, and animation.
        
        Args:
            player: Player object for AI targeting
            world_width: World width for bounds checking
            world_height: World height for bounds checking
            ground_y: Ground Y position
        """
        # Apply gravity
        self.vel_y += self.gravity

        # Apply knockback decay
        self.knockback_vel_x *= self.knockback_decay
        if abs(self.knockback_vel_x) < 0.1:
            self.knockback_vel_x = 0

        # Move with knockback
        self.rect.x += int(self.vel_x + self.knockback_vel_x)
        self.rect.y += int(self.vel_y)

        # Collision with player - prevent overlapping
        # Get hitboxes
        my_hitbox = self.get_hitbox()
        player_hitbox = player.get_hitbox()
        
        # If colliding, push back
        if my_hitbox.colliderect(player_hitbox):
            # Push away from player
            if player.rect.centerx > self.rect.centerx:
                # Player is to the right, push enemy left
                self.rect.x -= 2
            else:
                # Player is to the left, push enemy right
                self.rect.x += 2
            # Stop movement
            self.vel_x = 0

        # Floor collision
        if self.rect.bottom >= ground_y:
            self.rect.bottom = ground_y
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        # Keep inside horizontal bounds based on hitbox (not sprite image)
        # Shift the sprite rect so the hitbox remains inside the world bounds.
        hb = self.get_hitbox()
        if hb.left < 0:
            overlap = 0 - hb.left
            self.rect.x += overlap
        if hb.right > world_width:
            overlap = hb.right - world_width
            self.rect.x -= overlap

        # Update cooldowns
        now = pygame.time.get_ticks()
        if self.hit_cooldown > 0 and now - self.hit_cooldown >= self.hit_cooldown_duration:
            self.hit_cooldown = 0

        if self.attack_cooldown > 0 and now - self.attack_cooldown >= self.attack_cooldown_duration:
            self.attack_cooldown = 0

        # Death state - play death animation and don't update AI
        if self.state == 'death':
            self._update_animation(loop=False)
            return

        # Hit state - play hit animation briefly
        if self.state == 'hit':
            finished = self._update_animation(loop=False)
            if finished:
                self.locked = False
                self.vel_x = 0
                self._set_state('idle')
            return

        # Update AI (always, to keep facing player)
        self._update_ai(player, now)

        # Attack states - play attack animation
        if self.state.startswith('attack'):
            finished = self._update_animation(loop=False)
            if finished:
                self.locked = False
                self.vel_x = 0
                self._set_state('idle')
            return

        # Choose idle/run animation based on velocity
        if self.on_ground:
            if abs(self.vel_x) > 0.5:
                self._set_state('run')
            else:
                self._set_state('idle')
        else:
            # In air, use run animation
            self._set_state('run')

        self._update_animation(loop=True)

    def _update_ai(self, player, now):
        """Update AI to pursue and attack player while maintaining safe distance."""
        # Calculate distance to player
        dist = abs(player.rect.centerx - self.rect.centerx)

        # Always face the player
        if player.rect.centerx > self.rect.centerx:
            self.facing = 1
        else:
            self.facing = -1

        # Remember player position
        self.last_player_x = player.rect.centerx

        # Don't pursue if dead or being hit
        if self.state in ('hit', 'death'):
            self.vel_x = 0
            return

        # Don't move during attack
        if self.state.startswith('attack'):
            self.vel_x = 0
            return

        # Decision tree based on distance
        
        # 1. If TOO CLOSE (closer than retreat distance) -> BACK AWAY
        if dist < self.retreat_distance:
            # Back away from player
            if player.rect.centerx > self.rect.centerx:
                self.vel_x = -self.speed  # Move left
            else:
                self.vel_x = self.speed   # Move right
            self.pursuing = True
            return

        # 2. If in perfect attack distance and cooldown is ready -> ATTACK
        if dist < self.attack_distance and self.attack_cooldown == 0:
            self.attack()
            self.vel_x = 0
            self.pursuing = True
            return

        # 3. If between retreat and attack distance -> MAINTAIN DISTANCE (idle)
        if dist < self.attack_distance:
            # Just stay put, don't move
            self.vel_x = 0
            self.pursuing = True
            return

        # 4. If in detection range but beyond attack distance -> PURSUE
        if dist < self.detection_range:
            if player.rect.centerx > self.rect.centerx:
                self.vel_x = self.speed
            else:
                self.vel_x = -self.speed
            self.pursuing = True
            return

        # 5. Out of range -> IDLE
        self.vel_x = 0
        self.pursuing = False

    def attack(self):
        """Trigger an attack. Alternates between attack1 and attack2."""
        if self.state.startswith('attack') or self.state == 'death':
            return
        
        # Alternate between attack1 and attack2
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
        # Check if still in cooldown (invulnerable)
        now = pygame.time.get_ticks()
        if self.hit_cooldown > 0 and now - self.hit_cooldown < self.hit_cooldown_duration:
            return False

        self.current_hp -= amount
        self.hit_cooldown = now

        # trigger flash effect
        self.flash_timer = now

        # Knockback away from attacker
        knockback_strength = 15
        self.knockback_vel_x = knockback_strength * knockback_direction

        if self.current_hp > 0:
            self._set_state('hit')
            self.locked = True
        else:
            self._set_state('death')
            self.death_time = now  # Record death time for removal after animation
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
            # Fallback visual
            pygame.draw.rect(surface, (200, 0, 0), self.rect)
            return

        frame = frames[self.anim_index % len(frames)]
        # Flip if facing left
        if self.facing < 0:
            frame = pygame.transform.flip(frame, True, False)

        # Apply camera offset
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        surface.blit(frame, (screen_x, screen_y))

        # Flash overlay when damaged (only over sprite silhouette)
        now = pygame.time.get_ticks()
        if getattr(self, 'flash_timer', 0) and now - self.flash_timer < self.flash_duration:
            try:
                white_frame = frame.copy()
                # Use RGB add so alpha stays untouched
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
            # Fallback visual
            pygame.draw.rect(surface, (200, 0, 0), (*pos, self.width, self.height))
            return

        frame = frames[self.anim_index % len(frames)]
        # Flip if facing left
        if self.facing < 0:
            frame = pygame.transform.flip(frame, True, False)

        surface.blit(frame, pos)

        # Flash overlay when damaged (only over sprite silhouette)
        now = pygame.time.get_ticks()
        if getattr(self, 'flash_timer', 0) and now - self.flash_timer < self.flash_duration:
            try:
                white_frame = frame.copy()
                # Use RGB add so alpha stays untouched
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
        # Compute hitbox top-left relative to sprite rect.topleft using explicit offsets.
        hitbox_x = int(self.rect.x + self.hitbox_offset_x)
        hitbox_y = int(self.rect.y + self.hitbox_offset_y)

        return pygame.Rect(hitbox_x, hitbox_y, int(self.hitbox_width), int(self.hitbox_height))

    def get_rect(self):
        """Get the sprite drawing rect."""
        return self.rect

    def is_alive(self):
        """Check if enemy is alive."""
        return self.current_hp > 0