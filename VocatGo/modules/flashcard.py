"""
flashcard.py - Logic hiển thị và xử lý flashcard
"""
import streamlit as st
from modules.word_manager import load_words
from modules.spaced_repetition import get_due_words, update_word_review
from modules.utils import shuffle_list, format_progress

def init_flashcard_session(mode="review", filter_words=None):
    """
    Khởi tạo session state cho flashcard
    
    Args:
        mode: "review" (ôn từ cần học hôm nay), "all" (xem tất cả từ), "filtered" (từ được lọc)
        filter_words: list các từ cần lọc (chỉ dùng khi mode="filtered")
    """
    if mode == "review":
        words_df = get_due_words()
    elif mode == "filtered" and filter_words:
        # Lọc theo danh sách từ
        all_words = load_words()
        words_df = all_words[all_words['word'].isin(filter_words)]
    else:
        words_df = load_words()
    
    # Set mode trước khi check empty
    st.session_state.flashcard_mode = mode
    
    # QUAN TRỌNG: Lưu filter_words ngay cả khi empty
    if mode == "filtered" and filter_words:
        st.session_state.flashcard_filter_words = filter_words
    
    if words_df.empty:
        st.session_state.flashcard_list = []
        return
    
    # Shuffle và chuyển thành list indices
    indices = list(words_df.index)
    shuffled_indices = shuffle_list(indices)
    
    st.session_state.flashcard_list = shuffled_indices
    st.session_state.flashcard_current = 0
    st.session_state.flashcard_show_answer = False
    st.session_state.flashcard_completed = 0

