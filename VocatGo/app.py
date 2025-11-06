"""
app.py - Ứng dụng học từ vựng cá nhân với Streamlit
Chạy: streamlit run app.py
Fixed: Navigation khi ôn flashcard từ lịch sử quiz
"""
import streamlit as st
from modules.word_manager import (
    load_words, add_word, update_word, delete_word, 
    search_words, import_csv
)
from modules.flashcard import clear_flashcard_session, init_flashcard_session, display_flashcard
from modules.quiz import init_quiz_session, display_quiz
from modules.dashboard import display_dashboard
from modules.spaced_repetition import get_due_words, reset_word_progress
from modules.quiz_history_display import show_quiz_history_page

# Cấu hình trang
st.set_page_config(
    page_title="VocatGo - Vocab Learning App",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .footer {
        position: fixed;
        right: 10px;
        bottom: 10px;
        background-color: rgba(255, 255, 255, 0.9);
        color: #666;
        padding: 5px 12px;
        font-size: 11px;
        border-radius: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        z-index: 999;
    }
    
    /* Tăng kích thước font sidebar */
    [data-testid="stSidebar"] {
        font-size: 18px;
    }
    [data-testid="stSidebar"] .st-emotion-cache-16txtl3 h2 {
        font-size: 24px;
        font-weight: bold;
    }
    [data-testid="stSidebar"] label {
        font-size: 18px !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 18px !important;
    }
    [data-testid="stSidebar"] .stMetric label {
        font-size: 16px !important;
    }
    [data-testid="stSidebar"] .stMetric [data-testid="stMetricValue"] {
        font-size: 28px !important;
    }
    [data-testid="stSidebar"] p {
        font-size: 15px !important;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    """Hàm chính"""
    
    # Header với logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="main-header"><h1>📚 VocatGo</h1><p>Học từ vựng thông minh với phương pháp lặp lại ngắt quãng</p></div>', 
                       unsafe_allow_html=True)
    
    # Sidebar menu
    with st.sidebar:
        # Logo nhỏ trong sidebar (tùy chọn)
        try:
            st.image("assets/VocatGo_Logo.png", width=400)
        except:
            st.image("https://img.icons8.com/fluency/96/book.png", width=80)
        
        st.markdown("## 🎯 Menu")
        
        # Xử lý navigation từ các trang khác
        default_menu = "🏠 Trang chủ"
        
        # QUAN TRỌNG: Kiểm tra nếu đang trong session flashcard hoặc quiz
        # Ưu tiên GIỮ người dùng ở trang hiện tại nếu đang làm việc
        if 'flashcard_list' in st.session_state and st.session_state.flashcard_list:
            default_menu = "🧠 Học & Ôn tập"
        elif 'quiz_questions' in st.session_state:
            default_menu = "🧩 Kiểm tra (Quiz)"
        # Kiểm tra nếu có filter_words nhưng chưa init flashcard
        elif 'flashcard_filter_words' in st.session_state and st.session_state.flashcard_filter_words:
            default_menu = "🧠 Học & Ôn tập"
        # Kiểm tra navigate từ các nút bấm
        elif 'navigate_to' in st.session_state:
            default_menu = st.session_state.navigate_to
            del st.session_state.navigate_to
        
        menu = st.radio(
            "Chọn chức năng:",
            ["🏠 Trang chủ", 
             "🧠 Học & Ôn tập",
             "🧩 Kiểm tra (Quiz)",
             "📚 Kho từ vựng",
             "📊 Thống kê",
             "📜 Lịch sử Quiz",
             "⚙️ Quản lý từ"],
            index=["🏠 Trang chủ", 
                   "🧠 Học & Ôn tập",
                   "🧩 Kiểm tra (Quiz)",
                   "📚 Kho từ vựng",
                   "📊 Thống kê",
                   "📜 Lịch sử Quiz",
                   "⚙️ Quản lý từ"].index(default_menu),
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Thống kê nhanh
        df = load_words()
        due_count = len(get_due_words())
        
        st.metric("📚 Tổng số từ", len(df))
        st.metric("⏰ Cần ôn hôm nay", due_count)
        
        st.markdown("---")
        st.caption("💡 **Tip:** Ôn từ đều đặn mỗi ngày để nhớ lâu hơn!")
    
    # Main content
    if menu == "🏠 Trang chủ":
        show_home()
    
    elif menu == "🧠 Học & Ôn tập":
        show_flashcard_page()
    
    elif menu == "🧩 Kiểm tra (Quiz)":
        show_quiz_page()
    
    elif menu == "📚 Kho từ vựng":
        show_vocabulary_page()
    
    elif menu == "📊 Thống kê":
        display_dashboard()

    elif menu == "📜 Lịch sử Quiz":
        show_quiz_history_page()
    
    elif menu == "⚙️ Quản lý từ":
        show_word_management()
    
    # Footer nhỏ ở góc phải dưới
    st.markdown("""
        <div class="footer">
            Made with ❤️ by Nguyễn Vẹn Toàn
        </div>
    """, unsafe_allow_html=True)

def show_home():
    """Trang chủ"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 👋 Chào mừng đến với VocabGo!")
        st.markdown("""
        Ứng dụng giúp bạn học và ghi nhớ từ vựng hiệu quả với **phương pháp lặp lại ngắt quãng** (Spaced Repetition System).
        
        ### 🌟 Tính năng chính:
        
        - **🧠 Học & Ôn tập:** Flashcard thông minh, tự động lên lịch ôn tập
        - **🧩 Kiểm tra:** Quiz trắc nghiệm và điền từ
        - **📚 Kho từ vựng:** Quản lý và tìm kiếm từ dễ dàng
        - **📊 Thống kê:** Theo dõi tiến độ học tập của bạn
        - **⚙️ Quản lý:** Thêm, sửa, xóa từ và import/export CSV
        
        ### 🚀 Bắt đầu ngay:
        """)
        
        df = load_words()
        due_today = len(get_due_words())
        
        if df.empty:
            st.info("📝 Bạn chưa có từ vựng nào. Hãy vào **Quản lý từ** để thêm từ mới!")
        elif due_today > 0:
            st.success(f"🎯 Bạn có **{due_today} từ** cần ôn hôm nay! Hãy vào **Học & Ôn tập** để bắt đầu.")
        else:
            st.success("🎉 Bạn đã hoàn thành việc ôn tập hôm nay! Tuyệt vời!")
    
    with col2:
        st.markdown("### 📈 Tiến độ học tập")
        
        if not df.empty:
            total = len(df)
            mastered = len(df[df['review_count'] >= 6])
            in_progress = total - mastered
            
            st.metric("Tổng số từ", total)
            st.metric("Đã thành thục", mastered, delta=f"{(mastered/total*100):.0f}%")
            st.metric("Đang học", in_progress)
            
            # Progress bar
            progress = mastered / total if total > 0 else 0
            st.progress(progress)
            st.caption(f"Hoàn thành {progress*100:.0f}%")

def show_flashcard_page():
    """Trang Flashcard"""
    st.markdown("## 🧠 Học & Ôn tập")
    
    # Kiểm tra nếu đang có flashcard_list (đang trong session flashcard)
    if 'flashcard_list' in st.session_state and st.session_state.flashcard_list:
        # Hiển thị flashcard trực tiếp
        display_flashcard()
        return
    
    # Kiểm tra nếu đang ôn từ sai từ lịch sử quiz (có filter nhưng chưa init)
    if 'flashcard_filter_words' in st.session_state and st.session_state.flashcard_filter_words:
        # Hiển thị thông báo
        st.info(f"🎯 Đang ôn **{len(st.session_state.flashcard_filter_words)} từ** hay sai từ lịch sử quiz")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔙 Quay lại", use_container_width=True, key="btn_back_from_filtered"):
                # Xóa filter và flashcard session
                clear_flashcard_session()
                st.rerun()
        
        # Khởi tạo flashcard với từ được lọc
        all_words_df = load_words()
        valid_words = [w for w in st.session_state.flashcard_filter_words if w in all_words_df['word'].values]
        
        if not valid_words:
            st.warning("⚠️ Không tìm thấy từ nào trong kho từ vựng!")
            if st.button("🏠 Về trang chủ", use_container_width=True, key="btn_home_no_words"):
                clear_flashcard_session()
                st.rerun()
            return
        
        # Cập nhật lại danh sách từ hợp lệ và init
        st.session_state.flashcard_filter_words = valid_words
        init_flashcard_session("filtered", valid_words)
        
        # Sau khi init, rerun để hiển thị flashcard
        st.rerun()
        return
    
    # Chế độ bình thường - chọn tab để bắt đầu
    tab1, tab2 = st.tabs(["⏰ Ôn từ hôm nay", "📖 Xem tất cả từ"])
    
    with tab1:
        st.markdown("### Ôn tập các từ cần học hôm nay")
        
        due_words = get_due_words()
        
        if due_words.empty:
            st.success("🎉 Bạn đã hoàn thành việc ôn tập hôm nay!")
            st.info("💡 Hãy quay lại vào ngày mai hoặc chọn tab 'Xem tất cả từ' để ôn tổng.")
        else:
            st.info(f"📚 Có **{len(due_words)} từ** cần ôn hôm nay")
            
            if st.button("🚀 Bắt đầu ôn tập", type="primary", use_container_width=True, key="btn_start_review"):
                init_flashcard_session(mode="review")
                st.rerun()
    
    with tab2:
        st.markdown("### Xem và ôn tất cả từ vựng")
        
        all_words = load_words()
        
        if all_words.empty:
            st.warning("⚠️ Chưa có từ vựng nào. Hãy thêm từ mới!")
        else:
            st.info(f"📚 Tổng cộng **{len(all_words)} từ** trong kho")
            
            if st.button("🚀 Xem tất cả Flashcard", type="primary", use_container_width=True, key="btn_start_all"):
                init_flashcard_session(mode="all")
                st.rerun()

def show_quiz_page():
    """Trang Quiz"""
    st.markdown("## 🧩 Kiểm tra kiến thức")
    
    if 'quiz_questions' not in st.session_state:
        # Hiển thị số từ cần ôn hôm nay
        due_words = get_due_words()
        if not due_words.empty:
            st.info(f"⏰ Có **{len(due_words)} từ** cần ôn hôm nay. Bạn có thể làm quiz với những từ này!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            num_questions = st.number_input(
                "Số câu hỏi:",
                min_value=1,
                max_value=100,
                value=10,
                step=1,
                help="Sử dụng nút +/- hoặc nhập trực tiếp"
            )
        
        with col2:
            quiz_type = st.selectbox(
                "Loại bài kiểm tra:",
                ["Trắc nghiệm", "Điền từ"]
            )
        
        with col3:
            # Tùy chọn nguồn từ vựng
            quiz_source = st.selectbox(
                "Nguồn từ vựng:",
                ["Tất cả từ", "Từ cần ôn hôm nay"]
            )
        
        st.markdown("---")
        
        quiz_type_code = "multiple_choice" if quiz_type == "Trắc nghiệm" else "typing"
        
        if st.button("🚀 Bắt đầu Quiz", type="primary", use_container_width=True):
            # Xác định nguồn từ
            if quiz_source == "Từ cần ôn hôm nay":
                if due_words.empty:
                    st.warning("⚠️ Không có từ nào cần ôn hôm nay!")
                    return
                success = init_quiz_session(num_questions, quiz_type_code, filter_due=True)
            else:
                success = init_quiz_session(num_questions, quiz_type_code, filter_due=False)
            
            if success:
                st.rerun()
            else:
                st.error("❌ Không đủ từ để tạo quiz! Cần ít nhất 4 từ trong kho.")
    else:
        display_quiz()

def show_vocabulary_page():
    """Trang Kho từ vựng"""
    st.markdown("## 📚 Kho từ vựng")
    
    # Thanh tìm kiếm
    search_term = st.text_input("🔍 Tìm kiếm từ hoặc nghĩa:", placeholder="Nhập từ cần tìm...")
    
    df = load_words()
    
    if search_term:
        df = search_words(search_term)
        st.caption(f"Tìm thấy {len(df)} kết quả")
    
    # Bộ lọc
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_option = st.selectbox(
            "Lọc theo:",
            ["Tất cả", "Cần ôn hôm nay", "Đã thành thục", "Chưa thành thục"]
        )
    
    with col2:
        sort_by = st.selectbox(
            "Sắp xếp theo:",
            ["Mới nhất", "Cũ nhất", "A-Z", "Z-A"]
        )
    
    # Áp dụng bộ lọc
    if filter_option == "Cần ôn hôm nay":
        df = get_due_words()
    elif filter_option == "Đã thành thục":
        df = df[df['review_count'] >= 6]
    elif filter_option == "Chưa thành thục":
        df = df[df['review_count'] < 6]
    
    # Sắp xếp
    if not df.empty:
        if sort_by == "Mới nhất":
            df = df.sort_values('start_date', ascending=False)
        elif sort_by == "Cũ nhất":
            df = df.sort_values('start_date', ascending=True)
        elif sort_by == "A-Z":
            df = df.sort_values('word', ascending=True)
        elif sort_by == "Z-A":
            df = df.sort_values('word', ascending=False)
    
    st.markdown("---")
    
    # Hiển thị danh sách từ
    if df.empty:
        st.info("📭 Không có từ nào phù hợp với bộ lọc")
    else:
        st.caption(f"Hiển thị {len(df)} từ")
        
        for idx, row in df.iterrows():
            # Tạo tiêu đề expander với POS và phiên âm (chỉ dùng markdown, không dùng HTML)
            title = f"**{row['word']}**"
            
            # Thêm POS (từ loại)
            if row.get('pos') and row['pos']:
                title += f" **[{row['pos']}]**"
            
            # Thêm phiên âm - in nghiêng
            if row.get('phonetic') and row['phonetic']:
                title += f" *{row['phonetic']}*"
            
            title += f" — {row['meaning']}"
            
            with st.expander(title, expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Hiển thị từ loại (nếu có)
                    if row.get('pos') and row['pos']:
                        st.markdown(f"**Từ loại:** {row['pos']}")
                    
                    # Hiển thị phiên âm (nếu có)
                    if row.get('phonetic') and row['phonetic']:
                        st.markdown(f"**Phiên âm:** {row['phonetic']}")
                    
                    st.markdown(f"**Nghĩa:** {row['meaning']}")
                    
                    if row['example']:
                        st.markdown(f"**Ví dụ:** {row['example']}")
                    
                    st.caption(f"📅 Bắt đầu: {row['start_date']} | "
                             f"🔄 Đã ôn: {row['review_count']} lần | "
                             f"📆 Ôn tiếp: {row['next_review']}")
                
                with col2:
                    if st.button("🔄 Reset", key=f"reset_{idx}", use_container_width=True):
                        success, msg = reset_word_progress(idx)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

def show_word_management():
    """Trang Quản lý từ"""
    st.markdown("## ⚙️ Quản lý từ vựng")
    
    tab1, tab2, tab3 = st.tabs(["➕ Thêm từ mới", "✏️ Sửa/Xóa từ", "📥 Import/Export"])
    
    with tab1:
        st.markdown("### Thêm từ mới")
        
        with st.form("add_word_form", clear_on_submit=True):
            word = st.text_input("Từ tiếng Anh *", placeholder="Ví dụ: beautiful")
            pos = st.text_input("Từ loại (POS)", placeholder="Ví dụ: adj, n, v")
            phonetic = st.text_input("Phiên âm (IPA)", placeholder="Ví dụ: /ˈbjuːtɪfl/")
            meaning = st.text_input("Nghĩa tiếng Việt *", placeholder="Ví dụ: đẹp, xinh đẹp")
            example = st.text_area("Câu ví dụ (tùy chọn)", 
                                  placeholder="Ví dụ: She is a beautiful girl.")
            
            submitted = st.form_submit_button("➕ Thêm từ", type="primary", use_container_width=True)
            
            if submitted:
                if not word or not meaning:
                    st.error("❌ Vui lòng điền đầy đủ từ và nghĩa!")
                else:
                    success, msg = add_word(word.strip(), pos.strip(), phonetic.strip(), meaning.strip(), example.strip())
                    
                    if success:
                        st.success(msg)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(msg)
    
    with tab2:
        st.markdown("### Chỉnh sửa hoặc xóa từ")
        
        df = load_words()
        
        if df.empty:
            st.info("📭 Chưa có từ nào trong kho")
        else:
            word_options = [f"{row['word']} — {row['meaning']}" for idx, row in df.iterrows()]
            
            selected = st.selectbox("Chọn từ cần sửa/xóa:", word_options)
            
            if selected:
                selected_idx = word_options.index(selected)
                selected_word = df.iloc[selected_idx]
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### ✏️ Chỉnh sửa")
                    
                    with st.form(f"edit_form_{selected_idx}"):
                        new_word = st.text_input("Từ:", value=selected_word['word'])
                        new_pos = st.text_input("Từ loại:", value=selected_word.get('pos', ''))
                        new_phonetic = st.text_input("Phiên âm:", value=selected_word.get('phonetic', ''))
                        new_meaning = st.text_input("Nghĩa:", value=selected_word['meaning'])
                        new_example = st.text_area("Ví dụ:", value=selected_word['example'])
                        
                        if st.form_submit_button("💾 Lưu", type="primary", use_container_width=True):
                            success, msg = update_word(selected_idx, new_word, new_pos, new_phonetic, new_meaning, new_example)
                            
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                
                with col2:
                    st.markdown("#### 🗑️ Xóa từ")
                    st.warning("⚠️ Hành động này không thể hoàn tác!")
                    
                    if st.button("🗑️ Xóa từ này", type="secondary", use_container_width=True):
                        success, msg = delete_word(selected_idx)
                        
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
    
    with tab3:
        st.markdown("### Import & Export CSV")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📥 Import từ CSV")
            
            uploaded_file = st.file_uploader("Chọn file CSV", type=['csv'])
            
            if uploaded_file is not None:
                if st.button("📥 Import", type="primary", use_container_width=True):
                    # Lưu file tạm
                    with open("temp_import.csv", "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    success, msg = import_csv("temp_import.csv")
                    
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        
        with col2:
            st.markdown("#### 📤 Export sang CSV")
            
            df = load_words()
            
            if df.empty:
                st.info("Chưa có dữ liệu để export")
            else:
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                
                st.download_button(
                    label="📤 Download CSV",
                    data=csv,
                    file_name="vocab_backup.csv",
                    mime="text/csv",
                    use_container_width=True,
                    type="primary"
                )

if __name__ == "__main__":
    main()