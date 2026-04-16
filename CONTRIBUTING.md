# Contributing to FlowFeed

Thank you for your interest in contributing to FlowFeed! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- pip (recommended) or uv

### Setup Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/gitstq/flowfeed.git
   cd flowfeed
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Run tests:
   ```bash
   pytest
   ```

### For China Mainland Users

Use mirror sources for faster downloads:
```bash
pip install -e ".[dev]" -i https://mirrors.aliyun.com/pypi/simple/
```

## Adding a New Source

1. Create a new file in `flowfeed/sources/` (e.g., `my_source.py`)
2. Inherit from `SourceBase` and implement the `fetch()` method:

```python
from flowfeed.sources.base import FetchError, NewsItem, SourceBase

class MySource(SourceBase):
    source_id = "mysource"
    source_name = "My Source"
    source_url = "https://example.com"
    category = "general"
    description = "Description of the source"
    rate_limit_seconds = 300

    async def fetch(self, count: int = 50) -> list[NewsItem]:
        items = []
        # ... your fetch logic here ...
        return items
```

3. Register the source in `flowfeed/sources/__init__.py`:
   - Add the import
   - Add to `ALL_SOURCES` list
   - Add to `SOURCE_REGISTRY` dict

4. Add tests in `tests/`

## Code Style

- Follow PEP 8 conventions
- Use `ruff` for linting:
  ```bash
  ruff check flowfeed/
  ```
- Maximum line length: 100 characters
- Type hints are encouraged

## Commit Convention

Follow [Angular Commit](https://www.conventionalcommits.org/) convention:

```
feat: add new news source
fix: resolve parsing issue in weibo source
docs: update README
refactor: optimize deduplication algorithm
test: add unit tests for hackernews source
chore: update dependencies
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes
4. Run tests: `pytest`
5. Run linter: `ruff check flowfeed/`
6. Commit with conventional format
7. Push and open a Pull Request

## Issue Reporting

When reporting issues, please include:

- Python version
- Operating system
- FlowFeed version
- Error messages / stack traces
- Steps to reproduce

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
