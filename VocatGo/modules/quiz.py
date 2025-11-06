"""
quiz.py - Tạo và xử lý bài kiểm tra (Quiz)
Updated: Hidden hints for typing questions
"""
import streamlit as st
import random
from modules.word_manager import load_words
from modules.utils import shuffle_list
from modules.quiz_history import save_quiz_result

def init_quiz_session(num_questions, quiz_type, filter_due=False):
    """
    Khởi tạo session cho quiz
    
    Args:
        num_questions: số câu hỏi
        quiz_type: "multiple_choice" hoặc "typing"
        filter_due: True nếu chỉ lấy từ cần ôn hôm nay
    """
    # Import thêm get_due_words
    from modules.spaced_repetition import get_due_words
    
    # Lấy danh sách từ
    if filter_due:
        df = get_due_words()
        if df.empty:
            return False
    else:
        df = load_words()
    
    if len(df) < 4:  # Cần ít nhất 4 từ cho multiple choice
        return False
    
    # Chọn ngẫu nhiên câu hỏi
    num_questions = min(num_questions, len(df))
    selected_indices = random.sample(list(df.index), num_questions)
    
    # Tạo câu hỏi
    questions = []
    for idx in selected_indices:
        word_data = df.loc[idx]  # Dùng .loc thay vì .iloc
        
        if quiz_type == "multiple_choice":
            question = create_multiple_choice_question(idx, df)
        else:  # typing
            question = create_typing_question(idx, word_data)
        
        questions.append(question)
    
    # Lưu vào session state
    st.session_state.quiz_questions = questions
    st.session_state.quiz_current = 0
    st.session_state.quiz_answers = []
    st.session_state.quiz_type = quiz_type
    st.session_state.quiz_score = 0
    st.session_state.quiz_wrong_words = []
    st.session_state.quiz_answered = False
    st.session_state.quiz_show_hint = False  # Mới: flag để hiển thị gợi ý
    st.session_state.quiz_filter_due = filter_due  # Lưu thông tin nguồn từ
    
    return True

def create_multiple_choice_question(correct_idx, df):
    """Tạo câu hỏi trắc nghiệm"""
    correct_word = df.loc[correct_idx]
    
    # Lấy 3 đáp án sai ngẫu nhiên
    other_indices = [i for i in df.index if i != correct_idx]
    
    # Nếu không đủ từ khác, lấy từ toàn bộ kho
    if len(other_indices) < 3:
        all_words = load_words()
        other_indices = [i for i in all_words.index if i != correct_idx]
    
    wrong_indices = random.sample(other_indices, min(3, len(other_indices)))
    
    # Tạo danh sách đáp án
    choices = [correct_word['meaning']]
    
    # Load lại toàn bộ từ để lấy đáp án sai (nếu cần)
    all_words = load_words()
    for idx in wrong_indices:
        if idx in df.index:
            choices.append(df.loc[idx]['meaning'])
        else:
            choices.append(all_words.loc[idx]['meaning'])
    
    # Shuffle
    random.shuffle(choices)
    correct_answer = choices.index(correct_word['meaning'])
    
    return {
        'type': 'multiple_choice',
        'word': correct_word['word'],
        'correct_meaning': correct_word['meaning'],
        'choices': choices,
        'correct_index': correct_answer,
        'example': correct_word['example']
    }

def create_typing_question(idx, word_data):
    """Tạo câu hỏi điền từ"""
    return {
        'type': 'typing',
        'word': word_data['word'],
        'meaning': word_data['meaning'],
        'example': word_data['example']
    }

def display_quiz():
    """Hiển thị quiz"""
    
    if 'quiz_questions' not in st.session_state:
        st.error("❌ Lỗi: Quiz chưa được khởi tạo!")
        return
    
    questions = st.session_state.quiz_questions
    current_idx = st.session_state.quiz_current
    
    # Kiểm tra đã hoàn thành chưa
    if current_idx >= len(questions):
        show_quiz_results()
        return
    
    # Header
    col1, col2, col3 = st.columns([2, 3, 1])
    
    with col1:
        st.markdown(f"### Câu {current_idx + 1}/{len(questions)}")
    
    with col2:
        progress = current_idx / len(questions)
        st.progress(progress)
    
    with col3:
        if st.button("❌ Thoát"):
            clear_quiz_session()
            st.rerun()
    
    st.markdown("---")
    
    # Hiển thị câu hỏi
    question = questions[current_idx]
    
    if question['type'] == 'multiple_choice':
        display_multiple_choice(question, current_idx)
    else:
        display_typing_question(question, current_idx)

