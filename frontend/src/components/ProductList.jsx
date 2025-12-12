import React from 'react'

export default function ProductList({products, addToCart}){
  return (
    <div className="product-list" aria-live="polite">
      <h1>Products</h1>
      {products.length === 0 ? (
        <p>No products yet. Add via backend POST /products.</p>
      ) : (
        <ul>
          {products.map(p=> (
            <li key={p.id} className="product-item">
              <div>
                <strong>{p.name}</strong>
                <div className="price">${p.price.toFixed(2)}</div>
              </div>
              <button type="button" onClick={()=>addToCart(p.id)} className="add" aria-label={`Add ${p.name} to cart`}>Add</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
