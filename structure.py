"""
AetherCore3/
│
├── src/
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   └── existencias.py          # Header, Detalle, ArchivoOrigen, Nacional
│   │   ├── value_objects/
│   │   │   ├── __init__.py
│   │   │   ├── fecha_contable.py       # FechaContable
│   │   │   └── tipo_valor.py           # TipoValor (código num + abreviatura CU/EU/etc)
│   │   └── exceptions/
│   │       ├── __init__.py
│   │       └── dominio_existencias_exception.py
│   │
│   ├── application/
│   │   ├── __init__.py
│   │   ├── interfaces/
│   │   │   ├── __init__.py
│   │   │   ├── i_existencias_parser.py     # IExistenciasParser
│   │   │   ├── i_existencias_aggregator.py # IExistenciasAggregator
│   │   │   └── i_existencias_output.py     # IExistenciasOutput
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── existencias_parser_service.py
│   │   │   ├── existencias_aggregator_service.py
│   │   │   └── existencias_output_service.py
│   │   └── orchestrators/
│   │       ├── __init__.py
│   │       └── existencias_orchestrator.py # (para usar luego con watchdog)
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── settings_existencias.py     # lee .env y configura paths
│   │   ├── file_system/
│   │   │   ├── __init__.py
│   │   │   ├── existencias_txt_reader.py   # lee líneas
│   │   │   ├── existencias_txt_writer.py   # escribe nacional
│   │   │   └── existencias_path_manager.py # arma carpetas día/gestionados/copias
│   │   └── watchdog/
│   │       ├── __init__.py
│   │       └── existencias_file_watcher.py # más adelante
│   │
│   ├── shared/
│   │   ├── __init__.py
│   │   └── result.py                        # Success/Failure genérico (si quieres)
│   │
│   └── presentation/
│       ├── __init__.py
│       └── console/
│           ├── __init__.py
│           └── console_existencias.py       # CLI manual
│
├── config/
│   ├── config.yaml                          # si usas YAML extra, opcional
│   └── config.dev.yaml                      # opcional
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── pyproject.toml
└── README.md
"""