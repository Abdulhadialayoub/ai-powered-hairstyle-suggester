# Backend Unit Tests

This directory contains all unit tests for the AI Hairstyle Suggester backend.

## Test Structure

```
tests/
├── __init__.py                          # Package initialization
├── test_api.py                          # API endpoint tests
├── test_face_analysis.py                # Face analysis tests
├── test_recommendation_engine.py        # Recommendation engine tests
├── test_user_database.py                # User database tests
├── test_usage_tracker.py                # Usage tracking tests
├── test_ai_tryon.py                     # AI try-on tests
├── test_stable_image_ultra_service.py   # Stable Image Ultra tests
└── README.md                            # This file
```

## Running Tests

### Run all tests:
```bash
cd backend
python -m pytest tests/
```

### Run specific test file:
```bash
python -m pytest tests/test_api.py
```

### Run with coverage:
```bash
python -m pytest tests/ --cov=. --cov-report=html
```

### Run specific test:
```bash
python -m pytest tests/test_api.py::TestAnalyzeEndpoint::test_analyze_success
```

## Test Categories

### 1. API Tests (`test_api.py`)
- Face analysis endpoint
- Recommendations endpoint
- Try-on endpoint
- Favorites endpoint
- Error handling

### 2. Face Analysis Tests (`test_face_analysis.py`)
- Face detection
- Face shape classification
- Confidence scoring
- Edge cases

### 3. Recommendation Engine Tests (`test_recommendation_engine.py`)
- Hairstyle recommendations
- Face shape matching
- Filtering and sorting
- Database queries

### 4. User Database Tests (`test_user_database.py`)
- User creation
- Favorites management
- Data persistence
- CRUD operations

### 5. Usage Tracker Tests (`test_usage_tracker.py`)
- Usage logging
- Cost tracking
- Statistics
- Data export

### 6. AI Try-On Tests (`test_ai_tryon.py`)
- Image generation
- Style application
- Error handling
- API integration

### 7. Stable Image Ultra Tests (`test_stable_image_ultra_service.py`)
- Service initialization
- Image generation
- API calls
- Error handling

## Requirements

Install test dependencies:
```bash
pip install pytest pytest-cov pytest-mock
```

## Writing New Tests

Follow these guidelines:

1. **Naming**: Test files should start with `test_`
2. **Structure**: Use classes to group related tests
3. **Mocking**: Mock external API calls
4. **Assertions**: Use clear, descriptive assertions
5. **Documentation**: Add docstrings to test functions

Example:
```python
import pytest
from unittest.mock import Mock, patch

class TestMyFeature:
    """Tests for my feature."""
    
    def test_success_case(self):
        """Test successful operation."""
        # Arrange
        input_data = "test"
        
        # Act
        result = my_function(input_data)
        
        # Assert
        assert result == expected_output
    
    def test_error_case(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            my_function(invalid_input)
```

## CI/CD Integration

Tests are automatically run on:
- Pull requests
- Commits to main branch
- Before deployment

## Coverage Goals

- Overall coverage: > 80%
- Critical paths: > 95%
- API endpoints: 100%

## Troubleshooting

### Tests fail with import errors
```bash
# Add backend to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Tests fail with missing dependencies
```bash
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock
```

### Tests fail with API errors
- Check API keys in `.env`
- Mock external API calls
- Use test fixtures

## Contact

For questions about tests, contact the development team.
