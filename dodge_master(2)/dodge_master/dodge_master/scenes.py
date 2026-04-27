# ==========================================
# 文件名: scenes.py
# 职责: 场景图层管理 (主菜单 -> 游戏中 -> 暂停 -> 结算)
# 负责人: 成员 A (组长)
# ==========================================
import pygame
import random
from config import *
from player import Player
from level_manager import LevelManager
from hud import HUD
from particle import ParticleSystem
from collision import advanced_collision
from powerups import Shield, PowerUp, HealthPack

def get_font(size):
    try:
        # 依次尝试加载：微软雅黑、黑体、宋体
        return pygame.font.SysFont(['microsoftyahei', 'simhei', 'stsong'], size)
    except:
        return pygame.font.Font(None, size)

class Scene:
    """场景基类"""
    def handle_events(self, events): pass
    def update(self): pass
    def draw(self, surface): pass

class SceneManager:
    """场景调度器"""
    def __init__(self, storage, sound_mgr):
        self.storage = storage
        self.sound_mgr = sound_mgr
        self.current_scene = StartScene(self)
        self.font = get_font(48)

    def switch_scene(self, new_scene):
        self.current_scene = new_scene

    def run_frame(self, screen, events):
        self.current_scene.handle_events(events)
        self.current_scene.update()
        self.current_scene.draw(screen)

