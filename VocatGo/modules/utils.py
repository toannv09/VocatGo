"""
utils.py - Các hàm phụ trợ cho ứng dụng học từ vựng
"""
from datetime import datetime, timedelta
import random

def get_today():
    """Lấy ngày hôm nay dạng string dd-mm-yyyy"""
    return datetime.now().strftime("%d-%m-%Y")

def str_to_date(date_str):
    """Chuyển string dd-mm-yyyy thành datetime object"""
    try:
        return datetime.strptime(date_str, "%d-%m-%Y")
    except:
        return datetime.now()

def date_to_str(date_obj):
    """Chuyển datetime object thành string dd-mm-yyyy"""
    return date_obj.strftime("%d-%m-%Y")

def add_days(date_str, days):
    """Cộng thêm số ngày vào date string"""
    date_obj = str_to_date(date_str)
    new_date = date_obj + timedelta(days=days)
    return date_to_str(new_date)

def is_due_today(next_review_str):
    """Kiểm tra xem từ có cần ôn hôm nay không"""
    try:
        next_review = str_to_date(next_review_str)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return next_review <= today
    except:
        return False

def shuffle_list(lst):
    """Trộn ngẫu nhiên danh sách"""
    shuffled = lst.copy()
    random.shuffle(shuffled)
    return shuffled

def format_progress(current, total):
    """Format tiến độ: 5/20 (25%)"""
    if total == 0:
        return "0/0 (0%)"
    percentage = (current / total) * 100
    return f"{current}/{total} ({percentage:.0f}%)"