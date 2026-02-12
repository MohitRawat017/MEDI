import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
});

export const uploadPDF = async (files) => {
    const formData = new FormData();
    // Verify variable type and iterate if it's an array or list
    if (files.length) {
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }
    } else {
        formData.append('files', files);
    }

    // endpoint is /upload_pdfs/ from backend/routes/upload_pdf.py
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

    // endpoint is /ask/ from backend/routes/ask_question.py
    const response = await api.post('/ask/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data', // Backend uses Form(...)
        }
    });
    return response.data;
};

export default api;
