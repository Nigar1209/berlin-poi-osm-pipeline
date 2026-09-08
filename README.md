# Berlin POI OSM Pipeline

A **config-driven geospatial data engineering pipeline** that ingests, standardizes, and refreshes Berlin Point-of-Interest (POI) data from OpenStreetMap using **Apache Airflow, Docker, and PostgreSQL/PostGIS**.

The system dynamically generates and processes multiple POI layers through a single Airflow DAG, enabling scalable ingestion without hardcoded table-specific logic.

Developed during a **Data Engineering internship**, the project contributes to a broader location-intelligence system aimed at supporting **AI-driven recommendations for urban living and exploration**.

---

## Project Purpose

This project addresses a real-world data engineering challenge: building a maintainable pipeline for continuously evolving geospatial POI data.

The pipeline is designed to:

- Ingest multiple POI categories from OpenStreetMap
- Handle heterogeneous tag structures across different POI layers
- Enforce a consistent schema across all generated tables
- Allow new POI layers to be onboarded **without modifying DAG code**
- Support repeatable full-refresh processing
- Provide controlled and reproducible local execution

The result is a **single dynamic Airflow pipeline driven by external configuration**.

---

## Key Features

### Dynamic Airflow DAG

- A single DAG processes all configured POI layers
- Layer-specific tasks are generated dynamically
- Pipeline logic is separated from individual POI categories

### Config-Driven Architecture

Pipeline behavior is defined through JSON configuration files:

- `core_columns.json` — shared schema definition
- `osm_tables.json` — POI layer definitions and OSM extraction tags

Adding a new layer therefore requires configuration changes rather than modifications to the DAG implementation.

### Scalable Table Onboarding

New POI categories can be added by extending the configuration.

For example, a new layer can define:

- Target table name
- OSM tags used for extraction
- Layer-specific attributes

without introducing new hardcoded transformation logic.

### Geospatial Processing

- OpenStreetMap data extraction using tag-based filters
- Standardized geometry handling
- PostgreSQL/PostGIS storage
- Geographic enrichment using Berlin district/neighborhood boundaries

### Full Refresh Strategy

The pipeline uses a **full-refresh approach**, rebuilding POI tables on each execution.

This was selected to keep the initial implementation simple and reliable while avoiding unnecessary incremental-processing complexity.

### Execution Strategy Evaluation

Two execution strategies were evaluated:

- **Pure parallel execution**
- **Batched execution**

Although pure parallel execution provided higher theoretical concurrency, batch execution offered better stability and resource control in the constrained local Docker environment.

### Dockerized Environment

The complete Airflow environment is containerized using Docker, providing reproducible local orchestration and simplifying setup.

---

##  Core Technical Idea

**Separate pipeline logic from layer configuration**  
The DAG remains stable, while behavior is defined externally through JSON configuration files.

* **`core_columns.json`**: Defines the shared schema across all POI tables.
* **`osm_tables.json`**: Defines per-layer attributes:
  * Table name
  * OSM extraction tags
  * Layer-specific attributes

> This decoupling allows new layers to be added seamlessly **without modifying any pipeline logic**.

---

##  Pipeline Overview

1. **Airflow triggers the DAG**
2. **Configuration files are loaded**
3. **Pipeline iterates through configured layers**
4. **OSM data is fetched** per layer
5. **Shared transformations are applied**
6. **Layer-specific attributes are appended**
7. **Tables are fully refreshed** in PostgreSQL/PostGIS
8. **Ingestion metadata is recorded**

---

##  Local Execution

The pipeline runs locally via Docker:

1. **Configure environment variables**
2. **Start Docker services**
3. **Access Airflow UI**
4. **Trigger the DAG**
5. **Monitor execution**

---

##  Design Principles

* **Configuration over hardcoding**
* **Consistency with flexibility**
* **Simplicity over unnecessary complexity**
* **Reproducibility via containerization**
* **Controlled execution over maximum concurrency**

---

##  Outcome

This project delivers a **scalable, production-style ingestion pipeline** for geospatial POI data.

It demonstrates:
* Airflow-based orchestration
* Config-driven pipeline design
* Geospatial data processing
* Execution strategy evaluation
* Real-world engineering trade-offs

---

##  Author

Developed as part of a **Data Engineering Internship** focused on geospatial data pipelines and location-intelligence systems.

---

##  License

Distributed under the [MIT License](LICENSE).
---

