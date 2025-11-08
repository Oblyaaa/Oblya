import './AboutPage.css'

const AboutPage = () => {
  return (
    <div className="about-page">
      <div className="container">
        <h1 className="page-title">О нас</h1>

        <section className="about-section">
          <div className="about-content">
            <h2>Добро пожаловать в РОМАШКА</h2>
            <p>
              Мы - современный интернет-магазин мебели, который уже более 10 лет помогает 
              создавать уютные и стильные интерьеры. Наша миссия - сделать качественную мебель 
              доступной каждому, кто ценит комфорт и красоту в своем доме.
            </p>
            <p>
              Мы тщательно отбираем каждый товар, работая только с проверенными производителями, 
              которые используют экологически чистые материалы и современные технологии производства.
            </p>
          </div>
          <div className="about-image">
            <img src="https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800" alt="О нас" />
          </div>
        </section>

        <section className="values-section">
          <h2>Наши ценности</h2>
          <div className="values-grid">
            <div className="value-item">
              <span className="value-icon">⭐</span>
              <h3>Качество</h3>
              <p>Мы гарантируем высокое качество всей продукции и предоставляем официальную гарантию производителя.</p>
            </div>
            <div className="value-item">
              <span className="value-icon">💚</span>
              <h3>Экологичность</h3>
              <p>Вся мебель изготавливается из безопасных материалов, соответствующих экологическим стандартам.</p>
            </div>
            <div className="value-item">
              <span className="value-icon">👥</span>
              <h3>Клиентоориентированность</h3>
              <p>Наши консультанты всегда готовы помочь вам выбрать идеальную мебель для вашего дома.</p>
            </div>
            <div className="value-item">
              <span className="value-icon">🚀</span>
              <h3>Инновации</h3>
              <p>Мы следим за последними трендами в дизайне и предлагаем актуальные решения для интерьера.</p>
            </div>
          </div>
        </section>

        <section className="stats-section">
          <h2>МебельПремиум в цифрах</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-number">10+</div>
              <div className="stat-label">Лет на рынке</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">5000+</div>
              <div className="stat-label">Довольных клиентов</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">1000+</div>
              <div className="stat-label">Моделей мебели</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">50+</div>
              <div className="stat-label">Городов доставки</div>
            </div>
          </div>
        </section>

        <section className="team-section">
          <h2>Наша команда</h2>
          <p className="team-description">
            Наша команда состоит из профессионалов, которые любят свое дело и всегда готовы 
            помочь вам найти идеальное решение для вашего интерьера. От дизайнеров до менеджеров 
            по доставке - каждый член нашей команды стремится обеспечить лучший сервис.
          </p>
        </section>
      </div>
    </div>
  )
}

export default AboutPage

