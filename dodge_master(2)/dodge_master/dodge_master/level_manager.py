# ==========================================
# 文件名: level_manager.py
# 职责: 管理游戏难度曲线、关卡切换、决定障碍物生成频率
# 负责人: 成员 C (玩法)
# ==========================================
import random
from config import LEVEL_CONFIG
from obstacles import Spike, Boulder, TrapZone, Laser

class LevelManager:
    def __init__(self):
        self.current_level = 1
        self.level_timer = 0
        self.level_duration = 30 * 60  # 每关持续 30 秒 (60FPS)
        self.spawn_timer = 0
        self.level_up_flag = True
        self.load_level_config()

    def _generate_dynamic_config(self, level):
        """动态生成超高关卡的配置"""
        # spawn_rate: 基础值为20，每5关增加1，上限为30
        spawn_rate = min(20 + (level - 5) // 5, 30)
        # speed_mult: 基础值为3.0，每关增加0.1，上限为5.0
        speed_mult = min(3.0 + (level - 5) * 0.1, 5.0)
        # trap_count: 基础值为4，每3关增加1，上限为8
        trap_count = min(4 + (level - 5) // 3, 8)
        # track_prob: 基础值为0.3，每关增加0.02，上限为0.7
        track_prob = min(0.3 + (level - 5) * 0.02, 0.7)
        return {
            "spawn_rate": spawn_rate,
            "speed_mult": speed_mult,
            "trap_count": trap_count,
            "track_prob": track_prob
        }

    def load_level_config(self):
        """加载当前关卡的配置参数"""
        if self.current_level in LEVEL_CONFIG:
            config = LEVEL_CONFIG[self.current_level]
        else:
            config = self._generate_dynamic_config(self.current_level)
            
        self.spawn_rate = config["spawn_rate"]
        self.speed_mult = config["speed_mult"]
        self.trap_count = config["trap_count"]
        self.track_prob = config["track_prob"]

    def update(self):
        """更新关卡进度计时器"""
        self.level_timer += 1
        self.spawn_timer += 1
        self.level_up_flag = False

        # 检查是否满足进入下一关的条件
        if self.level_timer >= self.level_duration:
            self.current_level += 1
            self.level_timer = 0
            self.spawn_timer = 0
            self.level_up_flag = True
            self.load_level_config()

    def should_spawn_obstacle(self):
        """是否达到了生成障碍物的时间间隔"""
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_timer = 0
            return True
        return False

    def generate_obstacle(self, player_ref):
        """
        基于当前难度权重生成具体的障碍物实例。
        作为工厂模式（Factory Pattern）的应用。
        """
        # 随着关卡提升，Boulder 和 Laser 的权重逐渐增加
        choices = ["Boulder", "Spike", "Trap"]
        weights = [60, 40, 20]

        # 从第3关开始，加入 Laser
        if self.current_level >= 3:
            choices.append("Laser")
            # Laser 的权重随关卡提升，最高权重为 40
            laser_weight = min(10 + (self.current_level - 3) * 5, 40)
            weights.append(laser_weight)
        
        obs_type = random.choices(choices, weights=weights, k=1)[0]
        
        if obs_type == "Spike":
            # 根据等级决定方向：等级越高，从非上方出现的概率越大
            # 基础概率：80% 从下往上，20% 从其他方向
            # 每级增加 5% 的其他方向概率，上限 60%
            non_up_prob = min(0.2 + (self.current_level - 1) * 0.05, 0.6)
            
            if random.random() < non_up_prob:
                direction = random.choice(["down", "left", "right"])
            else:
                direction = "up"
            
            return Spike(direction=direction, level=self.current_level)
        elif obs_type == "Trap":
            return TrapZone()
        elif obs_type == "Laser":
            return Laser()
        elif obs_type == "Boulder":
            # 根据 track_prob 判定是否生成追踪石块
            is_tracking = random.random() < self.track_prob
            return Boulder(speed_mult=self.speed_mult, is_tracking=is_tracking, player_ref=player_ref)

    def get_progress_ratio(self):
        """返回当前关卡进度 (0.0 ~ 1.0)，可供 UI 渲染进度条"""
        return self.level_timer / self.level_duration