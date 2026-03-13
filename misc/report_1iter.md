<!-- 
pandoc report_1iter.md -o report_1iter.pdf --pdf-engine=xelatex 
-->
---
# === Grundinfos für die Titelseite ===
title: "Projekt:LibriMe"
subtitle: "Report zur 1.Iteration"
author:
  - Florian Fuchs
  - Dominik Bliem-Zupansky
  - Vladimir Tsankov
  - Philip Macheiner
date: \today

# === Inhaltsverzeichnis & Nummerierung ===
toc: true
toc-title: "Inhaltsverzeichnis"
toc-depth: 3
number-sections: true

# === Dokumenteinstellungen ===
lang: de-AT
documentclass: article
papersize: a4
pdf-engine: xelatex

# === Layout & Abstände ===
geometry: "left=1.5cm, right=1.5cm, top=2.5cm, bottom=2.5cm, headheight=15pt"

# === LaTeX-Präambel (header-includes) ===
header-includes: |
  \usepackage{fancyhdr}
  \usepackage{amsmath}
  \usepackage{amssymb}
  \usepackage{fontspec}
  \usepackage{listings}
  \usepackage{xcolor}

  \pagestyle{fancy}

  \fancyfoot[L]{Projekt: LibriMe}
  \fancyfoot[C]{\thepage}

  \definecolor{codegreen}{rgb}{0,0.6,0}
  \definecolor{codegray}{rgb}{0.5,0.5,0.5}
  \definecolor{codepurple}{rgb}{0.58,0,0.82}
  \definecolor{backcolour}{rgb}{0.95,0.95,0.95}

  \lstset{
     backgroundcolor=\color{backcolour},   
     commentstyle=\color{codegreen},
     keywordstyle=\color{magenta},
     numberstyle=\tiny\color{codegray},
     stringstyle=\color{codepurple},
     basicstyle=\ttfamily\small,
     breaklines=true,
     postbreak=\mbox{\textcolor{red}{$\hookrightarrow$}\space},
     numbers=left,                    
     numbersep=5pt,                  
     showstringspaces=false,
     tabsize=2,
     language=bash 
  }

  \newcommand{\N}{\mathbb{N}}
  \newcommand{\Z}{\mathbb{Z}}
  \newcommand{\Q}{\mathbb{Q}}
  \newcommand{\R}{\mathbb{R}}
---

\newpage

# Projektbeschreibung

![alt text](img/logoMedium.png)\

**Projektname**: LibriMe


**Ziel:** 
Entwicklung einer benutzerfreundlichen Webanwendung zur automatischen Umwandlung von PDF-Dokumenten/Bilder(mit Text) in natürlich klingende Audiobooks.

**Projektidee:** 
Viele Studierende und Berufstätige haben Schwierigkeiten, umfangreiche Skripte, Texte, oder Bücher vollständig zu lesen. Oder Eltern möchten ihren Kindern gerne etwas vorlesen, haben jedoch nicht die Zeit und es gibt kein Hörbuch über die Geschichte die sie Ihren Kindern vorlesen möchten. Gleichzeitig möchten viele Menschen ihre Zeit, etwa beim Autofahren, Pendeln oder bei Hausarbeiten produktiver nutzen, um Neues zu lernen oder einfach nur ein Hörbuch zu hören. Herkömmliche Text-to-Speech-Lösungen klingen jedoch oft unnatürlich und unangenehm anzuhören. 


**Lösungsansatz:**
LibriMe bietet die Möglichkeit, PDF-Dokumente/Bilder(mit Text) in Audiodateien mit hochwertige Sprachausgaben umzuwandeln. Nutzer laden dazu ihre PDF-Dokumente/Bilder(mit Text) direkt in die Webapplikation hoch, und das System erstellt daraus automatisch eine natürlich klingende Audiofassung. Hierbei kann der Benutzer bestimmen, in welcher Sprache und mit welcher Stimme, das Audiofile erstellt werden soll. 

**Technische Umsetzung:**
Über ein Webinterface lädt der Nutzer ein PDF-Dokument/Bild(mit Text) hoch. Im Hintergrund wird der Auftrag an ein Module übergeben, welches die modernsten Sprachsynthese-Technologien nutzt. Dabei wird KI-gestützt eine realistische und flüssige Stimmen erzeugt, die sich deutlich von klassischen Text-to-Speech-Stimmen unterscheidet. Dadurch entsteht ein professionell wirkendes Hörerlebnis, das Lernen und Informationsaufnahme deutlich angenehmer macht.

**Zielgruppe:** Folgende Gruppen stehen im Fokus

 - Studierende, die ihre Lernmaterialien unterwegs anhören möchten 
 - Berufstätige, die Weiterbildung in ihren Alltag integrieren möchten
 - Eltern die ihren Kindern gerne Hörbuche vorspielen. 
 - Alle, die Texte lieber hören als lesen


**Mehrwert:**
LibriMe vereint Benutzerfreundlichkeit, Produktivität und moderne KI-Technologie, um das Lernen und Informationsmanagement im Alltag neu zu gestalten.

