# Awesome List Agent CLI

A command-line interface for processing Awesome List URLs using an AI agent that extracts metadata, parses content, and simulates MCP server calls.

## Features

- 🔍 **Parse Awesome Lists**: Extracts topic, description, categories, and metadata
- 📊 **Detailed Analysis**: Identifies programming language, counts items, and categorizes content
- 🔗 **MCP Integration**: Simulates MCP server calls with context information
- 📝 **Comprehensive Logging**: Configurable logging levels with file output
- 💾 **JSON Export**: Save results to JSON files for further processing
- 🎛️ **Flexible CLI**: Multiple options for different use cases

## Installation

1. Make sure you have the required dependencies:
```bash
# Activate your virtual environment first
source venv/bin/activate

# Install the required packages (if not already installed)
pip install aiohttp pydantic
```

2. Ensure the `awesome_list_agent` module is properly set up in your Python path.

## Usage

### Basic Usage

```bash
python3 awesome_list_interface.py <awesome_list_url>
```

**Example:**
```bash
python3 awesome_list_interface.py https://github.com/vinta/awesome-python
```

### Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--log-level` | Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `--log-level DEBUG` |
| `--log-file` | Specify custom log file path | `--log-file my_app.log` |
| `--output-file` | Save results to JSON file | `--output-file results.json` |
| `--quiet` | Suppress console output (logs still written) | `--quiet` |
| `--help` | Show help message | `--help` |

### Usage Examples

#### 1. Basic Processing
```bash
python3 awesome_list_interface.py https://github.com/sindresorhus/awesome
```

#### 2. Debug Mode with JSON Export
```bash
python3 awesome_list_interface.py \\
  --log-level DEBUG \\
  --output-file awesome-python.json \\
  https://github.com/vinta/awesome-python
```

#### 3. Quiet Mode
```bash
python3 awesome_list_interface.py \\
  --quiet \\
  --log-file processing.log \\
  --output-file results.json \\
  https://github.com/avelino/awesome-go
```

#### 4. Custom Log File
```bash
python3 awesome_list_interface.py \\
  --log-file custom-$(date +%Y%m%d).log \\
  https://github.com/rust-unofficial/awesome-rust
```

## Output

### Console Output
The CLI provides a user-friendly display showing:
- 📊 **Parsed Information**: Topic, description, language, item count, categories
- 📂 **Categories**: List of main categories found
- 📝 **Summary**: Generated context summary
- 🔗 **MCP Server Result**: Simulated server response

### Log Files
Logs are automatically saved to the `logs/` directory with timestamps. The log files contain:
- Detailed execution flow
- HTTP request/response information
- Parsing steps and results
- Error details with stack traces
- Performance metrics

### JSON Export
When using `--output-file`, results are saved in JSON format:
```json
{
  "timestamp": "2024-01-01T12:00:00",
  "url": "https://github.com/vinta/awesome-python",
  "processing_result": {
    "status": "success",
    "parsed_data": {
      "topic": "Python",
      "description": "A curated list of awesome Python frameworks...",
      "language": "Python",
      "total_items": 1250,
      "categories": ["Web Frameworks", "Data Science", "Machine Learning"],
      "context_summary": "This is an Awesome List focused on Python..."
    },
    "mcp_result": {
      "mcp_status": "success",
      "message": "MCP server processed URL: ...",
      "timestamp": "2024-01-01T12:00:00"
    }
  }
}
```

## Logging Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| `DEBUG` | Detailed execution info, HTTP details, parsing steps | Development, troubleshooting |
| `INFO` | General progress, major steps | Normal operation |
| `WARNING` | Potential issues that don't stop execution | Monitoring |
| `ERROR` | Errors that prevent processing | Error tracking |
| `CRITICAL` | Critical system errors | System monitoring |

## Examples Script

Run the examples script to see various usage patterns:

```bash
# Show example URLs and usage patterns
python3 awesome_list_examples.py

# Run automated examples (creates test files)
python3 awesome_list_examples.py --run-examples
```

## Popular Awesome Lists to Try

1. **General**: https://github.com/sindresorhus/awesome
2. **Python**: https://github.com/vinta/awesome-python
3. **JavaScript**: https://github.com/sorrycc/awesome-javascript
4. **Go**: https://github.com/avelino/awesome-go
5. **Rust**: https://github.com/rust-unofficial/awesome-rust
6. **Java**: https://github.com/akullpp/awesome-java
7. **Ruby**: https://github.com/markets/awesome-ruby
8. **Machine Learning**: https://github.com/josephmisiti/awesome-machine-learning
9. **Vue.js**: https://github.com/vuejs/awesome-vue
10. **React**: https://github.com/enaqx/awesome-react

## File Structure

```
codetv/
├── awesome_list_interface.py      # Main CLI application
├── awesome_list_logging.py        # Logging configuration
├── awesome_list_examples.py       # Usage examples
├── awesome_list_agent/            # Agent framework
│   ├── awesome_list_agent.py     # Main agent class
│   └── tools/
│       └── awesome_list_parser.py # Parsing tool
├── logs/                          # Auto-generated log files
└── results/                       # JSON output files (when specified)
```

## Troubleshooting

### Common Issues

1. **Network Errors**: Check internet connection and URL accessibility
2. **Parsing Errors**: Some lists may have unusual formats - check logs for details
3. **Module Not Found**: Ensure Python path includes the awesome_list_agent module
4. **Permission Errors**: Ensure write access to logs/ and results/ directories

### Debug Mode

For detailed troubleshooting, always use debug mode:
```bash
python3 awesome_list_interface.py --log-level DEBUG <url>
```

### Log Analysis

Check the generated log files in the `logs/` directory for detailed execution information, including:
- HTTP request/response details
- Content parsing steps
- Error stack traces
- Performance timing

## Integration

The CLI is designed to be easily integrated into larger workflows:

- **Shell Scripts**: Use with exit codes for automation
- **CI/CD Pipelines**: Process lists as part of build processes
- **Data Processing**: JSON output can be consumed by other tools
- **Monitoring**: Log files can be monitored for operational insights

## MCP Server Integration

Currently, the CLI simulates MCP server calls. To integrate with a real MCP server:

1. Modify the `call_mcp_server` method in `awesome_list_agent.py`
2. Add actual MCP client code
3. Configure MCP server endpoints and authentication
4. Update error handling for real network calls

## Contributing

To extend the CLI:

1. **New Features**: Add options to `parse_arguments()` in the interface
2. **Enhanced Parsing**: Modify methods in `AwesomeListParser`
3. **Output Formats**: Add new export formats in `save_results_to_file()`
4. **Logging**: Adjust logging levels and formats in `awesome_list_logging.py`
