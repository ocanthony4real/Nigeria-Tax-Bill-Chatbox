# Contributing

Thank you for your interest in contributing to the Nigeria Tax Bill Chatbot!

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Git
- Docker (optional)

### Setup Development Environment

1. **Fork the repository**

   Click the "Fork" button on GitHub.

2. **Clone your fork**

   ```bash
   git clone https://github.com/YOUR_USERNAME/Nigeria-Tax-Bill-Chatbox.git
   cd Nigeria-Tax-Bill-Chatbox
   ```

3. **Install dependencies**

   ```bash
   # Python
   poetry install
   # or
   pip install -r requirements.txt

   # Node.js (frontend)
   cd web/frontend
   npm install
   ```

4. **Set up environment**

   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

---

## Development Workflow

### Branch Naming

| Type | Format | Example |
|------|--------|---------|
| Feature | `feature/description` | `feature/add-export-pdf` |
| Bug Fix | `fix/description` | `fix/citation-parsing` |
| Docs | `docs/description` | `docs/update-api-reference` |
| Refactor | `refactor/description` | `refactor/rag-pipeline` |

### Making Changes

1. **Create a branch**

   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make your changes**

3. **Run tests**

   ```bash
   pytest tests/
   ```

4. **Run linting**

   ```bash
   ruff check .
   black --check .
   ```

5. **Commit changes**

   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

6. **Push to your fork**

   ```bash
   git push origin feature/my-feature
   ```

7. **Create Pull Request**

   Go to GitHub and create a PR from your fork.

---

## Code Style

### Python

We use:
- **Black** for formatting
- **Ruff** for linting
- **MyPy** for type checking

```bash
# Format
black .

# Lint
ruff check --fix .

# Type check
mypy llm_engineering
```

### TypeScript

We use:
- **ESLint** for linting
- **Prettier** for formatting

```bash
cd web/frontend
npm run lint
npm run format
```

### Pre-commit Hooks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

---

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `style` | Formatting |
| `refactor` | Code refactoring |
| `test` | Adding tests |
| `chore` | Maintenance |

**Examples:**

```
feat: add PDF export functionality
fix: correct section parsing for multi-digit sections
docs: update API reference with new endpoints
refactor: simplify RAG pipeline context formatting
```

---

## Pull Request Guidelines

### PR Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
- [ ] Tests pass locally
- [ ] New tests added

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes
```

### Review Process

1. Create PR with description
2. Wait for CI checks to pass
3. Request review from maintainers
4. Address feedback
5. Merge when approved

---

## Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=llm_engineering

# Specific test
pytest tests/test_rag.py
```

### Writing Tests

```python
# tests/test_example.py
import pytest
from llm_engineering.application.rag import TaxBillRetriever

def test_retriever_search():
    retriever = TaxBillRetriever()
    results = retriever.search("VAT rate", k=5)

    assert len(results) == 5
    assert all(hasattr(r, 'content') for r in results)

@pytest.fixture
def sample_chunk():
    return TaxBillChunk(
        id="test",
        content="Test content",
        section="148",
        page_number=88
    )
```

---

## Documentation

### Building Docs

```bash
# Install MkDocs
pip install mkdocs-material

# Serve locally
mkdocs serve

# Build
mkdocs build
```

### Writing Docs

- Use clear, concise language
- Include code examples
- Add diagrams where helpful
- Keep navigation structure logical

---

## Areas for Contribution

### Good First Issues

Look for issues labeled `good first issue`:

- Documentation improvements
- Bug fixes
- Test coverage
- UI enhancements

### Feature Ideas

- Multi-document support (Companies Act, etc.)
- Conversation memory
- PDF export
- Admin dashboard
- Offline mode

### Technical Improvements

- Performance optimization
- Better error handling
- Improved caching
- Monitoring/observability

---

## Community

### Communication

- **GitHub Issues** - Bug reports, feature requests
- **Pull Requests** - Code contributions
- **Discussions** - Questions, ideas

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help newcomers
- Follow project guidelines

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Recognition

Contributors are recognized in:

- README.md Contributors section
- Release notes
- Documentation credits

Thank you for contributing!
