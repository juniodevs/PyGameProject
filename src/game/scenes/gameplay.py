import pygame
import random
from ..settings import WHITE, ATTACK_RANGE, ATTACK_HEIGHT_FACTOR
from ..entities.player import Player
from ..entities.enemy import Enemy
from ..camera import Camera
from ..background import ParallaxBackground

class Gameplay:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()

        self.world_width = 2400  
        self.world_height = 2400  

        self.ground_y = self.world_height - 150

        self.player = Player(400, self.ground_y - 160)

        self.enemies = []
        test_enemy = Enemy(1000, self.ground_y - 160)
        self.enemies.append(test_enemy)

        self.kill_count = 0

        self.camera = Camera(self.screen_width, self.screen_height, self.world_width, self.world_height)

        self.background = ParallaxBackground(self.screen_width, self.screen_height, self.world_width, self.ground_y)

        try:
            self.app.audio.crossfade_music('gameplay', fade_ms=800)
        except Exception:
            pass

        self.font = self._choose_game_font(28)

        self.debug_attacks = False  

        self.is_dead = False
        self.death_time = 0  
        self.death_countdown = 5  
        self.attack_cooldown_ms = 500
        self.last_attack_time = 0

    def _choose_game_font(self, size, bold=False):
        """Pick a game-like font if available, otherwise fall back to system default.

        Tries a small list of common game/arcade fonts and falls back to SysFont.
        """
        preferred = [
            'PressStart2P',
            'ArcadeClassic',
            'Impact',
            'Arial Black',
            'Verdana',
            'Courier New',
            'Arial',
        ]
        for name in preferred:
            try:
                path = pygame.font.match_font(name)
                if path:
                    return pygame.font.Font(path, size)
            except Exception:
                continue

        return pygame.font.SysFont(None, size, bold=bold)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.app.running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:

                self.app.go_to_menu()

            if event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                now = pygame.time.get_ticks()
                if now - self.last_attack_time >= self.attack_cooldown_ms:
                    self.last_attack_time = now
                    try:
                        self.app.audio.play_variant('attack')
                    except Exception:
                        pass
                    self.player.attack()

            if event.key == pygame.K_h:
                self.player.take_damage(1)

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

        self.player.update(self.world_width, self.world_height, self.ground_y)

        for enemy in self.enemies:
            enemy.update(self.player, self.world_width, self.world_height, self.ground_y)

        self._check_player_attack_collision()

        self._check_enemy_attack_collision()

        now = pygame.time.get_ticks()

        for enemy in self.enemies:
            if enemy.current_hp <= 0 and now - enemy.death_time > 1000:
                self.kill_count += 1
                self._spawn_new_enemy()  

        self.enemies = [e for e in self.enemies if not (e.current_hp <= 0 and now - e.death_time > 1000)]

        if self.player.current_hp <= 0 and not self.is_dead:
            self.is_dead = True
            self.death_time = pygame.time.get_ticks()

        if self.is_dead:
            now = pygame.time.get_ticks()
            elapsed_ms = now - self.death_time
            elapsed_s = elapsed_ms / 1000.0

            if elapsed_s >= self.death_countdown:

                self.app.go_to_menu()

        self.camera.update(self.player.rect)

    def render(self, screen):

        self.background.draw(screen, self.camera)

        for enemy in self.enemies:
            enemy_screen_rect = self.camera.apply(enemy.rect)

            if enemy_screen_rect.right > 0 and enemy_screen_rect.left < self.screen_width:
                enemy.draw_at(screen, enemy_screen_rect.topleft)

                self._draw_enemy_hp(screen, enemy, enemy_screen_rect)

        player_screen_rect = self.camera.apply(self.player.rect)

        if player_screen_rect.right > 0 and player_screen_rect.left < self.screen_width:
            self.player.draw_at(screen, player_screen_rect.topleft)

        instr = self.font.render('Esc - Voltar ao Menu', True, WHITE)
        screen.blit(instr, (10, 10))

        kills_text = self.font.render(f'Kills: {self.kill_count}', True, WHITE)
        screen.blit(kills_text, (10, 50))

        self._draw_hp_overlay(screen)

        if self.is_dead:
            self._draw_death_countdown(screen)

    def _draw_hp_overlay(self, screen):
        """Draw HP overlay showing current HP / max HP as visual hearts/bars."""

        hp_x = self.screen_width - 200
        hp_y = 20

        hp_label = self.font.render(f'HP: {self.player.current_hp} / {self.player.max_hp}', True, WHITE)
        screen.blit(hp_label, (hp_x, hp_y))

        bar_width = 25
        bar_height = 20
        bar_gap = 5
        bar_x = hp_x
        bar_y = hp_y + 35

        for i in range(self.player.max_hp):

            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))

            if i < self.player.current_hp:

                color = (0, 200, 0)
            else:

                color = (50, 50, 50)

            pygame.draw.rect(screen, color, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 2)  

            bar_x += bar_width + bar_gap

    def _draw_death_countdown(self, screen):
        """Draw death screen with countdown to return to menu."""

        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        now = pygame.time.get_ticks()
        elapsed_ms = now - self.death_time
        remaining_s = max(0, self.death_countdown - (elapsed_ms / 1000.0))

        large_font = self._choose_game_font(72)
        death_text = large_font.render('VOCÊ MORREU', True, (255, 0, 0))
        text_rect = death_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 80))
        screen.blit(death_text, text_rect)

        countdown_font = self._choose_game_font(48)
        countdown_text = countdown_font.render(f'Retornando em: {int(remaining_s) + 1}s', True, WHITE)
        countdown_rect = countdown_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
        screen.blit(countdown_text, countdown_rect)

    def _check_player_attack_collision(self):
        """Check if player's attack hit any enemies with improved hitbox detection."""

        if not self.player.state.startswith('attack'):
            return

        player_hb = self.player.get_hitbox()
        attack_range = ATTACK_RANGE

        attack_height = max(8, int(player_hb.height * ATTACK_HEIGHT_FACTOR))
        attack_y = player_hb.top + (player_hb.height - attack_height) // 2

        if self.player.facing > 0:
            attack_rect = pygame.Rect(player_hb.right, attack_y, attack_range, attack_height)
        else:
            attack_rect = pygame.Rect(player_hb.left - attack_range, attack_y, attack_range, attack_height)

        for enemy in self.enemies:
            enemy_hitbox = enemy.get_hitbox()
            if attack_rect.colliderect(enemy_hitbox):

                damage_amount = 2
                knockback_dir = 1 if self.player.facing > 0 else -1
                if self.debug_attacks:
                    print(f"ATTACK hit: attack_rect={attack_rect}, enemy_rect={enemy.rect}, enemy_hitbox={enemy_hitbox}")
                killed = enemy.take_damage(damage_amount, knockback_dir)

                knockback_strength = 10
                self.player.knockback_vel_x = knockback_strength * (-self.player.facing)

                now = pygame.time.get_ticks()

                try:
                    self.app.trigger_slow_motion(duration_ms=220, scale=0.35)
                except Exception:
                    pass
                try:
                    self.camera.start_shake(duration_ms=260, magnitude=8)
                except Exception:
                    pass

                try:
                    self.app.audio.play_variant('attack')
                    self.app.audio.play_variant('hit')
                except Exception:
                    pass

                self.player.flash_timer = now
                try:
                    self.app.trigger_zoom(duration_ms=220, magnitude=1.06)
                except Exception:
                    pass

                if killed:

                    try:
                        self.app.audio.play_variant('die')
                    except Exception:
                        pass

    def _check_enemy_attack_collision(self):
        """Check if any enemy is attacking and hitting the player."""
        for enemy in self.enemies:

            if enemy.state != 'attack1' and enemy.state != 'attack2':
                continue

            attack_range = ATTACK_RANGE
            enemy_hb = enemy.get_hitbox()

            attack_height = max(8, int(enemy_hb.height * ATTACK_HEIGHT_FACTOR))
            attack_y = enemy_hb.top + (enemy_hb.height - attack_height) // 2

            if enemy.facing > 0:
                attack_rect = pygame.Rect(enemy_hb.right, attack_y, attack_range, attack_height)
            else:
                attack_rect = pygame.Rect(enemy_hb.left - attack_range, attack_y, attack_range, attack_height)

            player_hitbox = self.player.get_hitbox()

            if attack_rect.colliderect(player_hitbox):

                damage_amount = 1
                self.player.take_damage(damage_amount)

                knockback_strength = 15
                self.player.knockback_vel_x = knockback_strength * (-enemy.facing)

                try:
                    self.app.trigger_slow_motion(duration_ms=220, scale=0.35)
                except Exception:
                    pass
                try:
                    self.camera.start_shake(duration_ms=260, magnitude=10)
                except Exception:
                    pass
                try:
                    self.app.trigger_zoom(duration_ms=220, magnitude=1.08)
                except Exception:
                    pass

                try:
                    self.app.audio.play_variant('hit')
                except Exception:
                    pass

                if self.player.current_hp <= 0:
                    try:
                        self.app.audio.play_variant('die')
                        self.app.audio.crossfade_music('game_over', fade_ms=1000)
                    except Exception:
                        pass

    def _draw_enemy_hp(self, screen, enemy, enemy_screen_rect):
        """Draw enemy HP bar above the enemy sprite."""

        bar_width = 60
        bar_height = 8
        bar_margin = 5  

        bar_x = enemy_screen_rect.centerx - bar_width // 2
        bar_y = enemy_screen_rect.top - bar_height - bar_margin

        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        if enemy.current_hp > enemy.max_hp // 2:
            hp_color = (0, 200, 0)  
        elif enemy.current_hp > 1:
            hp_color = (200, 200, 0)  
        else:
            hp_color = (200, 0, 0)  

        hp_ratio = enemy.current_hp / enemy.max_hp
        filled_width = int(bar_width * hp_ratio)
        if filled_width > 0:
            pygame.draw.rect(screen, hp_color, (bar_x, bar_y, filled_width, bar_height))

        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)

        hp_font = self._choose_game_font(16)
        hp_text = hp_font.render(f'{enemy.current_hp}/{enemy.max_hp}', True, (255, 255, 255))
        text_rect = hp_text.get_rect(center=(enemy_screen_rect.centerx, bar_y - 12))
        screen.blit(hp_text, text_rect)

    def _draw_debug_hitboxes(self, screen):
        """Draw debug hitboxes for collision detection testing."""

        player_screen_rect = self.camera.apply(self.player.rect)
        pygame.draw.rect(screen, (255, 255, 0), player_screen_rect, 2)

        player_hitbox = self.player.get_hitbox()
        player_hitbox_screen = self.camera.apply(player_hitbox)
        pygame.draw.rect(screen, (255, 0, 0), player_hitbox_screen, 2)

        for enemy in self.enemies:

            enemy_screen_rect = self.camera.apply(enemy.rect)
            pygame.draw.rect(screen, (0, 255, 255), enemy_screen_rect, 2)

            enemy_hitbox = enemy.get_hitbox()
            enemy_hitbox_screen = self.camera.apply(enemy_hitbox)
            pygame.draw.rect(screen, (255, 0, 255), enemy_hitbox_screen, 2)

        debug_font = self._choose_game_font(20)
        debug_text = debug_font.render('Amarelo=Player Sprite | Vermelho=Player Hitbox | Ciano=Enemy Sprite | Magenta=Enemy Hitbox', True, (255, 255, 0))
        screen.blit(debug_text, (10, self.screen_height - 30))

    def _spawn_new_enemy(self):
        """Spawn a new enemy at a random location on the map."""

        min_spawn_dist = 600  
        while True:
            spawn_x = random.randint(100, self.world_width - 100)

            if abs(spawn_x - self.player.rect.centerx) > min_spawn_dist:
                break

        spawn_y = self.ground_y - 160
        new_enemy = Enemy(spawn_x, spawn_y)
        self.enemies.append(new_enemy)

    def update_events(self):

        pass