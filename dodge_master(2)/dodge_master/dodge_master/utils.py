# ==========================================
# 文件名: utils.py
# 职责: 提供数学运算、向量归一化、图形面生成等复用工具函数
# 负责人: 成员 A (组长)
# ==========================================
import pygame
import math

def get_distance(p1, p2):
    """计算两点之间的欧几里得距离"""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def normalize_vector(dx, dy):
    """向量归一化，用于保证斜向移动与直线移动速度一致"""
    dist = math.hypot(dx, dy)
    if dist == 0:
        return 0, 0
    return dx / dist, dy / dist

def create_transparent_surface(width, height, color, alpha):
    """
    生成一个带有透明度的 Surface。
    由于 Pygame 原生不支持直接绘制带有 alpha 的图元到主屏幕，
    需先绘制到独立的 Surface 上再 blit。
    """
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    surf.fill((*color[:3], alpha))
    return surf

def clamp(value, min_val, max_val):
    """钳制数值在指定范围内"""
    return max(min_val, min(value, max_val))