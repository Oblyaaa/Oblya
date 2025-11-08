import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { products } from '../data/products'
import { useCart } from '../context/CartContext'
import './ProductPage.css'

const ProductPage = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { addToCart } = useCart()
  const [selectedImage, setSelectedImage] = useState(0)
  const [quantity, setQuantity] = useState(1)

  const product = products.find(p => p.id === parseInt(id))

  if (!product) {
    return (
      <div className="product-page">
        <div className="container">
          <p>Товар не найден</p>
        </div>
      </div>
    )
  }

  const handleAddToCart = () => {
    addToCart(product, quantity)
    navigate('/cart')
  }

  return (
    <div className="product-page">
      <div className="container">
        <button className="back-button" onClick={() => navigate(-1)}>
          ← Назад
        </button>

        <div className="product-details">
          {/* Images */}
          <div className="product-images">
            <div className="main-image">
              <img src={product.images[selectedImage]} alt={product.name} />
              {product.oldPrice && (
                <span className="discount-badge">
                  -{Math.round((1 - product.price / product.oldPrice) * 100)}%
                </span>
              )}
            </div>
            <div className="thumbnail-images">
              {product.images.map((img, index) => (
                <img
                  key={index}
                  src={img}
                  alt={`${product.name} ${index + 1}`}
                  className={selectedImage === index ? 'active' : ''}
                  onClick={() => setSelectedImage(index)}
                />
              ))}
            </div>
          </div>

          {/* Product Info */}
          <div className="product-info-section">
            <h1>{product.name}</h1>
            
            <div className="product-rating-section">
              <div className="rating">
                <span className="stars">{'⭐'.repeat(Math.floor(product.rating))}</span>
                <span className="rating-value">{product.rating}</span>
                <span className="reviews-count">({product.reviews} отзывов)</span>
              </div>
            </div>

            <div className="product-price-section">
              {product.oldPrice && (
                <span className="old-price">{product.oldPrice.toLocaleString()} ₽</span>
              )}
              <span className="current-price">{product.price.toLocaleString()} ₽</span>
            </div>

            <div className="product-description-section">
              <h3>Описание</h3>
              <p>{product.fullDescription}</p>
            </div>

            <div className="product-specs">
              <div className="spec-item">
                <span className="spec-label">Материал:</span>
                <span className="spec-value">{product.material}</span>
              </div>
              <div className="spec-item">
                <span className="spec-label">Размеры:</span>
                <span className="spec-value">{product.dimensions}</span>
              </div>
              <div className="spec-item">
                <span className="spec-label">Цвет:</span>
                <span className="spec-value">{product.color}</span>
              </div>
              <div className="spec-item">
                <span className="spec-label">Стиль:</span>
                <span className="spec-value">{product.style}</span>
              </div>
            </div>

            <div className="availability">
              {product.inStock ? (
                <span className="in-stock">✓ В наличии</span>
              ) : (
                <span className="out-of-stock">✗ Нет в наличии</span>
              )}
            </div>

            <div className="purchase-section">
              <div className="quantity-controls">
                <label>Количество:</label>
                <div className="quantity-input">
                  <button onClick={() => setQuantity(Math.max(1, quantity - 1))}>-</button>
                  <input
                    type="number"
                    min="1"
                    value={quantity}
                    onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                  />
                  <button onClick={() => setQuantity(quantity + 1)}>+</button>
                </div>
              </div>

              <button
                className="add-to-cart-button"
                onClick={handleAddToCart}
                disabled={!product.inStock}
              >
                {product.inStock ? 'Добавить в корзину' : 'Товар недоступен'}
              </button>
            </div>

            <div className="product-features">
              <div className="feature">
                <span className="feature-icon">🚚</span>
                <span>Бесплатная доставка от 50000 ₽</span>
              </div>
              <div className="feature">
                <span className="feature-icon">🛡️</span>
                <span>Гарантия 2 года</span>
              </div>
              <div className="feature">
                <span className="feature-icon">⚡</span>
                <span>Быстрая сборка</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProductPage

