import os
import threading
import time
import random
import pygame
try:
    import numpy as np
except Exception:
    np = None

class AudioManager:

    DEFAULT_SFX_EXT = ('.wav', '.ogg', '.mp3')
    DEFAULT_MUSIC_EXT = ('.ogg', '.mp3', '.wav')

    def __init__(self, assets_path=None, num_channels=16):

        if assets_path is None:
            base = os.path.dirname(__file__)
            assets_path = os.path.abspath(os.path.join(base, '..', '..', 'assets'))
        self.assets_path = assets_path
        self.sfx_path = os.path.join(self.assets_path, 'sounds')
        self.music_path = os.path.join(self.assets_path, 'music')

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:

            pass

        self.sounds = {}  
        self.channels = {}  
        self.variant_sounds = {}
        self._menu_ramp_thread = None
        self._battle_thread = None
        self._battle_stop_event = None
        self._battle_channels = []
        self._battle_base_target = None
        self._battle_channel_fraction = {}
        self._processed_cache = {}
        self._processing = {}

        try:
            pygame.mixer.set_num_channels(max(8, int(num_channels)))
        except Exception:
            pass

        self.master_volume = 1.0
        self.sfx_volume = 0.2
        self.music_volume = 0.2

    def _find_file(self, directory, name, exts):

        candidate = os.path.join(directory, name)
        if os.path.isfile(candidate):
            return candidate

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

            snd = self.load_sound(name)
        if snd is None:

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

        if os.path.isabs(filename) and os.path.isfile(filename):
            path = filename
        else:
            path = self._find_file(self.music_path, filename, self.DEFAULT_MUSIC_EXT)
        if not path:
            return False
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)

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

        if os.path.isabs(filename) and os.path.isfile(filename):
            new_path = filename
        else:
            new_path = self._find_file(self.music_path, filename, self.DEFAULT_MUSIC_EXT)
        if not new_path:
            return False

        try:
            pygame.mixer.music.fadeout(int(fade_ms))
        except Exception:
            pass

        def _delayed_start(path, loops, start, fade_ms, wait_s):
            try:
                time.sleep(wait_s)

                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
                pygame.mixer.music.play(loops=loops, start=start, fade_ms=int(fade_ms))
            except Exception:
                pass

        wait_seconds = delay if delay is not None else (float(fade_ms) / 1000.0)
        t = threading.Thread(target=_delayed_start, args=(new_path, loops, start, fade_ms, wait_seconds), daemon=True)
        t.start()
        return True

    def play_menu_music(self, filename='menumusic', target_volume=1.0, ramp_ms=5000, fade_ms=800):
        path = None
        if os.path.isabs(filename) and os.path.isfile(filename):
            path = filename
        else:
            path = self._find_file(self.music_path, filename, self.DEFAULT_MUSIC_EXT)
        if not path:
            return False
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.0)
            pygame.mixer.music.play(loops=-1, fade_ms=fade_ms)
        except Exception:
            return False
        def _ramp(target, ms):
            steps = max(1, int(ms/100))
            for i in range(1, steps+1):
                if not pygame.mixer.get_init():
                    break
                vol = (i/steps) * float(target)
                try:
                    pygame.mixer.music.set_volume(vol * self.music_volume * self.master_volume)
                except Exception:
                    pass
                time.sleep(ms/steps/1000.0)
        if self._menu_ramp_thread and self._menu_ramp_thread.is_alive():
            pass
        t = threading.Thread(target=_ramp, args=(target_volume, ramp_ms), daemon=True)
        self._menu_ramp_thread = t
        t.start()
        return True

    def _get_music_sound(self, name):
        if os.path.isabs(name) and os.path.isfile(name):
            return name
        return self._find_file(self.music_path, name, self.DEFAULT_MUSIC_EXT)

    def start_battle_music(self, names=('battlemusic1','battlemusic2'), channel_count=2, target_volume=1.0, crossfade_s=3.0):
        files = []
        for n in names:
            p = self._get_music_sound(n)
            if p:
                files.append(p)
        if not files:
            return False
        try:
            pygame.mixer.music.fadeout(800)
        except Exception:
            pass
        total_channels = pygame.mixer.get_num_channels()
        ch_indices = list(range(max(0, total_channels-2), total_channels))
        self._battle_channels = [pygame.mixer.Channel(i) for i in ch_indices]
        stop_event = threading.Event()
        self._battle_stop_event = stop_event
        self._battle_base_target = float(target_volume)
        self._battle_channel_fraction = {}
        def _runner(file_list, stop_evt):
            order = file_list[:]
            random.shuffle(order)
            idx = 0
            prev_ch = None
            while not stop_evt.is_set():
                path = order[idx % len(order)]
                try:
                    snd = pygame.mixer.Sound(path)
                except Exception:
                    return
                ch = self._battle_channels[idx % len(self._battle_channels)]
                ch.set_volume(0.0)
                self._battle_channel_fraction[ch] = 0.0
                ch.play(snd)
                length = snd.get_length()
                start_time = time.time()
                fade_start = max(0.0, length - float(crossfade_s))
                ch.set_volume(0.0)
                ramp_steps = max(1, int(float(crossfade_s) / 0.1))
                for step in range(ramp_steps):
                    if stop_evt.is_set():
                        break
                    frac = ((step+1)/ramp_steps)
                    self._battle_channel_fraction[ch] = frac
                    vol = frac * float(target_volume) * self.music_volume * self.master_volume
                    try:
                        ch.set_volume(vol)
                    except Exception:
                        pass
                    time.sleep(float(crossfade_s)/ramp_steps)
                wait = max(0.0, length - float(crossfade_s))
                elapsed = time.time() - start_time
                remaining = wait - elapsed
                while remaining > 0 and not stop_evt.is_set():
                    time.sleep(min(0.5, remaining))
                    elapsed = time.time() - start_time
                    remaining = wait - elapsed
                if prev_ch and prev_ch != ch:
                    try:
                        prev_ch.fadeout(int(float(crossfade_s)*1000))
                    except Exception:
                        pass
                prev_ch = ch
                idx += 1
            for c in self._battle_channels:
                try:
                    c.fadeout(500)
                except Exception:
                    pass
        t = threading.Thread(target=_runner, args=(files, stop_event), daemon=True)
        self._battle_thread = t
        t.start()
        return True

    def stop_battle_music(self):
        if self._battle_stop_event:
            try:
                self._battle_stop_event.set()
            except Exception:
                pass
        self._battle_stop_event = None
        self._battle_thread = None

    def set_master_volume(self, volume):
        self.master_volume = max(0.0, min(1.0, float(volume)))
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
        for snd in self.sounds.values():
            try:
                snd.set_volume(self.sfx_volume * self.master_volume)
            except Exception:
                pass
        if self._battle_base_target and self._battle_channels:
            for ch in self._battle_channels:
                try:
                    frac = self._battle_channel_fraction.get(ch, 1.0)
                    ch.set_volume(frac * self._battle_base_target * self.music_volume * self.master_volume)
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
        if self._battle_base_target and self._battle_channels:
            for ch in self._battle_channels:
                try:
                    frac = self._battle_channel_fraction.get(ch, 1.0)
                    ch.set_volume(frac * self._battle_base_target * self.music_volume * self.master_volume)
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
            os.path.join(self.assets_path, 'aounds', category),
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

    def play_sound_effect(self, name, pitch=1.0, bitcrush=1, distortion=0.0, volume=1.0, layers=None, async_process=True, cache=True):
        if np is None:
            return self.play_variant(name) if os.path.isdir(os.path.join(self.assets_path, 'aounds', name)) or os.path.isdir(os.path.join(self.sfx_path, name)) else self.play_sound(name, volume=volume)
        try:
            path = self._find_file(self.sfx_path, name, self.DEFAULT_SFX_EXT)
            if not path:
                dirp = self._find_variant_dir(name)
                if dirp:
                    files = [os.path.join(dirp, f) for f in os.listdir(dirp) if os.path.splitext(f)[1].lower() in self.DEFAULT_SFX_EXT]
                    if not files:
                        return None
                    path = random.choice(files)
            if not path:
                return None

            if layers is None:
                layers = [
                    {'pitch': pitch, 'bitcrush': bitcrush, 'distortion': distortion, 'gain': 1.0},
                    {'pitch': pitch * 1.12, 'bitcrush': max(1, bitcrush + 1), 'distortion': max(0.0, distortion * 0.6), 'gain': 0.45},
                ]

            key = (path, tuple((int(round(l.get('pitch',1.0)*100)), int(l.get('bitcrush',1)), int(round(l.get('distortion',0.0)*100)), int(round(l.get('gain',1.0)*100))) for l in layers))
            if cache and key in self._processed_cache:
                snd = self._processed_cache[key]
                try:
                    snd.set_volume(volume * self.sfx_volume * self.master_volume)
                    ch = snd.play()
                    return ch
                except Exception:
                    pass

            if async_process:
                if cache and key in self._processing:
                    return self.play_sound(name, volume=volume*0.5)
                def _bg():
                    try:
                        self._processing[key] = True
                        snd = self._process_and_make_sound(path, layers)
                        if snd is not None and cache:
                            self._processed_cache[key] = snd
                        if snd is not None:
                            try:
                                snd.set_volume(volume * self.sfx_volume * self.master_volume)
                                snd.play()
                            except Exception:
                                pass
                    finally:
                        try:
                            del self._processing[key]
                        except Exception:
                            pass
                t = threading.Thread(target=_bg, daemon=True)
                t.start()
                return self.play_sound(name, volume=volume*0.55)
            else:
                snd = self._process_and_make_sound(path, layers)
                if snd is None:
                    return self.play_sound(name, volume=volume)
                if cache:
                    self._processed_cache[key] = snd
                try:
                    snd.set_volume(volume * self.sfx_volume * self.master_volume)
                    return snd.play()
                except Exception:
                    return None
        except Exception:
            return None

    def _process_and_make_sound(self, path, layers):
        try:
            base = pygame.mixer.Sound(path)
            arr = pygame.sndarray.array(base)
            if arr.dtype != np.int16:
                arr = arr.astype(np.int16)
            if arr.ndim == 1:
                arr = arr[:, None]
            maxv = float(2 ** (16 - 1) - 1)
            fbase = arr.astype(np.float32) / maxv
            mix = np.zeros_like(fbase)
            for layer in layers:
                p = float(layer.get('pitch', 1.0))
                bc = int(layer.get('bitcrush', 1))
                d = float(layer.get('distortion', 0.0))
                g = float(layer.get('gain', 1.0))

                in_len = fbase.shape[0]
                out_len = max(1, int(in_len / p))
                old_idx = np.linspace(0, in_len - 1, num=in_len)
                new_idx = np.linspace(0, in_len - 1, num=out_len)
                new_f = np.zeros((out_len, fbase.shape[1]), dtype=np.float32)
                for ch in range(fbase.shape[1]):
                    new_f[:, ch] = np.interp(new_idx, old_idx, fbase[:, ch])

                if bc > 1:
                    crushed = new_f[::bc, :]
                    repeats = int(np.ceil(new_f.shape[0] / crushed.shape[0]))
                    new_f = np.repeat(crushed, repeats, axis=0)[:new_f.shape[0], :]

                if d > 0.0:
                    gain = 1.0 + d * 15.0
                    new_f = np.tanh(new_f * gain)

                if new_f.shape[0] != mix.shape[0]:
                    if new_f.shape[0] < mix.shape[0]:
                        new_f = np.pad(new_f, ((0, mix.shape[0]-new_f.shape[0]), (0,0)), mode='constant')
                    else:
                        new_f = new_f[:mix.shape[0], :]

                mix += new_f * float(g)

            peak = np.max(np.abs(mix))
            if peak > 1e-5:
                mix = mix / max(1.0, peak)

            out = (mix * maxv).clip(-maxv, maxv-1).astype(np.int16)
            if out.shape[1] == 1:
                out = out.flatten()
            snd = pygame.sndarray.make_sound(out)
            return snd
        except Exception:
            return None