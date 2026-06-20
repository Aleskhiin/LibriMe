# LibriMe Backend

Das LibriMe Backend dient als zentraler Dienst zur Verwaltung und Verarbeitung von Dokumenten-Jobs. Es ermöglicht das Hochladen von PDF-Dateien, deren Statusverfolgung sowie die anschließende Generierung von Audio-Inhalten über eine asynchrone Pipeline.

Die Anwendung läuft produktiv nativ in der **Google Cloud** (unter Verwendung von Cloud Run, Google Cloud Storage, Cloud Pub/Sub, Cloud SQL und Google Cloud Identity Platform), bietet jedoch eine vollständige lokale Entwicklungsumgebung.

---

## Kernfunktionen

* **Job-Verwaltung**: Erstellung, Statusverfolgung und Löschen von PDF-Verarbeitungsaufträgen.
* **Hybride Authentifizierung**:
  * **Anonyme Sessions**: Unregistrierte Nutzer erhalten automatisch ein lokales, verschlüsseltes JWT-Cookie (`libriME_jwt`), um die App sofort nutzen zu können.
  * **Google Cloud Identity Platform**: Registrierte Benutzer authentifizieren sich sicher per Google ID-Token über den `Authorization: Bearer <token>` Header.
* **Automatische Job-Migration**: Sobald sich ein anonymer Nutzer registriert oder einloggt und das erste Mal mit seinem Google-Konto anfragt, migriert das Backend alle zuvor erstellten anonymen Jobs auf seinen permanenten Google-Account und löscht das temporäre Cookie.
* **Asynchrone Verarbeitung**: Entkopplung zeitaufwendiger Tasks (wie PDF-zu-Audio-Konvertierung) über Message Broker.

---

## Technologie-Stack

* **Laufzeitumgebung**: Java 17
* **Framework**: Spring Boot 3.5.7 (Spring Security, Spring Data JPA)
* **Datenbank**: MySQL (lokal) / Cloud SQL (in Google Cloud)
* **Messaging Broker**: RabbitMQ (lokal) / Google Cloud Pub/Sub (in Google Cloud)
* **Dateispeicher**: Lokales Dateisystem (lokal) / Google Cloud Storage (in Google Cloud)
* **Token-Validierung**: JSON Web Tokens (JJWT) & Google API Public Certificate Verification
* **API-Dokumentation**: SpringDoc OpenAPI (Swagger UI)

---

## Voraussetzungen für die lokale Ausführung

* **Java Development Kit (JDK) 17**
* **Apache Maven 3.x**
* **Docker & Docker Compose**
* **OpenSSL** (zum Generieren von lokalen Secrets)

---

## Lokale Einrichtung und Ausführung

### 1. Umgebungsvariablen konfigurieren
Kopiere das bereitgestellte Template, um deine lokale Konfigurationsdatei zu erstellen:
```bash
cp .env.example .env
```

Generiere einen sicheren Schlüssel für die lokalen anonymen JWT-Cookies und trage ihn in deiner `.env` unter `JWT_SECRET` ein:
```bash
openssl rand -base64 32
```

*(Optional)* Trage deine GCP-Projekt-ID in der `.env` unter `GCP_PROJECT_ID` ein, falls du die Validierung von Google-OAuth-Token lokal testen möchtest.

### 2. Lokale Infrastruktur starten
Starte die benötigte Datenbank (MySQL) und den Message Broker (RabbitMQ) über Docker Compose:
```bash
docker compose -f compose.example.yaml up -d
```

### 3. Anwendung starten
Kompiliere das Projekt und starte die Spring Boot-App:
```bash
mvn spring-boot:run
```

Die REST-API ist anschließend lokal unter `http://localhost:8080` erreichbar.

---

## API-Dokumentation

Nach dem Start der Anwendung kannst du die interaktive Swagger-Dokumentation im Browser aufrufen:
`http://localhost:8080/swagger-ui/index.html`

---

## Projektstruktur

* `src/main/java/org/librime/libribackend/DB`: Entitäten, Repositories und Services für die Persistenzschicht (Job-Verwaltung & Migration).
* `src/main/java/org/librime/libribackend/MQHandler`: Nachrichten-Queue-Anbindungen (RabbitMQ und Cloud Pub/Sub).
* `src/main/java/org/librime/libribackend/Security`: Konfiguration von Spring Security, JWT-Generierung und Google Cloud Identity Platform Token-Validierung.
* `src/main/java/org/librime/libribackend/Storage`: Abstraktion des Dateispeichers (lokal und GCS).
* `src/main/java/org/librime/libribackend/restservice`: REST-Controller und Datenübertragungsobjekte (DTOs).

---

## Tests ausführen

Die Unit- und Integrationstests können mit folgendem Maven-Befehl ausgeführt werden:
```bash
mvn test
```
