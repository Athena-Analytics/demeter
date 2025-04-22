# Demeter

A Flask-based web service that provides base64 encoding/decoding functionality and remote proxy configuration management.

## Features

- Health check endpoint
- Base64 encoding/decoding
- Remote proxy configuration management
- Docker support
- Logging system

## Prerequisites

- Python 3.x
- Docker (optional)
- Docker Compose (optional)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd demeter
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.lock
   ```

4. Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   ```

## Running the Application

### Local Development

```bash
python app.py
```

### Using Docker

```bash
docker-compose up --build
```

Or use the rebuild script:
```bash
./rebuild_docker.sh
```

## API Endpoints

- `GET /health` - Health check endpoint
- `GET /encode/` - Base64 encoding endpoint
- `GET /decode/` - Base64 decoding endpoint
- `GET /remote_config/<tool_type>` - Get remote proxy configuration

## Development

For development setup and guidelines, please refer to [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.