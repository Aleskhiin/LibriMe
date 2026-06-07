# Stage 1: Build stage
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app

# Copy pom.xml and source code
COPY pom.xml .
COPY src ./src

# Build the application
RUN mvn clean package -DskipTests

# Stage 2: Run stage
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# Copy the built JAR from the build stage
COPY --from=build /app/target/libribackend-0.0.1-SNAPSHOT.jar app.jar

# Configuration for local file storage (creates the directory in the container)
RUN mkdir -p /app/files

EXPOSE 8080

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]
