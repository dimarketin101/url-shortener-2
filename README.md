# URL Shortener

Лек URL shortener с FastAPI + SQLite. Може да се стартира локално или да се деплойне безплатно.

## 🚀 Бърз старт (локално)

### 1. Инсталация
```bash
# Клонирай репозиторито
git clone <repository-url>
cd url-shortener

# Създай виртуална среда
python -m venv venv

# Активирай виртуалната среда
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Инсталирай dependencies
pip install -r requirements.txt
```

### 2. Конфигурация
```bash
# Копирай примерния .env файл
cp .env.example .env

# Редактирай .env с твоя домен
BASE_DOMAIN=http://localhost:8000
```

### 3. Стартиране
```bash
# Локално разработка
python main.py

# Или с uvicorn директно
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Тестване
Отвори браузър на: `http://localhost:8000`

**Тестови URL-ове:**
- Дълъг URL: `https://www.google.com/search?q=fastapi+url+shortener`
- Custom code: `mylink123`

---

## 🌐 Deploy на Render (Free)

### Стъпка 1: Създай акаунт
1. Отиди на [render.com](https://render.com)
2. Регистрирай се с GitHub

### Стъпка 2: Подготовка
```bash
# Инициализирай git репозиторито (ако не е)
git init
git add .
git commit -m "Initial commit"

# Качи на GitHub
git remote add origin <your-github-repo>
git push -u origin main
```

### Стъпка 3: Създай Web Service на Render
1. В Render dashboard → "New" → "Web Service"
2. Свържи GitHub репозиторито
3. Настройки:
   - **Name:** url-shortener (или каквото искаш)
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Стъпка 4: Environment Variables
В Render Dashboard → Environment:
```
BASE_DOMAIN=https://url-shortener.onrender.com
```
(Замени с твоя реален домен след деплой)

### Стъпка 5: Deploy
Кликни "Create Web Service" → Render автоматично ще деплойне!

**URL:** `https://url-shortener.onrender.com`

**⚠️ Забележка:** SQLite на Render е ephemeral (изчезва при рестарт). За production с постоянна база данни, използвай Railway или добави Render Disk ($5/месец).

---

## 🚂 Deploy на Railway (Free + Persistent)

Railway е по-добър избор за SQLite, защото има persistent storage.

### Стъпка 1: Инсталирай Railway CLI
```bash
# Windows (с PowerShell)
npm install -g @railway/cli

# Linux/Mac
npm install -g @railway/cli
```

### Стъпка 2: Логин и създаване
```bash
# Логни се
railway login

# Инициализирай проект
railway init

# Избери "Empty Project"
```

### Стъпка 3: Environment Variables
```bash
railway variables set BASE_DOMAIN=https://url-shortener.up.railway.app
```

### Стъпка 4: Deploy
```bash
# Деплой
railway up

# Отвори в браузър
railway open
```

**URL:** `https://url-shortener.up.railway.app`

**✅ Предимство:** Данните в SQLite се запазват при рестарт!

---

## 🖥️ Deploy на VPS (DigitalOcean, Hetzner, etc.)

### Изисквания
- Linux сървър (Ubuntu 20.04+)
- Python 3.8+
- Nginx (за reverse proxy)
- Домейн (опционално)

### Стъпка 1: Инсталация на сървъра
```bash
# SSH към сървъра
ssh user@your-server-ip

# Инсталирай dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv nginx git

# Клонирай проекта
cd /var/www
git clone https://github.com/yourusername/url-shortener.git
cd url-shortener

# Създай виртуална среда
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Създай .env файл
echo "BASE_DOMAIN=https://your-domain.com" > .env
```

### Стъпка 2: Systemd Service
```bash
sudo nano /etc/systemd/system/url-shortener.service
```

Постави това:
```ini
[Unit]
Description=URL Shortener
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/url-shortener
Environment="PATH=/var/www/url-shortener/venv/bin"
ExecStart=/var/www/url-shortener/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

```bash
# Стартирай service
sudo systemctl start url-shortener
sudo systemctl enable url-shortener

# Провери статус
sudo systemctl status url-shortener
```

### Стъпка 3: Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/url-shortener
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Активирай конфигурацията
sudo ln -s /etc/nginx/sites-available/url-shortener /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Стъпка 4: SSL (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 📁 Структура на проекта

```
url-shortener/
├── main.py              # FastAPI приложение
├── database.py          # SQLite операции
├── utils.py             # Helper функции
├── requirements.txt     # Dependencies
├── .env.example         # Примерни environment variables
├── .gitignore          # Git ignore
├── README.md           # Този файл
├── templates/          # HTML темплейти
│   ├── index.html
│   └── error.html
└── static/             # CSS и assets
    └── style.css
```

---

## ⚙️ Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BASE_DOMAIN` | Базов домейн за short URLs | `https://myapp.com` |

---

## 🧪 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Главна страница |
| POST | `/shorten` | Създава short URL |
| GET | `/{short_code}` | Redirect към оригиналния URL |
| GET | `/api/stats` | Статистика (опционално) |

---

## 🔒 Безопасност

- ✅ Parameterized SQL queries (защита от SQL injection)
- ✅ URL validation с validators библиотека
- ✅ Input sanitization
- ✅ CORS защита (FastAPI default)

---

## 💡 Примерни URL-ове за тестване

```
https://www.google.com
https://github.com/tiangolo/fastapi
https://stackoverflow.com/questions/tagged/python
```

---

## 📞 Проблеми?

**Въпроси?** Провери логовете:

```bash
# Render
Виж в Render Dashboard → Logs

# Railway
railway logs

# VPS
sudo journalctl -u url-shortener -f
sudo tail -f /var/log/nginx/error.log
```

**SQLite грешки?** Увери се че папката е writable:
```bash
chmod 755 /var/www/url-shortener
```

---

**Готово!** 🎉 Твоят URL shortener е онлайн!