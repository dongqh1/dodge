# ==========================================
# 文件名: main.py
# 职责: Pygame 初始化，装载场景管理器，开启主循环
# 负责人: 成员 A (组长)
# ==========================================
import pygame
from config import *
from scenes import SceneManager
from storage import Storage
from sound_manager import SoundManager

def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # 初始化全局系统
    storage = Storage()
    sound_mgr = SoundManager()
    
    # 初始化场景调度器
    scene_manager = SceneManager(storage, sound_mgr)

    running = True
    while running:
        try:
            # 获取全部事件并传递给当前场景
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

            # 帧执行：事件处理 -> 数据更新 -> 画面渲染
            scene_manager.run_frame(screen, events)

            pygame.display.flip()
            clock.tick(FPS)
        except KeyboardInterrupt:
            # 优雅处理 Ctrl+C 中断
            running = False

    # 退出前确保资源释放与安全存档
    storage.save_data()
    pygame.quit()

if __name__ == "__main__":
    main()