class DetectionRenderer {
    constructor(canvasElement, videoElement) {
        this.canvas = canvasElement;
        this.ctx = this.canvas.getContext('2d');
        this.video = videoElement;
        this.latestDetections = [];
    }

    updateDetections(detections) {
        this.latestDetections = detections;
    }

    drawVideoFrame() {
        this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
    }

    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.drawVideoFrame();

        const scaleX = this.canvas.width / this.video.videoWidth;
        const scaleY = this.canvas.height / this.video.videoHeight;

        this.latestDetections.forEach(detection => {
            const [x1, y1, x2, y2] = detection.bbox;
            const color = detection.class.includes('NO-') ? 'red' : 'green';

            const scaledX1 = x1 * scaleX;
            const scaledY1 = y1 * scaleY;
            const scaledX2 = x2 * scaleX;
            const scaledY2 = y2 * scaleY;

            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = 2;
            this.ctx.strokeRect(scaledX1, scaledY1, scaledX2 - scaledX1, scaledY2 - scaledY1);

            this.ctx.fillStyle = color;
            this.ctx.font = '12px Arial';
            this.ctx.fillText(`${detection.class} ${detection.confidence.toFixed(2)}`, scaledX1, scaledY1 > 10 ? scaledY1 - 5 : 10);
        });

        requestAnimationFrame(() => this.render());
    }

    start() {
        this.render();
    }
}
