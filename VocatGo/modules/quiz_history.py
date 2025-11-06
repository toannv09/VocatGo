"""
quiz_history.py - Quản lý lịch sử làm quiz
"""
import pandas as pd
import os
from datetime import datetime

# Đường dẫn file
QUIZ_LOG_PATH = "data/history_quiz/quiz_log.csv"
QUIZ_WRONG_WORDS_PATH = "data/history_quiz/quiz_wrong_words.csv"

def ensure_history_folder():
    """Đảm bảo thư mục lưu lịch sử tồn tại"""
    os.makedirs("data/history_quiz", exist_ok=True)

def save_quiz_result(quiz_type, score, total, wrong_words):
    """
    Lưu kết quả quiz vào file
    
    Args:
        quiz_type: "multiple_choice" hoặc "typing"
        score: số câu đúng
        total: tổng số câu
        wrong_words: list các từ sai [{word, meaning, example}, ...]
    """
    ensure_history_folder()
    
    # Lưu vào quiz_log.csv
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    accuracy = (score / total * 100) if total > 0 else 0
    wrong_count = len(wrong_words)
    
    log_data = {
        'time': timestamp,
        'quiz_type': quiz_type,
        'score': score,
        'total': total,
        'accuracy': round(accuracy, 1),
        'wrong_count': wrong_count
    }
    
    # Đọc file cũ hoặc tạo mới
    if os.path.exists(QUIZ_LOG_PATH):
        df_log = pd.read_csv(QUIZ_LOG_PATH)
        df_log = pd.concat([df_log, pd.DataFrame([log_data])], ignore_index=True)
    else:
        df_log = pd.DataFrame([log_data])
    
    df_log.to_csv(QUIZ_LOG_PATH, index=False, encoding='utf-8-sig')
    
    # Lưu các từ sai vào quiz_wrong_words.csv
    if wrong_words:
        wrong_data = []
        for word_info in wrong_words:
            wrong_data.append({
                'time': timestamp,
                'word': word_info['word'],
                'meaning': word_info['meaning'],
                'example': word_info.get('example', ''),
                'quiz_type': quiz_type
            })
        
        if os.path.exists(QUIZ_WRONG_WORDS_PATH):
            df_wrong = pd.read_csv(QUIZ_WRONG_WORDS_PATH)
            df_wrong = pd.concat([df_wrong, pd.DataFrame(wrong_data)], ignore_index=True)
        else:
            df_wrong = pd.DataFrame(wrong_data)
        
        df_wrong.to_csv(QUIZ_WRONG_WORDS_PATH, index=False, encoding='utf-8-sig')

def load_quiz_log():
    """Đọc lịch sử quiz"""
    if os.path.exists(QUIZ_LOG_PATH):
        return pd.read_csv(QUIZ_LOG_PATH)
    return pd.DataFrame(columns=['time', 'quiz_type', 'score', 'total', 'accuracy', 'wrong_count'])

def load_wrong_words():
    """Đọc danh sách từ sai"""
    if os.path.exists(QUIZ_WRONG_WORDS_PATH):
        return pd.read_csv(QUIZ_WRONG_WORDS_PATH)
    return pd.DataFrame(columns=['time', 'word', 'meaning', 'example', 'quiz_type'])

def get_most_wrong_words(top_n=10):
    """
    Lấy top N từ sai nhiều nhất
    
    Args:
        top_n: số lượng từ muốn lấy
    
    Returns:
        DataFrame với columns: word, meaning, wrong_count
    """
    df_wrong = load_wrong_words()
    
    if df_wrong.empty:
        return pd.DataFrame(columns=['word', 'meaning', 'wrong_count'])
    
    # Đếm số lần sai của mỗi từ
    word_counts = df_wrong.groupby(['word', 'meaning']).size().reset_index(name='wrong_count')
    word_counts = word_counts.sort_values('wrong_count', ascending=False)
    
    return word_counts.head(top_n)

def get_quiz_stats():
    """
    Thống kê tổng quan về quiz
    
    Returns:
        dict với các thông tin: total_quizzes, avg_accuracy, best_score, total_questions
    """
    df_log = load_quiz_log()
    
    if df_log.empty:
        return {
            'total_quizzes': 0,
            'avg_accuracy': 0,
            'best_score': 0,
            'total_questions': 0
        }
    
    return {
        'total_quizzes': len(df_log),
        'avg_accuracy': round(df_log['accuracy'].mean(), 1),
        'best_score': round(df_log['accuracy'].max(), 1),
        'total_questions': df_log['total'].sum()
    }

def get_wrong_words_by_time(time_str):
    """
    Lấy danh sách từ sai của 1 lần làm quiz cụ thể
    
    Args:
        time_str: timestamp của quiz (format: "YYYY-MM-DD HH:MM")
    
    Returns:
        DataFrame chứa các từ sai trong quiz đó
    """
    df_wrong = load_wrong_words()
    
    if df_wrong.empty:
        return pd.DataFrame(columns=['word', 'meaning', 'example', 'quiz_type'])
    
    # Lọc theo thời gian
    return df_wrong[df_wrong['time'] == time_str]

def clear_history():
    """Xóa toàn bộ lịch sử quiz"""
    if os.path.exists(QUIZ_LOG_PATH):
        os.remove(QUIZ_LOG_PATH)
    
    if os.path.exists(QUIZ_WRONG_WORDS_PATH):
        os.remove(QUIZ_WRONG_WORDS_PATH)
    
    return True, "✅ Đã xóa toàn bộ lịch sử quiz!"