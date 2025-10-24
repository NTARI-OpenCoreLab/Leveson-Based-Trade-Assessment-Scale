# Contributing to LBTAS

## How to Contribute

Contributions are made through the NTARI Slack workspace.

**Join the discussion**: https://ntari.slack.com/archives/C09N88JN2SH

## Types of Contributions

### Code Contributions
- Bug fixes
- Feature implementations
- Performance improvements
- Documentation updates

### Research Contributions
- Use case studies
- Academic papers using LBTAS
- Integration examples
- Analysis of rating effectiveness

### Community Contributions
- Issue reporting
- Feature suggestions
- Documentation improvements
- Translation support

## Development Process

### 1. Discussion
Discuss your proposed changes in the Slack channel before beginning work.

### 2. Fork and Branch
```bash
git clone https://github.com/NTARI-OpenCoreLab/Leveson-Based-Trade-Assessment-Scale.git
cd Leveson-Based-Trade-Assessment-Scale
git checkout -b feature/your-feature-name
```

### 3. Code Standards

**Python Style**
- Follow PEP 8
- Use type hints
- Include docstrings for all functions and classes
- Keep functions focused and under 50 lines

**Documentation Style**
- Write in factual, technical language
- Avoid adjectives and adverbs
- Include code examples
- Test all examples

### 4. Testing

Test your changes:
```bash
# Test basic functionality
python3 lbtas.py rate --exchange "TestService"
python3 lbtas.py view --exchange "TestService"
python3 lbtas.py report

# Test as library
python3 -c "from lbtas import LevesonRatingSystem; rs = LevesonRatingSystem(); rs.add_exchange('test'); print('OK')"
```

### 5. Commit Messages

Format: `type: brief description`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code restructuring
- `test`: Test additions or changes
- `chore`: Maintenance tasks

Examples:
```
feat: add CSV export format
fix: handle empty rating lists in report
docs: update installation instructions
```

### 6. Pull Request

1. Push your branch to your fork
2. Open a pull request to main branch
3. Reference any related issues
4. Describe changes made and reasoning
5. Wait for review and discussion in Slack

## Code of Conduct

### Standards

- Respect all contributors
- Focus on technical merit
- Provide constructive feedback
- Accept critique of your contributions
- Prioritize project goals over personal preferences

### Prohibited Behavior

- Personal attacks or harassment
- Discriminatory language or behavior
- Trolling or inflammatory comments
- Sharing others' private information
- Unethical or unprofessional conduct

### Enforcement

Violations may result in:
1. Warning
2. Temporary suspension from project
3. Permanent ban from project

Report violations to: forge@ntari.org

## License

By contributing, you agree that your contributions will be licensed under AGPL-3.0.

All contributions must:
- Be your original work or properly attributed
- Not violate any third-party rights
- Comply with AGPL-3.0 requirements

## Questions

For questions about contributing:
1. Ask in Slack: https://ntari.slack.com/archives/C09N88JN2SH
2. Open an issue on GitHub
3. Email: forge@ntari.org

## Recognition

Contributors are recognized in:
- Git commit history
- Release notes
- Project documentation

Contribution types recognized:
- Code contributions (commits)
- Research contributions (citations)
- Documentation contributions (documentation credits)
- Community support (acknowledgments)
