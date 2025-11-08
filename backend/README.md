# Backend API для магазина РОМАШКА

## Запуск сервера

```bash
npm run server
# или с автоперезагрузкой
npm run dev:server
```

Сервер запустится на `http://localhost:3001`

## API Endpoints

### Товары

- `GET /api/products` - получить все товары
  - Query параметры:
    - `category` - фильтр по категории
    - `minPrice` - минимальная цена
    - `maxPrice` - максимальная цена
    - `color` - фильтр по цвету
    - `search` - поиск по названию/описанию

- `GET /api/products/search?q=query` - поиск товаров

- `GET /api/products/:id` - получить товар по ID

### Корзина

- `GET /api/cart/:sessionId` - получить корзину
- `POST /api/cart/:sessionId/add` - добавить товар в корзину
  - Body: `{ product: {...}, quantity: 1 }`
- `PUT /api/cart/:sessionId/update` - обновить количество товара
  - Body: `{ productId: 1, quantity: 2 }`
- `DELETE /api/cart/:sessionId/remove/:productId` - удалить товар из корзины
- `DELETE /api/cart/:sessionId/clear` - очистить корзину

### Заказы

- `GET /api/orders` - получить все заказы
- `GET /api/orders/:orderId` - получить заказ по ID
- `POST /api/orders` - создать новый заказ
  - Body: `{ customer, items, total, deliveryAddress, paymentMethod, phone, email }`
- `PUT /api/orders/:orderId/status` - обновить статус заказа
  - Body: `{ status: 'confirmed' }`
  - Статусы: `pending`, `confirmed`, `processing`, `shipped`, `delivered`, `cancelled`

### Контакты

- `GET /api/contacts/messages` - получить все сообщения
- `POST /api/contacts` - отправить сообщение
  - Body: `{ name, email, phone, subject, message }`

## Health Check

- `GET /api/health` - проверка работы сервера

## Примеры использования

### Получить все товары категории "Гостиная"

```bash
GET http://localhost:3001/api/products?category=living-room
```

### Добавить товар в корзину

```bash
POST http://localhost:3001/api/cart/session123/add
Content-Type: application/json

{
  "product": {
    "id": 1,
    "name": "Диван \"Комфорт\"",
    "price": 45900
  },
  "quantity": 1
}
```

### Создать заказ

```bash
POST http://localhost:3001/api/orders
Content-Type: application/json

{
  "customer": "Иван Иванов",
  "items": [
    {
      "id": 1,
      "name": "Диван \"Комфорт\"",
      "price": 45900,
      "quantity": 1
    }
  ],
  "total": 45900,
  "deliveryAddress": "г. Москва, ул. Примерная, д. 1, кв. 1",
  "paymentMethod": "card",
  "phone": "+7 (999) 123-45-67",
  "email": "ivan@example.com"
}
```

## Примечания

- В текущей реализации данные хранятся в памяти и будут потеряны при перезапуске сервера
- Для production используйте базу данных (MongoDB, PostgreSQL и т.д.)
- Добавьте аутентификацию и авторизацию для админ-панели
- Добавьте валидацию данных с помощью библиотеки типа Joi или express-validator

