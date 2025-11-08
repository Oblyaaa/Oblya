import { Link } from 'react-router-dom'
import { useCart } from '../context/CartContext'
import './Header.css'

const Header = () => {
  const { getTotalItems } = useCart()

  return (
    <header className="header">
      <div className="header-container">
        <Link to="/" className="logo">
          <span className="logo-icon">🌼</span>
          <span className="logo-text">РОМАШКА</span>
        </Link>
        
        <nav className="nav">
          <Link to="/" className="nav-link">Главная</Link>
          <Link to="/catalog" className="nav-link">Каталог</Link>
          <Link to="/about" className="nav-link">О нас</Link>
          <Link to="/delivery" className="nav-link">Доставка</Link>
          <Link to="/contacts" className="nav-link">Контакты</Link>
        </nav>

        <div className="header-actions">
          <Link to="/cart" className="cart-link">
            <span className="cart-icon">🛒</span>
            <span className="cart-count">{getTotalItems()}</span>
          </Link>
        </div>
      </div>
    </header>
  )
}

export default Header

