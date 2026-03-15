// Script para usar escáner QR con cámara web
// Requiere: https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.js

class EscanerQR {
    constructor(elementoId) {
        this.video = document.getElementById(elementoId);
        this.scanner = null;
    }

    iniciar(callback) {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
                .then(stream => {
                    this.video.srcObject = stream;
                    this.video.setAttribute('playsinline', true);
                    this.video.play();
                    this.detectarCodigo(callback);
                })
                .catch(error => {
                    console.error('Error al acceder a la cámara:', error);
                    mostrarNotificacion('No se pudo acceder a la cámara', 'error');
                });
        } else {
            mostrarNotificacion('Tu navegador no soporta acceso a cámara', 'error');
        }
    }

    detectarCodigo(callback) {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');

        const detectar = () => {
            if (this.video.readyState === this.video.HAVE_ENOUGH_DATA) {
                canvas.width = this.video.videoWidth;
                canvas.height = this.video.videoHeight;
                context.drawImage(this.video, 0, 0, canvas.width, canvas.height);

                const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
                const code = jsQR(imageData.data, imageData.width, imageData.height);

                if (code) {
                    console.log('Código detectado:', code.data);
                    if (callback) callback(code.data);
                    this.detener();
                    return;
                }
            }
            requestAnimationFrame(detectar);
        };

        detectar();
    }

    detener() {
        if (this.video.srcObject) {
            this.video.srcObject.getTracks().forEach(track => track.stop());
            this.video.srcObject = null;
        }
    }
}

// Uso:
/*
const escaner = new EscanerQR('video-escaner');
escaner.iniciar((codigo) => {
    console.log('Código leído:', codigo);
    mostrarNotificacion('Código leído: ' + codigo, 'success');
});
*/
