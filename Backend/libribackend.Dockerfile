FROM openjdk:25-rc-jdk-slim
WORKDIR /app
COPY ./release/libribackend-0.0.1-SNAPSHOT.jar /app
EXPOSE 8080
CMD ["java", "-jar", "libribackend-0.0.1-SNAPSHOT.jar"]