import axios from 'axios';

// Same-origin by default: the Vite dev server and the production nginx both
// proxy the API routes to the backend. Override with VITE_API_URL when the
// frontend and backend live on different origins (e.g. Render static site).
const API_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
    baseURL: API_URL,
});

export const uploadPDF = async (files) => {
    const formData = new FormData();
    for (const file of files) {
        formData.append('files', file);
    }

    const response = await api.post('/upload_pdfs/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const askQuestion = async (question, namespace) => {
    const formData = new FormData();
    formData.append('question', question);
    formData.append('namespace', namespace);

    const response = await api.post('/ask/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const uploadPrescription = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload_prescription/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const askPrescription = async (sessionId, question) => {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('question', question);

    const response = await api.post('/ask_prescription/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};
