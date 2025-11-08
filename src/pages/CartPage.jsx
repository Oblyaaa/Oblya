import { Link } from 'react-router-dom'
import { useCart } from '../context/CartContext'
import './CartPage.css'

const CartPage = () => {
  const { cartItems, removeFromCart, updateQuantity, getTotalPrice, clearCart } = useCart()

  if (cartItems.length === 0) {
    return (
      <div className="cart-page">
        <div className="container">
          <h1 className="page-title">Корзина</h1>
          <div className="empty-cart">
            <span className="empty-cart-icon">🛒</span>
            <h2>Ваша корзина пуста</h2>
            <p>Добавьте товары из каталога</p>
            <Link to="/catalog" className="go-to-catalog-button">
              Перейти в каталог
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="cart-page">
      <div className="container">
        <h1 className="page-title">Корзина</h1>

        <div className="cart-layout">
          <div className="cart-items">
            {cartItems.map(item => (
              <div key={item.id} className="cart-item">
                <Link to={`/product/${item.id}`} className="cart-item-image">
                  <img src={item.image} alt={item.name} />
                </Link>
                <div className="cart-item-info">
                  <Link to={`/product/${item.id}`}>
                    <h3>{item.name}</h3>
                  </Link>
                  <p className="cart-item-description">{item.description}</p>
                  <div className="cart-item-price">
                    {item.oldPrice && (
                      <span className="old-price">{item.oldPrice.toLocaleString()} ₽</span>
                    )}
                    <span className="current-price">{item.price.toLocaleString()} ₽</span>
                  </div>
                </div>
                <div className="cart-item-controls">
                  <div className="quantity-controls">
                    <button onClick={() => updateQuantity(item.id, item.quantity - 1)}>-</button>
                    <span>{item.quantity}</span>
                    <button onClick={() => updateQuantity(item.id, item.quantity + 1)}>+</button>
                  </div>
                  <div className="cart-item-total">
                    {(item.price * item.quantity).toLocaleString()} ₽
                  </div>
                  <button
                    className="remove-button"
                    onClick={() => removeFromCart(item.id)}
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
            <button className="clear-cart-button" onClick={clearCart}>
              Очистить корзину
            </button>
          </div>

          <div className="cart-summary">
            <h2>Итого</h2>
            <div className="summary-row">
              <span>Товаров:</span>
              <span>{cartItems.reduce((sum, item) => sum + item.quantity, 0)}</span>
            </div>
            <div className="summary-row">
              <span>Сумма:</span>
              <span className="total-price">{getTotalPrice().toLocaleString()} ₽</span>
            </div>
            <div className="summary-info">
              <p>💰 Бесплатная доставка при заказе от 50000 ₽</p>
            </div>
            <button className="checkout-button">
              Оформить заказ
            </button>
            <Link to="/catalog" className="continue-shopping">
              Продолжить покупки
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CartPage

