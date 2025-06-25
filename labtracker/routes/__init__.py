# labtracker/routes/__init__.py
from flask import Blueprint

# API 전용 블루프린트 정의  (이 파일에서는 *정의*만!)
bp = Blueprint("api", __name__)

# -------------------------------------------
# 여기에 실제 API 엔드포인트들을 이어서 import
# -------------------------------------------
# from .cases_api import *   # 예) /api/cases/...
# from .files_api import *   # 예) /api/files/...
# 필요한 모듈을 이 줄 아래에 자유롭게 추가