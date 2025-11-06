"""
word_manager.py - Quản lý từ vựng: thêm, sửa, xóa, load/save CSV
"""
import pandas as pd
import os
from modules.utils import get_today, add_days

CSV_FILE = "data/vocab/words.csv"

def init_csv():
    """Khởi tạo file CSV nếu chưa tồn tại"""
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=['word', 'pos', 'phonetic', 'meaning', 'example', 'start_date', 'review_count', 'next_review'])
        df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')

def load_words():
    """Load danh sách từ vựng từ CSV"""
    init_csv()
    try:
        df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
        # Đảm bảo các cột cần thiết tồn tại
        required_cols = ['word', 'pos', 'phonetic', 'meaning', 'example', 'start_date', 'review_count', 'next_review']
        for col in required_cols:
            if col not in df.columns:
                if col in ['pos', 'phonetic']:  # Thêm 'pos' vào đây
                    df[col] = ''
                elif col in ['word', 'meaning', 'example', 'start_date', 'next_review']:
                    df[col] = ''
                else:
                    df[col] = 0
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return pd.DataFrame(columns=['word', 'pos', 'phonetic', 'meaning', 'example', 'start_date', 'review_count', 'next_review'])

def save_words(df):
    """Lưu danh sách từ vựng vào CSV"""
    try:
        df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
        return True
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False

def add_word(word, pos, phonetic, meaning, example=""):  # Thêm tham số pos
    """
    Thêm từ mới vào kho từ vựng
    Returns: (success: bool, message: str)
    """
    df = load_words()
    
    # Kiểm tra từ đã tồn tại chưa
    if not df.empty and word.lower() in df['word'].str.lower().values:
        return False, f"❌ Từ '{word}' đã tồn tại trong kho!"
    
    # Tạo bản ghi mới
    today = get_today()
    tomorrow = add_days(today, 1)
    
    new_word = pd.DataFrame([{
        'word': word,
        'pos': pos,          # Thêm dòng này
        'phonetic': phonetic,
        'meaning': meaning,
        'example': example,
        'start_date': today,
        'review_count': 0,
        'next_review': tomorrow
    }])
    
    # Thêm vào dataframe
    df = pd.concat([df, new_word], ignore_index=True)
    
    if save_words(df):
        return True, f"✅ Đã thêm từ '{word}' thành công!"
    else:
        return False, "❌ Lỗi khi lưu file!"

def update_word(index, word, pos, phonetic, meaning, example):  # Thêm tham số pos
    """
    Cập nhật thông tin từ vựng
    Returns: (success: bool, message: str)
    """
    df = load_words()
    
    if index < 0 or index >= len(df):
        return False, "❌ Index không hợp lệ!"
    
    # Kiểm tra trùng lặp (nếu đổi sang từ khác đã tồn tại)
    if word.lower() != df.iloc[index]['word'].lower():
        if word.lower() in df['word'].str.lower().values:
            return False, f"❌ Từ '{word}' đã tồn tại!"
    
    # Cập nhật
    df.at[index, 'word'] = word
    df.at[index, 'pos'] = pos        # Thêm dòng này
    df.at[index, 'phonetic'] = phonetic
    df.at[index, 'meaning'] = meaning
    df.at[index, 'example'] = example
    
    if save_words(df):
        return True, f"✅ Đã cập nhật từ '{word}' thành công!"
    else:
        return False, "❌ Lỗi khi lưu file!"

def delete_word(index):
    """
    Xóa từ vựng
    Returns: (success: bool, message: str)
    """
    df = load_words()
    
    if index < 0 or index >= len(df):
        return False, "❌ Index không hợp lệ!"
    
    word = df.iloc[index]['word']
    df = df.drop(index).reset_index(drop=True)
    
    if save_words(df):
        return True, f"✅ Đã xóa từ '{word}' thành công!"
    else:
        return False, "❌ Lỗi khi lưu file!"

def search_words(search_term):
    """
    Tìm kiếm từ vựng theo từ hoặc nghĩa
    Returns: DataFrame chứa kết quả tìm kiếm
    """
    df = load_words()
    
    if df.empty or not search_term:
        return df
    
    search_term = search_term.lower()
    
    # Tìm trong cột word và meaning
    mask = (
        df['word'].str.lower().str.contains(search_term, na=False) |
        df['meaning'].str.lower().str.contains(search_term, na=False)
    )
    
    return df[mask]

def import_csv(file_path):
    """
    Import từ vựng từ file CSV khác
    Returns: (success: bool, message: str)
    """
    try:
        new_df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        # Kiểm tra cấu trúc file
        required_cols = ['word', 'meaning']
        if not all(col in new_df.columns for col in required_cols):
            return False, "❌ File CSV không đúng định dạng! Cần có cột 'word' và 'meaning'."
        
        # Load dữ liệu hiện tại
        current_df = load_words()
        
        # Thêm các cột còn thiếu cho file import
        today = get_today()
        tomorrow = add_days(today, 1)
        
        if 'example' not in new_df.columns:
            new_df['example'] = ''
        if 'phonetic' not in new_df.columns:
            new_df['phonetic'] = ''
        if 'pos' not in new_df.columns:
            new_df['pos'] = ''
        if 'start_date' not in new_df.columns:
            new_df['start_date'] = today
        if 'review_count' not in new_df.columns:
            new_df['review_count'] = 0
        if 'next_review' not in new_df.columns:
            new_df['next_review'] = tomorrow
        
        # Lọc các từ chưa tồn tại
        if not current_df.empty:
            existing_words = current_df['word'].str.lower().values
            new_df = new_df[~new_df['word'].str.lower().isin(existing_words)]
        
        if new_df.empty:
            return False, "⚠️ Không có từ mới nào để import (tất cả đã tồn tại)!"
        
        # Gộp và lưu
        combined_df = pd.concat([current_df, new_df], ignore_index=True)
        
        if save_words(combined_df):
            return True, f"✅ Đã import thành công {len(new_df)} từ mới!"
        else:
            return False, "❌ Lỗi khi lưu file!"
            
    except Exception as e:
        return False, f"❌ Lỗi khi đọc file: {str(e)}"