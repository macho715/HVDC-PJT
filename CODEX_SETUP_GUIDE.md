# 🤖 HVDC Codex Fix Setup Guide

## 📋 Overview

This guide explains how to set up and use the automated Codex Fix system for the HVDC Project. The system uses OpenAI GPT-4 to automatically fix code issues and create pull requests.

## 🚀 Quick Start

### 1. Prerequisites

- GitHub repository with Actions enabled
- OpenAI API key
- GitHub token with appropriate permissions

### 2. Required Secrets

Add these secrets to your GitHub repository:

```bash
# Required secrets in GitHub Settings > Secrets and variables > Actions
OPENAI_API_KEY=your_openai_api_key_here
GH_TOKEN=your_github_token_here  # Optional, uses github.token by default
```

### 3. Trigger Methods

#### Method 1: Issue Comment (Recommended)
Comment on any issue with:
```
/codex fix mypy path=src task="fix type annotations"
```

#### Method 2: Manual Workflow Dispatch
1. Go to Actions tab
2. Select "Codex Fix - HVDC Project"
3. Click "Run workflow"
4. Fill in parameters:
   - **Path**: `src` (default)
   - **Task**: `fix mypy errors` (default)
   - **Max Diff**: `8000` (default)

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 access | - | ✅ Yes |
| `GH_TOKEN` | GitHub token for PR creation | `github.token` | ❌ No |

### Workflow Parameters

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `path` | Target directory to scan | `src` | `src`, `tools`, `tests` |
| `task` | Description of fix task | `fix mypy errors` | `refactor imports`, `apply ruff fixes` |
| `max_diff` | Maximum diff size in characters | `8000` | `4000`, `8000`, `16000` |

## 📁 File Structure

```
HVDC-PJT/
├── .github/
│   ├── workflows/
│   │   ├── codex-fix.yaml          # Main Codex workflow
│   │   ├── quality-gates.yaml      # Quality checks
│   │   └── security-scan.yaml      # Security scanning
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── codex_fix_request.md    # Codex-specific template
│   ├── CODEOWNERS                  # Code ownership rules
│   ├── PULL_REQUEST_TEMPLATE.md    # PR template
│   └── SECURITY.md                 # Security policy
├── tools/
│   └── codex_fix.py               # Main Codex script
├── pyproject.toml                 # Project configuration
└── src/                          # Source code directory
```

## 🎯 Usage Examples

### Basic MyPy Fix
```bash
# Via issue comment
/codex fix mypy path=src

# Via workflow dispatch
Path: src
Task: fix mypy errors
Max Diff: 8000
```

### Import Refactoring
```bash
# Via issue comment
/codex refactor path=src task="fix import statements and add __init__.py files"

# Via workflow dispatch
Path: src
Task: refactor imports
Max Diff: 4000
```

### Code Formatting
```bash
# Via issue comment
/codex format path=src task="apply ruff fixes and black formatting"

# Via workflow dispatch
Path: src
Task: apply ruff fixes
Max Diff: 6000
```

### Specific File Fix
```bash
# Via issue comment
/codex fix path=src/logistics.py task="fix type annotations and add docstrings"

# Via workflow dispatch
Path: src/logistics.py
Task: fix type annotations
Max Diff: 2000
```

## 🔍 Quality Gates

The system automatically runs these quality checks:

### Code Quality
- **Ruff**: Linting and code style
- **Black**: Code formatting
- **isort**: Import sorting
- **MyPy**: Type checking

### Security
- **Bandit**: Python security scanning
- **Safety**: Dependency vulnerability scanning
- **Semgrep**: Static analysis security scanning

### Testing
- **pytest**: Unit and integration tests
- **Coverage**: Code coverage reporting

## 🚨 Troubleshooting

### Common Issues

#### 1. "OPENAI_API_KEY not set"
**Solution**: Add the secret to GitHub repository settings

#### 2. "Patch apply failed"
**Solution**: Check if the generated diff is valid and try with a smaller `max_diff`

#### 3. "No changes detected"
**Solution**: The code might already be compliant, or try a different task description

#### 4. "Quality gates failed"
**Solution**: Review the failed checks and fix manually, or adjust the task description

### Debug Mode

Enable verbose logging by modifying the workflow:

```yaml
- name: Run Codex agent
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    VERBOSE: true
  run: |
    python tools/codex_fix.py \
      --path "${{ steps.args.outputs.path }}" \
      --task "${{ steps.args.outputs.task }}" \
      --max-diff "${{ steps.args.outputs.max_diff }}" \
      --verbose
```

## 📊 Monitoring and Metrics

### Workflow Status
- Check the Actions tab for workflow runs
- Review logs for detailed execution information
- Monitor PR creation and quality gate results

### Success Metrics
- **PR Success Rate**: Target ≥80%
- **Quality Gate Pass Rate**: Target ≥95%
- **Average Fix Time**: Target <5 minutes
- **User Satisfaction**: Monitor issue comments and feedback

## 🔒 Security Considerations

### API Key Security
- Store `OPENAI_API_KEY` as a GitHub secret
- Use least-privilege access for `GH_TOKEN`
- Regularly rotate API keys

### Code Review
- All automated changes require review
- Security team approval for sensitive changes
- Audit trail for all automated modifications

### Data Privacy
- No sensitive data sent to OpenAI
- Local processing of code before API calls
- Secure handling of generated diffs

## 🚀 Advanced Configuration

### Custom Prompts
Modify the system prompt in `tools/codex_fix.py`:

```python
system_prompt = """Your custom prompt here..."""
```

### Workflow Customization
Add custom steps to `.github/workflows/codex-fix.yaml`:

```yaml
- name: Custom validation
  run: |
    # Your custom validation logic
```

### Integration with Other Tools
The system can be integrated with:
- Slack notifications
- Jira ticket updates
- Email notifications
- Custom dashboards

## 📞 Support

For issues or questions:

1. **GitHub Issues**: Create an issue using the bug report template
2. **Codex Fix Request**: Use the codex fix request template
3. **Security Issues**: Follow the security policy in `SECURITY.md`
4. **Documentation**: Check this guide and inline code comments

## 🔄 Updates and Maintenance

### Regular Updates
- Update OpenAI API model versions
- Refresh security scanning tools
- Update quality gate configurations
- Review and update prompts

### Monitoring
- Track API usage and costs
- Monitor workflow performance
- Review user feedback and issues
- Update documentation as needed

---

**Last Updated**: 2025-01-25  
**Version**: 3.4.0  
**Maintainer**: HVDC Team
