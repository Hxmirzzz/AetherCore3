# Aplicación de Existencias Centralizadas (AetherCore 3)

## Descripción General

Esta aplicación en Python automatiza el procesamiento de planos de existencias de billete enviados por diferentes
sucursales en formato TXT y genera un archivo nacional consolidado por fecha contable y tipo de valor (CU, EU, etc.).

**Flujo básico:**

1. Leer los archivos origen ubicados en la carpeta `PLANOS`
   (por ejemplo `C:\CERTIFICACIONES\NOMBRE_ENTIDAD\EXISTENCIAS\PLANOS`).
2. Parsear cada archivo con estructura:
   - 1 registro tipo 01 (cabecera)
   - N registros tipo 02 (detalles de denominaciones)
3. Construir objetos de dominio (`PlanoExistenciasNacional`) agregando todos los archivos del mismo día y tipo de valor.
4. Generar un único archivo nacional TXT por tipo de valor y fecha contable, centralizado en Bogotá (BOG).
5. Mover versiones anteriores del nacional a una carpeta de `COPIAS`.
6. Mover los planitos de entrada procesados a `PLANOS/gestionados`.
7. (Opcional) Ejecutar en modo *watch* con `watchdog`, monitoreando la carpeta 24/7.

---

## Características

### 📄 Procesamiento de archivos origen (PLANOS)

Los archivos tienen la siguiente estructura:

**Tipo 01 – Cabecera**
```
01,codigo_dane_ciudad,nombre_ciudad,fecha_certificado,codigo_transportadora,
nit_cliente,nombre_cliente,codigo_divisa,nombre_divisa,codigo_fondo,nombre_fondo
```
Ejemplo:
```
01,13001,CARTAGENA,17/10/2025,BRK,860006797,BANCO,9,EURO,1,OFICINAS
```

**Tipo 02 – Detalle**
```
02,tipo_valor,nombre_tipo_valor,codigo_calidad,nombre_calidad,
valor_den_1,cant_den_1,
valor_den_2,cant_den_2,
...
valor_den_8,cant_den_8
```
Ejemplo:
```
02,24,Euro,2,Buen Estado,500,0,200,11,100,0,50,40,20,0,10,0,5,0,2,0
```

Cada archivo origen contiene exactamente un registro tipo 01 y uno o más registros tipo 02. El nombre del archivo trae
datos clave (cliente, ciudad, fecha/hora, tipo de valor).

> **Aclaración de la documentación original:** no se rellenan campos con ceros o espacios si no se usa la longitud
> completa. En CSV esto significa dejar comas consecutivas cuando un valor está vacío (`02,24,Euro,2,Buen Estado,500,0,200,11,,,,,,,`).

En el TXT nacional, la app respeta la misma filosofía: cuando valor o cantidad son 0 se escribe vacío.

### 🎯 Objetivo del módulo

Centralizar múltiples archivos de existencias de diferentes ciudades para una misma fecha y tipo de valor, generando un
archivo nacional por combinación.

Ejemplos:
- `VYBUBOG2510252359CU.TXT` → todo CU del 25/10/2025
- `VYBUBOG2510252359EU.TXT` → todo EU del 25/10/2025

Dentro del archivo nacional se concatenan todos los bloques `{01 + 02s}` que comparten fecha contable y tipo de valor.
La ciudad original permanece en cada cabecera, aunque el archivo resultante se nombre con `BOG` por ser centralizado.

---

## 🧱 Estructura del proyecto

