class DetectionRenderer {
    constructor(canvasElement) {
        this.canvas = canvasElement;
        this.ctx = this.canvas.getContext('2d');
        this.latestDetections = [];
    }

    updateDetections(detections) {
        this.latestDetections = detections;
    }

    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.latestDetections.forEach(detection => {
            const [x1, y1, x2, y2] = detection.bbox;
            const color = detection.class.includes('NO-') ? 'red' : 'green';

            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = 2;
            this.ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

            this.ctx.fillStyle = color;
            this.ctx.font = '12px Arial';
            this.ctx.fillText(`${detection.class} ${detection.confidence.toFixed(2)}`, x1, y1 > 10 ? y1 - 5 : 10);
        });

        requestAnimationFrame(() => this.render());
    }

    start() {
        this.render();
    }
}