class StartScene(Scene):
    def __init__(self, manager):
        self.manager = manager
        self.font_title = get_font(60)
        self.font_info = get_font(20)

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                self.manager.switch_scene(GameScene(self.manager))

    def draw(self, surface):
        surface.fill(COLORS["BG"])
        title = self.font_title.render(TITLE, True, COLORS["PLAYER"])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        
        high_score = self.font_info.render(f"历史最高分: {self.manager.storage.data['highscore']}", True, COLORS["GOLD"])
        surface.blit(high_score, (SCREEN_WIDTH//2 - high_score.get_width()//2, 250))



        
        tips = self.font_info.render("按 [空格键] 开始游戏", True, COLORS["TEXT"])
        surface.blit(tips, (SCREEN_WIDTH//2 - tips.get_width()//2, 400))
        
        ctrl = self.font_info.render("操作: WASD 移动 | SPACE 冲刺 | P 暂停", True, (150, 150, 150))
        surface.blit(ctrl, (SCREEN_WIDTH//2 - ctrl.get_width()//2, 480))

class GameScene(Scene):
    """最庞大的核心逻辑场景"""
    def __init__(self, manager):
        self.manager = manager
        self.player = Player(self.manager.sound_mgr)
        self.level_mgr = LevelManager()
        self.hud = HUD()
        self.particles = ParticleSystem()
        self.obstacles = []
        self.powerups = pygame.sprite.Group()
        self.powerup_spawn_timer = 0
        self.powerup_spawn_interval = 15 * 60 # 15秒
        self.score = 0
        self.survival_frames = 0
        self.font = get_font(72)
        self.manager.sound_mgr.play_bgm('sound/bgm.mp3')

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_p:
                    # 切换到暂停场景，并把当前自己作为背景传递过去
                    self.manager.switch_scene(PauseScene(self.manager, self))


    def update(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update()
        self.survival_frames += 1

        # 冲刺拖尾特效
        if self.player.dash_timer > 0:
            self.particles.emit_trail(self.player.pos.x, self.player.pos.y, COLORS["PLAYER"])

        # 生成障碍物
        self.level_mgr.update()
        if self.level_mgr.should_spawn_obstacle():
            obs = self.level_mgr.generate_obstacle(self.player)
            if obs: self.obstacles.append(obs)

        # 遍历障碍物并检测碰撞
        for obs in self.obstacles[:]:
            obs.update()
            
            # 安全越过计分机制
            if getattr(obs, 'is_dead', False) and not obs.passed:
                self.score += 10
                obs.passed = True
                self.obstacles.remove(obs)
                continue

            # 碰撞判断
            is_lethal = getattr(obs, 'state', 'active') in ('active', 'flying')
            if is_lethal and advanced_collision(self.player, obs):
                hit_result = self.player.hit()
                if hit_result == "real_hit": # 真实受击
                    self.manager.sound_mgr.play("hit")
                    self.particles.emit_explosion(self.player.pos.x, self.player.pos.y, COLORS["SPIKE"])
                elif hit_result == "shield_break": # 护盾破碎
                    self.manager.sound_mgr.play("hit") # 可以换成一个护盾破碎音效
                    self.particles.emit_explosion(self.player.pos.x, self.player.pos.y, COLORS["PLAYER"])
                    
            if self.player.is_dead:
                self.manager.sound_mgr.play("gameover")
                self.manager.switch_scene(GameOverScene(self.manager, self.score, self.survival_frames//60))
                return # 死亡立刻中断当前帧更新

        # 更新并生成道具
        self.powerup_spawn_timer += 1
        if self.powerup_spawn_timer >= self.powerup_spawn_interval:
            self.powerup_spawn_timer = 0
            # 从屏幕顶部随机位置生成
            pos = (random.randint(50, SCREEN_WIDTH - 50), -30)
            powerup_type = random.choice([Shield, HealthPack])
            self.powerups.add(powerup_type(pos))
        
        self.powerups.update()

        # 检测玩家与道具的碰撞
        collided_powerups = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in collided_powerups:
            powerup.activate(self.player)
            self.manager.sound_mgr.play("coin")

    def draw(self, surface):
        surface.fill(COLORS["BG"])
        
        for obs in self.obstacles: obs.draw(surface)
        self.powerups.draw(surface)
        self.particles.update_and_draw(surface)
        self.player.draw(surface)
        self.hud.draw(surface, self.player, self.level_mgr, self.score)

        # 关卡切换大字
        if self.level_mgr.level_up_flag:
            lvl_text = self.font.render(f"LEVEL {self.level_mgr.current_level}", True, COLORS["GOLD"])
            surface.blit(lvl_text, (SCREEN_WIDTH//2 - lvl_text.get_width()//2, SCREEN_HEIGHT//3))

class PauseScene(Scene):
    def __init__(self, manager, game_scene):
        self.manager = manager
        self.game_scene = game_scene
        self.font = get_font(72)
        # 生成半透明遮罩
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 150))

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_p:
                self.manager.switch_scene(self.game_scene) # 恢复游戏

    def draw(self, surface):
        self.game_scene.draw(surface) # 保持底层画面
        surface.blit(self.overlay, (0, 0))
        text = self.font.render("PAUSED", True, COLORS["TEXT"])
        surface.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2))

class GameOverScene(Scene):
    def __init__(self, manager, score, time):
        self.manager = manager
        self.font = get_font(48)
        # 存档数据结算
        self.is_new_record, self.achievements = self.manager.storage.update_score(score, time)
        self.score = score
        self.time = time

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    self.manager.switch_scene(GameScene(self.manager))
                elif e.key == pygame.K_q:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

    def draw(self, surface):
        surface.fill(COLORS["BG"])
        title = self.font.render("GAME OVER", True, COLORS["SPIKE"])
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        score_text = self.font.render(f"最终得分: {self.score}", True, COLORS["TEXT"])
        surface.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 200))
        
        if self.is_new_record:
            record_text = self.font.render("🎉 新纪录诞生! 🎉", True, COLORS["GOLD"])
            surface.blit(record_text, (SCREEN_WIDTH//2 - record_text.get_width()//2, 260))

        if self.achievements:
            ach_text = self.font.render(f"解锁成就: {', '.join(self.achievements)}", True, COLORS["PLAYER"])
            surface.blit(ach_text, (SCREEN_WIDTH//2 - ach_text.get_width()//2, 320))

        tips = self.font.render("按 R 重新开始 | 按 Q 退出", True, (150, 150, 150))
        surface.blit(tips, (SCREEN_WIDTH//2 - tips.get_width()//2, 450))