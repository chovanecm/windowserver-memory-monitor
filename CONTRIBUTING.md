# Contributing to WindowServer Memory Monitor

Thank you for your interest in contributing! This project aims to help macOS users manage WindowServer memory leaks caused by third-party applications.

## How to Contribute

### Reporting Issues

Before creating an issue, please check if a similar issue already exists.

When reporting a bug, include:
- macOS version
- Python version (`python3 --version`)
- Complete error messages or logs
- Steps to reproduce the issue
- Expected vs. actual behavior

### Suggesting Enhancements

We welcome feature requests! Please include:
- Clear description of the proposed feature
- Use case and motivation
- Any implementation ideas (optional)

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes**:
   - Follow existing code style (PEP 8 for Python)
   - Add comments for complex logic
   - Update documentation if needed
3. **Test your changes**:
   - Run the script manually: `python3 monitor_dockdoor.py --dry-run`
   - Test with verbose output: `python3 monitor_dockdoor.py --dry-run --verbose`
   - Verify on your macOS version
4. **Update documentation**:
   - Update README.md if adding features
   - Add examples if applicable
5. **Commit your changes**:
   - Use clear, descriptive commit messages
   - Reference issue numbers if applicable
6. **Submit a pull request**

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code
- Use type hints where appropriate
- Add docstrings for functions and classes
- Keep functions focused and modular

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/mac-windowserver-memleak-workaround.git
cd mac-windowserver-memleak-workaround

# Test the script
python3 monitor_dockdoor.py --dry-run --verbose

# Make changes and test again
```

## Testing

Currently, testing is done manually. When testing:

1. Test with `--dry-run` to avoid actual app restarts
2. Verify memory reading accuracy against Activity Monitor
3. Test config file parsing with various settings
4. Verify logging output is clear and helpful

## Project Goals

- **Simplicity**: Keep the solution lightweight and easy to understand
- **Safety**: No sudo required, user-level permissions only
- **Reliability**: Robust error handling and clear feedback
- **Usability**: Easy installation and configuration

## Questions?

Feel free to open an issue for questions or discussion!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
