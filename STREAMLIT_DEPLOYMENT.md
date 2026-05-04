# 🚀 Despliegue en Streamlit Cloud

## Para tu Profesor: Acceso Online

Tu profesor puede acceder directamente a la aplicación sin instalar nada visitando:
```
https://share.streamlit.io/adricelada143/TFG---Volatilidad-IBEX-35/main/03_analisis_negocio/dashboard/app.py
```

> **Si el enlace anterior no funciona**, es porque aún no está desplegado. Sigue los pasos abajo para hacerlo.

---

## Instrucciones para Desplegar

### Paso 1: Conectar tu repositorio a Streamlit Cloud

1. Ve a **https://streamlit.io/cloud**
2. Haz clic en **"Create app"**
3. Selecciona:
   - **Repository**: `adricelada143/TFG---Volatilidad-IBEX-35`
   - **Branch**: `main`
   - **File path**: `03_analisis_negocio/dashboard/app.py`

### Paso 2: Configuración (opcional)

1. En **"Advanced settings"** (si es necesario):
   - **Python version**: 3.11
   - **Install dependencies from**: `03_analisis_negocio/dashboard/requirements.txt`

### Paso 3: ¡Listo!

Streamlit desplegará automáticamente tu app. Compartir el enlace público con tu profesor.

---

## ¿Qué está incluido?

✅ Toda la base de datos (`tfg.db`)  
✅ Todos los datos procesados (CSVs)  
✅ Dashboard interactivo con 6 páginas  
✅ Modelos de volatilidad  
✅ Event study de publicaciones macro

---

## Notas de Rendimiento

- **Primera carga**: ~30-45 segundos (carga datos en caché)
- **Actualizaciones posteriores**: <5 segundos (caché en memoria)
- **No requiere interactividad**: Si no cambia filtros, no se recalcula

Si tienes problemas de rendimiento:
1. Reduce el rango de fechas en los filtros
2. Selecciona menos activos
3. Streamlit Cloud ofrece upgrades de CPU si es necesario