**GIT:**
[https://git-iit.fh-joanneum.at/swd24-hackathon/librime](https://git-iit.fh-joanneum.at/swd24-hackathon/librime)

# Rollen

## Rollenverteilung

| Name                   | Rolle                                   |
|------------------------|-----------------------------------------|
| Dominik Bliem-Zupansky | Frontend Entwickler                     |
| Florian Fuchs          | AI Modul Entwickler & Projektmanagement |
| Vladimir Tsankov       | AI Modul Entwickler                     |
| Philip Macheiner       | Backend Entwickler & Projektmanagement  |

## Rollenbeschreibung  

  **Rolle:** Frontend Entwickler  
  **Technologien:** React, TypeScript, HTML, CSS (Tailwind oder Material UI), REST / GraphQL APIs, Integration mit RabbitMQ-basiertem Backend

**Aufgaben und Verantwortlichkeiten:**  

 - Entwicklung und Implementierung einer modernen, intuitiven und benutzerfreundlichen Web-GUI für die App Librime mit React und TypeScript.
 - Gestaltung einer klaren und übersichtlichen Benutzeroberfläche, die eine einfache Bedienung und nahtlose Nutzererfahrung gewährleistet.
 - Integration von Upload-Funktionen für PDF- und Bilddateien (Drag & Drop und Dateiauswahl).
 - Entwicklung von Komponenten zur Auswahl von Sprache und Stimme für die Audiobook-Erzeugung.
 - Bereitstellung des erzeugten Audiobook zum Download oder zum direkt Abspielen mittels Audioplayer.
 - Sicherstellung der responsiven Darstellung auf Desktop, Tablet und Mobile.
 - Kommunikation mit dem Backend, das über RabbitMQ gesteuert wird, zur Übermittlung von Dateien und Parametern für die Audiobook-Erzeugung.
 - Sicherstellung von Performance, Zugänglichkeit und Wartbarkeit des Frontends.
 - Zusammenarbeit mit Backend-Entwicklern zur Definition und Optimierung der Schnittstellen zwischen Web-GUI und RabbitMQ-basiertem Backend.
 - Dokumentation des Frontend-Codes und der Benutzeroberfläche in der Projekt-README.

**Ziele der Rolle:** Bereitstellung einer intuitiven Weboberfläche, die Anwendern ermöglicht:
Ein PDFs oder Bilder hochzuladen, anschließt soll eine Sprache und Stimme ausgewählt werden.
Anschließend soll die Verarbeitung über RabbitMQ orchestriert werden, damit das Audiobook auf den Backend im AI Module erstellt wird.
Nachdem das Audiobooks generiert wurde und bereitgestellt wurde, soll es möglich sein das Audiobook abzuspielen oder downzuloaden.

**Rolle:** AI-Modul Entwickler  
**Technologien:** Python, PyTorch, F5-TTS, RabbitMQ, OpenCV(pytesseract), PDF-Verarbeitung (PyPDF2)

**Aufgaben und Verantwortlichkeiten:**

 - Entwicklung und Implementierung von AI-Modulen, die PDF-Dateien einlesen und den Textinhalt extrahieren.
 - Anwendung von OCR-Technologien mittels OpenCV(pytesseract), um Text aus Bildern eingebetteten ist zu erkennen.
 - Nutzung von PyTorch für die Verarbeitung und Modellierung der AI-Module.
 - Erstellung von Audiobooks mithilfe des F5-TTS-Moduls auf Basis der ausgelesenen Texte.
 - Sicherstellung der Kommunikation zwischen Backend und AI-Modul über RabbitMQ (Nachrichtenübermittlung, Task-Queue).
 - Übergabe des erstellten Audiobooks an das Backend zur weiteren Nutzung durch die Web-GUI.
 - Optimierung der Module in Bezug auf Performance, Genauigkeit der Texterkennung und Stabilität der Audiobook-Erstellung.
 - Dokumentation der AI-Module, Abläufe und Schnittstellen in der Projekt-README.
 - Zusammenarbeit mit Frontend- und Backend-Entwicklern zur Integration des AI-Moduls in die Gesamtlösung.

**Ziele der Rolle:** Vollständige und zuverlässige Textextraktion aus PDFs (PyPDF2) und Bildern mit OpenCV (pytesseract).
Die Erstellung von hochwertige Audiobooks mit F5-TTS.
Nahtlose Übergabe und Integration der erzeugten Audiodateien in das Backend, welches es dann an den Frontend übergeben wird. 

**Rolle:** Backend Entwickler  
**Technologien:** Java, Springboot, RabbitMQ

**Aufgaben und Verantwortlichkeiten:**

- Entwicklung und Implementierung eines Backends zur Annahme und Verarbeitung von PDF-Dateien
- Bereitstellung einer REST API für das Frontend zur Erstellung und Statusabfrage von Vertonungsjobs
- Einrichtung und automatisierte Bereitstellung einer Messagequeue mit RabbitMQ
- Erstellung und Versand von Nachrichten an die Messagequeue zur Weiterverarbeitung durch das AI-Modul
- Dokumentation der Backend-Struktur, Abläufe und Schnittstellen in der Projekt-README
- Optimierung des Backends hinsichtlich Skalierbarkeit und Performance
- Enge Zusammenarbeit mit Frontend- und AI-Modul-Entwicklern zur Integration in die Gesamtlösung

**Ziele der Rolle:** Es soll ein stabiles und performantes Backend bereitgestellt werden, das eine zuverlässige Verarbeitung
von Vertonungsjobs über eine REST API ermöglicht und eine einfache, fehlerfreie Kommunikation mit der Messagequeue sicherstellt.  

**Rolle:** Projektmanagement  
**Technologien:** -

**Aufgaben und Verantwortlichkeiten:**

- Planung und Organisation des Projektablaufs
- Koordination zwischen Teilbereichen und Teammitgliedern
- Dokumentation von Projektfortschritt und Entscheidungen
- Unterstützung der Kommunikation im Team und mit Betreuenden
- Überwachung von Zeitplan, Aufgaben und Risiken

**Ziele der Rolle:** Es soll ein reibungsloser Projektablauf gewährleistet werden, indem Kommunikation, Abstimmung und
Dokumentation im Team effektiv organisiert und die Einhaltung von Terminen sichergestellt werden.