import os
import threading
import time
import random
import pygame


class AudioManager:

    DEFAULT_SFX_EXT = ('.wav', '.ogg', '.mp3')
    DEFAULT_MUSIC_EXT = ('.ogg', '.mp3', '.wav')

    def __init__(self, assets_path=None, num_channels=16):
        # Locate assets folder by default relative to this file: ../../assets
        if assets_path is None:
            base = os.path.dirname(__file__)
            assets_path = os.path.abspath(os.path.join(base, '..', '..', 'assets'))
        self.assets_path = assets_path
        self.sfx_path = os.path.join(self.assets_path, 'sounds')
        self.music_path = os.path.join(self.assets_path, 'music')

        # Ensure mixer is initialized
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:
            # In some environments mixer init may fail; we don't crash the app.
            pass

        # Sound storage
        self.sounds = {}  # name -> pygame.mixer.Sound
        self.channels = {}  # optional named channels
        self.variant_sounds = {}

        # Reserve channels
        try:
            pygame.mixer.set_num_channels(max(8, int(num_channels)))
        except Exception:
            pass

        # Volume controls
        self.master_volume = 1.0
        self.sfx_volume = 1.0
        self.music_volume = 0.6

    def _find_file(self, directory, name, exts):
        # If name already has an extension and exists, return it
        candidate = os.path.join(directory, name)
        if os.path.isfile(candidate):
            return candidate

        # Try with extensions
        for e in exts:
            candidate = os.path.join(directory, name + e)
            if os.path.isfile(candidate):
                return candidate
        return None

    def load_sound(self, name, filename=None):
        fname = filename or name
        path = self._find_file(self.sfx_path, fname, self.DEFAULT_SFX_EXT)
        if not path:
            return None
        try:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(self.sfx_volume * self.master_volume)
            self.sounds[name] = snd
            return snd
        except Exception:
            return None

    def play_sound(self, name, volume=1.0, maxtime=0, fade_ms=0):
        """Play a sound by name. Will attempt to lazily load from assets/sounds.

        name may be a key previously loaded via load_sound or a filename (with extension).
        """
        snd = self.sounds.get(name)
        if snd is None:
            # Try to load
            snd = self.load_sound(name)
        if snd is None:
            # If name looks like a filename with extension, try that
            if os.path.splitext(name)[1]:
                snd = self.load_sound(name, filename=name)
        if snd is None:
            return None

        try:
            ch = snd.play(loops=0, maxtime=maxtime, fade_ms=fade_ms)
            if ch:
                ch.set_volume(volume * self.sfx_volume * self.master_volume)
            return ch
        except Exception:
            return None

    def play_music(self, filename, loops=-1, start=0.0, fade_ms=0):
        """Play background music file from assets/music. filename may have extension or not."""
        # If full path passed, use it
        if os.path.isabs(filename) and os.path.isfile(filename):
            path = filename
        else:
            path = self._find_file(self.music_path, filename, self.DEFAULT_MUSIC_EXT)
        if not path:
            return False
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
            # pygame's music.play supports fade_ms for fade-in
            pygame.mixer.music.play(loops=loops, start=start, fade_ms=fade_ms)
            return True
        except Exception:
            return False

    def stop_music(self, fade_ms=0):
        try:
            if fade_ms:
                pygame.mixer.music.fadeout(fade_ms)
            else:
                pygame.mixer.music.stop()
        except Exception:
            pass

    def crossfade_music(self, filename, loops=-1, start=0.0, fade_ms=1000, delay=None):
        """Crossfade from the currently playing music to a new track.

        This will fade out the current music over fade_ms milliseconds, and then
        start the new track with a fade-in of fade_ms milliseconds. The operation
        is non-blocking: it uses a background thread to wait the appropriate time
        before loading and playing the new track.

        If `delay` is provided (in seconds), it overrides the computed wait time
        between fadeout and new-track start; otherwise the new track will start
        after `fade_ms/1000.0` seconds.
        """
        # Determine path for new music
        if os.path.isabs(filename) and os.path.isfile(filename):
            new_path = filename
        else:
            new_path = self._find_file(self.music_path, filename, self.DEFAULT_MUSIC_EXT)
        if not new_path:
            return False

        # Fade out current music gracefully
        try:
            pygame.mixer.music.fadeout(int(fade_ms))
        except Exception:
            pass

        # Start a background thread to wait and then start new music with fade-in
        def _delayed_start(path, loops, start, fade_ms, wait_s):
            try:
                time.sleep(wait_s)
                # Load and play new music with fade-in
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
                pygame.mixer.music.play(loops=loops, start=start, fade_ms=int(fade_ms))
            except Exception:
                pass

        wait_seconds = delay if delay is not None else (float(fade_ms) / 1000.0)
        t = threading.Thread(target=_delayed_start, args=(new_path, loops, start, fade_ms, wait_seconds), daemon=True)
        t.start()
        return True

    def set_master_volume(self, volume):
        self.master_volume = max(0.0, min(1.0, float(volume)))
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
        for snd in self.sounds.values():
            try:
                snd.set_volume(self.sfx_volume * self.master_volume)
            except Exception:
                pass

    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, float(volume)))
        for snd in self.sounds.values():
            try:
                snd.set_volume(self.sfx_volume * self.master_volume)
            except Exception:
                pass

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, float(volume)))
        try:
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
        except Exception:
            pass

    def mute(self):
        self.set_master_volume(0.0)

    def unmute(self):
        self.set_master_volume(1.0)

    def preload_folder(self, folder='sounds'):
        """Preload all sounds from assets/sounds into memory (useful for short SFX)."""
        directory = self.sfx_path if folder == 'sounds' else os.path.join(self.assets_path, folder)
        if not os.path.isdir(directory):
            return 0
        loaded = 0
        for fn in os.listdir(directory):
            name, ext = os.path.splitext(fn)
            if ext.lower() in self.DEFAULT_SFX_EXT:
                if name not in self.sounds:
                    if self.load_sound(name, filename=fn):
                        loaded += 1
        return loaded

    def _find_variant_dir(self, category):
        candidates = [
            os.path.join(self.sfx_path, category),
            os.path.join(self.assets_path, 'sounds', category),
        ]
        for c in candidates:
            if os.path.isdir(c):
                return c
        return None

    def play_variant(self, category, volume=1.0, loops=0, maxtime=0, fade_ms=0):
        dirpath = self._find_variant_dir(category)
        if not dirpath:
            return None
        files = [f for f in os.listdir(dirpath) if os.path.splitext(f)[1].lower() in self.DEFAULT_SFX_EXT]
        if not files:
            return None
        fname = random.choice(files)
        full = os.path.join(dirpath, fname)
        snd = self.variant_sounds.get(full)
        if snd is None:
            try:
                snd = pygame.mixer.Sound(full)
                self.variant_sounds[full] = snd
            except Exception:
                return None
        try:
            snd.set_volume(volume * self.sfx_volume * self.master_volume)
            ch = snd.play(loops=loops, maxtime=maxtime, fade_ms=fade_ms)
            return ch
        except Exception:
            return None
