from api_client import post, print_json


if __name__ == "__main__":
    result = post("/api/robot/arm/grab", {"object_id": "red_cube"})
    print_json("机械臂抓取结果", result)