def display_multiple_choice(question, current_idx):
    """Hiển thị câu hỏi trắc nghiệm"""
    st.markdown(f"### 📝 Chọn nghĩa đúng của từ:")
    st.markdown(f"<h1 style='text-align: center; color: #667eea;'>{question['word']}</h1>", 
               unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Nếu chưa trả lời, hiển thị form
    if not st.session_state.quiz_answered:
        user_answer = st.radio(
            "Chọn đáp án:",
            options=range(len(question['choices'])),
            format_func=lambda x: question['choices'][x],
            key=f"answer_{current_idx}"
        )
        
        if st.button("✅ Trả lời", type="primary", use_container_width=True, key=f"submit_{current_idx}"):
            # Lưu đáp án và đánh giá
            is_correct = (user_answer == question['correct_index'])
            
            st.session_state.quiz_answers.append({
                'question': question['word'],
                'user_answer': question['choices'][user_answer],
                'correct_answer': question['correct_meaning'],
                'is_correct': is_correct
            })
            
            if is_correct:
                st.session_state.quiz_score += 1
            else:
                st.session_state.quiz_wrong_words.append({
                    'word': question['word'],
                    'meaning': question['correct_meaning'],
                    'example': question['example']
                })
            
            st.session_state.quiz_answered = True
            st.rerun()
    
    # Nếu đã trả lời, hiển thị kết quả
    else:
        last_answer = st.session_state.quiz_answers[-1]
        
        if last_answer['is_correct']:
            st.success("✅ Chính xác!")
        else:
            st.error(f"❌ Sai rồi! Đáp án đúng là: **{question['correct_meaning']}**")
        
        # Hiển thị ví dụ nếu có
        if question['example']:
            st.info(f"💡 Ví dụ: {question['example']}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Nút tiếp theo
        if st.button("➡️ Câu tiếp theo", type="primary", use_container_width=True, key=f"next_{current_idx}"):
            st.session_state.quiz_current += 1
            st.session_state.quiz_answered = False
            st.rerun()

def display_typing_question(question, current_idx):
    """Hiển thị câu hỏi điền từ"""
    st.markdown(f"### ✏️ Điền từ tiếng Anh tương ứng:")
    
    st.markdown(f"<h2 style='text-align: center; color: #667eea;'>{question['meaning']}</h2>", 
               unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Nếu chưa trả lời
    if not st.session_state.quiz_answered:
        # Nút hiển thị gợi ý (chỉ khi có example)
        if question['example']:
            # Khởi tạo flag show_hint nếu chưa có
            if 'quiz_show_hint' not in st.session_state:
                st.session_state.quiz_show_hint = False
            
            col_hint1, col_hint2, col_hint3 = st.columns([1, 1, 1])
            with col_hint2:
                if not st.session_state.quiz_show_hint:
                    if st.button("💡 Xem gợi ý", use_container_width=True, key=f"hint_{current_idx}"):
                        st.session_state.quiz_show_hint = True
                        st.rerun()
            
            # Hiển thị gợi ý nếu đã bấm nút
            if st.session_state.quiz_show_hint:
                st.info(f"💡 Gợi ý: {question['example']}")
                st.markdown("<br>", unsafe_allow_html=True)
        
        user_answer = st.text_input(
            "Nhập từ tiếng Anh:",
            placeholder="Type the English word...",
            key=f"answer_{current_idx}"
        ).strip().lower()
        
        if st.button("✅ Trả lời", type="primary", use_container_width=True, key=f"submit_{current_idx}"):
            if not user_answer:
                st.warning("⚠️ Vui lòng nhập đáp án!")
                return
            
            correct_word = question['word'].lower()
            is_correct = (user_answer == correct_word)
            
            st.session_state.quiz_answers.append({
                'question': question['meaning'],
                'user_answer': user_answer,
                'correct_answer': question['word'],
                'is_correct': is_correct
            })
            
            if is_correct:
                st.session_state.quiz_score += 1
            else:
                st.session_state.quiz_wrong_words.append({
                    'word': question['word'],
                    'meaning': question['meaning'],
                    'example': question['example']
                })
            
            st.session_state.quiz_answered = True
            st.rerun()
    
    # Nếu đã trả lời, hiển thị kết quả
    else:
        last_answer = st.session_state.quiz_answers[-1]
        
        if last_answer['is_correct']:
            st.success(f"✅ Chính xác! Đáp án: **{question['word']}**")
        else:
            st.error(f"❌ Sai rồi! Bạn trả lời: **{last_answer['user_answer']}** | Đáp án đúng: **{question['word']}**")
        
        # Hiển thị ví dụ sau khi trả lời
        if question['example']:
            st.info(f"💡 Ví dụ: {question['example']}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Nút tiếp theo
        if st.button("➡️ Câu tiếp theo", type="primary", use_container_width=True, key=f"next_{current_idx}"):
            st.session_state.quiz_current += 1
            st.session_state.quiz_answered = False
            st.session_state.quiz_show_hint = False  # Reset flag cho câu tiếp theo
            st.rerun()

def show_quiz_results():
    """Hiển thị kết quả quiz"""
    st.markdown("## 🎯 Kết quả Quiz")
    
    score = st.session_state.quiz_score
    total = len(st.session_state.quiz_questions)
    percentage = (score / total * 100) if total > 0 else 0
    
    # Hiển thị thông tin nguồn từ
    if st.session_state.get('quiz_filter_due', False):
        st.info("📚 Bài quiz từ: **Từ cần ôn hôm nay**")
    
    # Lưu kết quả vào lịch sử (chỉ lưu 1 lần)
    if 'quiz_result_saved' not in st.session_state:
        save_quiz_result(
            quiz_type=st.session_state.quiz_type,
            score=score,
            total=total,
            wrong_words=st.session_state.quiz_wrong_words
        )
        st.session_state.quiz_result_saved = True
    
    # Hiển thị điểm
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Số câu đúng", f"{score}/{total}")
    
    with col2:
        st.metric("Điểm số", f"{percentage:.0f}%")
    
    with col3:
        if percentage >= 80:
            st.metric("Xếp loại", "🌟 Xuất sắc")
        elif percentage >= 60:
            st.metric("Xếp loại", "👍 Khá")
        else:
            st.metric("Xếp loại", "💪 Cần cố gắng")
    
    # Hiển thị balloons nếu đạt điểm cao
    if percentage >= 80:
        st.balloons()
    
    st.markdown("---")
    
    # Danh sách từ sai
    if st.session_state.quiz_wrong_words:
        st.markdown("### ❌ Các từ cần ôn lại:")
        
        for word_info in st.session_state.quiz_wrong_words:
            with st.expander(f"**{word_info['word']}** — {word_info['meaning']}"):
                st.markdown(f"**Nghĩa:** {word_info['meaning']}")
                if word_info['example']:
                    st.markdown(f"**Ví dụ:** {word_info['example']}")
    else:
        st.success("🎉 Tuyệt vời! Bạn đã trả lời đúng tất cả!")
    
    st.markdown("---")
    
    # Nút điều hướng
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Làm lại Quiz", use_container_width=True):
            num_questions = len(st.session_state.quiz_questions)
            quiz_type = st.session_state.quiz_type
            filter_due = st.session_state.get('quiz_filter_due', False)
            clear_quiz_session()
            init_quiz_session(num_questions, quiz_type, filter_due)
            st.rerun()
    
    with col2:
        if st.button("📊 Xem lịch sử", use_container_width=True):
            # Set flag để chuyển sang trang lịch sử
            st.session_state.navigate_to = "📜 Lịch sử Quiz"
            clear_quiz_session()
            st.rerun()
    
    with col3:
        if st.button("🏠 Về trang chủ", type="primary", use_container_width=True):
            clear_quiz_session()
            st.rerun()

def clear_quiz_session():
    """Xóa session state của quiz"""
    keys_to_remove = [
        'quiz_questions',
        'quiz_current',
        'quiz_answers',
        'quiz_type',
        'quiz_score',
        'quiz_wrong_words',
        'quiz_answered',
        'quiz_result_saved',
        'quiz_show_hint',
        'quiz_num_questions'
    ]
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]