import pygame
from config import *
from player import Player
from collision import check_aabb, check_circle

# 1. 初始化沙盒环境
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# 2. 实例化我们写的玩家类
test_player = Player()

# 3. 创建两个测试用的虚拟障碍物
# 测试障碍物 A：一个静态矩形 (用于 AABB 测试)
dummy_rect = pygame.Rect(400, 200, 100, 100)
# 测试障碍物 B：一个静态圆形 (用于 圆形距离测试)
dummy_circle_pos = (200, 400)
dummy_circle_radius = 50

running = True
print(">>> 沙盒测试已启动！尝试使用 WASD 移动，空格键冲刺。")

while running:
    # --- 事件处理 ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- 更新逻辑 ---
    keys = pygame.key.get_pressed()
    test_player.handle_input(keys)
    test_player.update()

    # --- 碰撞测试输出 ---
    p_rect = test_player.get_rect()
    # 测矩形
    if check_aabb(p_rect, dummy_rect):
        print("💥 触发 AABB 碰撞！碰到了矩形障碍物！")
        test_player.hit() # 测试受击扣血和无敌帧
        
    # 测圆形
    if check_circle(test_player.pos, test_player.radius, dummy_circle_pos, dummy_circle_radius):
        print("⭕ 触发圆形碰撞！碰到了圆形障碍物！")

    # --- 渲染画面 ---
    screen.fill(COLORS["BG"])
    
    # 画测试障碍物
    pygame.draw.rect(screen, COLORS["SPIKE"], dummy_rect)
    pygame.draw.circle(screen, COLORS["BOULDER"], dummy_circle_pos, dummy_circle_radius)
    
    # 画玩家
    test_player.draw(screen)
    
    # 显示调试信息（血量和技能状态）
    font = pygame.font.Font(None, 24)
    info = font.render(f"Lives: {test_player.lives} | Dash CD: {test_player.dash_cd_timer}", True, COLORS["TEXT"])
    screen.blit(info, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()