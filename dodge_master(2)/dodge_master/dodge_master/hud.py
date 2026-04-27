# ==========================================
# 文件名: hud.py
# 职责: 游戏内 UI 界面绘制（血条、冷却、分数）
# 负责人: 成员 D (视听与存档)
# ==========================================
import pygame
from config import *

class HUD:
    def __init__(self):
        # 尝试加载中文字体，失败则使用系统默认
        try:
            self.font_normal = pygame.font.SysFont(['simhei', 'microsoftyahei'], 24)
            self.font_large = pygame.font.SysFont(['simhei', 'microsoftyahei'], 36)
        except:
            self.font_normal = pygame.font.Font(None, 28)
            self.font_large = pygame.font.Font(None, 40)

    def draw(self, surface, player, level_mgr, score):
        # 1. 绘制顶部信息条半透明背景
        ui_bg = pygame.Surface((SCREEN_WIDTH, 40), pygame.SRCALPHA)
        ui_bg.fill(COLORS["UI_BG"])
        surface.blit(ui_bg, (0, 0))

        # 2. 绘制生命值 (红心/方块)
        life_text = self.font_normal.render("生命: ", True, COLORS["TEXT"])
        surface.blit(life_text, (20, 10))
        # for i in range(player.lives):
        #     pygame.draw.rect(surface, COLORS["SPIKE"], (80 + i * 25, 12, 15, 15))
        for i in range(player.lives):
            self.draw_heart(surface, 85 + i * 28, 9, 22)
        # 3. 绘制分数与时间
        score_text = self.font_normal.render(f"得分: {score}", True, COLORS["GOLD"])
        time_text = self.font_normal.render(f"时间: {level_mgr.level_timer // 60}s", True, COLORS["TEXT"])
        surface.blit(score_text, (300, 10))
        surface.blit(time_text, (450, 10))

        # 4. 绘制关卡与进度
        level_text = self.font_normal.render(f"关卡: {level_mgr.current_level}", True, COLORS["TEXT"])
        surface.blit(level_text, (SCREEN_WIDTH - 150, 10))
        # 进度条
        progress = level_mgr.get_progress_ratio()
        pygame.draw.rect(surface, (100, 100, 100), (SCREEN_WIDTH - 150, 35, 130, 4))
        pygame.draw.rect(surface, COLORS["PLAYER"], (SCREEN_WIDTH - 150, 35, int(130 * progress), 4))

        # 5. 绘制冲刺技能 CD 条 (跟随玩家或固定位置)
        cd_ratio = 1 - (player.dash_cd_timer / DASH_COOLDOWN)
        cd_color = COLORS["PLAYER"] if cd_ratio == 1.0 else (150, 150, 150)
        pygame.draw.rect(surface, (50, 50, 50), (20, 50, 100, 8))
        pygame.draw.rect(surface, cd_color, (20, 50, int(100 * cd_ratio), 8))
        if cd_ratio == 1.0:
            ready_text = self.font_normal.render("SPACE 冲刺就绪!", True, cd_color)
            surface.blit(ready_text, (20, 65))

    def draw_heart(self, surface, x, y, size=16):
        """
        绘制一个红心
        x, y 是红心左上角位置
        size 是红心大小
        """
        color = (220, 40, 60)

        # 左上圆
        pygame.draw.circle(
            surface,
            color,
            (x + size // 4, y + size // 3),
            size // 4
        )

        # 右上圆
        pygame.draw.circle(
            surface,
            color,
            (x + size * 3.2 // 4, y + size // 3),
            size // 4
        )

        # 下方三角形
        points = [
            (x, y + size // 3),
            (x + size, y + size // 3),
            (x + size // 2, y + size)
        ]

        pygame.draw.polygon(surface, color, points)