import './ContactsPage.css'

const ContactsPage = () => {
  return (
    <div className="contacts-page">
      <div className="container">
        <h1 className="page-title">Контакты</h1>

        <div className="contacts-layout">
          <div className="contacts-info">
            <section className="contact-section">
              <h2>Свяжитесь с нами</h2>
              <p>Мы всегда рады ответить на ваши вопросы и помочь с выбором мебели.</p>

              <div className="contact-items">
                <div className="contact-item">
                  <span className="contact-icon">📞</span>
                  <div>
                    <h3>Телефон</h3>
                    <p>+7 (495) 123-45-67</p>
                    <p>+7 (800) 123-45-67 (бесплатно по России)</p>
                    <p className="contact-hours">Пн-Пт: 9:00-20:00, Сб-Вс: 10:00-18:00</p>
                  </div>
                </div>

                <div className="contact-item">
                  <span className="contact-icon">✉️</span>
                  <div>
                    <h3>Email</h3>
                    <p>info@romashka.ru</p>
                    <p>order@romashka.ru</p>
                  </div>
                </div>

                <div className="contact-item">
                  <span className="contact-icon">📍</span>
                  <div>
                    <h3>Адрес</h3>
                    <p>г. Москва, ул. Мебельная, д. 1</p>
                    <p>ТЦ "РОМАШКА", 2 этаж</p>
                    <p className="contact-hours">Пн-Вс: 10:00-21:00</p>
                  </div>
                </div>

                <div className="contact-item">
                  <span className="contact-icon">💬</span>
                  <div>
                    <h3>Онлайн-консультант</h3>
                    <p>Чат на сайте работает круглосуточно</p>
                    <p>Среднее время ответа: 2 минуты</p>
                  </div>
                </div>
              </div>
            </section>

            <section className="social-section">
              <h2>Мы в социальных сетях</h2>
              <div className="social-links">
                <a href="#" className="social-link">
                  <span className="social-icon">📘</span>
                  <span>Facebook</span>
                </a>
                <a href="#" className="social-link">
                  <span className="social-icon">📷</span>
                  <span>Instagram</span>
                </a>
                <a href="#" className="social-link">
                  <span className="social-icon">📱</span>
                  <span>VK</span>
                </a>
                <a href="#" className="social-link">
                  <span className="social-icon">📺</span>
                  <span>YouTube</span>
                </a>
              </div>
            </section>
          </div>

          <div className="contact-form-section">
            <h2>Напишите нам</h2>
            <form className="contact-form">
              <div className="form-group">
                <label htmlFor="name">Ваше имя *</label>
                <input type="text" id="name" name="name" required />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email *</label>
                <input type="email" id="email" name="email" required />
              </div>

              <div className="form-group">
                <label htmlFor="phone">Телефон</label>
                <input type="tel" id="phone" name="phone" />
              </div>

              <div className="form-group">
                <label htmlFor="subject">Тема обращения *</label>
                <select id="subject" name="subject" required>
                  <option value="">Выберите тему</option>
                  <option value="order">Вопрос по заказу</option>
                  <option value="delivery">Доставка</option>
                  <option value="return">Возврат/обмен</option>
                  <option value="consultation">Консультация</option>
                  <option value="other">Другое</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="message">Сообщение *</label>
                <textarea id="message" name="message" rows="5" required></textarea>
              </div>

              <button type="submit" className="submit-button">
                Отправить сообщение
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ContactsPage

