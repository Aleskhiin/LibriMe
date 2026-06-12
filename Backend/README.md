# LibriMe Backend

The LibriMe Backend application serves as the central service for managing and processing document jobs. The system enables file uploads, translation, and subsequent audio content generation via an asynchronous processing pipeline.

## Core Features

* Job Management: Creation and status tracking of processing orders.
* Authentication: JWT-based security for endpoints.
* Flexible Infrastructure: Support for local development environments and cloud-native integrations (Google Cloud Platform).
* Asynchronous Communication: Decoupling of services via message queues.

## Technology Stack

* Runtime Environment: Java 17
* Framework: Spring Boot 3.5.7
* Persistence: MySQL (via Spring Data JPA)
* Messaging Provider: RabbitMQ or Google Cloud Pub/Sub
* Storage Provider: Local file system or Google Cloud Storage (GCS)
* Security: Spring Security with JSON Web Tokens (JWT)
* Documentation: SpringDoc OpenAPI (Swagger UI)

## Prerequisites

The following components are required for operation and development:

* Java Development Kit (JDK) 17
* Apache Maven 3.x
* Docker and Docker Compose
* OpenSSL (for generating secrets)

## Installation and Setup

### 1. Environment Variable Configuration

The application uses environment variables for configuration. Create a .env file in the root directory based on the provided template:

```bash
cp .env.example .env
```

Generate a secure JWT key and enter it into the .env file:

```bash
openssl rand -base64 32
```

### 2. Start Infrastructure

The project provides a Docker Compose configuration to start the required services (database and message broker) locally:

```bash
docker compose -f compose.example.yaml up -d
```

### 3. Build and Start Application

Use Maven to compile and start the application:

```bash
mvn spring-boot:run
```

The API is then accessible at http://localhost:8080.

## API Documentation

After starting the application, the interactive API documentation can be accessed via Swagger UI:

http://localhost:8080/swagger-ui/index.html

## Project Structure

* src/main/java/org/librime/libribackend/DB: Contains entities, repositories, and services for the persistence layer.
* src/main/java/org/librime/libribackend/MQHandler: Implementations for RabbitMQ and Google Cloud Pub/Sub.
* src/main/java/org/librime/libribackend/Security: Configuration of JWT authentication and security filters.
* src/main/java/org/librime/libribackend/Storage: Abstraction of file storage (Local/GCS).
* src/main/java/org/librime/libribackend/restservice: REST controllers and data transfer objects (Records).

## Run Tests

The test suite includes unit and integration tests. These can be executed with the following command:

```bash
mvn test
```
