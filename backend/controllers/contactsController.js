import { v4 as uuidv4 } from 'uuid';

// Простое хранилище сообщений в памяти (в реальном приложении используйте БД)
const messages = [];

// Отправить сообщение
export const sendContactMessage = (req, res) => {
  try {
    const { name, email, phone, subject, message } = req.body;

    if (!name || !email || !message) {
      return res.status(400).json({
        success: false,
        message: 'Не указаны обязательные поля: имя, email, сообщение'
      });
    }

    const messageId = uuidv4();
    const contactMessage = {
      id: messageId,
      name,
      email,
      phone: phone || '',
      subject: subject || 'Общий вопрос',
      message,
      read: false,
      createdAt: new Date().toISOString()
    };

    messages.push(contactMessage);

    // В реальном приложении здесь можно отправить email администратору

    res.status(201).json({
      success: true,
      message: 'Сообщение успешно отправлено',
      contactMessage
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Ошибка при отправке сообщения',
      error: error.message
    });
  }
};

// Получить все сообщения
export const getContactMessages = (req, res) => {
  try {
    res.json({
      success: true,
      count: messages.length,
      messages: messages.reverse() // Последние сообщения первыми
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Ошибка при получении сообщений',
      error: error.message
    });
  }
};

