

# Changelog

Todos los cambios importantes de este proyecto se documentan en este archivo.

El formato sigue la convención de [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

### Added
- Sistema completo de juez de código con FastAPI
- Almacenamiento en base de datos mongodb
- Soporte para múltiples lenguajes de programación (Python, JavaScript, Java)
- Ejecución segura de código con Docker (producción) y local (desarrollo)
- API REST completa con documentación automática
- Sistema de problemas con casos de prueba
- Evaluación automática de submisiones de código
- Gestión de usuarios y roles (admin/estudiante)
- CORS configurado para integración con frontend

### Technical Details
- **Framework**: FastAPI con Uvicorn
- **Validación**: Pydantic para schemas y validación
- **Ejecución de código**: Docker para producción, subprocess para desarrollo
- **Documentación**: Swagger UI y ReDoc automáticos
- **Lenguajes soportados**: Python, JavaScript, Java
- **Almacenamiento**: Mongodb

### API Endpoints
- **Autenticación**: `/api/v1/auth/` (login)
- **Problemas**: `/api/v1/problems/` (CRUD completo)
- **Submisiones**: `/api/v1/submissions/` (enviar y evaluar código)
- **Documentación**: `/docs` (Swagger), `/redoc` (ReDoc)

### Development Features
- Problema de ejemplo: "Suma de dos números"
- Casos de prueba incluidos
- Modo desarrollo sin Docker
- Hot reload para desarrollo

## [1.0.0] - 2025-06-29
### Added
- Versión inicial del proyecto
