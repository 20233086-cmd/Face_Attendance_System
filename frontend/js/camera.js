let stream = null;
const video = document.getElementById('webcam');
const canvas = document.getElementById('snapshot');

// Bật Webcam
async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480, facingMode: "user" }, 
            audio: false 
        });
        video.srcObject = stream;
        console.log("Camera đã khởi động.");
    } catch (err) {
        alert("Không thể truy cập Webcam: " + err.message);
    }
}

// Tắt Webcam
function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
        console.log("Đã tắt camera.");
    }
}

// Chụp ảnh từ khung hình video hiện tại (trả về File/Blob dạng JPEG)
function captureFrameBlob() {
    return new Promise((resolve) => {
        if (!stream) resolve(null);
        
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
        
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Xuất ảnh ra định dạng Blob JPEG
        canvas.toBlob((blob) => {
            resolve(blob);
        }, 'image/jpeg', 0.85);
    });
}
