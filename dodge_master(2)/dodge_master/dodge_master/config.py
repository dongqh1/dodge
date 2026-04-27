# ==========================================
# 文件名: config.py
# 职责: 集中管理全局静态常量、颜色字典、难度配置与物理参数
# 负责人: 成员 A (组长)
# ==========================================

# 屏幕与渲染配置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Dodge Master - 终极避障"

# 调色板 (RGB)
COLORS = {
    "BG": (20, 20, 25),          # 深色背景
    "PLAYER": (0, 255, 255),     # 赛博蓝
    "PLAYER_INVINCIBLE": (255, 255, 255, 128), # 无敌闪烁态
    "SPIKE": (255, 50, 50),      # 危险红
    "BOULDER": (150, 150, 150),  # 石块灰
    "BOULDER_TRACK": (200, 50, 255), # 追踪石块紫
    "TRAP_WARNING": (255, 165, 0, 100), # 陷阱预警橙 (半透明)
    "TRAP_ACTIVE": (255, 0, 0, 150),    # 陷阱激活红
    "GOLD": (255, 215, 0),       # 金币黄
    "TEXT": (240, 240, 240),     # 文本白
    "UI_BG": (40, 40, 50, 200)   # UI半透明底色
}

# 玩家物理参数
PLAYER_RADIUS = 15
PLAYER_ACCEL = 0.8       # 加速度 (决定起步快慢)
PLAYER_FRICTION = 0.85   # 摩擦力阻尼 (0~1，越小越滑)
PLAYER_MAX_SPEED = 6.0   # 最大常规移速
DASH_MULTIPLIER = 3.0    # 冲刺速度倍率
DASH_DURATION = 18       # 冲刺持续帧数 (0.3秒 * 60FPS)
DASH_COOLDOWN = 300      # 冲刺冷却帧数 (5秒 * 60FPS)
INVINCIBLE_FRAMES = 120  # 受伤后无敌帧 (2秒 * 60FPS)

# 关卡难度配置模板 (数据驱动)
# 格式: {关卡号: {"spawn_rate": 生成间隔(帧), "speed_mult": 速度倍率, "trap_count": 陷阱数, "track_prob": 追踪石块概率}}
LEVEL_CONFIG = {
    1: {"spawn_rate": 90, "speed_mult": 1.0, "trap_count": 1, "track_prob": 0.0},
    2: {"spawn_rate": 70, "speed_mult": 1.5, "trap_count": 2, "track_prob": 0.05},
    3: {"spawn_rate": 50, "speed_mult": 2.0, "trap_count": 2, "track_prob": 0.15},
    4: {"spawn_rate": 35, "speed_mult": 2.5, "trap_count": 3, "track_prob": 0.20},
    5: {"spawn_rate": 24, "speed_mult": 3.0, "trap_count": 4, "track_prob": 0.30}
}