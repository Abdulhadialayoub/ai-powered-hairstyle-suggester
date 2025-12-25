# Testing Guide

## Quick Start

### Run all tests:
```bash
# Windows
run_all_tests.bat

# Linux/Mac
python -m pytest tests/ -v --cov=. --cov-report=html
```

### Run quick tests (no coverage):
```bash
# Windows
run_quick_tests.bat

# Linux/Mac
python -m pytest tests/ -v
```

## Test Structure

```
backend/
├── tests/                              # All test files
│   ├── __init__.py                     # Package init
│   ├── conftest.py                     # Shared fixtures
│   ├── test_api.py                     # API tests
│   ├── test_face_analysis.py           # Face analysis tests
│   ├── test_recommendation_engine.py   # Recommendation tests
│   ├── test_user_database.py           # Database tests
│   ├── test_usage_tracker.py           # Usage tracking tests
│   ├── test_ai_tryon.py                # AI try-on tests
│   └── test_stable_image_ultra_service.py
├── pytest.ini                          # Pytest configuration
├── run_all_tests.bat                   # Windows test runner
└── run_quick_tests.bat                 # Quick test runner
```

## Test Categories

### 1. Unit Tests
Test individual functions and classes in isolation.

**Files:**
- `test_face_analysis.py`
- `test_recommendation_engine.py`
- `test_usage_tracker.py`

**Run:**
```bash
python -m pytest tests/ -m unit
```

### 2. Integration Tests
Test API endpoints and service integration.

**Files:**
- `test_api.py`
- `test_ai_tryon.py`

**Run:**
```bash
python -m pytest tests/ -m integration
```

### 3. Database Tests
Test database operations and persistence.

**Files:**
- `test_user_database.py`

**Run:**
```bash
python -m pytest tests/ -m database
```

## Running Specific Tests

### Run single test file:
```bash
python -m pytest tests/test_api.py -v
```

### Run specific test class:
```bash
python -m pytest tests/test_api.py::TestAnalyzeEndpoint -v
```

### Run specific test function:
```bash
python -m pytest tests/test_api.py::TestAnalyzeEndpoint::test_analyze_success -v
```

### Run tests matching pattern:
```bash
python -m pytest tests/ -k "face" -v
```

## Coverage Reports

### Generate HTML coverage report:
```bash
python -m pytest tests/ --cov=. --cov-report=html
```

View report: Open `htmlcov/index.html` in browser

### Generate terminal coverage report:
```bash
python -m pytest tests/ --cov=. --cov-report=term
```

### Coverage by file:
```bash
python -m pytest tests/ --cov=. --cov-report=term-missing
```

## Test Markers

Use markers to categorize and run specific test groups:

```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass
```

**Available markers:**
- `unit` - Unit tests
- `integration` - Integration tests
- `slow` - Slow running tests
- `api` - API endpoint tests
- `database` - Database tests
- `ai` - AI service tests

**Run by marker:**
```bash
python -m pytest tests/ -m "unit and not slow"
```

## Fixtures

Common fixtures are defined in `tests/conftest.py`:

- `sample_image_bytes` - Sample image for testing
- `sample_face_data` - Sample face analysis data
- `sample_hairstyle` - Sample hairstyle data
- `mock_env_vars` - Mock environment variables
- `app_client` - Flask test client

**Usage:**
```python
def test_something(sample_image_bytes, app_client):
    # Use fixtures
    response = app_client.post('/api/analyze', data=sample_image_bytes)
    assert response.status_code == 200
```

## Mocking External APIs

Always mock external API calls in tests:

```python
from unittest.mock import patch, Mock

@patch('replicate.run')
def test_ai_tryon(mock_replicate):
    mock_replicate.return_value = ['http://example.com/result.jpg']
    # Test code here
```

## Test Data

Test data is stored in:
- `tests/fixtures/` - Sample images and files
- `conftest.py` - Fixture definitions

## Continuous Integration

Tests run automatically on:
- Every commit
- Pull requests
- Before deployment

## Troubleshooting

### Import errors:
```bash
# Add backend to Python path
set PYTHONPATH=%PYTHONPATH%;%CD%
```

### Missing dependencies:
```bash
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock
```

### API key errors:
- Check `.env` file
- Use mock fixtures
- Set test environment variables

### Database errors:
- Use in-memory database for tests
- Clean up after each test
- Use fixtures for test data

## Best Practices

1. **Isolation**: Each test should be independent
2. **Mocking**: Mock external services and APIs
3. **Cleanup**: Clean up resources after tests
4. **Naming**: Use descriptive test names
5. **Documentation**: Add docstrings to tests
6. **Assertions**: Use clear, specific assertions
7. **Coverage**: Aim for >80% coverage

## Example Test

```python
import pytest
from unittest.mock import Mock, patch

class TestFaceAnalysis:
    """Tests for face analysis functionality."""
    
    def test_detect_face_success(self, sample_image_bytes):
        """Test successful face detection."""
        # Arrange
        from face_analysis import detect_face
        
        # Act
        result = detect_face(sample_image_bytes)
        
        # Assert
        assert result is not None
        assert 'face_shape' in result
        assert result['confidence'] > 0.5
    
    @patch('face_analysis.model.predict')
    def test_detect_face_with_mock(self, mock_predict, sample_image_bytes):
        """Test face detection with mocked model."""
        # Arrange
        mock_predict.return_value = np.array([[0.1, 0.9, 0.0]])
        
        # Act
        result = detect_face(sample_image_bytes)
        
        # Assert
        assert result['face_shape'] == 'oval'
        mock_predict.assert_called_once()
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## Contact

For questions about testing, contact the development team.
