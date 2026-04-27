# ==========================================
# 文件名: sound_manager.py
# 职责: 集中管理 BGM 与游戏音效
# 负责人: 成员 D (视听与存档)
# ==========================================
import pygame

class SoundManager:
    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        silent_buffer = bytearray([128] * 4410)
        self.dummy_sound = pygame.mixer.Sound(buffer=silent_buffer)

        self.sounds = {
            "hit": pygame.mixer.Sound('sound/hit.mp3'),
            "dash": pygame.mixer.Sound('sound/dash.wav'),
            "warning": self.dummy_sound,
            "coin": pygame.mixer.Sound('sound/coin.wav'),
            "gameover": pygame.mixer.Sound('sound/gameover.wav')
        }

    def play(self, sound_name, start=0):
        """播放短促音效"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

    def play_bgm(self, filepath=None):
        """播放背景音乐 (如果提供路径)"""
        if filepath:
            try:
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
                print(f"背景音乐加载成功: {filepath}")
            except Exception as e:
                print(f"背景音乐加载失败: {e}")