```
AetherCore3/
│
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   └── existencias.py
│   │   ├── value_objects/
│   │   │   ├── fecha_contable.py
│   │   │   └── tipo_valor.py
│   │   └── exceptions/
│   │       └── dominio_existencias_exception.py
│   │
│   ├── application/
│   │   ├── interfaces/
│   │   │   ├── i_existencias_parser.py
│   │   │   ├── i_existencias_aggregator.py
│   │   │   └── i_existencias_output.py
│   │   ├── services/
│   │   │   ├── existencias_parser_service.py
│   │   │   ├── existencias_aggregator_service.py
│   │   │   └── existencias_output_service.py
│   │   └── orchestrators/
│   │       └── existencias_orchestrator.py
│   │
│   ├── infrastructure/
│   │   ├── config/settings_existencias.py
│   │   ├── file_system/
│   │   │   ├── existencias_txt_reader.py
│   │   │   ├── existencias_txt_writer.py
│   │   │   └── existencias_path_manager.py
│   │   └── watchdog/existencia_file_watcher.py
│   │
│   ├── shared/result.py
│   └── presentation/console/console_existencia.py
│
├── tests/
|   ├── conftest.py              # Fixtures compartidos
|   ├── unit/                    # Tests unitarios
|   │   ├── domain/
|   │   │   ├── test_fecha_contable.py
|   │   │   ├── test_tipo_valor.py
|   │   │   └── test_existencias_entities.py
|   │   └── application/
|   │       ├── test_parser_service.py
|   │       └── test_aggregator_service.py
|   ├── integration/             # Tests de integración
|   │   ├── test_parser_con_reader.py
|   │   └── test_orchestrator.py
|   └── fixtures/                # Archivos de prueba
|      ├── archivos_origen/
|      │   ├── VYBUBOG2511210750CU.TXT
|      │   └── VYBUCTG2511210752EU.TXT
|      └── expected_output/
|         └── VYBUBOG2511210800CU.TXT
|
├── config/
├── .env / .env.example
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Relación con Clean Architecture / SOLID

- **domain**: entidades puras (`PlanoExistenciasHeader`, `PlanoExistenciasDetalle`, `PlanoExistenciasNacional`) sin
  importar infraestructura.
- **application**: servicios y casos de uso (`ExistenciasParserService`, `ExistenciasAggregatorService`,
  `ExistenciasOutputService`, `ExistenciasProcessingOrchestrator`). Dependen de interfaces.
- **infrastructure**: implementaciones concretas (`ExistenciasTxtReader`, `ExistenciasTxtWriter`,
  `ExistenciasFileWatcher`).
- **presentation**: CLI (`console_existencia.py`) para procesamientos puntuales o modo *watch*.

---

## ⚙️ Configuración

### 1. Variables de entorno (`.env`)

Ejemplo base:
```
EXISTENCIAS_ORIGEN_DIR=C:\CERTIFICACIONES\NOMBRE_ENTIDAD\EXISTENCIAS\PLANOS
EXISTENCIAS_NACIONAL_DIR=C:\CERTIFICACIONES\NOMBRE_ENTIDAD\NACIONAL
EXISTENCIAS_LOG_DIR=C:\CERTIFICACIONES\NOMBRE_ENTIDAD\logs
EXISTENCIAS_WATCH_INTERVAL=5
```
`settings_existencias.py` lee estas variables y construye `ExistenciasSettings`, usado por `ExistenciasPathManager`.

### 2. Rutas generadas

- **Origen gestionados**: `...\PLANOS\gestionados`
- **Nacional por fecha**: `...\NACIONAL\YYMMDD\VYBUBOGYYMMDDHHMITV.TXT`
- **Copias** (para versiones previas): `...\NACIONAL\YYMMDD\COPIAS\VYBUBOG..._timestamp.TXT`

---

## 🔧 Instalación

```bash
git clone <repo> AetherCore3
cd AetherCore3
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/macOS
pip install -r requirements.txt
```

Duplica `.env.example` a `.env` y ajusta rutas reales.

---

## 🚀 Uso

### 1. Procesar una fecha concreta
```bash
python -m src.presentation.console.console_existencia --fecha 2025-10-25
```
- Busca archivos origen del 25/10/2025.
- Parsea cabecera/detalles, agrupa por fecha y tipo de valor.
- Genera los nacionales necesarios (CU, EU...).
- Mueve planitos procesados a `PLANOS/gestionados`.

### 2. Modo watcher 24/7
```bash
python -m src.presentation.console.console_existencia --watch
```
- Usa `watchdog` para detectar TXT nuevos.
- Si llega un archivo, lo parsea, genera/actualiza el nacional y mueve el antiguo a `COPIAS`.
- Mueve el archivo origen a `PLANOS/gestionados`.

### 3. Validaciones

- Cada archivo debe tener 1 registro tipo 01 y ≥1 registro tipo 02.
- Si faltan campos críticos se registra el error (y puedes moverlo a una carpeta de errores si se extiende).
- La fecha contable oficial es la del header (no la del nombre de archivo).

---

## 📝 Logs

Los logs se almacenan en `EXISTENCIAS_LOG_DIR` (o un valor por defecto). Se registran eventos como:
- Archivos detectados y parseados
- Errores de formato
- Generación de nacionales/backups
- Movimientos a `gestionados`

---

## Contacto / Soporte

- **Autor**: Hxmir (Hamir)
- **Correo**: jamir08david@gmail.com