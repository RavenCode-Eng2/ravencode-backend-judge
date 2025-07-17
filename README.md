# 🦉 RavenCode – Módulo de Juez de Código

Este repositorio forma parte del proyecto **RavenCode**, una plataforma de aprendizaje interactiva diseñada para enseñar 
programación a adolescentes de 12 a 16 años. Aquí se encuentra exclusivamente el **servicio de Juez de Código**, que gestiona 
la evaluación automática de submisiones de código, la ejecución segura de programas y la validación de casos de prueba.

---

## 🚀 ¿Cómo ejecutar el módulo?

### 🧠 Backend – FastAPI

1. Ir a la carpeta del backend:
```bash
   cd ravencode-backend-judge
```
2. Crear entorno virtual:
```bash
   python -m venv venv
```
3. Activar entorno
* En Windows
```bash
   venv\Scripts\activate
```
* En Mac/Linux
```bash
   source venv/bin/activate
```
4. Instalar dependencias
```bash
   pip install -r requirements.txt
```
5. Ejecutar el servidor
```bash
   uvicorn app.main:app --reload --port 8000
```
6. Verificar en el navegador:

   http://localhost:8000

7. Documentación Swagger Endpoints

   http://localhost:8000/docs


## Observabilidad📊📈

### **Prerrequisitos**⚙️

Antes de comenzar, asegúrate de tener las siguientes herramientas instaladas:

Prometheus📡 - Para la recolección de métricas.

Grafana💻 - Para la visualización de métricas.

### **Configuración Prometheus** 🔧

Tu archivo prometheus.yml de configuración debe verse asi:
```bash
global:
scrape_interval: 15s  # Set the scrape interval to every 15 seconds.
evaluation_interval: 15s  # Evaluate rules every 15 seconds.

# Scrape configuration for Prometheus itself.
scrape_configs:
- job_name: "prometheus"
   static_configs:
   - targets: ["localhost:9090"]
      labels:
         app: "prometheus"

# Scrape configuration for FastAPI service
- job_name: "fastapi-service"
   static_configs:
   - targets: ["localhost:8000"]  # Replace with your FastAPI service URL and port
      labels:
         app: "fastapi"
```

#### **Iniciar Prometheus** 🚀
1. Abre una terminal (cmd o PowerShell).
2. Navega hasta la carpeta donde descomprimiste Prometheus.
3. Ejecuta el siguiente comando para iniciar Prometheus:
```bash
   prometheus.exe --config.file=prometheus.yml
```

#### **Acceder a Prometheus** 🖥️

1. Una vez iniciado, abre un navegador y accede a: 

   http://localhost:9090 

2. Puedes usar la pestaña Status > Targets para verificar que Prometheus esté recolectando las métricas de tu aplicación.


### **Configuración Grafana** 📊

1. Abre una terminal (cmd o PowerShell).

2. Navega a la carpeta bin dentro de la carpeta de Grafana 

   ```bash
      cd C:\grafana\bin
   ```

3. Ejecuta el siguiente comando para iniciar Grafana:
   ```bash
      grafana-server.exe
   ```
   #### **Acceder a Grafana** 🖥️
   1. Abre un navegador y accede a:
   
       http://localhost:4000 

   2. El usuario y la contraseña por defecto son admin.

Despues de tener los pasos anteirores, solo debes configurar Prometheus como fuente de datos en grafana y crea un Dashboard para visualizar tus consultas PromQL.

## 🔐 Funcionalidades del módulo

### **Evaluación de Código**
* Ejecución segura de código en contenedores Docker
* Soporte para múltiples lenguajes (Python, JavaScript, Java)
* Límites de tiempo y memoria configurables
* Validación automática contra casos de prueba

### **Gestión de Problemas**
* Creación y gestión de problemas de programación
* Sistema de casos de prueba (muestra y ocultos)
* Diferentes niveles de dificultad
* Metadatos completos (tiempo límite, memoria límite)

### **Sistema de Submisiones**
* Envío asíncrono de código para evaluación
* Seguimiento del estado de evaluación
* Resultados detallados por caso de prueba
* Métricas de rendimiento (tiempo, memoria, puntuación)

### **API REST Completa**
* Autenticación JWT opcional
* Documentación automática con Swagger/ReDoc
* Endpoints para problemas, submisiones y autenticación
* CORS configurado para integración con frontend

## 📁 Estructura del Proyecto

```
ravencode-backend-judge/
├── app/
│   ├── core/           # Configuración y utilidades core
│   ├── models/         # Modelos de datos
│   ├── routers/        # Endpoints de la API
│   ├── schemas/        # Esquemas Pydantic
│   └── main.py         # Aplicación principal
├── scripts/            # Scripts de configuración
├── requirements.txt    # Dependencias Python
└── README.md          # Este archivo
```

## 🛠️ Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido
- **MongoDB**: Base de datos NoSQL para almacenamiento
- **Docker**: Contenedores para ejecución segura de código
- **Prometheus**: Recolección de métricas
- **JWT**: Autenticación y autorización
- **Pydantic**: Validación de datos y serialización

## 👥 Equipo de desarrollo
Proyecto desarrollado por el equipo Cuervos en el curso Ingeniería de Software II – Universidad Nacional de Colombia.

* Diego Felipe Solorzano Aponte

* Laura Valentina Pabon Cabezas

* Diana Valentina Chicuasuque Rodríguez

* Carlos Arturo Murcia Andrade

* Sergio Esteban Rendon Umbarila

* Mateo Andrés Vivas Acosta

* Jorge Andrés Torres Leal

#### Docente: Ing. Camilo Ernesto Vargas Romero
#### Semestre: 2025-1
