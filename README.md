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
