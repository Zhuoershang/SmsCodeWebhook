from ninja import NinjaAPI
from django.core.cache import cache
import time
from .schemas import SendSmsMsgRequest, GetCodeRequest, ResponseSchema
import re
import requests
import json
from datetime import datetime, timedelta
from SmsCodeWebhook.const import (
    code_key,
    CODE_TIMEOUT,
    WAIT_TIME,
    MAX_WAIT_TIME,
    sms_code_pattern
)
api = NinjaAPI()

''' 原始请求代码
@api.post("/getCode", response=ResponseSchema)
def get_code(request, request_body: GetCodeRequest):
    start_time = time.time()
    key = request_body.phone_number
    while True:
        code = cache.get(key)

        if code:
            cache.delete(key)  # 删除已使用的验证码
            return ResponseSchema(err_code=0, message="Success", data={"code": code})

        if time.time() - start_time > MAX_WAIT_TIME:
            return ResponseSchema(err_code=408, message="获取验证码超时")

        time.sleep(WAIT_TIME)
'''
@api.post("/getCode", response=ResponseSchema)
def get_code(request, request_body: GetCodeRequest):
    start_time = time.time()
    key = request_body.phone_number
    
    while True:
        """处理短信数据并生成响应"""
        sms_data = get_sms_data()
        if sms_data:
            # 提取所需字段
            # 如果短信为空，则get_sms_data()返回数据为空None，则直接跳过，继续下一轮获取。
            # phone_number = sms_data.get("phone_number", "")
            sms_msg = sms_data.get("sms_msg", "")
            sms_timestamp = sms_data.get("smstime", "")
    
            # 这里来解析的短信内容
            re_pattern = re.compile(sms_code_pattern)
            match = re_pattern.search(sms_msg)
        if match:
            code = match.group(0)
        # 检查验证码有效性和时间有效性
        if code and is_within_5_minutes:
            del_sms_data()  # 删除webhook上的所有信息
            return ResponseSchema(err_code=0, message="Success", data={"code": code})

        if time.time() - start_time > MAX_WAIT_TIME:
            return ResponseSchema(err_code=408, message="获取验证码超时")
        
        time.sleep(WAIT_TIME)


@api.post("/sendSmsMsg", response=ResponseSchema)
def send_sms_msg(request, request_body: SendSmsMsgRequest):
    # 获取手机号码
    key = request_body.phone_number
    # 获取短信内容
    sms_msg = request_body.sms_msg
    # 这里来解析的短信内容
    re_pattern = re.compile(sms_code_pattern)
    match = re_pattern.search(sms_msg)
    if match:
        code = match.group(0)
        cache.set(key, code, timeout=CODE_TIMEOUT)
        return ResponseSchema(err_code=0, message="Set code successfully.")
    return ResponseSchema(err_code=400, message="Set code fail.")

def get_sms_data():
    """从 Webhook.site 获取最新的短信数据"""
    url = "https://webhook.site/token/b7522351-425c-477b-923f-a2faf086cd3d/request/latest/raw"
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查HTTP错误
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None
    except json.JSONDecodeError:
        print("响应不是有效的JSON格式")
        return None
def del_sms_data():
    """从 Webhook.site 删除所有的的短信数据"""
    url = "https://webhook.site/token/b7522351-425c-477b-923f-a2faf086cd3d/request"
    try:
        response = requests.delete(url)
        response.raise_for_status()  # 检查HTTP错误
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None
    except json.JSONDecodeError:
        print("响应不是有效的JSON格式")
        return None

def extract_verification_code(sms_msg):
    """从短信内容中提取验证码"""
    # 使用正则表达式匹配6位数字验证码
    match = re.search(r'验证码[：:]\s*(\d{6})', sms_msg)
    if match:
        return match.group(1)
    
    # 备用匹配模式：短信中直接包含6位连续数字
    match = re.search(r'\b\d{6}\b', sms_msg)
    if match:
        return match.group(0)
    
    return None

def is_within_5_minutes(sms_timestamp):
    """检查时间戳是否在5分钟内"""
    try:
        # 将毫秒时间戳转换为秒
        sms_time = datetime.fromtimestamp(int(sms_timestamp) / 1000)
        current_time = datetime.now()
        
        # 计算时间差
        time_diff = current_time - sms_time
        return time_diff <= timedelta(minutes=5)
    except (ValueError, TypeError, OverflowError):
        return False
'''
def process_sms():
    """处理短信数据并生成响应"""
    sms_data = get_sms_data()
    if not sms_data:
        return {
            "err_code": 404,
            "message": "未获取到短信数据",
            "data": None
        }
    
    # 提取所需字段
    phone_number = sms_data.get("phone_number", "")
    sms_msg = sms_data.get("sms_msg", "")
    sms_timestamp = sms_data.get("smstime", "")
    
    # 提取验证码
    verification_code = extract_verification_code(sms_msg)
    if not verification_code:
        return {
            "err_code": 422,
            "message": "短信中未找到验证码",
            "data": None
        }
    
    # 检查时间有效性
    if not is_within_5_minutes(sms_timestamp):
        return {
            "err_code": 408,
            "message": "验证码已超过5分钟有效期",
            "data": None
        }
    
    # 成功响应
    return {
        "err_code": 0,
        "message": "Success",
        "data": {
            "code": verification_code
        }
    }
'''


