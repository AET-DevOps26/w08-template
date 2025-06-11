# DevOps W07 In-Class Exercise Template

This repository contains a full-stack canteen application with a SvelteKit client, Spring Boot server, and LLM recommendation service. It demonstrates modern web application architecture and DevOps practices.

## Project Overview

This project includes:
- **Client**: SvelteKit with TypeScript, TailwindCSS, and reusable UI components for browsing canteen meals.
- **Server**: Spring Boot Java application with RESTful APIs, gRPC communication, and PostgreSQL integration.
- **LLM Service**: Python FastAPI service for generating meal recommendations using AI.
- **Database**: PostgreSQL for storing user preferences and application data.
- **DevOps**: Dockerized services, CI/CD pipelines, Helm charts, and production-ready deployment configurations.

## Prerequisites

- Node.js (v22 or later)
- Java JDK 21+
- Python 3.x
- Gradle
- Docker and Docker Compose
- Git
- Kubernetes and Helm (for Kubernetes deployment)

## Setup Instructions

### Clone the Repository

```bash
git clone https://github.com/yourusername/w07-template.git
cd w07-template
```

### Client Setup

1. Navigate to the `client` directory:
   ```bash
   cd client
   ```
2. Install dependencies:
   ```bash
   npm install
   ```

### Server Setup

1. Navigate to the `server` directory:
   ```bash
   cd server
   ```
2. Build the project:
   ```bash
   ./gradlew build
   ```

### LLM Service Setup

1. Navigate to the `llm` directory:
   ```bash
   cd llm
   ```
2. Install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip3 install -r requirements.txt
   ```

## Running the Application

### Start the Database

```bash
docker compose up database -d
```

### Start the Client

```bash
cd client
npm run dev
```
The client will be available at [http://localhost:3000](http://localhost:3000).

### Start the Server

```bash
cd server
./gradlew bootRun
```
The server API will be available at [http://localhost:8080](http://localhost:8080).

### Start the LLM Service

```bash
cd llm
python main.py
```
The LLM service will be available at [http://localhost:5000](http://localhost:5000).

### Prometheus

Access Prometheus at [http://localhost:9090](http://localhost:9090)

### Grafana

Access Grafana at [http://localhost:3001](http://localhost:3001)


## Development Workflow

### Client Development

- Built with SvelteKit and TypeScript for a modern, reactive UI.
- TailwindCSS for styling.
- Components and routes are organized in the `src` directory.
- Features meal browsing, favoriting, and user preferences.

### Server Development

- Built with Spring Boot for scalable and maintainable server services.
- Includes gRPC communication with the LLM service.
- PostgreSQL integration for user preferences storage.
- RESTful APIs for canteen data and user management.
- Gradle is used for dependency management and building.
- Source code is in the `src/main/java` directory.
- Tests are in the `src/test/java` directory.

### LLM Service Development

- Built with FastAPI for AI-powered meal recommendations.
- Integrates with external LLM APIs for generating personalized suggestions.
- Source code is in the `llm` directory.

## Building for Production

### Client Build

```bash
cd client
npm run build
```

### Server Build

```bash
cd server
./gradlew clean build
```

## Dockerized Deployment

The project includes Docker configurations for containerized deployment.

### Build and Run with Docker Compose

1. Build and start all services:
   ```bash
   docker compose up --build
   ```
2. Access the application:
   - Client: [http://localhost:3000](http://localhost:3000)
   - Server: [http://localhost:8080](http://localhost:8080)
   - LLM Service: [http://localhost:5000](http://localhost:5000)
   - Database: PostgreSQL on port 5432

## Kubernetes Deployment

The project includes Helm charts for Kubernetes deployment.

### Deploy with Helm

1. Update the `tumid` value in [`helm/canteen-app/values.yaml`](helm/canteen-app/values.yaml):
   ```yaml
   tumid: your-tum-id
   ```

2. Install the Helm chart:
   ```bash
   helm install canteen ./helm/canteen-app
   ```

## CI/CD Pipeline

The project includes GitHub Actions workflows for:
- **Building Docker Images**: Automatically builds and pushes Docker images to GitHub Container Registry.
- **Deploying Docker Images**: Deploys the application to a production environment using Docker Compose.

## Project Structure

```
├── client/                   # SvelteKit client
│   ├── src/                  # Source code
│   ├── static/               # Static assets
│   └── package.json          # Client dependencies
│
├── server/                   # Spring Boot server
│   ├── src/                  # Source code including gRPC services
│   ├── build.gradle          # Gradle build file
│   └── Dockerfile            # Server Dockerfile
|
├── grafana/provisioning      # Grafana service
│   ├── dashboards            # Grafana dashboard
│   ├── sample-dashboard.json # Example dashboard
|   ├── datasources           # Loki service
│   └── notifiers             # Alerts
|
├── Loki                      # Loki service
│   └── loki-config.yaml      # Loki configuration
|
├── Prometheus                # Prometheus service
│   └── prometheus.yaml       # Prometheus configuration
|
├── Promtail                  # Promtail service
│   └── promtail.yaml         # Promtail configuration
|
├── llm/                      # Python LLM service
│   ├── main.py               # FastAPI application
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile            # LLM service Dockerfile
│
├── docs/                     # API documentation (Bruno collection)
├── compose.yml               # Docker Compose for local development
└── .github/workflows/        # CI/CD workflows
```

## API Documentation

API documentation is available in the [`docs/CanteenApp Bruno`](docs/CanteenApp%20Bruno) directory as a Bruno collection for testing endpoints.

## License

This project is licensed under the MIT License.