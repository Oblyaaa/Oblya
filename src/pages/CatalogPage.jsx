import { useState, useMemo } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { products, categories } from '../data/products'
import { useCart } from '../context/CartContext'
import './CatalogPage.css'

const CatalogPage = () => {
  const { category } = useParams()
  const navigate = useNavigate()
  const { addToCart } = useCart()
  const [selectedCategory, setSelectedCategory] = useState(category || 'all')
  const [priceRange, setPriceRange] = useState([0, 200000])
  const [selectedColor, setSelectedColor] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')

  const handleBuyClick = (e, product) => {
    e.preventDefault()
    e.stopPropagation()
    addToCart(product, 1)
    navigate('/cart')
  }

  const handleQuickOrder = (e, product) => {
    e.preventDefault()
    e.stopPropagation()
    // Здесь можно добавить логику быстрого заказа
    alert(`Быстрый заказ: ${product.name}`)
  }

  const colors = ['Бежевый', 'Белый', 'Черный', 'Дуб', 'Разноцветный']

  // Функция для поиска по главным буквам/словам
  const matchesSearch = (product, query) => {
    if (!query.trim()) return true
    
    const queryLower = query.toLowerCase().trim()
    const nameLower = product.name.toLowerCase()
    const descLower = product.description.toLowerCase()
    
    // Простой поиск по совпадению в названии или описании
    if (nameLower.includes(queryLower) || descLower.includes(queryLower)) {
      return true
    }
    
    // Поиск по первым буквам слов в названии (например, "ДК" для "Диван Комфорт")
    const nameWords = nameLower.split(/\s+/)
    const nameInitials = nameWords.map(w => w[0] || '').join('')
    if (nameInitials.includes(queryLower) || queryLower.startsWith(nameInitials.substring(0, queryLower.length))) {
      return true
    }
    
    // Поиск по началу каждого слова
    const queryWords = queryLower.split(/\s+/).filter(w => w.length > 0)
    const allWordsMatch = queryWords.every(queryWord => {
      // Проверка, начинается ли какое-то слово с запроса
      const nameMatch = nameWords.some(nameWord => nameWord.startsWith(queryWord))
      const descWords = descLower.split(/\s+/)
      const descMatch = descWords.some(descWord => descWord.startsWith(queryWord))
      return nameMatch || descMatch
    })
    
    return allWordsMatch
  }

  const filteredProducts = useMemo(() => {
    let filtered = products

    // Filter by search query
    if (searchQuery.trim()) {
      filtered = filtered.filter(p => matchesSearch(p, searchQuery))
    }

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(p => p.category === selectedCategory)
    }

    // Filter by price
    filtered = filtered.filter(p => p.price >= priceRange[0] && p.price <= priceRange[1])

    // Filter by color
    if (selectedColor !== 'all') {
      filtered = filtered.filter(p => p.color === selectedColor)
    }

    // Default sort by popularity (reviews)
    filtered = [...filtered].sort((a, b) => b.reviews - a.reviews)

    return filtered
  }, [selectedCategory, priceRange, selectedColor, searchQuery])

  return (
    <div className="catalog-page">
      <div className="container">
        <h1 className="page-title">Каталог товаров</h1>

        <div className="catalog-layout">
          {/* Filters Sidebar */}
          <aside className="filters-sidebar">
            <h3>Фильтры</h3>

            {/* Category Filter */}
            <div className="filter-group">
              <h4>Категория</h4>
              <div className="filter-options">
                <label className="filter-option">
                  <input
                    type="radio"
                    name="category"
                    value="all"
                    checked={selectedCategory === 'all'}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                  />
                  <span>Все категории</span>
                </label>
                {categories.map(cat => (
                  <label key={cat.id} className="filter-option">
                    <input
                      type="radio"
                      name="category"
                      value={cat.id}
                      checked={selectedCategory === cat.id}
                      onChange={(e) => setSelectedCategory(e.target.value)}
                    />
                    <span>{cat.icon} {cat.name}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Price Filter */}
            <div className="filter-group">
              <h4>Цена</h4>
              <div className="price-range">
                <input
                  type="range"
                  min="0"
                  max="200000"
                  step="1000"
                  value={priceRange[1]}
                  onChange={(e) => setPriceRange([priceRange[0], parseInt(e.target.value)])}
                />
                <div className="price-inputs">
                  <span>От {priceRange[0].toLocaleString()} ₽</span>
                  <span>До {priceRange[1].toLocaleString()} ₽</span>
                </div>
              </div>
            </div>

            {/* Color Filter */}
            <div className="filter-group">
              <h4>Цвет</h4>
              <select
                value={selectedColor}
                onChange={(e) => setSelectedColor(e.target.value)}
                className="filter-select"
              >
                <option value="all">Все цвета</option>
                {colors.map(color => (
                  <option key={color} value={color}>{color}</option>
                ))}
              </select>
            </div>

            <button
              className="reset-filters"
              onClick={() => {
                setSelectedCategory('all')
                setPriceRange([0, 200000])
                setSelectedColor('all')
                setSearchQuery('')
              }}
            >
              Сбросить фильтры
            </button>
          </aside>

          {/* Products Grid */}
          <div className="products-section">
            <div className="products-header">
              <div className="search-container">
                <input
                  type="text"
                  className="search-input"
                  placeholder="🔍 Поиск по названию или описанию..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <p className="products-count">Найдено товаров: {filteredProducts.length}</p>
            </div>

            {filteredProducts.length === 0 ? (
              <div className="no-products">
                <p>Товары не найдены. Попробуйте изменить фильтры.</p>
              </div>
            ) : (
              <div className="products-grid">
                {filteredProducts.map(product => (
                  <div
                    key={product.id}
                    className="product-card"
                  >
                    <Link to={`/product/${product.id}`} className="product-card-link">
                      <div className="product-image">
                        <img src={product.image} alt={product.name} />
                        {product.oldPrice && (
                          <span className="discount-badge">
                            -{Math.round((1 - product.price / product.oldPrice) * 100)}%
                          </span>
                        )}
                        {product.isBestseller && (
                          <span className="bestseller-badge">Хит продаж</span>
                        )}
                        <button className="favorite-button" onClick={(e) => { e.preventDefault(); e.stopPropagation(); }}>
                          🤍
                        </button>
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
                    
                    {/* Hover Panel with Details */}
                    <div className="product-hover-panel">
                      <div className="hover-details">
                        {product.article && (
                          <div className="detail-item">
                            <span className="detail-label">Артикул:</span>
                            <span className="detail-value">{product.article}</span>
                          </div>
                        )}
                        {product.dimensions && (
                          <div className="detail-item">
                            <span className="detail-label">Размеры:</span>
                            <span className="detail-value">{product.dimensions}</span>
                          </div>
                        )}
                        <div className="detail-item">
                          <span className="detail-label">В наличии:</span>
                          <span className="detail-value">
                            {product.inStock 
                              ? `✓ Доставим за ${product.deliveryDays || '2-7'} ${product.deliveryDays?.includes('-') ? 'дней' : 'день'}` 
                              : 'Нет в наличии'}
                          </span>
                        </div>
                      </div>
                      <div className="hover-actions">
                        <button 
                          className="buy-button"
                          onClick={(e) => handleBuyClick(e, product)}
                          disabled={!product.inStock}
                        >
                          🛒 Купить
                        </button>
                        <button 
                          className="quick-order-button"
                          onClick={(e) => handleQuickOrder(e, product)}
                          disabled={!product.inStock}
                        >
                          Заказ в 1 клик
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CatalogPage

