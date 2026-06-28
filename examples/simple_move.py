from api_client import post, print_json


if __name__ == "__main__":
    state = post("/api/robot/chassis/move", {"command": "forward", "speed": 0.6})
    print_json("小车前进后的状态", state)

