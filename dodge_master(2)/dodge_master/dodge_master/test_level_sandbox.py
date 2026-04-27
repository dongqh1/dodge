import pygame
from config import *
from player import Player
from obstacles import Spike, Boulder, TrapZone
from level_manager import LevelManager
from collision import advanced_collision

# 1. 初始化 Pygame 与沙盒环境
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("阶段二测试：障碍物与关卡调度沙盒")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

# 2. 实例化核心模块
player = Player()
level_mgr = LevelManager()
active_obstacles = [] # 当前屏幕上的障碍物列表

print(">>> 进阶沙盒已启动！")
print(">>> 按 WASD 移动，按空格冲刺。")
print(">>> 开发者快捷键：按 'N' 键可直接跳过当前关卡（测试难度递增）。")

running = True
while running:
    # --- 事件处理 ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            # 开发者后门：按 N 键快速跳关，方便测试后期高难度
            if event.key == pygame.K_n:
                level_mgr.level_timer = level_mgr.level_duration
                print(f"⏩ 强制跳入下一关！当前关卡：{level_mgr.current_level + 1}")

    # --- 1. 玩家更新 ---
    keys = pygame.key.get_pressed()
    player.handle_input(keys)
    player.update()

    # --- 2. 关卡调度器更新与生成 ---
    level_mgr.update()
    if level_mgr.should_spawn_obstacle():
        # 工厂模式生成障碍物，并传入 player 引用供追踪石块使用
        new_obs = level_mgr.generate_obstacle(player)
        if new_obs:
            active_obstacles.append(new_obs)

    # --- 3. 障碍物更新与碰撞检测 ---
    for obs in active_obstacles[:]: # 使用切片拷贝遍历，方便在循环中删除元素
        obs.update()
        
        # 工业级三层碰撞检测
        # 注意：只有处于致命状态的障碍物才检测碰撞，预警状态不能扣血
        is_lethal = getattr(obs, 'state', 'active') == 'active' 
        
        if is_lethal and advanced_collision(player, obs):
            if player.hit():
                print(f"💥 玩家受到伤害！剩余生命：{player.lives}")

        # 对象池回收机制：清理生命周期结束的障碍物
        if obs.is_dead:
            active_obstacles.remove(obs)

    # --- 4. 画面渲染 ---
    screen.fill(COLORS["BG"])
    
    # 绘制障碍物 (底层)
    for obs in active_obstacles:
        obs.draw(screen)
        
    # 绘制玩家 (顶层)
    player.draw(screen)

    # --- 5. 调试 UI 绘制 ---
    ui_texts = [
        f"Level: {level_mgr.current_level} / {level_mgr.max_level}",
        f"Time: {level_mgr.level_timer // 60}s / 30s",
        f"Lives: {player.lives}",
        f"Active Obstacles: {len(active_obstacles)}"
    ]
    
    for i, text in enumerate(ui_texts):
        surf = font.render(text, True, COLORS["TEXT"])
        screen.blit(surf, (10, 10 + i * 30))

    # 关卡切换大字提示测试
    if level_mgr.level_up_flag:
        lvl_surf = font.render(f"LEVEL {level_mgr.current_level} !", True, COLORS["GOLD"])
        screen.blit(lvl_surf, (SCREEN_WIDTH//2 - 50, 100))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()