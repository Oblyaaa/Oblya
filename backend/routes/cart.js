import express from 'express';
import { getCart, addToCart, updateCartItem, removeFromCart, clearCart } from '../controllers/cartController.js';

const router = express.Router();

// GET /api/cart/:sessionId - получить корзину
router.get('/:sessionId', getCart);

// POST /api/cart/:sessionId/add - добавить товар в корзину
router.post('/:sessionId/add', addToCart);

// PUT /api/cart/:sessionId/update - обновить количество товара
router.put('/:sessionId/update', updateCartItem);

// DELETE /api/cart/:sessionId/remove/:productId - удалить товар из корзины
router.delete('/:sessionId/remove/:productId', removeFromCart);

// DELETE /api/cart/:sessionId/clear - очистить корзину
router.delete('/:sessionId/clear', clearCart);

export default router;

