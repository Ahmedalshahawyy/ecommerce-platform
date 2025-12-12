# Contributing to Ecommerce Platform

Thank you for your interest in contributing! This guide explains how to set up your environment and submit changes.

## Development Setup

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies with dev extras
pip install -r requirements.txt
pip install ruff black pytest-cov

# Copy environment file
cp .env.example .env
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Install linting tools
npm install --save-dev eslint prettier eslint-plugin-react eslint-plugin-react-hooks
```

## Code Quality Standards

### Backend

Before committing, ensure code passes linting and formatting:

```bash
cd backend

# Check with ruff
ruff check .

# Format with black
black .

# Run tests
pytest tests/ -v
```

### Frontend

Before committing, ensure code passes linting:

```bash
cd frontend

# Lint
npm run lint

# Format
npm run format

# Build to check for errors
npm run build
```

## Testing Requirements

All pull requests must include tests:

### Backend Tests

```bash
cd backend

# Run unit tests
pytest tests/test_api.py -v

# Run integration tests (requires backend running)
pytest tests/test_integration.py -v

# Run all tests with coverage
pytest --cov=./ tests/
```

### Frontend Tests

```bash
cd frontend

# Run E2E tests (requires full stack running)
npm run test:e2e

# Or with UI
npx playwright test --ui
```

## Workflow

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/ecommerce-platform.git
   cd ecommerce-platform
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/descriptive-name
   ```

3. **Make Changes**
   - Write code following the style guides below
   - Add tests for new functionality
   - Update documentation as needed

4. **Run Quality Checks**
   ```bash
   # Backend
   cd backend && ruff check . && black . && pytest tests/

   # Frontend
   cd frontend && npm run lint && npm run format && npm run build
   ```

5. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add descriptive commit message"
   git push origin feature/descriptive-name
   ```

6. **Open Pull Request**
   - Use a clear title describing the change
   - Reference any related issues
   - Describe the motivation and implementation details
   - Screenshots for UI changes

## Style Guides

### Python (Backend)

- **Line length**: 100 characters (configured in pyproject.toml)
- **Formatter**: black
- **Linter**: ruff with fixes enabled
- **Type hints**: Encouraged for new functions
- **Docstrings**: Use for public APIs

Example:

```python
def create_user(email: str, password: str) -> User:
    """Create a new user account.
    
    Args:
        email: User's email address
        password: User's password (will be hashed)
        
    Returns:
        Created User object
    """
    user = User(email=email)
    user.set_password(password)
    return user
```

### JavaScript/React (Frontend)

- **Line length**: 100 characters
- **Formatter**: Prettier
- **Linter**: ESLint
- **Naming**: camelCase for functions/variables, PascalCase for components
- **Comments**: JSDoc for complex logic

Example:

```javascript
/**
 * Adds an item to the shopping cart
 * @param {string} productId - The product to add
 * @param {number} quantity - How many to add
 * @returns {Promise<void>}
 */
const addToCart = async (productId, quantity) => {
  const response = await fetch(`${API_URL}/cart`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ product_id: productId, quantity }),
  });
  return response.json();
};
```

## Database Changes

If you modify models in `backend/models.py`:

1. Create a new migration:
   ```bash
   cd backend
   alembic revision --autogenerate -m "describe your change"
   ```

2. Review the generated file in `alembic/versions/`

3. Apply locally:
   ```bash
   python migrate.py
   ```

4. Test:
   ```bash
   pytest tests/test_api.py -v
   ```

5. Commit both the model change and migration file

## Commit Messages

Use conventional commit format:

```
feat: add new product filtering
fix: resolve cart item duplication bug
docs: update API endpoints documentation
test: add tests for user registration
chore: update dependencies
refactor: simplify authentication logic
```

## CI/CD Pipeline

All pull requests automatically run:

- ✅ Backend tests (pytest)
- ✅ Frontend lint & build
- ✅ Integration tests with PostgreSQL
- ✅ E2E tests with Playwright

All checks must pass before merging.

## Questions?

- Check existing [GitHub Issues](https://github.com/your-repo/issues)
- Start a [GitHub Discussion](https://github.com/your-repo/discussions)
- Open a pull request with a question in the description

Thank you for contributing! 🙌
