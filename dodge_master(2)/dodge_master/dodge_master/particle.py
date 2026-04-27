# ==========================================
# 文件名: particle.py
# 职责: 提供动态粒子特效，提升视觉打击感
# 负责人: 成员 D (视听与存档)
# ==========================================
import pygame
import random
from config import *

class Particle:
    def __init__(self, x, y, color, speed_x, speed_y, size, lifetime):
        self.x = x
        self.y = y
        self.color = list(color)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.size = size
        self.lifetime = lifetime
        self.max_life = lifetime

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.size *= 0.95 # 每帧逐渐缩小
        self.lifetime -= 1

    def draw(self, surface):
        if self.size > 0.5:
            # 透明度随生命周期衰减
            alpha = int(255 * (self.lifetime / self.max_life))
            s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color[:3], alpha), (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit_explosion(self, x, y, color):
        """生成爆炸破片粒子"""
        for _ in range(15):
            sx = random.uniform(-4, 4)
            sy = random.uniform(-4, 4)
            size = random.randint(3, 8)
            life = random.randint(20, 40)
            self.particles.append(Particle(x, y, color, sx, sy, size, life))

    def emit_trail(self, x, y, color):
        """生成冲刺尾迹粒子"""
        size = random.randint(5, 10)
        self.particles.append(Particle(x, y, color, 0, 0, size, 15))

    def update_and_draw(self, surface):
        """更新所有粒子并清理死亡粒子"""
        for p in self.particles[:]:
            p.update()
            p.draw(surface)
            if p.lifetime <= 0 or p.size < 0.5:
                self.particles.remove(p)