class SimpleVision:
    def __init__(self, simulator: "RobotSimulator"):
        self.simulator = simulator

    def detect_objects(self) -> list[dict]:
        self.simulator.add_log("视觉模块返回模拟目标列表")
        return [item.copy() for item in self.simulator.objects]


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from robot.simulator import RobotSimulator

