import { test, expect } from '@playwright/test'

const BASE_URL = 'http://localhost:5173'
const API_URL = 'http://localhost:8000'

test.describe('Ecommerce E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/`)
  })

  test('register and login', async ({ page }) => {
    // register
    const username = `user_${Date.now()}`
    const password = 'password123'
    
    await page.fill('input[aria-label="username"]', username)
    await page.fill('input[aria-label="password"]', password)
    await page.click('button:has-text("Register")')
    
    // verify register success
    await expect(page.locator('text=Registered')).toBeVisible({ timeout: 5000 })
    
    // clear fields and login
    await page.fill('input[aria-label="username"]', username)
    await page.fill('input[aria-label="password"]', password)
    await page.click('button:has-text("Login")')
    
    // verify logged in
    const logoutBtn = page.locator('button:has-text("Logout")')
    await expect(logoutBtn).toBeEnabled({ timeout: 5000 })
  })

  test('add product to cart', async ({ page }) => {
    // register/login first
    const username = `user_${Date.now()}`
    const password = 'password123'
    
    await page.fill('input[aria-label="username"]', username)
    await page.fill('input[aria-label="password"]', password)
    await page.click('button:has-text("Register")')
    await expect(page.locator('text=Registered')).toBeVisible({ timeout: 5000 })
    
    await page.fill('input[aria-label="username"]', username)
    await page.fill('input[aria-label="password"]', password)
    await page.click('button:has-text("Login")')
    await expect(page.locator('button:has-text("Logout")').first()).toBeEnabled({ timeout: 5000 })
    
    // add product to cart
    const addBtns = page.locator('button[aria-label*="Add"]')
    if (await addBtns.count() > 0) {
      await addBtns.first().click()
      // verify cart has item
      await expect(page.locator('.cart li')).toHaveCount(1, { timeout: 5000 })
    }
  })
})
