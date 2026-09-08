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

## Repository Structure

```text
berlin-poi-osm-pipeline/
├── README.md
├── .gitignore
├── LICENSE
│
├── airflow/
│   ├── dags/
│   │   └── core_osm_table_generator_dag.py
│   ├── .env.example
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── requirements.txt
│
├── config/
│   ├── core_columns.json
│   ├── lor_ortsteile.geojson
│   └── osm_tables.json
│
├── data_reference/
│   └── wikidata_stars_candidates.csv
│
├── docs/
│   ├── 01_project_overview.md
│   ├── 02_initial_layer_analysis.md
│   ├── 03_data_model_and_column_strategy.md
│   ├── 04_pipeline_architecture.md
│   ├── 05_airflow_and_docker_setup.md
│   ├── 06_execution_strategy_experiment.md
│   ├── 07_final_design_decisions.md
│   │
│   ├── images/
│   │   ├── airflow_dag_graph.png
│   │   ├── airflow_mapped_tasks_batch.png
│   │   └── airflow_mapped_tasks_parallel.png
│   │
│   └── archive/
│       ├── dag_experiment/
│       │   ├── core_osm_table_generator_dag_experiment.py
│       │   └── README.md
│       ├── experiment_results/
│       │   └── osm_experiment_results.csv
│       └── dag_experiment_vs_final.diff
│
└── notebooks/
    └── osm_layer_exploration_hotels.ipynb
