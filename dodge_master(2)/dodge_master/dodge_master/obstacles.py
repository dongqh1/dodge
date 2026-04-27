# ==========================================
# 文件名: obstacles.py
# 职责: 障碍物基类与三种派生类（地刺、移动石块、陷阱）
# 负责人: 成员 C (玩法)
# ==========================================
import pygame
import random
import math
from config import *
from utils import create_transparent_surface, normalize_vector

class Obstacle:
    """障碍物基类"""
    def __init__(self):
        self.is_dead = False    # 生命周期结束标志（用于对象池回收）
        self.passed = False     # 是否已被计分
        self.shape_type = "rect" # 默认碰撞类型为矩形

    def update(self):
        pass

    def draw(self, surface):
        pass

    def get_rect(self):
        return pygame.Rect(0, 0, 0, 0)


class Spike(Obstacle):
    """
    【机制一：地刺】
    特性：固定位置，从地面弹出。带预警动画和高精度像素碰撞。
    可从四面八方出现，发射方向随等级提升。
    """
    def __init__(self, direction="up", level=1):
        super().__init__()
        self.width = 40
        self.height = 40
        self.direction = direction  # "up", "down", "left", "right"
        self.level = level
        
        # 根据方向确定位置
        if direction == "up":
            self.pos = pygame.math.Vector2(random.randint(50, SCREEN_WIDTH - 50), SCREEN_HEIGHT - self.height)
        elif direction == "down":
            self.pos = pygame.math.Vector2(random.randint(50, SCREEN_WIDTH - 50), 0)
        elif direction == "left":
            self.pos = pygame.math.Vector2(SCREEN_WIDTH - self.height, random.randint(50, SCREEN_HEIGHT - 50))
        elif direction == "right":
            self.pos = pygame.math.Vector2(0, random.randint(50, SCREEN_HEIGHT - 50))
        
        self.state = "warning" # 状态机：warning -> active -> flying -> dead
        self.timer = 60        # 预警时间 1秒 (60帧)
        
        # 发射相关属性
        self.can_fly = False   # 是否可以发射
        self.is_flying = False # 是否正在飞行
        self.fly_speed = 8     # 飞行速度
        
        # 根据等级决定是否发射：等级越高，发射概率越大
        # 1级: 0%, 2级: 10%, 3级: 20%, ... 最高 80%
        fly_prob = min((level - 1) * 0.1, 0.8)
        if level > 1 and random.random() < fly_prob:
            self.can_fly = True
        
        self.shape_type = "mask" # 启用第三层像素级碰撞
        
        # 预先生成致命状态的遮罩 (Mask)，优化性能
        self.active_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # 根据方向画三角形
        if direction == "up":
            pygame.draw.polygon(self.active_surface, COLORS["SPIKE"], 
                                [(self.width//2, 0), (0, self.height), (self.width, self.height)])
        elif direction == "down":
            pygame.draw.polygon(self.active_surface, COLORS["SPIKE"], 
                                [(0, 0), (self.width, 0), (self.width//2, self.height)])
        elif direction == "left":
            pygame.draw.polygon(self.active_surface, COLORS["SPIKE"], 
                                [(self.width, 0), (self.width, self.height), (0, self.height//2)])
        elif direction == "right":
            pygame.draw.polygon(self.active_surface, COLORS["SPIKE"], 
                                [(0, 0), (self.width, self.height//2), (0, self.height)])
        self.mask = pygame.mask.from_surface(self.active_surface)

    def update(self):
        self.timer -= 1
        if self.state == "warning" and self.timer <= 0:
            self.state = "active"
            self.timer = 60 # 致命状态持续 1 秒
            # 如果可以发射，预警结束后开始飞行
            if self.can_fly:
                self.state = "flying"
                self.is_flying = True
        elif self.state == "active" and self.timer <= 0:
            self.is_dead = True # 标记死亡，等待主循环回收
        elif self.state == "flying":
            # 飞行状态：沿发射方向移动
            if self.direction == "up":
                self.pos.y -= self.fly_speed
            elif self.direction == "down":
                self.pos.y += self.fly_speed
            elif self.direction == "left":
                self.pos.x -= self.fly_speed
            elif self.direction == "right":
                self.pos.x += self.fly_speed
            
            # 飞出屏幕后标记死亡
            if (self.pos.x < -50 or self.pos.x > SCREEN_WIDTH + 50 or
                self.pos.y < -50 or self.pos.y > SCREEN_HEIGHT + 50):
                self.is_dead = True

    def draw(self, surface):
        if self.state == "warning":
            # 预警状态：根据方向显示红光闪烁
            if (self.timer // 5) % 2 == 0:
                if self.direction == "up":
                    pygame.draw.rect(surface, COLORS["TRAP_WARNING"], 
                                     (self.pos.x, self.pos.y + 30, self.width, 10))
                elif self.direction == "down":
                    pygame.draw.rect(surface, COLORS["TRAP_WARNING"], 
                                     (self.pos.x, self.pos.y, self.width, 10))
                elif self.direction == "left":
                    pygame.draw.rect(surface, COLORS["TRAP_WARNING"], 
                                     (self.pos.x + 30, self.pos.y, 10, self.height))
                elif self.direction == "right":
                    pygame.draw.rect(surface, COLORS["TRAP_WARNING"], 
                                     (self.pos.x, self.pos.y, 10, self.height))
        elif self.state == "active":
            # 致命状态：绘制真实的三角形
            surface.blit(self.active_surface, self.pos)
        elif self.state == "flying":
            # 飞行状态：绘制三角形
            surface.blit(self.active_surface, self.pos)

    def get_rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)

    def get_mask(self):
        """为 collision.py 提供高精度判定掩码"""
        return self.mask

class Laser(Obstacle):
    """
    【机制四：激光】
    特性：横向或纵向全屏攻击，预警时间短，考验极限反应。
    """
    def __init__(self):
        super().__init__()
        self.orientation = random.choice(["horizontal", "vertical"])
        self.is_horizontal = (self.orientation == "horizontal")
        self.thickness = 20
        self.state = "warning"
        self.timer = 45 # 预警 0.75秒
        self.shape_type = "rect"

        if self.orientation == "horizontal":
            self.y = random.randint(self.thickness, SCREEN_HEIGHT - self.thickness)
            self.rect = pygame.Rect(0, self.y - self.thickness // 2, SCREEN_WIDTH, self.thickness)
        else: # vertical
            self.x = random.randint(self.thickness, SCREEN_WIDTH - self.thickness)
            self.rect = pygame.Rect(self.x - self.thickness // 2, 0, self.thickness, SCREEN_HEIGHT)

    def update(self):
        self.timer -= 1
        if self.state == "warning" and self.timer <= 0:
            self.state = "active"
            self.timer = 30 # 激光持续 0.5 秒
        elif self.state == "active" and self.timer <= 0:
            self.is_dead = True

    def draw(self, surface):
        if self.state == "warning":
            # 预警：在路径上绘制半透明的线
            if self.is_horizontal:
                pygame.draw.line(surface, COLORS["TRAP_WARNING"], (0, self.y), (SCREEN_WIDTH, self.y), 3)
            else:
                pygame.draw.line(surface, COLORS["TRAP_WARNING"], (self.x, 0), (self.x, SCREEN_HEIGHT), 3)
        elif self.state == "active":
            # 激活：绘制致命的激光束
            pygame.draw.rect(surface, COLORS["SPIKE"], self.rect)
            # 可以在中心加一条更亮的白线来增加视觉效果
            if self.is_horizontal:
                pygame.draw.line(surface, COLORS["TEXT"], (0, self.y), (SCREEN_WIDTH, self.y), 4)
            else:
                pygame.draw.line(surface, COLORS["TEXT"], (self.x, 0), (self.x, SCREEN_HEIGHT), 4)

    def get_rect(self):
        return self.rect
        
    def get_mask(self):
        """为 collision.py 提供高精度判定掩码"""
        return self.mask


class Boulder(Obstacle):
    """
    【机制二：移动石块】
    特性：从屏幕边缘出现，横向或纵向移动。10%概率变为追踪玩家的 AI 石块。
    """
    def __init__(self, speed_mult, is_tracking=False, player_ref=None):
        super().__init__()
        self.radius = random.randint(15, 30)
        self.shape_type = "circle" # 启用第二层圆形碰撞
        self.is_tracking = is_tracking
        self.player_ref = player_ref # 追踪需要知道玩家的位置
        self.lifetime = 480 if self.is_tracking else float('inf') # 追踪石块最多存在8秒
        
        self.speed = random.uniform(3.0, 6.0) * speed_mult
        # 随机决定生成在左侧、右侧、上方或下方
        spawn_edge = random.choice(["top", "bottom", "left", "right"])
        if spawn_edge == "left":
            self.pos = pygame.math.Vector2(-self.radius, random.randint(0, SCREEN_HEIGHT))
            self.vel = pygame.math.Vector2(self.speed, random.uniform(-1, 1))
        elif spawn_edge == "right":
            self.pos = pygame.math.Vector2(SCREEN_WIDTH + self.radius, random.randint(0, SCREEN_HEIGHT))
            self.vel = pygame.math.Vector2(-self.speed, random.uniform(-1, 1))
        elif spawn_edge == "top":
            self.pos = pygame.math.Vector2(random.randint(0, SCREEN_WIDTH), -self.radius)
            self.vel = pygame.math.Vector2(random.uniform(-1, 1), self.speed)
        else: # bottom
            self.pos = pygame.math.Vector2(random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + self.radius)
            self.vel = pygame.math.Vector2(random.uniform(-1, 1), -self.speed)

    def update(self):
        # 如果是追踪石块，会有一个生命周期
        if self.is_tracking:
            self.lifetime -= 1
            if self.lifetime <= 0:
                self.is_dead = True
                return

        # 如果是追踪石块，实时微调速度向量指向玩家
        if self.is_tracking and self.player_ref and not self.player_ref.is_dead:
            dx = self.player_ref.pos.x - self.pos.x
            dy = self.player_ref.pos.y - self.pos.y
            norm_x, norm_y = normalize_vector(dx, dy)
            # 引入追踪阻尼，使其缓慢转向而不是瞬间折返
            turn_speed = 0.25
            self.vel.x += norm_x * turn_speed
            self.vel.y += norm_y * turn_speed
            
            # 限制最高速度
            if self.vel.length() > self.speed:
                self.vel.scale_to_length(self.speed)

        self.pos += self.vel

        # 飞出屏幕较远距离后销毁
        if (self.pos.x < -100 or self.pos.x > SCREEN_WIDTH + 100 or 
            self.pos.y < -100 or self.pos.y > SCREEN_HEIGHT + 100):
            self.is_dead = True

    def draw(self, surface):
        color = COLORS["BOULDER_TRACK"] if self.is_tracking else COLORS["BOULDER"]
        pygame.draw.circle(surface, color, (int(self.pos.x), int(self.pos.y)), self.radius)

    def get_rect(self):
        return pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius*2, self.radius*2)


class TrapZone(Obstacle):
    """
    【机制三：陷阱跑道】
    特性：大面积半透明危险区域，给予玩家较长的反应时间，一旦激活直接限制一片区域。
    """
    def __init__(self):
        super().__init__()
        self.width = random.randint(100, 250)
        self.height = random.randint(100, 250)
        self.pos = pygame.math.Vector2(random.randint(50, SCREEN_WIDTH - self.width - 50), 
                                       random.randint(50, SCREEN_HEIGHT - self.height - 50))
        
        self.timer = 90 # 预警 1.5 秒
        self.state = "warning"
        self.shape_type = "rect" # 使用基础 AABB 检测
        
        # 预生成带有 Alpha 通道的图形面
        self.warn_surf = create_transparent_surface(self.width, self.height, COLORS["TRAP_WARNING"], 100)
        self.active_surf = create_transparent_surface(self.width, self.height, COLORS["TRAP_ACTIVE"], 180)

    def update(self):
        self.timer -= 1
        if self.state == "warning" and self.timer <= 0:
            self.state = "active"
            self.timer = 180 # 激活持续 3 秒
        elif self.state == "active" and self.timer <= 0:
            self.is_dead = True

    def draw(self, surface):
        if self.state == "warning":
            # 边框闪烁
            if (self.timer // 10) % 2 == 0:
                pygame.draw.rect(surface, COLORS["TRAP_WARNING"][:3], self.get_rect(), 3)
            surface.blit(self.warn_surf, self.pos)
        elif self.state == "active":
            surface.blit(self.active_surf, self.pos)
            # 画一个交叉的警告线
            pygame.draw.line(surface, (255, 0, 0), self.pos, (self.pos.x + self.width, self.pos.y + self.height), 2)

    def get_rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)