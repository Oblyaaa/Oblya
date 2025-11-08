import express from 'express';
import { getProducts, getProductById, searchProducts } from '../controllers/productsController.js';
import { products } from '../../src/data/products.js';

const router = express.Router();

// GET /api/products - получить все товары
router.get('/', getProducts);

// GET /api/products/search?q=query - поиск товаров
router.get('/search', searchProducts);

// GET /api/products/:id - получить товар по ID
router.get('/:id', getProductById);

export default router;

