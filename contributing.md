# Contributing to LBTAS

> 🌐 Also available in: [العربية](contributing.ar.md) · [Español](contributing.es.md) · [Français](contributing.fr.md) · [हिन्दी](contributing.hi.md) · [Português](contributing.pt.md) · [toki pona](contributing.tok.md) · [中文](contributing.zh.md) — community translation drafts per NTARI policy P2-002; this English original is authoritative.

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

## Licensing: inbound = outbound (NTARI DCO)

Contributions are accepted under a **Developer Certificate of Origin (DCO)**
sign-off (see the `DCO` file). Your contribution is licensed under this
project's existing AGPL-3.0 `LICENSE` — inbound matches outbound, there is no
CLA, and **copyright stays with you**. Because copyright remains distributed
across all contributors, no single party — including NTARI — can relicense the
corpus without unanimous consent.

Sign off every commit with `-s` (e.g. `git commit -s -m "..."`), which appends
your `Signed-off-by` trailer. A DCO check runs on each pull request against
`main`; if you forget, the failed check lists the commits to fix
(`git commit --amend --no-edit --signoff` for one, `git rebase --signoff HEAD~N`
for several, then `git push --force-with-lease`).
