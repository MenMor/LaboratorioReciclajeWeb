/**
 * Import function triggers from their respective submodules:
 *
 * const {onCall} = require("firebase-functions/v2/https");
 * const {onDocumentWritten} = require("firebase-functions/v2/firestore");
 *
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

const {onRequest} = require("firebase-functions/v2/https");
const logger = require("firebase-functions/logger");

// Create and deploy your first functions
// https://firebase.google.com/docs/functions/get-started

// exports.helloWorld = onRequest((request, response) => {
//   logger.info("Hello logs!", {structuredData: true});
//   response.send("Hello from Firebase!");
// });

const functions = require('firebase-functions');
const admin = require('firebase-admin');
admin.initializeApp();

exports.updateUserPoints = functions.https.onRequest(async (req, res) => {
    const qrCode = req.body.qr_code;
    const userId = req.body.user_id;

    try {
        // Verificar el código QR
        const qrCodeRef = admin.database().ref('qr_codes');
        const qrCodeSnapshot = await qrCodeRef.orderByChild('code').equalTo(qrCode).once('value');
        if (!qrCodeSnapshot.exists()) {
            return res.status(404).send({ message: 'Invalid QR Code', status: 'error' });
        }

        let transactionId = null;
        qrCodeSnapshot.forEach(childSnapshot => {
            const value = childSnapshot.val();
            if (value.code === qrCode) {
                transactionId = value.transaction;
            }
        });

        if (!transactionId) {
            return res.status(404).send({ message: 'Transaction not found for QR Code', status: 'error' });
        }

        // Obtener los detalles de la transacción
        const transactionRef = admin.database().ref(`recycling_transactions/${transactionId}`);
        const transactionSnapshot = await transactionRef.once('value');
        const transactionData = transactionSnapshot.val();
        if (!transactionData) {
            return res.status(404).send({ message: 'Transaction not found', status: 'error' });
        }

        // Obtener los datos del usuario
        const userRef = admin.database().ref(`users/${userId}`);
        const userSnapshot = await userRef.once('value');
        const userData = userSnapshot.val();
        if (!userData) {
            return res.status(404).send({ message: 'User not found', status: 'error' });
        }

        // Calcular los puntos
        const points = transactionData.quantity * transactionData.recyclable.value;

        // Actualizar puntos del usuario en Firebase
        const userPointsRef = userRef.child('points');
        const currentPointsSnapshot = await userPointsRef.once('value');
        let currentPoints = currentPointsSnapshot.val() || 0;
        if (typeof currentPoints === 'object') {
            currentPoints = currentPoints.points || 0;
        }

        const newPoints = currentPoints + points;
        await userPointsRef.set(newPoints);

        res.status(200).send({ message: 'QR Code verified and points added', status: 'success', new_points: newPoints });
    } catch (error) {
        res.status(500).send({ message: error.message, status: 'error' });
    }
});
