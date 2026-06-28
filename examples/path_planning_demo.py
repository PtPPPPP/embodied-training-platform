from api_client import post, print_json


if __name__ == "__main__":
    result = post(
        "/api/planner/path",
        {
            "start": {"x": 0, "y": 0},
            "goal": {"x": 8, "y": 8},
            "obstacles": [{"x": 3, "y": 3}, {"x": 3, "y": 4}, {"x": 4, "y": 4}],
        },
    )
    print_json("路径规划结果", {"path": result["path"]})

