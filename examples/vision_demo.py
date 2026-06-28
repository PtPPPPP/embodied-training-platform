from api_client import get, print_json


if __name__ == "__main__":
    result = get("/api/vision/objects")
    print_json("模拟视觉识别结果", result)

