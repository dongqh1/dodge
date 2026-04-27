from utils import get_distance, normalize_vector, clamp

print("--- 测试数学工具 ---")
print("距离测试 (期望 5.0):", get_distance((0,0), (3,4)))
print("归一化测试 (期望 0.6, 0.8):", normalize_vector(3, 4))
print("钳制测试 (期望 10):", clamp(15, 0, 10))
print("钳制测试 (期望 0):", clamp(-5, 0, 10))