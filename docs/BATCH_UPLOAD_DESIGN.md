# System Design: Aletheia Batch File Upload

## 1. UI Components (Frontend - React / Astro Cấu Trúc Đề Xuất)

- **`UploadDropzone`**: Xử lý logic Drag-and-drop, filter duplicate client-side (theo tên + dung lượng), parse extension hợp lệ.
- **`BatchConfigPanel`**: Quản lý state của mảng Metadata (domain, tags, toggles). Share chung context/state trước khi submit.
- **`BatchProgressHeader`**: Hiển thị tổng quan trạng thái Batch (Toàn cảnh vòng đời từ lúc bắt đầu cho tới lúc tất cả job ở trạng thái sinh / tử Cuối cùng: `Done` hoặc `Failed`).
- **`FileJobTable` & `JobRow`**: Component render danh sách Job ID và update trực tiếp qua Polling (hoặc WebSocket gốc/Server-Sent Events).
- **`BatchActionBar`**: Vùng chứa các nút điều hướng sau thao tác (Như `Ask this batch`).
- **`IngestErrorDrawer` / `Modal`**: Slide-out panel hoặc pop-up modal hiển thị raw error log từ backend khi user nhấn `[View Logs]` trên file lỗi.

## 2. API Contract Đề Xuất

### POST `/upload/batch`
- **Request (Multipart/form-data):**
  - Gửi `files` (array file blob).
  - Gửi field `metadata` (JSON serialized: `{domain: "...", tags: [...], ocr: false, skip_duplicates: true}`).
- **Response:**
  ```json
  {
    "batch_id": "b-12345",
    "jobs": [
      {"job_id": "j-11", "filename": "report_Q1.pdf", "status": "queued"},
      {"job_id": "j-22", "filename": "analysis.md", "status": "queued"}
    ]
  }
  ```

### GET `/upload/batch/{batch_id}`
- Trả về thông tin summary tiến trình tổng và details list job. Cần hỗ trợ pagination cho list jobs nếu vượt quá số lượng lớn (tuỳ chọn).

### GET `/jobs/{job_id}`
- Trả chi tiết trạng thái, phase hiện tại (`parsing`, `chunking`, `indexing`), tiến trình (`%`), và lỗi (nếu có).

### POST `/jobs/{job_id}/retry`
- Đưa job lỗi trở lại queue. Giữ nguyên `job_id` hoặc cấp `job_id` dạng nhánh con.

### POST `/jobs/{job_id}/cancel`
- Dừng ngay tác vụ đang ingest. Xoá chunk đã sinh nếu trạng thái roll-back hỗ trợ.

## 3. Các Nguyên Tắc Xử Lý (Core Rules)

1. **Idempotent dựa trên File Checksum (Hash):**
   - Backend quét hash SHA-256 (hoặc MD5) ngay sau khi thu nhận file. Nếu cờ `Skip duplicates` được bật, bypass Ingest Job và update status thành `done(duplicate)`.
2. **Concurrency Limit:**
   - Worker có luồng giới hạn (vd. 3-5 file chạy queue song song) để tránh dội RAM/CPU cho các tác vụ parsing PDF nặng hoặc OCR tốn GPU/Compute.
3. **Chunk-level Retry:**
   - Nếu file có quá nhiều section/chunk, tiến trình có cờ lưu checkpoint. Nếu fail ở đoạn index embedding cho 200 chunk cuối, khi retry không cần phải extract lại raw text từ file gốc ban đầu (Tiết kiệm chu kỳ OCR). Điều này cần thiết kế worker queue hỗ trợ step-based workflow.
4. **Cache Invalidate sau Indexing:**
   - Invalidate Memory/Redis Cache cho cụm `{source_id}` / `{batch_id}` hoặc namespace search liên quan ngay sau khi Indexer báo `Done`. Đảm bảo search query mới lấy ngay lập tức dữ liệu mới.
5. **Fault Isolation (Cách ly theo file):**
   - 1 bài báo cáo bị lỗi không block cả 10 báo cáo khác trong cùng 1 batch. Queue xử lý cần wrap try/catch cho tứng sub-task (job). Trang thái Error sẽ dừng độc lập ở cấp Job, cấp Batch vẫn chạy các Job tiếp theo.
