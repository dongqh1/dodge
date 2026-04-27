# ==========================================
# 文件名: storage.py
# 职责: 负责高分、游戏次数及成就记录的本地读写
# 负责人: 成员 D (视听与存档)
# ==========================================
import json
import os

class Storage:
    def __init__(self):
        self.filename = "save_data.json"
        self.data = {
            "highscore": 0,
            "games_played": 0,
            "achievements": []
        }
        self.load_data()

    def load_data(self):
        """加载本地存档，若损坏则静默恢复默认值"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    # 更新已有字段，防止旧版本存档缺少新字段
                    self.data.update(saved_data)
            except (json.JSONDecodeError, IOError):
                print("⚠️ 存档文件损坏或格式错误，已重置为初始状态。")
                self.save_data() # 覆盖损坏的文件

    def save_data(self):
        """将数据序列化为 JSON 并写入本地"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
        except IOError:
            print("❌ 存档保存失败！请检查文件权限。")

    def update_score(self, score, survival_time):
        """结算时调用，更新记录并检查成就"""
        self.data["games_played"] += 1
        is_new_record = False
        
        if score > self.data["highscore"]:
            self.data["highscore"] = score
            is_new_record = True

        # 成就系统逻辑
        achievements_unlocked_this_round = []
        if survival_time >= 100 and "幸存 100 秒" not in self.data["achievements"]:
            self.data["achievements"].append("幸存 100 秒")
            achievements_unlocked_this_round.append("幸存 100 秒")
        
        if score >= 1000 and "千分大师" not in self.data["achievements"]:
            self.data["achievements"].append("千分大师")
            achievements_unlocked_this_round.append("千分大师")

        self.save_data()
        return is_new_record, achievements_unlocked_this_round