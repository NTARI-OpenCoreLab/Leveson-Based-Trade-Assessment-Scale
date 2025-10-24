# Leveson-Based Trade Assessment Scale (LBTAS)

A rating system for digital commerce based on Nancy Leveson's aircraft software assessment methodology with bidirectional assessment criteria.

## Overview

The Leveson-Based Trade Assessment Scale (LBTAS) implements Nancy Leveson's aircraft software assessment methodology, developed for aerospace applications, adapted for digital commerce and economic assessment contexts. LBTAS provides a framework for capturing transaction quality data using a 6-point scale.

## The Problem with Traditional Rating Systems

5-star systems do not provide data that motivates producer improvement. The 5-star system was developed in 1958 by Forbes Travel Guide (formerly Mobil Travel Guide) to advertise hotel quality along US interstate highways. It was designed as a one-way communication system for highway travel, not for digital commerce.

**Limitations:**
- Ratings provide limited value in e-commerce contexts
- PR managers create barriers to policy change
- Granularity fails to capture transaction complexity
- One-directional assessment ignores consumer accountability
- Data insufficiency forces reliance on comment sections

## Why the Leveson Approach?

The Leveson System originates from aircraft software development where system failures result in loss of life or wasted R&D investment. This methodology:

- Uses a 6-point scale (from +4 to -1) with category definitions
- Compresses meaning into each rating level
- Reduces dependency on comment sections for data
- Enables bidirectional assessment (both producer and consumer)
- Supports data-driven improvement cycles

## Scale Definitions

### +4 **Delight**
Interaction anticipates the evolution of user practices and concerns post-transaction

### +3 **No Negative Consequences**
Interaction designed to prevent loss, exceed basic quality standards

### +2 **Basic Satisfaction**
Interaction meets socially acceptable standards, exceeding articulated user demands

### +1 **Basic Promise**
Interaction meets all articulated user demands, no more

### 0 **Cynical Satisfaction**
Interaction fulfills a basic promise requiring little to no discipline toward user satisfaction

### -1 **No Trust**
User was harmed, exploited, or received a product/service with evidence of no discipline or malicious intent

## Bidirectional Assessment

LBTAS enables two-way accountability in digital networks by maintaining ratings for both:

- **Producers**: Identifies providers
- **Consumers**: Identifies customers

This approach facilitates community self-regulation and reduces the need for centralized moderation.

## Features

- **Methodology**: Based on aerospace assessment frameworks
- **Bidirectional Assessment**: Rate both parties in transactions
- **Granularity**: 6-point scale with definitions
- **Dependencies**: Integration into systems
- **Database Support**: Persistence layer support
- **Open Source**: Community-driven development and customization

## Installation

```bash
# Clone the repository
git clone https://github.com/NTARI-OpenCoreLab/Leveson-Based-Trade-Assessment-Scale.git
cd Leveson-Based-Trade-Assessment-Scale

# Make executable (optional)
chmod +x lbtas.py

# Run directly
python3 lbtas.py --help
```

No external dependencies required. Uses Python 3 standard library only.

## Quick Start

```python
from lbtas import LevesonRatingSystem

# Initialize the rating system
rating_system = LevesonRatingSystem()

# Add an exchange (transaction)
rating_system.add_exchange("transaction_001")

# Add ratings (categories: reliability, usability, performance, support)
rating_system.add_rating(
    exchange_name="transaction_001",
    criterion="reliability",
    rating=3  # No Negative Consequences
)

# View average ratings
ratings = rating_system.view_ratings("transaction_001")
print(f"Ratings: {ratings}")
```

### Command Line Interface

```bash
# Interactive rating
python3 lbtas.py rate --exchange "MyService"

# Programmatic rating
python3 lbtas.py add --exchange "MyService" --criterion reliability --rating 3

# View ratings
python3 lbtas.py view --exchange "MyService"

# Generate report
python3 lbtas.py report

# Export data
python3 lbtas.py export --format json --output ratings.json
```

