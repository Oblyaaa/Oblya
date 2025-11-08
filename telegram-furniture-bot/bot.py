import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from data.products import PRODUCTS, CATEGORIES
import json
import os

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Путь к файлу с корзинами пользователей
CART_FILE = 'user_carts.json'

def load_carts():
    """Загружает корзины пользователей из файла"""
    if os.path.exists(CART_FILE):
        with open(CART_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_carts(carts):
    """Сохраняет корзины пользователей в файл"""
    with open(CART_FILE, 'w', encoding='utf-8') as f:
        json.dump(carts, f, ensure_ascii=False, indent=2)

def get_user_cart(user_id):
    """Получает корзину пользователя"""
    carts = load_carts()
    return carts.get(str(user_id), {})

def save_user_cart(user_id, cart):
    """Сохраняет корзину пользователя"""
    carts = load_carts()
    carts[str(user_id)] = cart
    save_carts(carts)

def format_price(price):
    """Форматирует цену"""
    return f"{price:,}".replace(",", " ") + " ₽"

def get_category_keyboard():
    """Создает клавиатуру с категориями"""
    keyboard = []
    row = []
    for i, (cat_id, cat_info) in enumerate(CATEGORIES.items()):
        if i % 2 == 0 and i > 0:
            keyboard.append(row)
            row = []
        row.append(InlineKeyboardButton(
            f"{cat_info['icon']} {cat_info['name'].split(' ', 1)[1]}",
            callback_data=f"category_{cat_id}"
        ))
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("📦 Все товары", callback_data="category_all")])
    keyboard.append([InlineKeyboardButton("🛒 Корзина", callback_data="cart")])
    keyboard.append([InlineKeyboardButton("ℹ️ О магазине", callback_data="about")])
    return InlineKeyboardMarkup(keyboard)

