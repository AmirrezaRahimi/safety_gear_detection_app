class Camera {
    constructor(videoElement) {
        this.video = videoElement;
        this.stream = null;
    }

    async start() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 640 },
                    height: { ideal: 360 },
                    facingMode: "environment"
                } 
            });
            this.video.srcObject = this.stream;
            await this.video.play();
        } catch (err) {
            console.error("Error accessing the camera:", err);
            throw err;
        }
    }

    stop() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
    }

    captureFrame() {
        const canvas = document.createElement('canvas');
        canvas.width = this.video.videoWidth;
        canvas.height = this.video.videoHeight;
        canvas.getContext('2d').drawImage(this.video, 0, 0);
        return canvas.toDataURL('image/jpeg', 0.8);
    }
}
