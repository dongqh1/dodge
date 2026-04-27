# ==========================================
# 文件名: collision.py
# 职责: 提供三层逐步精确的碰撞检测算法
# 负责人: 成员 B (主程)
# 参考: r/pygame 社区关于大批量精灵遮罩优化的讨论
# ==========================================
import pygame
import math
from utils import get_distance

def check_aabb(rect1, rect2):
    """
    第一层：AABB (Axis-Aligned Bounding Box) 矩形初筛
    算法最快，剔除 90% 不可能相交的物体。
    """
    return rect1.colliderect(rect2)

def check_circle(pos1, r1, pos2, r2):
    """
    第二层：包围盒中心点圆形距离判定
    适用于球形角色与类球形障碍物，计算复杂度居中。
    """
    dist = get_distance(pos1, pos2)
    return dist < (r1 + r2)

def check_mask(mask1, rect1_topleft, mask2, rect2_topleft):
    """
    第三层：像素遮罩级判定 (Pixel Perfect)
    针对不规则图形（如锐角地刺）。仅在 AABB 碰触后执行，极大节省性能。
    原理：计算两个 Mask 的重叠偏移量。
    """
    offset_x = int(rect2_topleft[0] - rect1_topleft[0])
    offset_y = int(rect2_topleft[1] - rect1_topleft[1])
    # overlap 返回第一个碰撞的像素坐标，若无碰撞返回 None
    return mask1.overlap(mask2, (offset_x, offset_y)) is not None

def advanced_collision(player, obstacle):
    """
    主调接口：对玩家和障碍物执行分层碰撞检测机制
    """
    p_rect = player.rect
    o_rect = obstacle.get_rect()

    # 第一关：AABB 初筛
    if not check_aabb(p_rect, o_rect):
        return False
        
    # 如果障碍物是圆形（例如某些石块），走第二关圆形检测
    if obstacle.shape_type == "circle":
        return check_circle(player.pos, player.radius, obstacle.pos, obstacle.radius)
        
    # 如果障碍物是不规则形状（如地刺），走第三关精确遮罩检测
    elif obstacle.shape_type == "mask":
        # 获取障碍物的 mask (障碍物类需自行生成并缓存 mask)
        o_mask = obstacle.get_mask()
        return check_mask(player.mask, p_rect.topleft, o_mask, o_rect.topleft)
        
    # 如果障碍物就是标准矩形（如陷阱区域）
    elif obstacle.shape_type == "rect":
        return True # AABB 已经通过了，直接返回 True

    return False