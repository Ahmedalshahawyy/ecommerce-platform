import React from 'react'

export default function Cart({cart}){
  return (
    <div className="cart" aria-label="Shopping cart">
      <h2>Your Cart</h2>
      {cart.length === 0 ? <p>Cart empty</p> : (
        <ul>
          {cart.map(c => (
            <li key={c.product_id}>{c.name} x {c.quantity} — ${c.price.toFixed(2)}</li>
          ))}
        </ul>
      )}
    </div>
  )
}
