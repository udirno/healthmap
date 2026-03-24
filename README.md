# HealthMap - AI-Powered Global Disease Intelligence Platform

> Global disease patterns, explained.


## Overview

HealthMap is an interactive, AI-augmented global health intelligence tool that lets users explore real-time disease trends, overlay environmental and socioeconomic context, and ask natural-language questions to understand emerging patterns.

## Features

- Interactive global disease map with regional drill-down
- Real-time metrics and trend analysis
- AI-powered natural language insights using Claude
- Climate and socioeconomic data overlays
- Correlation analysis between diseases and environmental factors
- Time-slider with animation for historical trends

## Tech Stack

### Frontend
- Next.js 16 (TypeScript)
- Mapbox GL JS
- TailwindCSS
- Recharts

### Backend
- FastAPI (Python)
- PostgreSQL + PostGIS
- Redis
- SQLAlchemy

### AI & Analytics
- Anthropic Claude API
- Pure Python statistical analysis
- Correlation analysis engine

## Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.11+
- Docker & Docker Compose
- Git

## Project Structure
```
healthmap/
├── frontend/          # Next.js application
├── backend/           # FastAPI server
├── data-pipeline/     # Data ingestion scripts
├── database/          # SQL migrations and seeds
└── docs/              # Documentation
```

## API Keys Required

1. **Anthropic API Key** - Get from https://console.anthropic.com/
2. **Mapbox Token** - Get from https://www.mapbox.com/
3. **OpenWeather API Key** - Get from https://openweathermap.org/api
