
# ==========================================

# 文件名: powerups.py

# 职责: 定义所有可拾取的道具/技能及其效果

# 负责人: 成员 B (新功能)

# ==========================================

import pygame

import random

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS



class PowerUp(pygame.sprite.Sprite):
    """道具基类"""
    def __init__(self, center, powerup_type):
        super().__init__()
        self.type = powerup_type
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self.vel = pygame.math.Vector2(0, 2) # 道具向下移动的速度

    def update(self):
        self.rect.move_ip(self.vel)
        # 如果道具移出屏幕底部，则自毁
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()



class Shield(PowerUp):

    """护盾道具"""

    def __init__(self, center):

        super().__init__(center, 'shield')

        pygame.draw.circle(self.image, COLORS["PLAYER"], (10, 10), 10)

        pygame.draw.circle(self.image, COLORS["TEXT"], (10, 10), 10, 2)



    def activate(self, player):
        player.activate_shield()

class HealthPack(PowerUp):
    """血包道具"""
    def __init__(self, center):
        super().__init__(center, 'health')
        # 绘制红色十字
        self.image.fill(COLORS["SPIKE"]) # 用危险红色作为背景
        pygame.draw.rect(self.image, COLORS["TEXT"], (8, 3, 4, 14)) # 垂直条
        pygame.draw.rect(self.image, COLORS["TEXT"], (3, 8, 14, 4)) # 水平条

    def activate(self, player):
        player.add_life()

