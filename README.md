# VocatGo

**VocatGo – Ứng dụng học từ vựng tiếng Anh thông minh với Flashcard & Quiz**  

VocatGo giúp bạn học từ vựng theo phương pháp **Spaced Repetition (SRS)**, làm quiz để củng cố kiến thức, và theo dõi tiến trình học tập.  
Ứng dụng trực quan, dễ sử dụng, có icon và trình bày đẹp mắt.

---

## 🎯 Mục đích
- Ghi nhớ từ vựng lâu dài bằng **SRS**.
- Ôn tập từ vựng và kiểm tra kiến thức qua **Quiz**.
- Theo dõi tiến bộ và thống kê hiệu suất học tập.
- Quản lý từ vựng dễ dàng: thêm, sửa, xóa, import/export CSV.

---

## 📂 Cấu trúc dự án

- **app.py** – Giao diện Streamlit chính
- **data/**
  - **vocab/** – Dữ liệu từ vựng (words.csv)
  - **history_quiz/** – Lưu `quiz_log.csv` và `quiz_wrong_words.csv`
- **modules/**
  - **spaced_repetition.py** – Tính toán lịch ôn
  - **flashcard.py** – Hiển thị & cập nhật flashcard
  - **quiz.py** – Logic quiz
  - **dashboard.py** – Thống kê & biểu đồ
  - **utils.py** – Hàm phụ trợ
- **assets/** – Icon, CSS, audio, logo (VocatGo.png)


- Các thư mục 📁 và file 📄 được minh họa để trực quan.
- `words.csv` chứa dữ liệu từ vựng, `history_quiz/` lưu lịch sử quiz.
- `modules/` chứa logic chính của ứng dụng.

---

## ⚡ Chức năng chính

### 1️⃣ Học & Ôn tập (Flashcard Mode)
- Hiển thị từ, ẩn nghĩa và ví dụ, hiện khi click.
- Nút ✅ “Đã nhớ” / ❌ “Quên” → cập nhật `review_count` & `next_review` theo **SRS**.
- Tiến độ: số từ đã ôn / tổng số từ cần ôn hôm nay.
- Chế độ xem toàn bộ flashcard để ôn nhanh.
- Ôn tập **từ hay sai nhất** bằng flashcard.

### 2️⃣ Kiểm tra (Quiz Mode)
- Chọn số lượng câu hỏi & dạng bài:
  - Trắc nghiệm nghĩa (multiple choice)
  - Nhập từ đúng (typing)
- Quiz dựa trên **từ cần ôn hôm nay** hoặc toàn bộ từ.
- Random câu hỏi, tính điểm, hiển thị kết quả + từ sai.
- Lưu danh sách từ sai để ôn lại riêng.

### 3️⃣ Kho từ vựng / Tổng ôn
- Duyệt toàn bộ từ vựng dạng flashcard.
- Tìm kiếm & lọc theo:
  - Số lần ôn (`review_count`)
  - Ngày bắt đầu (`start_date`)
  - Từ cần ôn hôm nay (`next_review <= hôm_nay`)

### 4️⃣ Dashboard (Thống kê)
- Số từ tổng cộng, số từ cần ôn hôm nay, số từ thành thục.
- Biểu đồ tiến độ ôn hàng ngày (bar chart / line chart).

### 5️⃣ Quản lý từ
- Thêm từ mới (tự động set `start_date`, `review_count=0`, `next_review=hôm_nay+1` nếu bỏ trống).
- Chỉnh sửa / Xóa từ.
- Import/Export CSV để sao lưu hoặc khôi phục.

### 6️⃣ Lịch sử Quiz
- Biểu đồ tiến bộ theo ngày.
- Thống kê **từ hay sai nhất**.
- Lưu:
  - `quiz_log.csv` (tổng hợp mỗi lần làm quiz)
  - `quiz_wrong_words.csv` (chi tiết từng từ sai)
- Ôn lại từ sai nhiều nhất bằng **flashcard** hoặc **quiz đặc biệt**.

---

## 📝 Cấu trúc file CSV từ vựng

`data/vocab/words.csv` gồm các cột:

| Cột            | Mô tả                                                                 | Bắt buộc | Ghi chú |
|----------------|----------------------------------------------------------------------|----------|---------|
| `word`         | Từ tiếng Anh                                                          | ✅       | Không được để trống |
| `pos`          | Loại từ (noun, verb, adj…)                                           | ✅       |       |
| `phonetic`     | Phiên âm                                                             | ✅       |       |
| `meaning`      | Nghĩa tiếng Việt                                                     | ✅       | Nếu có dấu phẩy, phải đặt trong `""` |
| `example`      | Ví dụ sử dụng từ                                                     | ✅       | Nếu có dấu phẩy, đặt trong `""` |
| `start_date`   | Ngày thêm từ (format: dd-mm-yyyy)                                    | ✅       |       |
| `review_count` | Số lần ôn đã ghi nhận                                               | ✅       | Mặc định 0 khi thêm từ mới |
| `next_review`  | Ngày ôn tiếp theo (format: dd-mm-yyyy)                               | ❌       | Có thể bỏ trống → chương trình tự tính dựa trên `start_date` và SRS |

**Ví dụ 1 dòng CSV hợp lệ:**
agreement,n,/əˈɡriː.mənt/,"sự thỏa thuận, hợp đồng","They reached an agreement after long discussions.",07-11-2025,0,08-11-2025

---

> 💡 Lưu ý:
> - Khi mở CSV trên VSCode hoặc Excel, kiểm tra `meaning` và `example` đã được đặt trong `" "` nếu chứa dấu phẩy.  
> - GitHub và Excel hiển thị CSV tương tự nhau, nhưng dấu ngoặc kép giúp tránh **thêm cột ngoài ý muốn**, tránh code chạy sai.

---

## ⚙️ Hướng dẫn cài đặt
```bash
git clone https://github.com/toannv09/VocatGo.git
cd VocatGo
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt
streamlit run app.py
