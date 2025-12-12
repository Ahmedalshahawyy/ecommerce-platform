import React, {useEffect, useState} from 'react'
import Login from './components/Login'
import ProductList from './components/ProductList'
import Cart from './components/Cart'

const API = 'http://localhost:8000'

export default function App(){
  const [products, setProducts] = useState([])
  const [token, setToken] = useState(localStorage.getItem('token') || '')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [cart, setCart] = useState([])

  useEffect(()=>{
    fetch(`${API}/products`)
      .then(r=>r.json())
      .then(setProducts)
      .catch(()=>setProducts([]))
  },[])

  useEffect(()=>{
    if(token) fetchCart()
  },[token])

  function saveToken(t){
    setToken(t)
    if(t) localStorage.setItem('token', t)
    else localStorage.removeItem('token')
  }

  async function register(){
    if(username.trim() === '' || password.trim() === ''){ alert('Both fields required'); return }
    const res = await fetch(`${API}/auth/register`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({username, password})
    })
    if(res.ok) alert('Registered, you can now log in')
    else alert('Register failed')
  }

  async function login(){
    if(username.trim() === '' || password.trim() === ''){ alert('Both fields required'); return }
    const body = new URLSearchParams({username, password})
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body
    })
    if(!res.ok){
      alert('Login failed')
      return
    }
    const data = await res.json()
    saveToken(data.access_token)
  }

  async function fetchCart(){
    const res = await fetch(`${API}/cart`, {headers: {Authorization: `Bearer ${token}`}})
    if(res.ok) setCart(await res.json())
  }

  async function addToCart(productId){
    if(!token){ alert('Login first'); return }
    const res = await fetch(`${API}/cart/add`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({product_id: productId, quantity: 1})
    })
    if(res.ok) fetchCart()
  }

  function logout(){ saveToken('') }

  return (
    <div className="app">
      <div className="header">
        <Login username={username} password={password} setUsername={setUsername} setPassword={setPassword} register={register} login={login} logout={logout} token={token} />
      </div>

      <main className="main">
        <ProductList products={products} addToCart={addToCart} />
        <Cart cart={cart} />
      </main>
    </div>
  )
}
