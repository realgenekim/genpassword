.PHONY: test test-fast test-verbose test-safety coverage clean install help

# Default target
help:
	@echo "genpassword - Safe Password Generator"
	@echo ""
	@echo "Usage:"
	@echo "  make test          Run all tests"
	@echo "  make test-fast     Run fast tests only (skip slow statistical tests)"
	@echo "  make test-verbose  Run tests with verbose output"
	@echo "  make test-safety   Run only P0 safety tests"
	@echo "  make coverage      Run tests with coverage report"
	@echo "  make install       Install dependencies"
	@echo "  make clean         Remove build artifacts"
	@echo "  make run           Generate a password"
	@echo "  make demo          Show all password modes"

# Run all tests
test:
	python -m pytest tests/ -v

# Fast tests (skip slow statistical ones)
test-fast:
	python -m pytest tests/ -v -k "not Distribution and not test_default_no_duplicates"

# Verbose with print output
test-verbose:
	python -m pytest tests/ -v -s

# Only safety-critical tests (P0)
test-safety:
	python -m pytest tests/ -v -k "Safety or DoubleClick"

# Run with coverage
coverage:
	python -m pytest tests/ --cov=genpassword --cov-report=term-missing --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

# Install dependencies
install:
	pip install pytest pytest-cov

# Clean build artifacts
clean:
	rm -rf __pycache__ tests/__pycache__ .pytest_cache htmlcov .coverage
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

# Generate a password
run:
	python genpassword.py

# Demo all modes
demo:
	@echo "Default (readable + strong):"
	@python genpassword.py --no-copy
	@echo ""
	@echo "Simple (easy to dictate):"
	@python genpassword.py --simple --no-copy
	@echo ""
	@echo "Paranoid (max symbols):"
	@python genpassword.py --paranoid --no-copy
	@echo ""
	@echo "Generate 5:"
	@python genpassword.py -n 5 --no-copy
