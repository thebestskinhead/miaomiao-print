const express = require('express');
const axios = require('axios');
const cors = require('cors');
const multer = require('multer');
const upload = multer({ storage: multer.memoryStorage() });

const app = express();
const PYTHON_SERVER = 'http://localhost:5000';

app.use(cors());
app.use(express.static('../frontend'));

// 打印机连接
app.post('/api/printer/connect', express.json(), async (req, res) => {
    try {
        const response = await axios.post(`${PYTHON_SERVER}/connect`, req.body);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ success: false, message: '连接失败' });
    }
});

// 提交打印任务
app.post('/api/print', upload.single('image'), async (req, res) => {
    try {
        const formData = new FormData();
        if (req.body.text) formData.append('text', req.body.text);
        if (req.file) formData.append('image', req.file.buffer);

        const response = await axios.post(`${PYTHON_SERVER}/print`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ success: false, message: '打印失败' });
    }
});

// 获取打印机状态
app.get('/api/printer/status', async (req, res) => {
    try {
        const response = await axios.get(`${PYTHON_SERVER}/status`);
        res.json(response.data);
    } catch (error) {
        res.json({ connected: false, mac: null });
    }
});

app.listen(3000, () => console.log('Node服务运行在 http://localhost:3000'));