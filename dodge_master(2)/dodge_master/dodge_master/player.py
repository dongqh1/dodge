# ==========================================
# 文件名: player.py
# 职责: 玩家类实现，包含惯性物理系统、冲刺技能状态机与渲染
# 负责人: 成员 B (主程)
# ==========================================
import pygame
from config import *
from utils import normalize_vector, clamp

class Player:
    def __init__(self, sound_mgr=None):
        # 位置与物理向量
        self.pos = pygame.math.Vector2(100, SCREEN_HEIGHT / 2)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        
        # 状态属性
        self.radius = PLAYER_RADIUS
        self.lives = 3
        self.is_dead = False
        self.shield_active = False
        
        # 技能与无敌状态机计时器
        self.dash_timer = 0
        self.dash_cd_timer = 0
        self.invulnerable_timer = 0
        
        # 音效管理器引用
        self.sound_mgr = sound_mgr
        
        # 用于像素级碰撞的 Surface 和 Mask
        self._surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self._surface, COLORS["PLAYER"], (self.radius, self.radius), self.radius)
        self.mask = pygame.mask.from_surface(self._surface)

    def handle_input(self, keys):
        """处理输入并转换为加速度"""
        self.acc.x, self.acc.y = 0, 0
        
        # 冲刺期间不受按键控制，保持冲刺方向
        if self.dash_timer > 0:
            return

        # 获取 8 方向输入
        if keys[pygame.K_w] or keys[pygame.K_UP]: self.acc.y = -PLAYER_ACCEL
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.acc.y = PLAYER_ACCEL
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.acc.x = -PLAYER_ACCEL
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.acc.x = PLAYER_ACCEL

        # 触发冲刺 (Dash)
        if keys[pygame.K_SPACE] and self.dash_cd_timer == 0 and (self.acc.x != 0 or self.acc.y != 0):
            self.dash_timer = DASH_DURATION
            self.dash_cd_timer = DASH_COOLDOWN
            # 冲刺瞬间爆发极高速度
            norm_x, norm_y = normalize_vector(self.acc.x, self.acc.y)
            self.vel.x = norm_x * PLAYER_MAX_SPEED * DASH_MULTIPLIER
            self.vel.y = norm_y * PLAYER_MAX_SPEED * DASH_MULTIPLIER
            if self.sound_mgr:
                self.sound_mgr.play("dash")

    def update(self):
        """物理迭代更新"""
        if self.is_dead: return

        # 1. 更新计时器
        if self.dash_timer > 0: self.dash_timer -= 1
        if self.dash_cd_timer > 0: self.dash_cd_timer -= 1
        if self.invulnerable_timer > 0: self.invulnerable_timer -= 1

        # 2. 运动学解算 (常规移动态)
        if self.dash_timer == 0:
            # 向量归一化保证斜向加速度不越界
            if self.acc.length() > 0:
                self.acc.scale_to_length(PLAYER_ACCEL)
            
            # v = v + a
            self.vel += self.acc
            
            # 应用摩擦阻力 (模拟空气阻力/地面摩擦)
            self.vel *= PLAYER_FRICTION
            
            # 限制最大常规速度
            if self.vel.length() > PLAYER_MAX_SPEED:
                self.vel.scale_to_length(PLAYER_MAX_SPEED)

        # 3. 位置更新 s = s + v
        self.pos += self.vel

        # 4. 屏幕边界限制 (坠落/撞墙判定在其他模块，此处仅限制坐标不出界)
        self.pos.x = clamp(self.pos.x, self.radius, SCREEN_WIDTH - self.radius)
        self.pos.y = clamp(self.pos.y, self.radius, SCREEN_HEIGHT - self.radius)

    def hit(self):
        """处理受击逻辑，返回 'real_hit', 'shield_break', 或 None"""
        if self.invulnerable_timer > 0 or self.is_dead:
            return None # 无敌或死亡状态，不受伤害

        if self.shield_active:
            self.shield_active = False
            self.invulnerable_timer = INVINCIBLE_FRAMES // 2 # 护盾破碎后给予短暂无敌
            return "shield_break"

        self.lives -= 1
        if self.lives <= 0:
            self.is_dead = True
        else:
            self.invulnerable_timer = INVINCIBLE_FRAMES
            # 受击后施加微小反弹力(可选)
            self.vel.x = -10
        return "real_hit"

    def activate_shield(self):
        """激活护盾"""
        self.shield_active = True

    def add_life(self):
        """增加一点生命值，但不超过上限"""
        self.lives = min(self.lives + 1, 3)

    def draw(self, surface):
        if self.is_dead: return
        
        # 无敌状态闪烁效果 (位运算控制闪烁频率)
        if self.invulnerable_timer > 0:
            if (self.invulnerable_timer // 5) % 2 == 0:
                return # 跳过当前帧绘制，形成闪烁

        # 冲刺时的视觉形变 (可选：拖影效果交由 particle.py 处理)
        color = COLORS["PLAYER"]
        if self.dash_timer > 0:
            color = (0, 200, 255) # 冲刺时颜色变浅

        pygame.draw.circle(surface, color, (int(self.pos.x), int(self.pos.y)), self.radius)

        # 绘制护盾
        if self.shield_active:
            shield_surface = pygame.Surface((self.radius*2.5, self.radius*2.5), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (255, 215, 0, 150), (self.radius*1.25, self.radius*1.25), self.radius*1.25)
            surface.blit(shield_surface, (self.pos.x - self.radius*1.25, self.pos.y - self.radius*1.25))

    @property
    def rect(self):
        """用于碰撞检测的矩形属性"""
        return pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius*2, self.radius*2)