def get_main_keyboard():
    """Создает главную клавиатуру"""
    keyboard = [
        [KeyboardButton("📦 Каталог"), KeyboardButton("🛒 Корзина")],
        [KeyboardButton("ℹ️ О магазине"), KeyboardButton("📞 Контакты")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_products_keyboard(category_id=None):
    """Создает клавиатуру с товарами категории"""
    keyboard = []
    products = []
    
    if category_id and category_id != 'all':
        products = [p for p in PRODUCTS.values() if p['category'] == category_id]
    else:
        products = list(PRODUCTS.values())
    
    for product in products[:10]:  # Показываем первые 10 товаров
        discount = ""
        if product['old_price']:
            discount = f" 🔥 -{int((1 - product['price']/product['old_price'])*100)}%"
        keyboard.append([InlineKeyboardButton(
            f"{product['name']}{discount}",
            callback_data=f"product_{product['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("◀️ Назад к категориям", callback_data="back_to_categories")])
    return InlineKeyboardMarkup(keyboard)

def get_product_keyboard(product_id):
    """Создает клавиатуру для товара"""
    product = PRODUCTS[product_id]
    
    keyboard = [
        [InlineKeyboardButton("➕ Добавить в корзину", callback_data=f"add_{product_id}")],
        [InlineKeyboardButton("🛒 Корзина", callback_data="cart")],
        [InlineKeyboardButton("◀️ Назад к товарам", callback_data=f"back_to_products_{product['category']}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_cart_keyboard(cart):
    """Создает клавиатуру для корзины"""
    keyboard = []
    for product_id, quantity in cart.items():
        product = PRODUCTS[int(product_id)]
        keyboard.append([
            InlineKeyboardButton(f"➖", callback_data=f"dec_{product_id}"),
            InlineKeyboardButton(f"{product['name']} x{quantity}", callback_data=f"product_{product_id}"),
            InlineKeyboardButton(f"➕", callback_data=f"inc_{product_id}")
        ])
        keyboard.append([InlineKeyboardButton(f"❌ Удалить {product['name']}", callback_data=f"remove_{product_id}")])
    
    if cart:
        keyboard.append([InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout")])
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_to_categories")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    from config import SITE_URL
    user = update.effective_user
    
    welcome_text = f"""
🪑 <b>Добро пожаловать в МебельПремиум!</b>

Привет, {user.first_name}! 👋

Мы предлагаем качественную мебель для вашего дома и офиса:
• 🛋️ Гостиная
• 🛏️ Спальня
• 🍽️ Кухня
• 💼 Офис
• 🍴 Столовая
• 🧸 Детская

<b>Преимущества:</b>
🚚 Бесплатная доставка от 50 000 ₽
🛡️ Гарантия 2 года
💰 Лучшие цены
⚡ Быстрая сборка

🌐 <b>Также доступен наш сайт:</b> {SITE_URL}

Выберите действие:
    """
    
    keyboard = [
        [InlineKeyboardButton("📦 Каталог", callback_data="back_to_categories")],
        [InlineKeyboardButton("🌐 Открыть сайт", url=SITE_URL)]
    ]
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )
    
    await update.message.reply_text(
        "Используйте кнопки ниже для навигации:",
        reply_markup=get_main_keyboard()
    )

async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает каталог категорий"""
    text = "📦 <b>Каталог товаров</b>\n\nВыберите категорию:"
    await update.message.reply_text(
        text,
        reply_markup=get_category_keyboard(),
        parse_mode='HTML'
    )

async def cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает корзину пользователя"""
    user_id = update.effective_user.id
    cart = get_user_cart(user_id)
    
    if not cart:
        text = "🛒 <b>Ваша корзина пуста</b>\n\nДобавьте товары из каталога!"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 Перейти в каталог", callback_data="back_to_categories")]
        ])
    else:
        text = "🛒 <b>Ваша корзина:</b>\n\n"
        total = 0
        
        for product_id, quantity in cart.items():
            product = PRODUCTS[int(product_id)]
            price = product['price'] * quantity
            total += price
            text += f"• {product['name']}\n"
            text += f"  {format_price(product['price'])} x {quantity} = {format_price(price)}\n\n"
        
        text += f"<b>Итого: {format_price(total)}</b>\n"
        if total >= 50000:
            text += "\n🎉 <b>Бесплатная доставка!</b>"
        else:
            text += f"\n💡 До бесплатной доставки осталось: {format_price(50000 - total)}"
        
        keyboard = get_cart_keyboard(cart)
    
    await update.message.reply_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о магазине"""
    from config import SITE_URL
    
    text = f"""
ℹ️ <b>О магазине МебельПремиум</b>

Мы - современный интернет-магазин мебели, который уже более 10 лет помогает создавать уютные и стильные интерьеры.

<b>Наши преимущества:</b>
⭐ Высокое качество продукции
💚 Экологически чистые материалы
👥 Профессиональные консультанты
🚀 Актуальные дизайнерские решения

<b>Статистика:</b>
• 10+ лет на рынке
• 5000+ довольных клиентов
• 1000+ моделей мебели
• 50+ городов доставки

<b>Контакты:</b>
📞 +7 (495) 123-45-67
✉️ info@mebelpremium.ru
📍 Москва, ул. Мебельная, 1

🕐 Режим работы:
Пн-Пт: 9:00-20:00
Сб-Вс: 10:00-18:00

🌐 <b>Посетите наш сайт:</b> {SITE_URL}

Для просмотра полного каталога, фотографий товаров и оформления заказа на сайте перейдите по ссылке выше.
    """
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Открыть сайт", url=SITE_URL)],
        [InlineKeyboardButton("📦 Каталог", callback_data="back_to_categories")],
        [InlineKeyboardButton("🛒 Корзина", callback_data="cart")]
    ])
    await update.message.reply_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )

async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Контакты"""
    text = """
📞 <b>Контакты</b>

<b>Телефон:</b>
+7 (495) 123-45-67
+7 (800) 123-45-67 (бесплатно по России)

<b>Email:</b>
info@mebelpremium.ru
order@mebelpremium.ru

<b>Адрес:</b>
г. Москва, ул. Мебельная, д. 1
ТЦ "МебельПремиум", 2 этаж

<b>Режим работы:</b>
Пн-Пт: 9:00-20:00
Сб-Вс: 10:00-18:00

<b>Онлайн-консультант:</b>
Работает круглосуточно
Среднее время ответа: 2 минуты
    """
    await update.message.reply_text(text, parse_mode='HTML')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на inline-кнопки"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    # Категории
    if data.startswith("category_"):
        category_id = data.split("_", 1)[1]
        if category_id == 'all':
            text = "📦 <b>Все товары:</b>\n\n"
            products = list(PRODUCTS.values())
        else:
            cat_info = CATEGORIES[category_id]
            text = f"{cat_info['icon']} <b>{cat_info['name']}</b>\n\n"
            products = [p for p in PRODUCTS.values() if p['category'] == category_id]
        
        if not products:
            text += "Товары в этой категории отсутствуют."
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ Назад", callback_data="back_to_categories")]
            ])
        else:
            text += f"Найдено товаров: {len(products)}\n\n"
            keyboard = get_products_keyboard(category_id if category_id != 'all' else None)
        
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode='HTML')
    
    # Товар
    elif data.startswith("product_"):
        product_id = int(data.split("_", 1)[1])
        product = PRODUCTS[product_id]
        
        text = f"<b>{product['name']}</b>\n\n"
        text += f"{product['full_description']}\n\n"
        text += f"<b>Характеристики:</b>\n"
        text += f"📏 Размеры: {product['dimensions']}\n"
        text += f"🎨 Материал: {product['material']}\n"
        text += f"🌈 Цвет: {product['color']}\n"
        text += f"✨ Стиль: {product['style']}\n\n"
        text += f"⭐ Рейтинг: {product['rating']} ({product['reviews']} отзывов)\n\n"
        
        if product['old_price']:
            discount = int((1 - product['price']/product['old_price'])*100)
            text += f"<s>{format_price(product['old_price'])}</s>\n"
            text += f"<b>{format_price(product['price'])} 🔥 -{discount}%</b>\n"
        else:
            text += f"<b>{format_price(product['price'])}</b>\n"
        
        if product['in_stock']:
            text += "\n✅ В наличии"
        else:
            text += "\n❌ Нет в наличии"
        
        keyboard = get_product_keyboard(product_id)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode='HTML')
    
    # Добавить в корзину
    elif data.startswith("add_"):
        product_id = int(data.split("_", 1)[1])
        cart = get_user_cart(user_id)
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        save_user_cart(user_id, cart)
        
        product = PRODUCTS[product_id]
        await query.answer(f"{product['name']} добавлен в корзину! ✅", show_alert=False)
    
    # Увеличить количество
    elif data.startswith("inc_"):
        product_id = int(data.split("_", 1)[1])
        cart = get_user_cart(user_id)
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        save_user_cart(user_id, cart)
        
        # Обновляем сообщение корзины
        cart = get_user_cart(user_id)
        text = "🛒 <b>Ваша корзина:</b>\n\n"
        total = 0
        
        for pid, quantity in cart.items():
            product = PRODUCTS[int(pid)]
            price = product['price'] * quantity
            total += price
            text += f"• {product['name']}\n"
            text += f"  {format_price(product['price'])} x {quantity} = {format_price(price)}\n\n"
        
        text += f"<b>Итого: {format_price(total)}</b>\n"
        if total >= 50000:
            text += "\n🎉 <b>Бесплатная доставка!</b>"
        else:
            text += f"\n💡 До бесплатной доставки осталось: {format_price(50000 - total)}"
        
        await query.edit_message_text(text, reply_markup=get_cart_keyboard(cart), parse_mode='HTML')
    
    # Уменьшить количество
    elif data.startswith("dec_"):
        product_id = int(data.split("_", 1)[1])
        cart = get_user_cart(user_id)
        if str(product_id) in cart:
            cart[str(product_id)] -= 1
            if cart[str(product_id)] <= 0:
                del cart[str(product_id)]
            save_user_cart(user_id, cart)
        
        # Обновляем сообщение корзины
        cart = get_user_cart(user_id)
        if not cart:
            text = "🛒 <b>Ваша корзина пуста</b>\n\nДобавьте товары из каталога!"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📦 Перейти в каталог", callback_data="back_to_categories")]
            ])
        else:
            text = "🛒 <b>Ваша корзина:</b>\n\n"
            total = 0
            
            for pid, quantity in cart.items():
                product = PRODUCTS[int(pid)]
                price = product['price'] * quantity
                total += price
                text += f"• {product['name']}\n"
                text += f"  {format_price(product['price'])} x {quantity} = {format_price(price)}\n\n"
            
            text += f"<b>Итого: {format_price(total)}</b>\n"
            if total >= 50000:
                text += "\n🎉 <b>Бесплатная доставка!</b>"
            else:
                text += f"\n💡 До бесплатной доставки осталось: {format_price(50000 - total)}"
            
            keyboard = get_cart_keyboard(cart)
        
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode='HTML')
    
    # Удалить из корзины
    elif data.startswith("remove_"):
        product_id = int(data.split("_", 1)[1])
        cart = get_user_cart(user_id)
        if str(product_id) in cart:
            del cart[str(product_id)]
            save_user_cart(user_id, cart)
        
        # Обновляем сообщение корзины
        cart = get_user_cart(user_id)
        if not cart:
            text = "🛒 <b>Ваша корзина пуста</b>\n\nДобавьте товары из каталога!"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📦 Перейти в каталог", callback_data="back_to_categories")]
            ])
        else:
            text = "🛒 <b>Ваша корзина:</b>\n\n"
            total = 0
            
            for pid, quantity in cart.items():
                product = PRODUCTS[int(pid)]
                price = product['price'] * quantity
                total += price
                text += f"• {product['name']}\n"
                text += f"  {format_price(product['price'])} x {quantity} = {format_price(price)}\n\n"
            
            text += f"<b>Итого: {format_price(total)}</b>\n"
            if total >= 50000:
                text += "\n🎉 <b>Бесплатная доставка!</b>"
            else:
                text += f"\n💡 До бесплатной доставки осталось: {format_price(50000 - total)}"
            
            keyboard = get_cart_keyboard(cart)
        
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode='HTML')
    
    # Корзина
    elif data == "cart":
        cart = get_user_cart(user_id)
        if not cart:
            text = "🛒 <b>Ваша корзина пуста</b>\n\nДобавьте товары из каталога!"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📦 Перейти в каталог", callback_data="back_to_categories")]
            ])
        else:
            text = "🛒 <b>Ваша корзина:</b>\n\n"
            total = 0
            
            for product_id, quantity in cart.items():
                product = PRODUCTS[int(product_id)]
                price = product['price'] * quantity
                total += price
                text += f"• {product['name']}\n"
                text += f"  {format_price(product['price'])} x {quantity} = {format_price(price)}\n\n"
            
            text += f"<b>Итого: {format_price(total)}</b>\n"
            if total >= 50000:
                text += "\n🎉 <b>Бесплатная доставка!</b>"
            else:
                text += f"\n💡 До бесплатной доставки осталось: {format_price(50000 - total)}"
            
            keyboard = get_cart_keyboard(cart)
        
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode='HTML')
    
    # Оформление заказа
    elif data == "checkout":
        cart = get_user_cart(user_id)
        if not cart:
            await query.answer("Корзина пуста!", show_alert=True)
            return
        
        total = sum(PRODUCTS[int(pid)]['price'] * qty for pid, qty in cart.items())
        
        text = "✅ <b>Заказ оформлен!</b>\n\n"
        text += f"<b>Состав заказа:</b>\n"
        for product_id, quantity in cart.items():
            product = PRODUCTS[int(product_id)]
            text += f"• {product['name']} x{quantity}\n"
        
        text += f"\n<b>Итого: {format_price(total)}</b>\n\n"
        text += "📞 С вами свяжется менеджер в ближайшее время для уточнения деталей доставки.\n\n"
        text += "Спасибо за заказ! 🙏"
        
        # Очищаем корзину
        save_user_cart(user_id, {})
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 Продолжить покупки", callback_data="back_to_categories")]
        ])
        
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode='HTML')
    
    # О магазине
    elif data == "about":
        from config import SITE_URL
        
        text = f"""
ℹ️ <b>О магазине МебельПремиум</b>

Мы - современный интернет-магазин мебели, который уже более 10 лет помогает создавать уютные и стильные интерьеры.

<b>Наши преимущества:</b>
⭐ Высокое качество продукции
💚 Экологически чистые материалы
👥 Профессиональные консультанты
🚀 Актуальные дизайнерские решения

<b>Статистика:</b>
• 10+ лет на рынке
• 5000+ довольных клиентов
• 1000+ моделей мебели
• 50+ городов доставки

🌐 <b>Посетите наш сайт:</b> {SITE_URL}

Для просмотра полного каталога, фотографий товаров и оформления заказа на сайте перейдите по ссылке выше.
        """
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 Открыть сайт", url=SITE_URL)],
            [InlineKeyboardButton("📦 Каталог", callback_data="back_to_categories")],
            [InlineKeyboardButton("🛒 Корзина", callback_data="cart")]
        ])
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode='HTML')
    
    # Назад к категориям
    elif data == "back_to_categories":
        text = "📦 <b>Каталог товаров</b>\n\nВыберите категорию:"
        await query.edit_message_text(text, reply_markup=get_category_keyboard(), parse_mode='HTML')
    
    # Назад к товарам категории
    elif data.startswith("back_to_products_"):
        category_id = data.split("_", 3)[3]
        cat_info = CATEGORIES[category_id]
        text = f"{cat_info['icon']} <b>{cat_info['name']}</b>\n\n"
        products = [p for p in PRODUCTS.values() if p['category'] == category_id]
        text += f"Найдено товаров: {len(products)}\n\n"
        keyboard = get_products_keyboard(category_id)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode='HTML')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    text = update.message.text
    
    if text == "📦 Каталог":
        await catalog(update, context)
    elif text == "🛒 Корзина":
        await cart(update, context)
    elif text == "ℹ️ О магазине":
        await about(update, context)
    elif text == "📞 Контакты":
        await contacts(update, context)
    else:
        await update.message.reply_text(
            "Используйте кнопки меню или команды:\n/start - Главное меню\n/catalog - Каталог\n/cart - Корзина",
            reply_markup=get_main_keyboard()
        )

def main():
    """Запуск бота"""
    from config import BOT_TOKEN
    
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ ОШИБКА: Установите BOT_TOKEN в файле .env или config.py")
        print("\n📝 Инструкция:")
        print("1. Создайте бота через @BotFather в Telegram")
        print("2. Получите токен")
        print("3. Создайте файл .env и добавьте: BOT_TOKEN=ваш_токен")
        return
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("catalog", catalog))
    application.add_handler(CommandHandler("cart", cart))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    print("🤖 Бот запущен!")
    print("Для остановки нажмите Ctrl+C")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

