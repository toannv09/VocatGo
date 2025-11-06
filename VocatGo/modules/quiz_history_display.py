"""
quiz_history_display.py - Hiển thị lịch sử làm quiz
Version: Fixed navigation to flashcard
"""
import streamlit as st
import pandas as pd
from modules.quiz_history import (
    load_quiz_log, 
    get_most_wrong_words,
    get_quiz_stats,
    get_wrong_words_by_time,
    clear_history
)

def show_quiz_history_page():
    """Hiển thị trang lịch sử quiz"""
    st.markdown("## 📜 Lịch sử Quiz")
    
    df_log = load_quiz_log()
    
    if df_log.empty:
        st.info("📭 Bạn chưa làm quiz nào. Hãy bắt đầu làm quiz để theo dõi tiến độ!")
        return
    
    # Tab chính
    tab1, tab2, tab3 = st.tabs(["📊 Tổng quan", "📈 Chi tiết", "❌ Từ sai nhiều"])
    
    with tab1:
        show_overview(df_log)
    
    with tab2:
        show_detailed_history(df_log)
    
    with tab3:
        show_most_wrong_words()

def show_overview(df_log):
    """Hiển thị tổng quan"""
    st.markdown("### 📊 Thống kê tổng quan")
    
    stats = get_quiz_stats()
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Số lần làm quiz", stats['total_quizzes'])
    
    with col2:
        st.metric("Tổng số câu hỏi", stats['total_questions'])
    
    with col3:
        st.metric("Điểm trung bình", f"{stats['avg_accuracy']}%")
    
    with col4:
        st.metric("Điểm cao nhất", f"{stats['best_score']}%")
    
    st.markdown("---")
    
    # Biểu đồ tiến bộ theo thời gian
    st.markdown("### 📈 Tiến bộ theo thời gian")
    
    if len(df_log) > 0:
        # Chuyển đổi time thành datetime
        df_chart = df_log.copy()
        df_chart['time'] = pd.to_datetime(df_chart['time'])
        df_chart = df_chart.sort_values('time')
        
        # Biểu đồ line chart
        st.line_chart(
            df_chart.set_index('time')['accuracy'],
            use_container_width=True
        )
        
        st.caption("💡 Đồ thị hiển thị % điểm của mỗi lần làm quiz")
    
    st.markdown("---")
    
    # So sánh hiệu suất giữa các loại quiz
    st.markdown("### 🎯 Hiệu suất theo loại quiz")
    
    col1, col2 = st.columns(2)
    
    with col1:
        mc_data = df_log[df_log['quiz_type'] == 'multiple_choice']
        if not mc_data.empty:
            st.metric(
                "📝 Trắc nghiệm",
                f"{mc_data['accuracy'].mean():.1f}%",
                delta=f"{len(mc_data)} lần làm"
            )
        else:
            st.info("Chưa có dữ liệu trắc nghiệm")
    
    with col2:
        typing_data = df_log[df_log['quiz_type'] == 'typing']
        if not typing_data.empty:
            st.metric(
                "✏️ Điền từ",
                f"{typing_data['accuracy'].mean():.1f}%",
                delta=f"{len(typing_data)} lần làm"
            )
        else:
            st.info("Chưa có dữ liệu điền từ")

