import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота (получите у @BotFather в Telegram)
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# ID администратора (ваш Telegram ID)
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))

# URL сайта (для ссылок на товары)
# Замените на ваш реальный URL сайта
SITE_URL = os.getenv('SITE_URL', 'https://your-site.com')  # Для продакшена
# SITE_URL = os.getenv('SITE_URL', 'http://localhost:5173')  # Для разработки

