# Release Checklist

## Before tagging
- [ ] Python package name `aiboss-sdk` is available on PyPI
- [ ] npm package `@aiboss/sdk` scope is ready
- [ ] GitHub Secrets configured: `PYPI_API_TOKEN`, `NPM_TOKEN`
- [ ] README and examples reflect current API
- [ ] `python -m build` passes
- [ ] `npm run build` passes

## Release steps
1. Bump versions in `python/pyproject.toml`, `python/setup.py`, `js/package.json`
2. Update `CHANGELOG.md`
3. Commit changes
4. Tag: `v0.1.0`
5. Create GitHub Release
6. Verify Actions published to PyPI and npm