def show_detailed_history(df_log):
    """Hiển thị chi tiết lịch sử"""
    st.markdown("### 📋 Danh sách chi tiết các lần làm quiz")
    
    # Bộ lọc
    col1, col2 = st.columns(2)
    
    with col1:
        filter_type = st.selectbox(
            "Lọc theo loại:",
            ["Tất cả", "Trắc nghiệm", "Điền từ"]
        )
    
    with col2:
        sort_order = st.selectbox(
            "Sắp xếp:",
            ["Mới nhất", "Cũ nhất", "Điểm cao nhất", "Điểm thấp nhất"]
        )
    
    # Áp dụng bộ lọc
    df_filtered = df_log.copy()
    
    if filter_type == "Trắc nghiệm":
        df_filtered = df_filtered[df_filtered['quiz_type'] == 'multiple_choice']
    elif filter_type == "Điền từ":
        df_filtered = df_filtered[df_filtered['quiz_type'] == 'typing']
    
    # Sắp xếp
    if sort_order == "Mới nhất":
        df_filtered = df_filtered.sort_values('time', ascending=False)
    elif sort_order == "Cũ nhất":
        df_filtered = df_filtered.sort_values('time', ascending=True)
    elif sort_order == "Điểm cao nhất":
        df_filtered = df_filtered.sort_values('accuracy', ascending=False)
    elif sort_order == "Điểm thấp nhất":
        df_filtered = df_filtered.sort_values('accuracy', ascending=True)
    
    st.markdown("---")
    
    if df_filtered.empty:
        st.info("Không có dữ liệu phù hợp với bộ lọc")
    else:
        st.caption(f"Hiển thị {len(df_filtered)} kết quả")
        
        # Hiển thị bảng đẹp hơn với expander để xem chi tiết
        for idx, row in df_filtered.iterrows():
            quiz_type_icon = "📝" if row['quiz_type'] == 'multiple_choice' else "✏️"
            quiz_type_name = "Trắc nghiệm" if row['quiz_type'] == 'multiple_choice' else "Điền từ"
            
            # Màu sắc và badge theo điểm
            if row['accuracy'] >= 80:
                badge = "🌟 Xuất sắc"
            elif row['accuracy'] >= 60:
                badge = "👍 Khá"
            else:
                badge = "💪 Cần cố gắng"
            
            # Tạo title cho expander
            expander_title = f"{quiz_type_icon} **{quiz_type_name}** • {row['time']} • **{row['score']}/{row['total']}** ({row['accuracy']}%) • {badge}"
            
            with st.expander(expander_title, expanded=False):
                # Hiển thị thông tin tổng quan
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Điểm số", f"{row['accuracy']}%")
                
                with col2:
                    st.metric("Số câu đúng", f"{row['score']}/{row['total']}")
                
                with col3:
                    st.metric("Số câu sai", row['wrong_count'])
                
                # Hiển thị danh sách từ sai (nếu có)
                if row['wrong_count'] > 0:
                    st.markdown("---")
                    st.markdown("#### ❌ Danh sách từ sai trong bài này:")
                    
                    # Lấy danh sách từ sai của quiz này
                    wrong_words = get_wrong_words_by_time(row['time'])
                    
                    if not wrong_words.empty:
                        # Hiển thị từng từ sai
                        for w_idx, w_row in wrong_words.iterrows():
                            with st.container():
                                col_word, col_meaning = st.columns([1, 2])
                                
                                with col_word:
                                    st.markdown(f"**{w_row['word']}**")
                                
                                with col_meaning:
                                    st.markdown(f"{w_row['meaning']}")
                                
                                # Hiển thị ví dụ nếu có
                                if w_row['example'] and str(w_row['example']).strip():
                                    st.caption(f"💡 Ví dụ: {w_row['example']}")
                                
                                st.markdown("")
                    else:
                        st.info("Không tìm thấy chi tiết từ sai")
                else:
                    st.success("🎉 Hoàn hảo! Không có từ nào sai trong bài này.")
            
            st.markdown("")
    
    # Nút xóa lịch sử
    st.markdown("### ⚠️ Quản lý lịch sử")
    
    if st.button("🗑️ Xóa toàn bộ lịch sử", type="secondary"):
        if st.session_state.get('confirm_clear_history'):
            success, msg = clear_history()
            if success:
                st.success(msg)
                del st.session_state.confirm_clear_history
                st.rerun()
        else:
            st.session_state.confirm_clear_history = True
            st.warning("⚠️ Bấm lại lần nữa để xác nhận xóa!")

def show_most_wrong_words():
    """Hiển thị từ sai nhiều nhất"""
    st.markdown("### ❌ Top 10 từ sai nhiều nhất")
    
    df_wrong = get_most_wrong_words(top_n=10)
    
    if df_wrong.empty:
        st.success("🎉 Bạn chưa làm sai từ nào! Tuyệt vời!")
        return
    
    st.caption("Những từ này cần được ôn lại kỹ hơn:")
    
    # Hiển thị danh sách
    for idx, row in df_wrong.iterrows():
        col1, col2, col3 = st.columns([3, 3, 1])
        
        with col1:
            st.markdown(f"**{row['word']}**")
        
        with col2:
            st.markdown(f"{row['meaning']}")
        
        with col3:
            st.error(f"❌ {row['wrong_count']}x")
        
        st.markdown("---")
    
    # Nút ôn lại các từ này
    st.markdown("### 🔄 Ôn lại các từ hay sai")
    
    st.info(f"💡 Có **{len(df_wrong)} từ** cần ôn kỹ. Bạn có thể tạo flashcard riêng hoặc làm quiz với những từ này.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📚 Ôn với Flashcard", use_container_width=True, type="primary", key="btn_flashcard_wrong"):
            # Set flag để chuyển sang trang flashcard
            st.session_state.flashcard_filter_words = df_wrong['word'].tolist()
            st.rerun()
    
    with col2:
        if st.button("🧩 Làm Quiz với từ này", use_container_width=True, key="btn_quiz_wrong"):
            st.info("Chức năng đang phát triển...")