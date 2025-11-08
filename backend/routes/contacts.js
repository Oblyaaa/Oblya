import express from 'express';
import { sendContactMessage, getContactMessages } from '../controllers/contactsController.js';

const router = express.Router();

// GET /api/contacts/messages - получить все сообщения (для админа)
router.get('/messages', getContactMessages);

// POST /api/contacts - отправить сообщение
router.post('/', sendContactMessage);

export default router;

