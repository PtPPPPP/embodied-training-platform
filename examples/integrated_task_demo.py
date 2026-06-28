from api_client import get, post, print_json


if __name__ == "__main__":
    objects = get("/api/vision/objects")
    print_json("1. 识别目标", objects)

    path = post(
        "/api/planner/path",
        {
            "start": {"x": 0, "y": 0},
            "goal": {"x": 6, "y": 2},
            "obstacles": [{"x": 3, "y": 3}, {"x": 3, "y": 4}, {"x": 4, "y": 4}],
        },
    )
    print_json("2. 规划到红色方块", {"path": path["path"]})

    move = post("/api/robot/chassis/move", {"command": "forward", "speed": 0.8})
    print_json("3. 小车移动", move)

    grab = post("/api/robot/arm/grab", {"object_id": "red_cube"})
    print_json("4. 抓取目标", grab)

