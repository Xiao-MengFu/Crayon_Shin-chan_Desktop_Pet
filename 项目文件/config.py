import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 大模型 API 调用配置
BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")