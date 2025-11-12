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
            self.app.audio.stop_music(fade_ms=600)
        except Exception:
            pass
        try:
            self.app.audio.start_battle_music(('battlemusic1','battlemusic2') , crossfade_s=3.0)
        except Exception:
            pass

        self.font = self._choose_game_font(28)

        self.is_dead = False
        self.death_time = 0  
        self.death_countdown = 5  
        # death menu (appear after death animation / short delay)
        self.death_menu_active = False
        self.death_menu_options = ['REINICIAR FASE', 'VOLTAR AO MENU']
        self.death_menu_index = 0
        self.death_menu_delay_ms = 700

        self.attack_cooldown_ms = 1000
        self.last_attack_time = 0

        self.paused = False
        self.pause_index = 0
        self.pause_options = ['CONTINUAR', 'CONFIGURAÇÃO', 'VOLTAR PARA O MENU']
        self.config_overlay = None

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
        if getattr(self, 'config_overlay', None):
            try:
                self.config_overlay.handle_event(event)
                return
            except Exception:

                try:
                    self.config_overlay._done()
                except Exception:
                    pass
                self.config_overlay = None
        # If player is dead and death menu is active, intercept input for choice selection
        if self.is_dead and self.death_menu_active:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.death_menu_index = (self.death_menu_index - 1) % len(self.death_menu_options)
                    return
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.death_menu_index = (self.death_menu_index + 1) % len(self.death_menu_options)
                    return
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    choice = self.death_menu_options[self.death_menu_index]
                    if choice == 'REINICIAR FASE':
                        # restart by reloading this scene
                        try:
                            # restore audio settings from config before restarting
                            try:
                                from ..utils.config import load_config
                                cfg = load_config()
                                try:
                                    self.app.audio.set_music_volume(cfg.get('music_volume', 0.6))
                                    self.app.audio.set_sfx_volume(cfg.get('sfx_volume', 1.0))
                                    self.app.audio.set_master_volume(cfg.get('master_volume', 1.0))
                                except Exception:
                                    pass
                            except Exception:
                                pass
                            self.app.change_scene(self.__class__)
                        except Exception:
                            # fallback: go to menu if restart fails
                            try:
                                from ..utils.config import load_config
                                cfg = load_config()
                                try:
                                    self.app.audio.set_music_volume(cfg.get('music_volume', 0.6))
                                    self.app.audio.set_sfx_volume(cfg.get('sfx_volume', 1.0))
                                    self.app.audio.set_master_volume(cfg.get('master_volume', 1.0))
                                except Exception:
                                    pass
                            except Exception:
                                pass
                            self.app.go_to_menu()
                    else:
                        # restore audio before returning to menu
                        try:
                            from ..utils.config import load_config
                            cfg = load_config()
                            try:
                                self.app.audio.set_music_volume(cfg.get('music_volume', 0.6))
                                self.app.audio.set_sfx_volume(cfg.get('sfx_volume', 1.0))
                                self.app.audio.set_master_volume(cfg.get('master_volume', 1.0))
                            except Exception:
                                pass
                        except Exception:
                            pass
                        self.app.go_to_menu()
                    return
                elif event.key == pygame.K_ESCAPE:
                    # treat as go to menu
                    self.app.go_to_menu()
                    return
            # also allow mouse click on options
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                try:
                    w, h = self.screen.get_size()
                    base_y = h // 2 + 20
                    for i, opt in enumerate(self.death_menu_options):
                        txt = self._choose_game_font(32).render(opt, True, (255, 255, 255))
                        txt_x = w // 2 - txt.get_width() // 2
                        txt_y = base_y + i * 56
                        rect = pygame.Rect(txt_x - 12, txt_y - 6, txt.get_width() + 24, txt.get_height() + 12)
                        if rect.collidepoint(mx, my):
                            if opt == 'REINICIAR FASE':
                                try:
                                    from ..utils.config import load_config
                                    try:
                                        cfg = load_config()
                                        try:
                                            self.app.audio.set_music_volume(cfg.get('music_volume', 0.6))
                                            self.app.audio.set_sfx_volume(cfg.get('sfx_volume', 1.0))
                                            self.app.audio.set_master_volume(cfg.get('master_volume', 1.0))
                                        except Exception:
                                            pass
                                    except Exception:
                                        pass
                                    self.app.change_scene(self.__class__)
                                except Exception:
                                    self.app.go_to_menu()
                            else:
                                try:
                                    from ..utils.config import load_config
                                    cfg = load_config()
                                    try:
                                        self.app.audio.set_music_volume(cfg.get('music_volume', 0.6))
                                        self.app.audio.set_sfx_volume(cfg.get('sfx_volume', 1.0))
                                        self.app.audio.set_master_volume(cfg.get('master_volume', 1.0))
                                    except Exception:
                                        pass
                                except Exception:
                                    pass
                                self.app.go_to_menu()
                            return
                except Exception:
                    pass

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:

                if self.config_overlay:

                    self.config_overlay._done()
                    self.config_overlay = None
                else:
                    self.paused = not self.paused

                return

            if self.paused:
                if event.key in (pygame.K_UP,):
                    self.pause_index = (self.pause_index - 1) % len(self.pause_options)
                elif event.key in (pygame.K_DOWN,):
                    self.pause_index = (self.pause_index + 1) % len(self.pause_options)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    choice = self.pause_options[self.pause_index]
                    if choice == 'CONTINUAR':
                        self.paused = False
                    elif choice == 'CONFIGURAÇÃO':

                        from .config_menu import ConfigMenu
                        self.config_overlay = ConfigMenu(self.app, on_done=self._close_config)
                    elif choice == 'VOLTAR PARA O MENU':
                        self.app.go_to_menu()

                return

            if event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                now = pygame.time.get_ticks()
                if now - self.last_attack_time >= self.attack_cooldown_ms:
                    self.last_attack_time = now
                    try:
                        self.app.audio.play_sound_effect('attack', pitch=1.1, bitcrush=1, distortion=0.03, volume=0.9)
                    except Exception:
                        pass
                    self.player.attack()

    def update(self):

        # don't update game logic while paused or config overlay
        if self.paused or self.config_overlay:
            return

        now = pygame.time.get_ticks()

        # If player is not dead, run normal update loop
        if not self.is_dead:
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
            self.player.update(self.world_width, self.world_height, self.ground_y)

            for enemy in self.enemies:
                enemy.update(self.player, self.world_width, self.world_height, self.ground_y)

            self._check_player_attack_collision()

            self._check_enemy_attack_collision()

            for enemy in self.enemies:
                if enemy.current_hp <= 0 and now - enemy.death_time > 1000:
                    self.kill_count += 1
                    self._spawn_new_enemy()  

            self.enemies = [e for e in self.enemies if not (e.current_hp <= 0 and now - e.death_time > 1000)]

            if self.player.current_hp <= 0 and not self.is_dead:
                self.is_dead = True
                self.death_time = now
                # mute sfx immediately because player is dead (avoid attack/hit sounds after death)
                try:
                    # try to set sfx volume to 0; config will be restored when restarting/going to menu
                    self.app.audio.set_sfx_volume(0)
                except Exception:
                    pass

        else:
            # Player is dead — wait a small delay for death animation, then show death menu
            elapsed_ms = now - self.death_time
            if not self.death_menu_active and elapsed_ms >= self.death_menu_delay_ms:
                self.death_menu_active = True
                self.death_menu_index = 0

        # keep camera centered on player even after death
        try:
            self.camera.update(self.player.rect)
        except Exception:
            pass

    def _close_config(self):
        self.config_overlay = None

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
            if getattr(self, 'death_menu_active', False):
                self._draw_death_menu(screen)
            else:
                self._draw_death_countdown(screen)

        if self.paused:
            self._render_pause(screen)
        if self.config_overlay:
            self.config_overlay.render(screen)

    def _render_pause(self, screen):
        w, h = screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        title = self._choose_game_font(48).render('PAUSADO', True, (255, 255, 255))
        screen.blit(title, (w // 2 - title.get_width() // 2, 100))

        y = 220
        for i, opt in enumerate(self.pause_options):
            color = (255, 220, 100) if i == self.pause_index else (255, 255, 255)
            text = self._choose_game_font(28).render(opt, True, color)
            text_x = w // 2 - text.get_width() // 2

            if i == self.pause_index:
                arrow_x = text_x - 40
                center_y = y + text.get_height() // 2
                pts = [(arrow_x + 28, center_y - 10), (arrow_x + 6, center_y), (arrow_x + 28, center_y + 10)]
                pygame.draw.polygon(screen, (255, 220, 100), pts)

            screen.blit(text, (text_x, y))
            y += 56

        hint_prefix = 'Use '
        hint_suffix = ' para navegar • Enter selecionar'
        try:
            hint_font = self._choose_game_font(20)
            prefix_surf = hint_font.render(hint_prefix, True, (200, 200, 200))
            suffix_surf = hint_font.render(hint_suffix, True, (200, 200, 200))
            arrow_w = 18
            gap = 6
            total_w = prefix_surf.get_width() + arrow_w + gap + arrow_w + suffix_surf.get_width()
            hint_x = w // 2 - total_w // 2
            hint_y = y + 6
            screen.blit(prefix_surf, (hint_x, hint_y))
            hx = hint_x + prefix_surf.get_width()

            self._draw_arrow_icon(screen, hx, hint_y, 'up', (240, 220, 160))
            hx += arrow_w + gap

            self._draw_arrow_icon(screen, hx, hint_y, 'down', (240, 220, 160))
            hx += arrow_w + gap
            screen.blit(suffix_surf, (hx, hint_y))
        except Exception:
            pass

    def _draw_arrow_icon(self, screen, x, y, direction, color=(240, 220, 160)):
        """Draw a small triangular arrow icon at (x,y). direction in ('left','right','up','down').

        x,y are the top-left of an area approx 18x18 where the icon will be drawn.
        """
        w = 18
        h = 18
        center_y = y + h // 2
        if direction in ('left', 'l'):
            pts = [(x + w - 2, center_y - 6), (x + 2, center_y), (x + w - 2, center_y + 6)]
        elif direction in ('right', 'r'):
            pts = [(x + 2, center_y - 6), (x + w - 2, center_y), (x + 2, center_y + 6)]
        elif direction in ('up', 'u'):
            pts = [(x + w // 2, center_y - 6), (x + 2, center_y + 6), (x + w - 2, center_y + 6)]
        else:
            pts = [(x + 2, center_y - 6), (x + w - 2, center_y - 6), (x + w // 2, center_y + 6)]
        pygame.draw.polygon(screen, color, pts)

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
        # Minimal overlay when dead before the death menu appears (no countdown text)
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        large_font = self._choose_game_font(72)
        death_text = large_font.render('VOCÊ MORREU', True, (255, 0, 0))
        text_rect = death_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 20))
        screen.blit(death_text, text_rect)

    def _draw_death_menu(self, screen):
        """Draw a simple menu allowing the player to Restart or go back to Menu."""
        w, h = screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        large_font = self._choose_game_font(72)
        title = large_font.render('VOCÊ MORREU', True, (255, 0, 0))
        screen.blit(title, (w // 2 - title.get_width() // 2, h // 2 - 140))

        base_y = h // 2 - 20
        for i, opt in enumerate(self.death_menu_options):
            is_sel = (i == self.death_menu_index)
            color = (255, 220, 100) if is_sel else (255, 255, 255)
            txt = self._choose_game_font(32).render(opt, True, color)
            txt_x = w // 2 - txt.get_width() // 2
            txt_y = base_y + i * 56

            # button background for clarity
            rect = pygame.Rect(txt_x - 12, txt_y - 6, txt.get_width() + 24, txt.get_height() + 12)
            pygame.draw.rect(screen, (40, 40, 40), rect, border_radius=6)
            if is_sel:
                pygame.draw.rect(screen, (255, 220, 100), rect, 3, border_radius=6)

            screen.blit(txt, (txt_x, txt_y))

        hint = self._choose_game_font(18).render('Use ↑/↓ para escolher • Enter para confirmar', True, (200, 200, 200))
        screen.blit(hint, (w // 2 - hint.get_width() // 2, base_y + len(self.death_menu_options) * 56 + 8))

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
                    self.app.audio.play_sound_effect(
                        'attack',
                        pitch=1.1,
                        bitcrush=1,
                        distortion=0.03,
                        volume=0.9,
                        layers=[
                            {'pitch': 1.0, 'bitcrush': 0, 'gain': 0.6},
                            {'pitch': 1.2, 'bitcrush': 2, 'gain': 0.4},
                        ],
                        async_process=True,
                        cache=True,
                    )

                    self.app.audio.play_sound_effect(
                        'hit',
                        pitch=0.95,
                        bitcrush=2,
                        distortion=0.06,
                        volume=1.0,
                        layers=[
                            {'pitch': 1.0, 'bitcrush': 0, 'gain': 0.5},
                            {'pitch': 0.8, 'bitcrush': 3, 'gain': 0.5},
                        ],
                        async_process=True,
                        cache=True,
                    )
                except Exception:
                    pass
                try:
                    self.app.trigger_zoom(duration_ms=220, magnitude=1.06)
                except Exception:
                    pass

                if killed:

                    try:

                        self.app.audio.play_sound_effect(
                            'die',
                            pitch=0.9,
                            bitcrush=3,
                            distortion=0.12,
                            volume=0.9,
                            layers=[
                                {'pitch': 1.0, 'bitcrush': 0, 'gain': 0.5},
                                {'pitch': 0.85, 'bitcrush': 4, 'gain': 0.5},
                            ],
                            async_process=True,
                            cache=True,
                        )
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