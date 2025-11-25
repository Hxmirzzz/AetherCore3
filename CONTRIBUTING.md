# Guía de Contribución

## Cómo Contribuir

1. **Fork** el repositorio
2. Crea una **rama** para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un **Pull Request**

## Estándares de Código

- **Formato**: Usa `black` para formatear código
- **Linting**: Ejecuta `ruff` antes de commit
- **Type hints**: Todos los métodos públicos deben tener type hints
- **Docstrings**: Usa Google Style para documentación
- **Tests**: Agrega tests para nuevas funcionalidades

## Ejecutar Tests
```bash
pytest                          # Todos los tests
pytest tests/unit/             # Solo unitarios
pytest --cov=src tests/        # Con cobertura
```

## Convenciones de Commit

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `test:` Agregar/modificar tests
- `refactor:` Refactorización de código
- `style:` Cambios de formato (no afectan funcionalidad)
```

---

## 📋 **CHECKLIST FINAL**

### **Para Producción** ✅

- [x] Clean Architecture implementada
- [x] Tests unitarios e integración
- [x] Constantes en lugar de números mágicos
- [x] Logging apropiado
- [x] Manejo de errores robusto
- [x] Type hints completos
- [ ] `.env.example` actualizado con notas
- [ ] README completo con todas las secciones
- [ ] Docstrings en todos los métodos públicos
- [ ] `CHANGELOG.md` creado
- [ ] Validación de directorios en startup

### **Nice to Have** 🎁

- [ ] Scripts de setup (Windows/Linux)
- [ ] GitHub Actions (CI/CD)
- [ ] Badges en README
- [ ] LICENSE file
- [ ] CONTRIBUTING.md

---

## 🎯 **RECOMENDACIÓN FINAL**

### **Para dar el proyecto por "Finalizado v1.0":**

1. ✅ **Implementa Prioridad Alta** (🔴) - **30 minutos**
   - Actualizar `.env.example`
   - Actualizar README (formatos, carpetas, casos especiales)
   - Crear `CHANGELOG.md`
   - Agregar docstrings faltantes

2. ✅ **Implementa Prioridad Media** (🟡) - **15 minutos**
   - Validación de directorios en startup
   - Scripts de setup

3. 🎁 **Opcional** (🟢) - Puedes hacerlo después
   - GitHub Actions
   - Badges
   - LICENSE
   - CONTRIBUTING.md

---

## 📦 **ESTRUCTURA FINAL COMPLETA**
```
AetherCore3/
├── .github/
│   └── workflows/
│       └── tests.yml
├── scripts/
│   ├── setup.bat
│   └── setup.sh
├── src/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   ├── shared/
│   └── presentation/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── .env
├── .env.example          # ✅ ACTUALIZAR
├── .gitignore
├── CHANGELOG.md          # ✅ CREAR
├── CONTRIBUTING.md       # 🎁 OPCIONAL
├── LICENSE               # 🎁 OPCIONAL
├── README.md             # ✅ ACTUALIZAR
├── pyproject.toml
└── requirements.txt