# PRD: Aletheia Multiple File Upload

## 1. Mục tiêu (Objective)
- Upload nhiều file một lần (Hỗ trợ các định dạng: PDF, DOCX, MD, TXT, CSV, JSON).
- Theo dõi tiến trình ingest theo thời gian thực (realtime) ở cấp độ từng file.
- Cung cấp cơ chế retry từng file riêng lẻ khi xảy ra lỗi, không gây ảnh hưởng đến các file khác trong batch.
- **Hậu xử lý:** Ngay sau khi hoàn thành, cung cấp CTA (Call To Action) cho phép truy vấn (Ask) trực tiếp trên corpus mới vừa upload.

## 2. Trải nghiệm Người dùng (UX Flow)

### A. Khu vực kéo thả (Dropzone)
- **Hành động:** Kéo-thả hoặc click chọn nhiều file cùng lúc.
- **Hiển thị danh sách file:**
  - Tên file, dung lượng.
  - Số trang (nếu frontend có thể parse trước hoặc ước lượng).
  - Trạng thái UI (chờ xử lý/queued, chuẩn bị upload).

### B. Thiết lập Metadata (Batch Config Panel)
- **Thuộc tính phân loại:** Domain/collection, Cài đặt ngôn ngữ (ví dụ: `vi`, `en`).
- **Gắn thẻ (Tags):** Cho phép nhập list tags (vd: `q1-report`, `internal`).
- **Tuỳ chọn xử lý nâng cao (Toggles):**
  - OCR if scanned
  - Skip duplicates (bỏ qua nếu file trùng checksum)
  - Auto-run enrichment (tự động làm giàu dữ liệu)

### C. Quá trình Upload & Queue (Batch Submission)
- **Nút bấm (Action):** `[ Upload N files ]`
- Tại thời điểm Submit, hệ thống gửi multipart request lên Backend, nhận lại `batch_id` kèm danh sách `job_id` tương ứng từng file để chuẩn bị theo dõi tiến độ.

### D. Bảng theo dõi tiến độ (Progress Board Realtime)
- **Tổng quan Batch:** Panel tóm tắt có (Total, Done, Failed, In-Progress, thông số ETA).
- **Bảng Chi tiết File (File Job Table):**
  - Hiển thị thanh Progress bar và trạng thái (queued, parsing, chunking, indexing, done, failed).
  - **Action per-file:** `[Retry]`, `[Cancel]`, `[View Logs]` (Xem nguyên nhân lỗi).

### E. Kết thúc (Completion)
- **Summary Box:** Hiển thị tổng quan `N files indexed thành công, M files thất bại`.
- **Hành động tiếp theo (CTA):**
  - `[ Ask this batch ]`: Mở cửa sổ chat với context/bộ lọc tự động trỏ đến các file vừa nạp.
  - `[ Open in Knowledge Explorer ]`: Mở trang quản trị tài liệu nội bộ.

## 3. Wireframe ASCII

### Màn hình 1: Upload Dropzone & Metadata
```text
+-------------------------------------------------------------+
|    ALETHEIA GATEWAY                       [ Go to Upload ]  |
+-------------------------------------------------------------+
|                                                             |
|   +-----------------------------------------------------+   |
|   |                  [ UploadDropzone ]                 |   |
|   |                                                     |   |
|   |         +-------------------------------+           |   |
|   |         |      [Cloud Upload Icon]      |           |   |
|   |         |  Drag & drop multiple files   |           |   |
|   |         |   or [ Browse Files ] button  |           |   |
|   |         +-------------------------------+           |   |
|   |                                                     |   |
|   |  Selected Files (3):                                |   |
|   |  - report_Q1.pdf (2.4MB)   [x]                      |   |
|   |  - analysis.md (12KB)      [x]                      |   |
|   |  - data.csv (8.1MB)        [x]                      |   |
|   +-----------------------------------------------------+   |
|                                                             |
|   +-----------------------------------------------------+   |
|   |                [ BatchConfigPanel ]                 |   |
|   |  Domain: [Finance v]      Language: [EN v]          |   |
|   |  Tags: [q1-report] [internal] [ + ]                 |   |
|   |                                                     |   |
|   |  ( ) OCR if scanned    (x) Skip duplicates          |   |
|   |  (x) Auto-run enrichment                            |   |
|   +-----------------------------------------------------+   |
|                                                             |
|                 [ UPLOAD 3 FILES ]                          |
+-------------------------------------------------------------+
```

### Màn hình 2: Batch Progress Board
```text
+-------------------------------------------------------------+
|    Upload Status: Batch #a1b2-c3d4                          |
|    Total: 3 | Done: 1 | Parsing: 1 | Failed: 1              |
|    ETA: ~00:45                                              |
+-------------------------------------------------------------+
|  File               | Status    | Progress | Action         |
|-------------------------------------------------------------|
|  report_Q1.pdf      | Indexing  | [====  ] | [Cancel]       |
|  analysis.md        | Done      | [======] | [View Logs]    |
|  data.csv           | Failed    | [!     ] | [Retry]        |
+-------------------------------------------------------------+
|                     [ Ask This Batch ]                      |
+-------------------------------------------------------------+
```
