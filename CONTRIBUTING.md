# Contributing to Microshare ERP Integration

Thank you for your interest in contributing to the Microshare ERP Integration project!

## Quick Start for Contributors

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/microshare-erp-integration.git
   cd microshare-erp-integration
   ```
3. **Set up development environment**:
   ```bash
   cp .env.example .env
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```
4. **Run tests** to ensure everything works:
   ```bash
   pytest
   ```

## Development Workflow

### Making Changes
1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Add tests for new functionality
4. Run the test suite: `pytest`
5. Run code formatting: `black .` and `isort .`
6. Commit your changes: `git commit -am "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

### Code Style
- We use [Black](https://black.readthedocs.io/) for Python code formatting
- We use [isort](https://pycqa.github.io/isort/) for import sorting
- Follow PEP 8 guidelines
- Add type hints to new functions
- Write docstrings for public functions and classes

### Testing
- Write tests for all new features
- Maintain or improve test coverage
- Use pytest for testing framework
- Tests should be in the `tests/` directory

## Project Structure

```
microshare-erp-integration/
├── src/microshare_client/    # Core Microshare API client
├── src/erp_adapter/          # Generic ERP integration patterns  
├── services/integration-api/ # FastAPI service
├── tests/                   # Test suite
├── docs/                    # Documentation
└── examples/                # Usage examples
```

## Questions or Issues?

- **Bug reports**: Create an issue with detailed information
- **Feature requests**: Create an issue describing the feature
- **Questions**: Start a discussion or create an issue
- **Security issues**: Email support@microshare.io

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
