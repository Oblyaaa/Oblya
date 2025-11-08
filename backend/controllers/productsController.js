import { products } from '../../src/data/products.js';

// Получить все товары
export const getProducts = (req, res) => {
  try {
    const { category, minPrice, maxPrice, color, search } = req.query;
    let filteredProducts = [...products];

    // Фильтрация по категории
    if (category && category !== 'all') {
      filteredProducts = filteredProducts.filter(p => p.category === category);
    }

    // Фильтрация по цене
    if (minPrice) {
      filteredProducts = filteredProducts.filter(p => p.price >= parseInt(minPrice));
    }
    if (maxPrice) {
      filteredProducts = filteredProducts.filter(p => p.price <= parseInt(maxPrice));
    }

    // Фильтрация по цвету
    if (color && color !== 'all') {
      filteredProducts = filteredProducts.filter(p => p.color === color);
    }

    // Поиск
    if (search) {
      const searchLower = search.toLowerCase();
      filteredProducts = filteredProducts.filter(p => 
        p.name.toLowerCase().includes(searchLower) ||
        p.description.toLowerCase().includes(searchLower)
      );
    }

    res.json({
      success: true,
      count: filteredProducts.length,
      products: filteredProducts
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Ошибка при получении товаров',
      error: error.message
    });
  }
};

// Получить товар по ID
export const getProductById = (req, res) => {
  try {
    const { id } = req.params;
    const product = products.find(p => p.id === parseInt(id));

    if (!product) {
      return res.status(404).json({
        success: false,
        message: 'Товар не найден'
      });
    }

    res.json({
      success: true,
      product
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Ошибка при получении товара',
      error: error.message
    });
  }
};

// Поиск товаров
export const searchProducts = (req, res) => {
  try {
    const { q } = req.query;
    
    if (!q) {
      return res.json({
        success: true,
        count: 0,
        products: []
      });
    }

    const searchLower = q.toLowerCase();
    const matchedProducts = products.filter(p => 
      p.name.toLowerCase().includes(searchLower) ||
      p.description.toLowerCase().includes(searchLower) ||
      (p.article && p.article.toString().includes(q))
    );

    res.json({
      success: true,
      count: matchedProducts.length,
      products: matchedProducts
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Ошибка при поиске товаров',
      error: error.message
    });
  }
};

