import express from 'express';
import { createOrder, getOrder, getOrders, updateOrderStatus } from '../controllers/ordersController.js';

const router = express.Router();

// GET /api/orders - получить все заказы (для админа)
router.get('/', getOrders);

// GET /api/orders/:orderId - получить заказ по ID
router.get('/:orderId', getOrder);

// POST /api/orders - создать новый заказ
router.post('/', createOrder);

// PUT /api/orders/:orderId/status - обновить статус заказа
router.put('/:orderId/status', updateOrderStatus);

export default router;

