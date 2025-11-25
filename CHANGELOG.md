# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [0.1.0] - 2025-11-22

### Agregado
- Procesamiento de archivos de existencias origen a nacional
- Validación de formatos de archivo (tipo 01 y 02)
- Agrupación por fecha contable y tipo de valor
- Movimiento automático a carpetas GESTIONADOS/ERRORES
- Generación de backups en carpeta COPIAS
- Modo watcher 24/7 con watchdog
- Tests unitarios e integración
- Uso de constantes para números mágicos
- Validación de tipos de valor múltiples
- Logging detallado de operaciones

### Características
- Clean Architecture (Domain, Application, Infrastructure)
- SOLID principles
- Type hints completos
- Documentación con docstrings Google Style

## [Unreleased]

### Por Hacer
- Validación de denominaciones por tipo de valor
- Dashboard web para monitoreo
- Notificaciones por email en caso de error
- Procesamiento batch de múltiples fechas
- Exportación de estadísticas