import './DeliveryPage.css'

const DeliveryPage = () => {
  return (
    <div className="delivery-page">
      <div className="container">
        <h1 className="page-title">Доставка и оплата</h1>

        <section className="delivery-section">
          <h2>Доставка</h2>
          
          <div className="delivery-options">
            <div className="delivery-option">
              <span className="delivery-icon">🚚</span>
              <h3>Бесплатная доставка</h3>
              <p className="delivery-condition">При заказе от 50 000 ₽</p>
              <p>Доставка осуществляется по всей России. Срок доставки: 3-7 рабочих дней.</p>
            </div>

            <div className="delivery-option">
              <span className="delivery-icon">💰</span>
              <h3>Платная доставка</h3>
              <p className="delivery-condition">При заказе до 50 000 ₽</p>
              <p>Стоимость доставки зависит от региона и веса товара. Обычно от 500 до 3000 ₽.</p>
            </div>

            <div className="delivery-option">
              <span className="delivery-icon">⚡</span>
              <h3>Экспресс-доставка</h3>
              <p className="delivery-condition">Доставка за 1-2 дня</p>
              <p>Доступна в крупных городах. Стоимость рассчитывается индивидуально.</p>
            </div>
          </div>

          <div className="delivery-info">
            <h3>Как происходит доставка?</h3>
            <ol className="delivery-steps">
              <li>После оформления заказа с вами свяжется менеджер для уточнения адреса и удобного времени доставки.</li>
              <li>Мы доставим товар по указанному адресу в согласованное время.</li>
              <li>При доставке вы можете проверить товар и убедиться в его качестве.</li>
              <li>Наши специалисты помогут собрать мебель прямо у вас дома (при необходимости).</li>
            </ol>
          </div>

          <div className="delivery-terms">
            <h3>Условия доставки</h3>
            <ul>
              <li>Доставка осуществляется только в рабочие дни с 9:00 до 20:00</li>
              <li>Подъем на этаж включен в стоимость доставки (до 5 этажа)</li>
              <li>При подъеме выше 5 этажа или при отсутствии лифта взимается дополнительная плата</li>
              <li>Вы можете отслеживать статус заказа в личном кабинете</li>
            </ul>
          </div>
        </section>

        <section className="payment-section">
          <h2>Способы оплаты</h2>

          <div className="payment-options">
            <div className="payment-option">
              <span className="payment-icon">💳</span>
              <h3>Банковской картой онлайн</h3>
              <p>Оплата картами Visa, MasterCard, МИР через защищенный платежный шлюз.</p>
            </div>

            <div className="payment-option">
              <span className="payment-icon">📱</span>
              <h3>Электронные кошельки</h3>
              <p>Оплата через Яндекс.Кассу, Qiwi, WebMoney и другие электронные системы.</p>
            </div>

            <div className="payment-option">
              <span className="payment-icon">💵</span>
              <h3>Наличными при получении</h3>
              <p>Оплата наличными курьеру при доставке товара.</p>
            </div>

            <div className="payment-option">
              <span className="payment-icon">🏦</span>
              <h3>Банковский перевод</h3>
              <p>Оплата по счету для юридических лиц и индивидуальных предпринимателей.</p>
            </div>
          </div>

          <div className="payment-security">
            <h3>Безопасность платежей</h3>
            <p>
              Все платежи обрабатываются через защищенные платежные системы. 
              Мы не храним данные ваших банковских карт. Все транзакции защищены протоколом SSL.
            </p>
          </div>
        </section>

        <section className="return-section">
          <h2>Возврат и обмен</h2>
          <div className="return-info">
            <p>
              Вы можете вернуть товар в течение 14 дней с момента покупки, если он не был в употреблении, 
              сохранены его товарный вид, потребительские свойства, пломбы, фабричные ярлыки.
            </p>
            <p>
              Возврат товара надлежащего качества возможен при условии сохранения его товарного вида 
              и упаковки. Расходы на доставку при возврате товара надлежащего качества несет покупатель.
            </p>
            <p>
              Товары ненадлежащего качества обмениваются или возвращаются в течение гарантийного срока. 
              Все расходы по возврату товара ненадлежащего качества несет продавец.
            </p>
          </div>
        </section>
      </div>
    </div>
  )
}

export default DeliveryPage

