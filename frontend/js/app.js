let checkinInterval = null;
const CHECKIN_SPEED_MS = 1500; // Tự động gửi ảnh mỗi 1.5 giây
const cameraSelect = document.getElementById('camera-select');

// --- Bật Camera: chỉ bắt đầu vòng lặp checkin SAU KHI camera đã khởi động xong ---
// (tránh gửi frame rỗng lúc video chưa kịp có kích thước, vì getUserMedia là bất đồng bộ)
document.getElementById('btn-start').addEventListener('click', async () => {
    await startCamera(); // hàm từ camera.js, gán biến `stream` dùng chung

    if (stream && !checkinInterval) {
        checkinInterval = setInterval(processRealtimeCheckin, CHECKIN_SPEED_MS);
    }
});

// --- Tắt Camera: dừng cả stream lẫn vòng lặp gửi frame ---
document.getElementById('btn-stop').addEventListener('click', () => {
    stopCamera(); // hàm từ camera.js
    if (checkinInterval) {
        clearInterval(checkinInterval);
        checkinInterval = null;
    }
});

// Hàm xử lý từng chu kỳ điểm danh
async function processRealtimeCheckin() {
    const blob = await captureFrameBlob();
    if (!blob) return;

    const cameraCode = cameraSelect ? cameraSelect.value : 'CAM-01';
    const result = await sendCheckinImage(blob, cameraCode);
    if (result) {
        updateUI(result);
    }
}

// Cập nhật giao diện khi có phản hồi từ Backend
// Lưu ý: response thật của Backend dùng status = "present" | "unknown" (không phải "success")
function updateUI(data) {
    const statusBox = document.getElementById('status-box');

    if (data.status === 'present') {
        statusBox.className = 'status success';
        statusBox.innerText = `Xác nhận: ${data.full_name} (${data.student_code}) - ${data.class_name}`;
        addAttendanceRow({
            time: data.checkin_time,
            studentId: data.student_code,
            name: data.full_name,
            className: data.class_name,
        });
    } else {
        statusBox.className = 'status unknown';
        statusBox.innerText = 'Cảnh báo: Phát hiện người lạ / Không nhận diện được!';
    }
}

// Thêm 1 dòng vào bảng lịch sử (dùng chung cho cả nạp lịch sử ban đầu và checkin realtime)
function addAttendanceRow({ time, studentId, name, className }) {
    const tableBody = document.getElementById('attendance-list');
    const rowId = `row-${studentId}`;

    // Tránh chèn trùng nếu sinh viên đã có trong bảng
    if (document.getElementById(rowId)) return;

    const displayTime = time ? new Date(time).toLocaleTimeString('vi-VN') : new Date().toLocaleTimeString('vi-VN');

    const newRow = document.createElement('tr');
    newRow.id = rowId;
    newRow.innerHTML = `
        <td>${displayTime}</td>
        <td>${studentId ?? '—'}</td>
        <td>${name ?? '—'}</td>
        <td>${className ?? '—'}</td>
        <td style="color: green; font-weight: bold;">Có mặt</td>
    `;
    tableBody.insertBefore(newRow, tableBody.firstChild);
}

// Nạp lại lịch sử điểm danh khi mở trang (để refresh không bị mất bảng)
async function loadInitialHistory() {
    const history = await fetchAttendanceHistory(20);
    history.forEach((item) => {
        // Lịch sử từ GET /history chỉ có student_id (số), không có tên/lớp/mã SV
        // vì bảng attendances không lưu trực tiếp thông tin đó -> chỉ hiển thị được ở mức cơ bản.
        if (item.status !== 'present') return;
        addAttendanceRow({
            time: item.checkin_time,
            studentId: item.student_id ?? '—',
            name: '—',
            className: '—',
        });
    });
}

window.addEventListener('DOMContentLoaded', loadInitialHistory);
