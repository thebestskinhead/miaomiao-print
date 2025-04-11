### 驱动作者：ihciah
https://github.com/ihciah/miaomiaoji-tool

### 环境
1. **python2,nodejs**
### 部署步骤

1. **安装依赖**
```bash
# Python2端
pip2 install flask pybluez opencv-python numpy

# Node端
cd node_server
npm install express axios cors multer
```

2. **启动服务**
```bash
# Python打印服务
cd print_server
python print_server.py

# Node.js服务
cd node_server
node server.js
```

3. **访问页面**
浏览器打开 `http://localhost:3000`

---

### 功能验证

1. **连接打印机**
   - 输入正确MAC格式（如`11:22:33:44:55:66`），点击连接
   - 观察状态栏显示连接状态

2. **文本打印**
   - 在文本框中输入文字，点击提交
   - 打印机应输出黑底白字内容

3. **图片打印**
   - 上传JPG/PNG图片，点击提交
   - 打印机应输出二值化后的图像

4. **异常测试**
   - 输入错误MAC地址，应提示格式错误
   - 断开打印机后尝试打印，应提示未连接

---

该实现完整覆盖了需求场景，具备队列管理、状态监控、异常处理等关键功能，可直接部署到支持蓝牙的服务器（如树莓派）使用。