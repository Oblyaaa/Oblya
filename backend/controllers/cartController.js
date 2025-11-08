// Простое хранилище корзин в памяти (в реальном приложении используйте БД)
const carts = new Map();

// Получить корзину
export const getCart = (req, res) => {
  try {
    const { sessionId } = req.params;
    const cart = carts.get(sessionId) || { items: [], total: 0 };

    // Пересчитать итого
    cart.total = cart.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    res.json({
      success: true,
      cart
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Ошибка при получении корзины',
      error: error.message
    });
  }
};

// Добавить товар в корзину
export const addToCart = (req, res) => {
  try {
    const { sessionId } = req.params;
    const { product, quantity = 1 } = req.body;

    if (!product || !product.id) {
      return res.status(400).json({
        success: false,
        message: 'Товар не указан'
      });
    }

    let cart = carts.get(sessionId) || { items: [] };

    // Проверить, есть ли товар уже в корзине
    const existingItemIndex = cart.items.findIndex(item => item.id === product.id);

    if (existingItemIndex !== -1) {
      // Увеличить количество
      cart.items[existingItemIndex].quantity += quantity;
    } else {
      // Добавить новый товар
      cart.items.push({
        ...product,
        quantity
      });
    }

    // Пересчитать итого
    cart.total = cart.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    carts.set(sessionId, cart);

    res.json({
      success: true,
      message: 'Товар добавлен в корзину',
      cart
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Ошибка при добавлении товара в корзину',
      error: error.message
    });
  }
};

// Обновить количество товара
export const updateCartItem = (req, res) => {
  try {
    const { sessionId } = req.params;
    const { productId, quantity } = req.body;

    if (!productId || quantity === undefined) {
      return res.status(400).json({
        success: false,
        message: 'Не указаны ID товара или количество'
      });
    }

    const cart = carts.get(sessionId);

    if (!cart) {
      return res.status(404).json({
        success: false,
        message: 'Корзина не найдена'
      });
    }

    const itemIndex = cart.items.findIndex(item => item.id === productId);

    if (itemIndex === -1) {
      return res.status(404).json({
        success: false,
        message: 'Товар не найден в корзине'
      });
    }

    if (quantity <= 0) {
      // Удалить товар, если количество <= 0
      cart.items.splice(itemIndex, 1);
    } else {
      cart.items[itemIndex].quantity = quantity;
    }

    // Пересчитать итого
    cart.total = cart.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    carts.set(sessionId, cart);

    res.json({
      success: true,
      message: 'Корзина обновлена',
      cart
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Ошибка при обновлении корзины',
      error: error.message
    });
  }
};

// Удалить товар из корзины
export const removeFromCart = (req, res) => {
  try {
    const { sessionId, productId } = req.params;

    const cart = carts.get(sessionId);

    if (!cart) {
      return res.status(404).json({
        success: false,
        message: 'Корзина не найдена'
      });
    }

    cart.items = cart.items.filter(item => item.id !== parseInt(productId));

    // Пересчитать итого
    cart.total = cart.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    carts.set(sessionId, cart);

    res.json({
      success: true,
      message: 'Товар удален из корзины',
      cart
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Ошибка при удалении товара из корзины',
      error: error.message
    });
  }
};

// Очистить корзину
export const clearCart = (req, res) => {
  try {
    const { sessionId } = req.params;

    carts.set(sessionId, { items: [], total: 0 });

    res.json({
      success: true,
      message: 'Корзина очищена',
      cart: { items: [], total: 0 }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Ошибка при очистке корзины',
      error: error.message
    });
  }
};

