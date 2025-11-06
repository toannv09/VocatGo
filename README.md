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
```
---

## 🌐 Demo trực tuyến

Bạn có thể thử nghiệm VocatGo trực tiếp tại:  
[https://vocatgo.streamlit.app/](https://vocatgo.streamlit.app/)

---

### ℹ️ Hướng dẫn sử dụng trên phiên bản web deploy miễn phí

1. **Import từ vựng**  
   - Vào **Quản lý từ (Manage Words)**.  
   - Sử dụng chức năng **Import CSV** để nạp danh sách từ bạn muốn học.  
   - CSV phải tuân theo cấu trúc chuẩn (`word`, `pos`, `phonetic`, `meaning`, `example`, `start_date`, `review_count`, `next_review`).  
   - Sau khi import, từ vựng sẽ xuất hiện trong Flashcard/Quiz để bạn học.

2. **Học & Ôn tập**  
   - Sử dụng các chế độ **Flashcard** và **Quiz** như bình thường.  
   - Ứng dụng sẽ cập nhật `next_review` và `review_count` theo tiến độ học.

3. **Export dữ liệu đã cập nhật**  
   - Sau khi học xong, vào lại **Quản lý từ (Manage Words)** và **Export CSV** để tải về.  
   - Việc này giúp bạn lưu lại các cập nhật như `next_review`, bởi vì phiên bản deploy miễn phí có thể **không lưu file CSV vĩnh viễn**.

---

### ⚠️ Lưu ý khi sử dụng bản deploy miễn phí

Do VocatGo hiện đang deploy trên **Streamlit Cloud free**, có một số hạn chế mà người dùng cần lưu ý:

1. **Dữ liệu có thể bị chia sẻ giữa người dùng**  
   - CSV mà bạn import (danh sách từ vựng) được lưu trên cùng một filesystem tạm thời của app.  
   - Nếu nhiều người cùng import CSV hoặc sử dụng app cùng lúc, **dữ liệu có thể bị trộn**, dẫn đến từ vựng của người khác xuất hiện trong danh sách của bạn.  

2. **Ứng dụng “ngủ đông” khi không có người dùng**  
   - Nếu app không được truy cập trong một thời gian, Streamlit Cloud free sẽ tạm dừng app.  
   - Khi mở lại, app cần **khởi động lại (“wake up”)**, và dữ liệu tạm thời trong memory/đĩa có thể bị reset.  
   - Vì vậy, **không nên tin tưởng việc dữ liệu tự động được lưu lâu dài**.

3. **Hướng sử dụng an toàn**  
   - Luôn **export CSV sau khi học xong**, để lưu lại tiến độ học và `next_review`.  
   - Tránh import CSV nhiều người cùng lúc để hạn chế bị trộn dữ liệu.  
   - Chuẩn bị sẵn CSV cá nhân để upload lại khi app vừa wake up.  

> 💡 Tóm lại: trên phiên bản free, hãy xem app như **công cụ học thử trực tuyến**.  
> Để lưu tiến độ cá nhân, luôn export CSV và chuẩn bị dữ liệu riêng khi import.
> Bạn có thể học trực tuyến ngay, nhưng **dữ liệu học tập quan trọng nên được export thường xuyên** để đảm bảo không mất tiến độ.

---

## 🚀 Hướng phát triển

Hiện tại, phiên bản VocatGo deploy trên Streamlit Cloud miễn phí **không lưu dữ liệu lâu dài**, nên người dùng cần tự export CSV để lưu tiến độ học tập.  

Các hướng phát triển trong tương lai:

1. **Tích hợp lưu trữ đám mây**  
   - Sử dụng **Google Sheets** hoặc các nền tảng lưu trữ trực tuyến khác để **lưu dữ liệu học tập tự động**, bao gồm `words.csv`, `quiz_log.csv` và `quiz_wrong_words.csv`.  
   - Người dùng có thể mở app từ bất cứ thiết bị nào và dữ liệu sẽ được đồng bộ hóa.

2. **Nâng cấp nền tảng deploy**  
   - Tìm các nền tảng khác ngoài Streamlit Cloud free để **hỗ trợ nhiều người dùng cùng lúc** và **lưu trữ dữ liệu vĩnh viễn**.  
   - Có thể kết hợp với dịch vụ hosting trả phí để tránh giới hạn tài nguyên, giảm thời gian khởi động khi app bị idle.


