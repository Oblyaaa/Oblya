import { Link } from 'react-router-dom'
import { categories, products } from '../data/products'
import './HomePage.css'

const HomePage = () => {
  const featuredProducts = products.slice(0, 6)
  const testimonials = [
    { name: 'Анна Смирнова', text: 'Отличный магазин! Диван превзошел все ожидания. Качество на высоте, доставка быстрая.', rating: 5 },
    { name: 'Дмитрий Петров', text: 'Заказывали кухню, очень довольны. Профессиональные консультанты помогли выбрать идеальный вариант.', rating: 5 },
    { name: 'Мария Иванова', text: 'Приобрели детскую кровать. Ребенок в восторге, а мы довольны качеством и безопасностью.', rating: 5 }
  ]

  return (
    <div className="homepage">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1>Мебель Премиум Класса от РОМАШКА</h1>
          <p>Широкий ассортимент качественной мебели с доставкой по всей России</p>
          <Link to="/catalog" className="cta-button">Смотреть каталог</Link>
        </div>
        <div className="hero-image">
          <img src="https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=1200" alt="Мебель" />
        </div>
      </section>

      {/* Advantages */}
      <section className="advantages">
        <div className="container">
          <div className="advantages-grid">
            <div className="advantage-item">
              <span className="advantage-icon">🚚</span>
              <h3>Бесплатная доставка</h3>
              <p>При заказе от 50000 ₽</p>
            </div>
            <div className="advantage-item">
              <span className="advantage-icon">🛡️</span>
              <h3>Гарантия качества</h3>
              <p>2 года гарантии на всю продукцию</p>
            </div>
            <div className="advantage-item">
              <span className="advantage-icon">💰</span>
              <h3>Лучшие цены</h3>
              <p>Регулярные акции и скидки</p>
            </div>
            <div className="advantage-item">
              <span className="advantage-icon">⚡</span>
              <h3>Быстрая сборка</h3>
              <p>Профессиональная сборка в день доставки</p>
            </div>
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="categories-section">
        <div className="container">
          <h2 className="section-title">Категории товаров</h2>
          <div className="categories-grid">
            {categories.map(category => (
              <Link
                key={category.id}
                to={`/catalog/${category.id}`}
                className="category-card"
              >
                <span className="category-icon">{category.icon}</span>
                <h3>{category.name}</h3>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="featured-products">
        <div className="container">
          <h2 className="section-title">Популярные товары</h2>
          <div className="products-grid">
            {featuredProducts.map(product => (
              <Link
                key={product.id}
                to={`/product/${product.id}`}
                className="product-card"
              >
                <div className="product-image">
                  <img src={product.image} alt={product.name} />
                  {product.oldPrice && (
                    <span className="discount-badge">
                      -{Math.round((1 - product.price / product.oldPrice) * 100)}%
                    </span>
                  )}
                </div>
                <div className="product-info">
                  <h3>{product.name}</h3>
                  <p className="product-description">{product.description}</p>
                  <div className="product-rating">
                    <span>⭐ {product.rating}</span>
                    <span>({product.reviews} отзывов)</span>
                  </div>
                  <div className="product-price">
                    {product.oldPrice && (
                      <span className="old-price">{product.oldPrice.toLocaleString()} ₽</span>
                    )}
                    <span className="current-price">{product.price.toLocaleString()} ₽</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
          <div className="section-footer">
            <Link to="/catalog" className="view-all-button">Посмотреть все товары</Link>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="testimonials">
        <div className="container">
          <h2 className="section-title">Отзывы наших клиентов</h2>
          <div className="testimonials-grid">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="testimonial-card">
                <div className="testimonial-rating">
                  {'⭐'.repeat(testimonial.rating)}
                </div>
                <p className="testimonial-text">"{testimonial.text}"</p>
                <p className="testimonial-author">— {testimonial.name}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}

export default HomePage

