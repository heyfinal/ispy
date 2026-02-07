# iSpy - iOS Device Diagnostic Tool

A comprehensive iOS device diagnostic and health monitoring tool with AI-powered analysis.

## Features

- **Device Detection**: Automatic detection of connected iOS devices
- **Health Scoring**: A+ to F grading system with detailed component analysis
- **10 Diagnostic Modules**:
  - Battery health and cycle analysis
  - Storage usage optimization
  - Network connectivity status
  - Security configuration audit
  - Performance profiling
  - Thermal state monitoring
  - Backup status verification
  - Accessibility features review
  - Crash log analysis
  - Installed apps management
- **AI-Powered Analysis**: OpenAI integration for intelligent troubleshooting
- **Export Reports**: JSON and text format support
- **Rich CLI**: Beautiful terminal output with progress indicators
- **Backup Acquisition**: Create and manage local iOS backups (non-jailbroken)
- **Case Builder**: Parse backup artifacts into a searchable case file
- **Raw Parsing Tools**: Plist and SQLite parsing from backups
- **Timeline + Search**: Build event timelines and keyword search across artifacts
- **Case Reports**: JSON/CSV/HTML exports

## Requirements

- macOS with libimobiledevice installed
- Python 3.10+
- Connected iOS device (trusted)

## Installation

```bash
# Install libimobiledevice (required)
brew install libimobiledevice

# Install iSpy
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

## Quick Start

```bash
# List connected devices
ispy devices

# Quick diagnostic check
ispy quick

# Full diagnostic with AI analysis
ispy full --output report.json

# Run specific modules
ispy diagnose --modules battery --modules storage

# Ask AI a question
ispy ask "Why is my battery draining fast?"
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `ispy devices` | List connected iOS devices |
| `ispy diagnose` | Run diagnostics (customizable) |
| `ispy quick` | Quick essential check |
| `ispy full` | Comprehensive diagnostic with AI |
| `ispy modules` | List available modules |
| `ispy ask` | Ask AI about iOS issues |
| `ispy backup` | Create and manage backups (acquire/extract/catalog) |
| `ispy parse` | Parse plist/SQLite files from backups |
| `ispy case` | Build a parsed case file from backups |
| `ispy version` | Show version |

## Configuration

Create `~/.config/ispy/config.yaml`:

```yaml
# OpenAI API key for AI features
openai_api_key: sk-your-key-here
openai_base_url: https://api.openai.com/v1

# Default modules to run
default_modules:
  - battery
  - storage
  - network
  - security

# Output settings
output:
  format: json
  verbose: false
```

Or use environment variables:

```bash
export OPENAI_API_KEY=sk-your-key-here
# Optional: OpenAI-compatible providers (DeepSeek, etc.)
export ISPY_OPENAI_BASE_URL=https://api.deepseek.com/v1
```

## Diagnostic Modules

### Battery
- Current charge level
- Cycle count analysis
- Health status (Good/Fair/Degraded)
- Charging recommendations

### Storage
- Total/used/free space
- Usage percentage
- Optimization suggestions

### Network
- WiFi connection status
- Cellular availability
- Connectivity recommendations

### Security
- Passcode status
- Activation state
- iOS version security score

### Performance
- CPU architecture info
- RAM analysis
- Uptime tracking

### Thermal
- Temperature monitoring
- Thermal state alerts
- Cooling recommendations

### Backup
- Last backup date
- Backup freshness status
- iCloud backup status

### Accessibility
- Active accessibility features
- Feature impact analysis

### Crashes
- Crash report analysis
- Top crashing apps
- Stability recommendations

### Apps
- Installed app count
- App listing (alphabetical)
- Cleanup suggestions

## Health Scoring

The health score combines multiple factors:

| Grade | Score | Meaning |
|-------|-------|---------|
| A+ | 95-100 | Excellent |
| A | 90-94 | Great |
| A- | 87-89 | Very Good |
| B+ | 83-86 | Good |
| B | 80-82 | Above Average |
| B- | 77-79 | Slightly Above Average |
| C+ | 73-76 | Average |
| C | 70-72 | Below Average |
| C- | 67-69 | Fair |
| D+ | 63-66 | Poor |
| D | 60-62 | Very Poor |
| D- | 57-59 | Critical |
| F | <57 | Failing |

## Python API

```python
from ispy import iSpyTool, Config

# Initialize
tool = iSpyTool()

# Get connected device
device = tool.get_device()

# Run diagnostics
report = tool.run_diagnostic(device, include_ai=True)

# Export report
tool.export_report(report, 'diagnostic_report.json')

# Quick check
quick_report = tool.run_quick_check(device)

# AI analysis
analysis = tool.analyze_with_ai("Why is storage full?")
```

## Forensics Workflow (CLI)

```bash
# Create a local backup
ispy backup create --udid <UDID>

# Build a parsed case file
ispy case build --backup ~/Library/Application\ Support/MobileSync/Backup/<UDID>

# Generate a timeline preview
ispy case timeline --case ~/ispy_cases/ispy_case_YYYYMMDD_HHMMSS.json

# Search artifacts
ispy case search --case ~/ispy_cases/ispy_case_YYYYMMDD_HHMMSS.json --query "example.com"

# Export a report
ispy case report --case ~/ispy_cases/ispy_case_YYYYMMDD_HHMMSS.json --format html --output report.html
```

## Development

```bash
# Clone repository
git clone https://github.com/yourusername/ispy.git
cd ispy

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy ispy

# Lint
ruff check ispy
```

## License

MIT License - See LICENSE file for details.