## Storage

LBTAS uses JSON file storage for persistence:

```python
# Initialize with storage file
rating_system = LevesonRatingSystem(storage_file='ratings.json')

# Ratings are saved automatically to the file
rating_system.add_exchange("service_001")
rating_system.add_rating("service_001", "reliability", 3)
```

Storage file format:
```json
{
  "service_001": {
    "reliability": [3, 4, 3],
    "usability": [2, 3],
    "performance": [4],
    "support": [3, 3, 2],
    "_metadata": {
      "created": "2024-09-04T10:30:00",
      "total_ratings": 10
    }
  }
}
```

### Rating Categories

Default categories:
- **Reliability**: Dependability and consistency
- **Usability**: Ease of use and user experience
- **Performance**: Speed and efficiency
- **Support**: Customer service quality

Custom categories can be defined during initialization.

## Use Cases

### Academic Research
- Study how rating scale design affects user behavior and market outcomes
- Measure effects of bidirectional assessment on trust and cooperation
- Analyze quality-based assessment alternatives to frameworks

### E-Commerce Platforms
- Implement quality metrics for marketplace transactions
- Enable community-driven reputation systems
- Reduce moderation overhead through self-regulation

### Digital Cooperatives
- Facilitate peer-to-peer accountability
- Support governance structures
- Enable data-driven policy improvements

## Architecture

LBTAS is implemented as a single Python module with:

1. **Core class**: `LevesonRatingSystem` manages ratings and storage
2. **JSON persistence**: File-based storage with automatic save
3. **CLI interface**: Command-line tool for interactive and programmatic use
4. **No external dependencies**: Uses Python standard library only

The system supports:
- Interactive rating collection
- Programmatic rating submission
- Custom rating categories
- Report generation and data export

## Documentation

- [Full Documentation](docs/README.md)
- [API Reference](docs/api.md)
- [Integration Guide](docs/integration.md)
- [Research Applications](docs/research.md)

## Contributing

Contributions are made through the NTARI Slack workspace:

**Join the discussion**: https://ntari.slack.com/archives/C09N88JN2SH

Please see our [Contributing Guidelines](CONTRIBUTING.md) for:

- Code style and standards
- Testing requirements
- Pull request process
- Community code of conduct

## Research & Development

This program was produced by the **Network Theory Applied Research Institute's Forge Laboratory** (now NTARI Research & Development) by Jodson B. Graves using ChatGPT-3 on September 4, 2024.

### About NTARI Research & Development

NTARI Research & Development is NTARI's software development program for creating digital systems and protocols that leverage network theory to enhance cooperative capabilities across the internet. We develop open-source tools, platforms, and frameworks that empower communities to build online ecosystems.

**Learn more and support NTARI**: [https://ntari.org](https://ntari.org)

## Citation

If you use LBTAS in your research, please cite:

```bibtex
@software{lbtas2024,
  title={Leveson-Based Trade Assessment Scale},
  author={Graves, Jodson B.},
  organization={Network Theory Applied Research Institute},
  year={2024},
  url={https://github.com/NTARI-OpenCoreLab/Leveson-Based-Trade-Assessment-Scale}
}
```

## References

- Leveson, N. G. (2011). *Engineering a Safer World: Systems Thinking Applied to Safety*. MIT Press.
- Leveson, N. G. (2020). *CAST Handbook: How to Learn More from Incidents and Accidents*. MIT.

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.

The AGPL-3.0 license requires that:
- Source code must be made available when the software is used over a network
- Modifications must be released under the same license
- Changes must be documented
- Network use is considered distribution

## Acknowledgments

- **Nancy Leveson** - Original methodology development
- **NTARI Research & Development** - Research and implementation
- **Open Source Community** - Contributions and feedback

---

**Maintained by**: [NTARI Research & Development](https://ntari.org)  
**Questions?** Open an issue or contact us at forge@ntari.org
