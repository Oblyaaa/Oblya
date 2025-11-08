# РОМАШКА - Интернет-магазин мебели

Современный веб-сайт для мебельного магазина, созданный с использованием React, Vite и Express.

## Установка и запуск

### 1. Установите зависимости:
```bash
npm install
```

### 2. Запуск фронтенда (React):
```bash
npm run dev
```
Откройте браузер и перейдите по адресу, который появится в консоли (обычно http://localhost:5173)

### 3. Запуск backend (Express API):
```bash
npm run server
```
Backend сервер запустится на http://localhost:3001

Или с автоперезагрузкой:
```bash
npm run dev:server
```

### 4. Запуск фронтенда и backend одновременно:

Откройте два терминала:
- Терминал 1: `npm run dev` (фронтенд)
- Терминал 2: `npm run server` (backend)

## Быстрый просмотр без npm

Откройте файл `index-simple.html` двойным кликом в браузере (упрощенная версия).

## Backend API

Backend API доступен на `http://localhost:3001/api`

### Основные endpoints:

- **Товары**: `/api/products`
- **Корзина**: `/api/cart/:sessionId`
- **Заказы**: `/api/orders`
- **Контакты**: `/api/contacts`
- **Health Check**: `/api/health`

Подробная документация API находится в файле `backend/README.md`

## Структура проекта

```
furniture-store/
├── src/                    # React приложение
│   ├── components/         # Компоненты
│   ├── pages/             # Страницы
│   ├── data/              # Данные товаров
│   └── context/           # React Context
├── backend/               # Backend API
│   ├── routes/            # Маршруты API
│   ├── controllers/       # Контроллеры
│   └── README.md          # Документация API
├── server.js              # Основной файл сервера
├── index.html             # Главная HTML страница
└── package.json           # Зависимости проекта
```

## Технологии

- **Frontend**: React, React Router, Vite
- **Backend**: Express.js, Node.js
- **Стили**: CSS3

