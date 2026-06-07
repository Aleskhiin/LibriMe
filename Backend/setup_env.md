# Environment Setup Guide

This project uses environment variables to manage configuration and secrets. Follow these steps to set up your local environment.

## 1. Create your `.env` file

Copy the provided example file to create your local environment configuration:

```bash
cp .env.example .env
```

The `.env` file is excluded from Git (via `.gitignore`) to prevent secrets from being committed.

## 2. Generate a JWT Secret

The application requires a secure secret key for signing JWT tokens. You can generate a random 32-character base64 string using OpenSSL:

```bash
openssl rand -base64 32
```

Copy the output and update the `JWT_SECRET` value in your `.env` file.

## 3. Configuration Variables

Update the following variables in your `.env` file as needed:

### Database (MySQL)
- `DB_HOST`: The hostname of your database (default: `localhost`).
- `DB_USERNAME`: Database user (default: `root`).
- `DB_PASSWORD`: Database password.

### RabbitMQ
- `RABBITMQ_HOST`: RabbitMQ server host (default: `localhost`).
- `RABBITMQ_PORT`: RabbitMQ port (default: `5672`).
- `RABBITMQ_USERNAME`: RabbitMQ username (default: `user`).
- `RABBITMQ_PASSWORD`: RabbitMQ password.

### JWT
- `JWT_SECRET`: Your generated secret key.
- `JWT_EXPIRATION`: Token expiration time in milliseconds (default: `86400000` or 24 hours).

## 4. Running the Application

### Using Docker Compose
The `compose.yaml` file automatically picks up variables from the `.env` file:

```bash
docker compose up -d
```

### Running Locally (Maven)
The Spring Boot application uses `springboot3-dotenv` to automatically load the `.env` file on startup.

```bash
mvn spring-boot:run
```
