// URL Backend FastAPI của TV3 (đúng prefix /api/v1/attendance, không phải /api)
const API_BASE_URL = "http://localhost:8000/api/v1";

// API Key phải khớp với API_KEY trong file .env của Backend (TV3).
// Sản phẩm thật nên có cơ chế cấp key riêng cho từng thiết bị, Tuần 1 dùng chung 1 key demo.
const API_KEY = "dev-secret-key-change-me";

/**
 * Gửi ảnh chụp từ Camera lên Backend để xử lý điểm danh.
 * @param {Blob} imageBlob - File ảnh dạng Blob
 * @param {string} cameraCode - Mã camera đang dùng, VD: "CAM-01" (bắt buộc, Backend yêu cầu)
 */
async function sendCheckinImage(imageBlob, cameraCode) {
    if (!imageBlob) return null;

    // Backend đọc field tên "image" (UploadFile) và "camera_code" (Form) -> phải đặt đúng tên field
    const formData = new FormData();
    formData.append('image', imageBlob, 'frame.jpg');
    formData.append('camera_code', cameraCode);

    try {
        const response = await fetch(`${API_BASE_URL}/attendance/checkin`, {
            method: 'POST',
            headers: { 'X-API-Key': API_KEY }, // endpoint checkin của TV3 yêu cầu xác thực
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            // Backend trả lỗi có cấu trúc { detail: "..." } (401, 400, 422...)
            console.error("Checkin thất bại:", data.detail || response.status);
            return null;
        }

        return data;
        /*
           Cấu trúc response THẬT từ Backend (TV3) - AttendanceCheckinResponse:
           - Nhận diện thành công:
             { success: true, status: "present", student_code: "SV001", full_name: "Nguyễn Văn An",
               class_name: "CNTT-K17", similarity_score: 0.31, checkin_time: "2026-...Z", message: "..." }
           - Không nhận diện được:
             { success: false, status: "unknown", similarity_score: 0.55, checkin_time: "...", message: "..." }
        */
    } catch (error) {
        console.error("Lỗi khi gọi API Check-in:", error);
        return null;
    }
}

/**
 * Lấy lịch sử điểm danh gần nhất, dùng để nạp lại bảng khi mở/refresh trang.
 * @param {number} limit - số bản ghi tối đa muốn lấy
 */
async function fetchAttendanceHistory(limit = 20) {
    try {
        const response = await fetch(`${API_BASE_URL}/attendance/history?limit=${limit}`);
        if (!response.ok) return [];
        return await response.json();
        // Mỗi item: { id, student_id, camera_id, status, similarity_score, checkin_time }
    } catch (error) {
        console.error("Lỗi khi tải lịch sử điểm danh:", error);
        return [];
    }
}
