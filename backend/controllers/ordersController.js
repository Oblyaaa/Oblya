import { v4 as uuidv4 } from 'uuid';

// Простое хранилище заказов в памяти (в реальном приложении используйте БД)
const orders = new Map();

// Создать заказ
export const createOrder = (req, res) => {
  try {
    const { customer, items, total, deliveryAddress, paymentMethod, phone, email } = req.body;

    if (!items || items.length === 0) {
      return res.status(400).json({
        success: false,
        message: 'Корзина пуста'
      });
    }

    if (!customer || !phone || !deliveryAddress) {
      return res.status(400).json({
        success: false,
        message: 'Не указаны обязательные поля: имя, телефон, адрес доставки'
      });
    }

    const orderId = uuidv4();
    const order = {
      id: orderId,
      customer,
      items,
      total,
      deliveryAddress,
      paymentMethod: paymentMethod || 'card',
      phone,
      email: email || '',
      status: 'pending', // pending, confirmed, processing, shipped, delivered, cancelled
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    orders.set(orderId, order);

    res.status(201).json({
      success: true,
      message: 'Заказ успешно создан',
      order
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Ошибка при создании заказа',
      error: error.message
    });
  }
};

// Получить заказ по ID
export const getOrder = (req, res) => {
  try {
    const { orderId } = req.params;
    const order = orders.get(orderId);

    if (!order) {
      return res.status(404).json({
        success: false,
        message: 'Заказ не найден'
      });
    }

    res.json({
      success: true,
      order
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Ошибка при получении заказа',
      error: error.message
    });
  }
};

// Получить все заказы
export const getOrders = (req, res) => {
  try {
    const ordersList = Array.from(orders.values());
    
    res.json({
      success: true,
      count: ordersList.length,
      orders: ordersList
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Ошибка при получении заказов',
      error: error.message
    });
  }
};

// Обновить статус заказа
export const updateOrderStatus = (req, res) => {
  try {
    const { orderId } = req.params;
    const { status } = req.body;

    const validStatuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled'];
    
    if (!validStatuses.includes(status)) {
      return res.status(400).json({
        success: false,
        message: `Неверный статус. Допустимые значения: ${validStatuses.join(', ')}`
      });
    }

    const order = orders.get(orderId);

    if (!order) {
      return res.status(404).json({
        success: false,
        message: 'Заказ не найден'
      });
    }

    order.status = status;
    order.updatedAt = new Date().toISOString();

    orders.set(orderId, order);

    res.json({
      success: true,
      message: 'Статус заказа обновлен',
      order
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Ошибка при обновлении статуса заказа',
      error: error.message
    });
  }
};

