# Continue IDE Configuration for HVDC Project

## 🚀 Setup Instructions

### 1. Install Continue Extension
- **VS Code**: Install "Continue" extension from marketplace
- **Cursor**: Built-in support (no installation needed)
- **JetBrains**: Install Continue plugin

### 2. Configure API Keys
Add to your environment variables or Continue settings:

```bash
# Required for GPT-4o
OPENAI_API_KEY=your_openai_api_key_here

# Optional for Claude 3.5 Sonnet
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. Custom Commands Usage

#### HVDC-specific Commands
- `hvdc-fix-mypy`: Fix MyPy type errors
- `hvdc-refactor`: Refactor following TDD principles
- `hvdc-add-tests`: Add comprehensive tests
- `hvdc-optimize-logistics`: Optimize logistics code

#### Usage in IDE
1. Select code
2. Press `Ctrl+Shift+P` (VS Code) or `Cmd+Shift+P` (Mac)
3. Type "Continue: Run Custom Command"
4. Select desired HVDC command

### 4. Integration with Existing Tools

#### Codex Fix Integration
- Continue can trigger GitHub Actions workflows
- Use custom commands to generate Codex fix requests
- Seamless integration with existing automation

#### MACHO-GPT Integration
- Maintains compatibility with MACHO-GPT v3.4-mini
- Preserves logistics domain logic
- Follows established project patterns

## 🔧 Configuration Details

### Models
- **Primary**: GPT-4o (128k context)
- **Secondary**: Claude 3.5 Sonnet (200k context)
- **Tab Completion**: GPT-4o

### Context Providers
- Git integration for change tracking
- Diff viewing for code changes
- Terminal access for command execution
- Open files context

### Customizations
- HVDC project-specific prompts
- Logistics domain expertise
- TDD and Kent Beck principles
- MACHO-GPT compatibility

## 📚 Best Practices

### Code Generation
1. Always maintain HVDC project structure
2. Follow TDD principles (Red-Green-Refactor)
3. Preserve MACHO-GPT integration
4. Include comprehensive error handling

### Testing
1. Generate tests for all new functionality
2. Include logistics domain test cases
3. Follow pytest conventions
4. Maintain high test coverage

### Documentation
1. Add docstrings for all functions
2. Include type hints
3. Document logistics business logic
4. Update README files as needed

## 🚨 Troubleshooting

### Common Issues
1. **API Key Not Found**: Check environment variables
2. **Model Not Responding**: Verify API key validity
3. **Context Too Long**: Use smaller code selections
4. **Integration Issues**: Check MACHO-GPT compatibility

### Support
- Check Continue documentation
- Review HVDC project guidelines
- Contact development team
- Check GitHub issues

---

**Last Updated**: 2025-01-25  
**Version**: 3.4.0  
**Maintainer**: HVDC Team
