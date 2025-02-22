from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from docx import Document
from mysql_db import query_db, insert_db  # Import MySQL functions
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config.from_object(config)

socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# User Model
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    user = query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
    if user:
        return User(user['id'], user['username'], user['password'])
    return None

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        insert_db("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        flash("Đăng ký thành công! Hãy đăng nhập.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = query_db("SELECT * FROM users WHERE username = %s", (username,), one=True)

        if user and check_password_hash(user['password'], password):
            login_user(User(user['id'], user['username'], user['password']))
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for('index'))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng!", "danger")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Bạn đã đăng xuất!", "info")
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return {"error": "No file uploaded"}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {"error": "No selected file"}, 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    doc = Document(filepath)
    content = "\n".join([para.text for para in doc.paragraphs])

    return {'text': content}  # Đảm bảo trả về 'text' thay vì 'content'


import time
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Kiểm tra thiết bị GPU/CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
if device.type == "cuda":
    print(f"Đang sử dụng GPU: {torch.cuda.get_device_name(0)}")
else:
    print("Đang sử dụng CPU")

# Tải model VinAI và tokenizer cho tiếng Anh sang tiếng Việt
tokenizer_en2vi = AutoTokenizer.from_pretrained("vinai/vinai-translate-en2vi-v2", src_lang="en_XX")
model_en2vi = AutoModelForSeq2SeqLM.from_pretrained("vinai/vinai-translate-en2vi-v2")
model_en2vi.to(device)

# Hàm dịch văn bản từ tiếng Anh sang tiếng Việt
def translate_en2vi(en_texts: str) -> str:
    input_ids = tokenizer_en2vi(en_texts, padding=True, return_tensors="pt").to(device)
    
    # Đo thời gian dịch
    start_time = time.time()
    
    output_ids = model_en2vi.generate(
        **input_ids,
        decoder_start_token_id=tokenizer_en2vi.lang_code_to_id["vi_VN"],
        num_return_sequences=1,
        num_beams=5,
        early_stopping=True
    )
    
    # Giải mã bản dịch
    vi_texts = tokenizer_en2vi.batch_decode(output_ids, skip_special_tokens=True)
    
    end_time = time.time()
    
    print(f"\nThời gian dịch: {end_time - start_time:.3f} giây")
    return vi_texts[0]  # Chỉ trả về một bản dịch đầu tiên

# Flask route and SocketIO event
@socketio.on('text_selected')
@login_required
def handle_text_selected(text):
    print(f'Text received: {text}')
    # Dịch văn bản nhận được từ tiếng Anh sang tiếng Việt
    translated_text = translate_en2vi(text)
    print(f'Translated text: {translated_text}')
    socketio.emit('text_ack', {'translated': translated_text})

# @socketio.on('text_selected')
# @login_required
# def handle_text_selected(text):
#     print(f'Text received: {text}')
#     translated_text = f"Đã nhận: {text}"
#     socketio.emit('text_ack', {'translated': translated_text})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

