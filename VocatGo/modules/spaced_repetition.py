"""
spaced_repetition.py - Hệ thống lặp lại ngắt quãng (SRS)
"""
from modules.word_manager import load_words, save_words
from modules.utils import get_today, add_days, is_due_today

# Khoảng cách ôn tập (ngày) theo số lần ôn
REVIEW_INTERVALS = [1, 3, 7, 14, 30, 60, 120]

def get_next_review_date(review_count):
    """
    Tính ngày ôn tiếp theo dựa trên số lần đã ôn
    """
    today = get_today()
    
    if review_count >= len(REVIEW_INTERVALS):
        # Đã thành thục, ôn sau 120 ngày
        interval = REVIEW_INTERVALS[-1]
    else:
        interval = REVIEW_INTERVALS[review_count]
    
    return add_days(today, interval)

def update_word_review(index, remembered):
    """
    Cập nhật tiến độ ôn tập của từ
    
    Args:
        index: vị trí từ trong dataframe
        remembered: True nếu nhớ, False nếu quên
    
    Returns: (success: bool, message: str)
    """
    df = load_words()
    
    if index < 0 or index >= len(df):
        return False, "❌ Index không hợp lệ!"
    
    current_count = int(df.at[index, 'review_count'])
    
    if remembered:
        # Nhớ: tăng review_count
        new_count = current_count + 1
        df.at[index, 'review_count'] = new_count
        df.at[index, 'next_review'] = get_next_review_date(new_count)
        message = f"✅ Tuyệt vời! Từ '{df.at[index, 'word']}' sẽ được ôn lại sau {REVIEW_INTERVALS[min(new_count, len(REVIEW_INTERVALS)-1)]} ngày."
    else:
        # Quên: giảm review_count (tối thiểu = 0)
        new_count = max(current_count - 1, 0)
        df.at[index, 'review_count'] = new_count
        # Ôn lại sau 1 ngày
        df.at[index, 'next_review'] = add_days(get_today(), 1)
        message = f"💪 Đừng lo! Từ '{df.at[index, 'word']}' sẽ xuất hiện lại vào ngày mai."
    
    if save_words(df):
        return True, message
    else:
        return False, "❌ Lỗi khi lưu file!"

def get_due_words():
    """
    Lấy danh sách các từ cần ôn hôm nay
    Returns: DataFrame
    """
    df = load_words()
    
    if df.empty:
        return df
    
    # Lọc các từ có next_review <= hôm nay
    due_mask = df['next_review'].apply(is_due_today)
    return df[due_mask].reset_index(drop=True)

def get_mastered_words():
    """
    Lấy danh sách các từ đã thành thục (review_count >= 6)
    Returns: DataFrame
    """
    df = load_words()
    
    if df.empty:
        return df
    
    return df[df['review_count'] >= 6].reset_index(drop=True)

def get_learning_words():
    """
    Lấy danh sách các từ đang học (review_count < 6)
    Returns: DataFrame
    """
    df = load_words()
    
    if df.empty:
        return df
    
    return df[df['review_count'] < 6].reset_index(drop=True)

def reset_word_progress(index):
    """
    Reset tiến độ học của một từ về ban đầu
    
    Args:
        index: vị trí từ trong dataframe
    
    Returns: (success: bool, message: str)
    """
    df = load_words()
    
    if index < 0 or index >= len(df):
        return False, "❌ Index không hợp lệ!"
    
    word = df.at[index, 'word']
    today = get_today()
    
    # Reset về trạng thái ban đầu
    df.at[index, 'start_date'] = today
    df.at[index, 'review_count'] = 0
    df.at[index, 'next_review'] = add_days(today, 1)
    
    if save_words(df):
        return True, f"🔄 Đã reset tiến độ của từ '{word}'. Bắt đầu học lại từ đầu!"
    else:
        return False, "❌ Lỗi khi lưu file!"

def get_review_stats():
    """
    Lấy thống kê về tiến độ ôn tập
    Returns: dict với các thông tin thống kê
    """
    df = load_words()
    
    if df.empty:
        return {
            'total': 0,
            'due_today': 0,
            'mastered': 0,
            'learning': 0,
            'mastered_percentage': 0
        }
    
    total = len(df)
    due_today = len(get_due_words())
    mastered = len(df[df['review_count'] >= 6])
    learning = total - mastered
    mastered_percentage = (mastered / total * 100) if total > 0 else 0
    
    return {
        'total': total,
        'due_today': due_today,
        'mastered': mastered,
        'learning': learning,
        'mastered_percentage': mastered_percentage
    }