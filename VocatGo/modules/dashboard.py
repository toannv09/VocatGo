"""
dashboard.py - Thống kê và biểu đồ học tập
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from modules.word_manager import load_words
from modules.spaced_repetition import get_review_stats, get_due_words
from modules.utils import str_to_date, get_today

def display_dashboard():
    """Hiển thị dashboard thống kê"""
    st.markdown("## 📊 Thống kê học tập")
    
    df = load_words()
    
    if df.empty:
        st.info("📭 Chưa có dữ liệu. Hãy thêm từ vựng để bắt đầu!")
        return
    
    # Tổng quan
    show_overview_stats()
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        show_progress_chart()
    
    with col2:
        show_review_distribution()
    
    st.markdown("---")
    
    # Lịch sử học tập
    show_learning_history()

def show_overview_stats():
    """Hiển thị thống kê tổng quan"""
    stats = get_review_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📚 Tổng số từ",
            value=stats['total']
        )
    
    with col2:
        st.metric(
            label="⏰ Cần ôn hôm nay",
            value=stats['due_today'],
            delta=f"{stats['due_today']} từ"
        )
    
    with col3:
        st.metric(
            label="🌟 Đã thành thục",
            value=stats['mastered'],
            delta=f"{stats['mastered_percentage']:.0f}%"
        )
    
    with col4:
        st.metric(
            label="📖 Đang học",
            value=stats['learning']
        )

def show_progress_chart():
    """Hiển thị biểu đồ tiến độ học tập"""
    st.markdown("### 📈 Phân bố mức độ thành thạo")
    
    df = load_words()
    
    # Phân loại theo review_count
    bins = [0, 1, 3, 6, float('inf')]
    labels = ['Mới học', 'Đang học', 'Khá', 'Thành thục']
    
    df['level'] = pd.cut(df['review_count'], bins=bins, labels=labels, right=False)
    level_counts = df['level'].value_counts()
    
    # Tạo dataframe cho chart
    chart_data = pd.DataFrame({
        'Mức độ': level_counts.index,
        'Số từ': level_counts.values
    })
    
    st.bar_chart(chart_data.set_index('Mức độ'))
    
    # Bảng chi tiết
    with st.expander("📋 Xem chi tiết"):
        for level in labels:
            count = level_counts.get(level, 0)
            st.write(f"**{level}:** {count} từ")

def show_review_distribution():
    """Hiển thị phân bố lịch ôn tập"""
    st.markdown("### 📅 Lịch ôn tập 7 ngày tới")
    
    df = load_words()
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Tạo danh sách 7 ngày tới
    dates = []
    counts = []
    
    for i in range(7):
        date = today + timedelta(days=i)
        date_str = date.strftime("%d-%m-%Y")
        
        # Đếm số từ cần ôn vào ngày đó
        count = len(df[df['next_review'] == date_str])
        
        dates.append(date.strftime("%d/%m"))
        counts.append(count)
    
    # Tạo chart
    chart_data = pd.DataFrame({
        'Ngày': dates,
        'Số từ': counts
    })
    
    st.line_chart(chart_data.set_index('Ngày'))
    
    # Highlight ngày hôm nay
    today_count = counts[0]
    if today_count > 0:
        st.info(f"📌 Hôm nay cần ôn **{today_count} từ**")
    else:
        st.success("🎉 Hôm nay không có từ cần ôn!")

def show_learning_history():
    """Hiển thị lịch sử học tập"""
    st.markdown("### 📖 Lịch sử học tập")
    
    df = load_words()
    
    # Sắp xếp theo start_date
    df_sorted = df.sort_values('start_date', ascending=False)
    
    # Nhóm theo tháng
    df_sorted['month'] = df_sorted['start_date'].apply(lambda x: str_to_date(x).strftime("%m/%Y"))
    
    monthly_stats = df_sorted.groupby('month').agg({
        'word': 'count',
        'review_count': 'sum'
    }).reset_index()
    
    monthly_stats.columns = ['Tháng', 'Số từ mới', 'Tổng lượt ôn']
    
    # Hiển thị bảng
    st.dataframe(
        monthly_stats,
        use_container_width=True,
        hide_index=True
    )
    
    # Từ học gần đây
    st.markdown("#### 🆕 10 từ học gần đây nhất:")
    
    recent_words = df_sorted.head(10)[['word', 'pos', 'phonetic', 'meaning', 'start_date', 'review_count']]
    recent_words.columns = ['Từ', 'Loại từ', 'Phiên âm', 'Nghĩa', 'Ngày bắt đầu', 'Số lần ôn']
    
    st.dataframe(
        recent_words,
        use_container_width=True,
        hide_index=True
    )
    
    # Top từ ôn nhiều nhất
    st.markdown("#### 🔥 Top 10 từ được ôn nhiều nhất:")
    
    top_reviewed = df.nlargest(10, 'review_count')[['word', 'pos', 'phonetic', 'meaning', 'review_count', 'next_review']]
    top_reviewed.columns = ['Từ', 'Loại từ', 'Phiên âm', 'Nghĩa', 'Số lần ôn', 'Ôn tiếp']
    
    st.dataframe(
        top_reviewed,
        use_container_width=True,
        hide_index=True
    )

def show_streak_info():
    """Hiển thị thông tin chuỗi ngày học liên tục (streak)"""
    # TODO: Cần thêm logic tracking streak trong tương lai
    pass