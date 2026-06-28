class SimulatedArm:
    def __init__(self, simulator: "RobotSimulator"):
        self.simulator = simulator

    def grab(self, object_id: str) -> dict:
        target = self.simulator.find_object(object_id)
        if target is None:
            self.simulator.add_log(f"抓取失败：未找到目标 {object_id}")
            return {"success": False, "message": f"未找到目标 {object_id}"}
        if target["status"] == "grabbed":
            return {"success": False, "message": f"目标 {object_id} 已被抓取"}

        self.simulator.arm["status"] = "moving"
        self.simulator.add_log(f"机械臂移动到 {target['name']}")
        self.simulator.arm["gripper"] = "closed"
        self.simulator.arm["holding"] = object_id
        self.simulator.arm["status"] = "holding"
        target["status"] = "grabbed"
        self.simulator.current_task = f"arm:grab:{object_id}"
        self.simulator.add_log(f"机械臂完成抓取：{target['name']}")
        return {"success": True, "message": f"已抓取 {target['name']}", "object": target}

    def reset(self):
        self.simulator.arm = {"status": "ready", "gripper": "open", "holding": None}
        self.simulator.add_log("机械臂复位")


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from robot.simulator import RobotSimulator