def display_flashcard():
    """Hiển thị flashcard và xử lý tương tác"""
    
    if not st.session_state.flashcard_list:
        st.warning("⚠️ Không có từ nào để ôn tập!")
        if st.button("🏠 Về trang chủ"):
            clear_flashcard_session()
            st.rerun()
        return
    
    # Hiển thị banner nếu đang ở mode filtered
    if st.session_state.get('flashcard_mode') == 'filtered':
        col1, col2 = st.columns([4, 1])
        with col1:
            st.info(f"🎯 Đang ôn **{len(st.session_state.flashcard_list)} từ** hay sai từ lịch sử quiz")
        with col2:
            if st.button("🔙 Thoát", key="btn_exit_filtered_mode"):
                clear_flashcard_session()
                st.rerun()
        st.markdown("---")
    
    # Lấy từ hiện tại
    current_idx = st.session_state.flashcard_current
    total = len(st.session_state.flashcard_list)
    
    # Kiểm tra đã hoàn thành chưa
    if current_idx >= total:
        show_flashcard_complete()
        return
    
    # Load dữ liệu
    df = load_words()
    word_index = st.session_state.flashcard_list[current_idx]
    
    # Kiểm tra index có hợp lệ không
    if word_index not in df.index:
        st.error(f"❌ Lỗi: Không tìm thấy từ với index {word_index}")
        if st.button("🏠 Về trang chủ"):
            clear_flashcard_session()
            st.rerun()
        return
    
    word_data = df.loc[word_index]
    
    # Header với progress
    col1, col2, col3 = st.columns([2, 3, 1])
    
    with col1:
        st.markdown(f"### Thẻ {current_idx + 1}/{total}")
    
    with col2:
        progress = (current_idx + st.session_state.flashcard_completed) / total
        st.progress(progress)
        st.caption(format_progress(current_idx + st.session_state.flashcard_completed, total))
    
    with col3:
        # Chỉ hiển thị nút thoát nếu KHÔNG phải mode filtered
        if st.session_state.get('flashcard_mode') != 'filtered':
            if st.button("❌ Thoát", key="btn_exit_flashcard"):
                clear_flashcard_session()
                st.rerun()
    
    st.markdown("---")
    
    # Card container
    with st.container():
        # Từ vựng (luôn hiển thị)
        st.markdown(f"<h1 style='text-align: center; color: #667eea;'>{word_data['word']}</h1>", 
                   unsafe_allow_html=True)
        
        # Hiển thị phiên âm và loại từ ngay dưới từ (nếu có)
        pos_phonetic = ""
        if word_data.get('pos') and word_data['pos']:
            pos_phonetic += f"<span style='color: #ff6b6b; font-weight: bold;'>[{word_data['pos']}]</span> "
        if word_data.get('phonetic') and word_data['phonetic']:
            pos_phonetic += f"<span style='font-style: italic;'>{word_data['phonetic']}</span>"

        if pos_phonetic:
            st.markdown(f"<p style='text-align: center; color: #888; font-size: 18px;'>{pos_phonetic}</p>", 
                    unsafe_allow_html=True)
    
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Nút lật thẻ
        if not st.session_state.get('flashcard_show_answer', False):
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔄 Lật thẻ xem đáp án", type="primary", use_container_width=True, key=f"flip_{current_idx}"):
                    st.session_state.flashcard_show_answer = True
                    st.rerun()
        
        # Hiển thị đáp án
        if st.session_state.get('flashcard_show_answer', False):
            st.markdown("---")
            
            # Nghĩa
            st.markdown(f"### 📖 Nghĩa:")
            st.markdown(f"<p style='font-size: 20px;'>{word_data['meaning']}</p>", 
                       unsafe_allow_html=True)
            
            # Ví dụ (nếu có)
            if word_data['example']:
                st.markdown(f"### 💡 Ví dụ:")
                st.info(word_data['example'])
            
            st.markdown("---")
            
            # Thông tin ôn tập
            if st.session_state.flashcard_mode == "review":
                st.caption(f"📊 Đã ôn: {word_data['review_count']} lần | "
                          f"📅 Ôn tiếp: {word_data['next_review']}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Nút đánh giá - CHỈ HIỆN Ở MODE REVIEW
            if st.session_state.flashcard_mode == "review":
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("❌ Quên rồi", type="secondary", use_container_width=True, key=f"forgot_{current_idx}"):
                        handle_flashcard_response(word_index, False)
                
                with col2:
                    if st.button("✅ Đã nhớ", type="primary", use_container_width=True, key=f"remember_{current_idx}"):
                        handle_flashcard_response(word_index, True)
            else:
                # Mode xem tất cả hoặc filtered - chỉ có nút Next
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("➡️ Thẻ tiếp theo", type="primary", use_container_width=True, key=f"next_{current_idx}"):
                        # Không gọi update_word_review, chỉ next
                        st.session_state.flashcard_current += 1
                        st.session_state.flashcard_show_answer = False
                        st.rerun()

def handle_flashcard_response(word_index, remembered):
    """Xử lý khi người dùng chọn Nhớ/Quên (CHỈ Ở MODE REVIEW)"""
    success, msg = update_word_review(word_index, remembered)
    
    if success:
        st.session_state.flashcard_completed += 1
        next_flashcard()
    else:
        st.error(msg)

def next_flashcard():
    """Chuyển sang flashcard tiếp theo"""
    st.session_state.flashcard_current += 1
    st.session_state.flashcard_show_answer = False
    st.rerun()

def show_flashcard_complete():
    """Hiển thị khi hoàn thành tất cả flashcard"""
    st.success("🎉 Chúc mừng! Bạn đã hoàn thành tất cả flashcard!")
    
    completed = st.session_state.flashcard_completed
    total = len(st.session_state.flashcard_list)
    
    if st.session_state.flashcard_mode == "review":
        st.markdown(f"### 📊 Kết quả ôn tập:")
        st.metric("Số từ đã ôn", completed)
        st.metric("Tổng số từ", total)
        
        if completed == total:
            st.balloons()
            st.markdown("### 🌟 Xuất sắc! Bạn đã ôn tất cả từ hôm nay!")
    elif st.session_state.flashcard_mode == "filtered":
        st.markdown(f"### 📚 Đã xem {total} từ hay sai")
        st.info("💡 Hãy luyện tập thêm với những từ này để ghi nhớ tốt hơn!")
    else:
        st.markdown(f"### 📚 Đã xem {total} thẻ từ vựng")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Ôn lại từ đầu", use_container_width=True):
            # Nếu là mode filtered, giữ lại filter
            if st.session_state.flashcard_mode == "filtered" and 'flashcard_filter_words' in st.session_state:
                init_flashcard_session("filtered", st.session_state.flashcard_filter_words)
            else:
                init_flashcard_session(st.session_state.flashcard_mode)
            st.rerun()
    
    with col2:
        if st.button("🏠 Về trang chủ", type="primary", use_container_width=True):
            clear_flashcard_session()
            st.rerun()

def clear_flashcard_session():
    """Xóa session state của flashcard"""
    keys_to_remove = [
        'flashcard_list',
        'flashcard_current',
        'flashcard_show_answer',
        'flashcard_mode',
        'flashcard_completed',
        'flashcard_filter_words'
    ]
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
