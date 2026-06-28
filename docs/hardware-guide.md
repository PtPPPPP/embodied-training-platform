# 硬件接入指南初版

当前 MVP 不接真实硬件。后续接入时保持同一套接口：

- 小车底盘替换 `SimulatedChassis`。
- 机械臂替换 `SimulatedArm`。
- 摄像头识别替换 `SimpleVision`。
- 路径规划和任务编排可以继续复用。

原则：真实硬件代码不要写进 `main.py`，也不要让前端直接依赖具体硬件型号。

