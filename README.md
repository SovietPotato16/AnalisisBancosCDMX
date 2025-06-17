# 🏦 Mapeador Multi-Bancos CDMX

Extractor y analizador de sucursales bancarias en la Ciudad de México que permite comparar **Santander**, **BBVA** y **Banorte** con análisis de competencia, visualización de reseñas y mapas interactivos.

## ✨ Nuevas Funcionalidades

### 🗺️ **Mapas Interactivos Mejorados**
- **Popups con reseñas completas**: Al hacer clic en una sucursal, ve las reseñas de usuarios
- **Capas separadas por banco**: Activa/desactiva la visualización de cada banco
- **Análisis de competencia**: Visualiza qué sucursales tienen competencia cercana
- **Mapas de calor por banco**: Identifica zonas de alta concentración

### 📊 **Análisis de Competencia**
- **Distancias entre sucursales**: Calcula automáticamente la distancia entre competidores
- **Comparación de ratings**: Analiza ventajas competitivas por zona
- **Identificación de zonas saturadas**: Encuentra áreas con alta concentración bancaria
- **Análisis por alcaldía**: Estadísticas comparativas por zona geográfica

### 🎯 **Búsqueda Multi-Banco**
- **Búsqueda simultánea**: Encuentra sucursales de los 3 bancos principales
- **Estrategias flexibles**: Por alcaldías, cuadrícula o códigos postales
- **Filtrado inteligente**: Evita duplicados y verifica autenticidad

## 🚀 Instalación

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar API Key de Google Maps
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto y habilita las APIs:
   - Places API
   - Maps JavaScript API
   - Geocoding API
3. Copia tu API Key al archivo `V1Extractor.py`:
```python
API_KEY = "TU_API_KEY_AQUI"
```

## 🎮 Uso

### Ejemplo Básico (Solo Santander)
```python
from V1Extractor import MultiBankCDMXMapper

# Inicializar
mapper = MultiBankCDMXMapper("TU_API_KEY")

# Buscar solo Santander
mapper.buscar_todas_sucursales_cdmx(
    estrategia='alcaldias',
    bancos=['Santander']
)

# Crear mapa
mapper.crear_mapa_interactivo_multibancos()
```

### Ejemplo Completo (Todos los Bancos)
```python
# Buscar todos los bancos
mapper.buscar_todas_sucursales_cdmx(
    estrategia='alcaldias',
    bancos=['Santander', 'BBVA', 'Banorte']
)

# Crear mapas con análisis
mapper.crear_mapa_interactivo_multibancos(incluir_analisis_competencia=True)
mapper.crear_mapa_alcaldias_comparativo()

# Análisis de competencia
competencia = mapper.calcular_distancias_competencia(radio_km=1.0)
analisis_zona = mapper.analizar_competencia_por_zona()

# Guardar datos
mapper.guardar_datos_multibancos()
```

## 📋 Estrategias de Búsqueda

### 🏛️ **Por Alcaldías** (Recomendado)
```python
mapper.buscar_todas_sucursales_cdmx(estrategia='alcaldias')
```
- Busca en las 16 alcaldías de CDMX
- Cobertura completa y eficiente
- Ideal para análisis por zona

### 🗺️ **Por Cuadrícula** (Exhaustivo)
```python
mapper.buscar_todas_sucursales_cdmx(
    estrategia='grid',
    radio=1500,      # Radio en metros
    tam_celda=2      # Tamaño de celda en km
)
```
- División sistemática de CDMX
- Encuentra sucursales en zonas remotas
- Mayor tiempo de ejecución

### 🎯 **Estrategia Mixta** (Más Completo)
```python
mapper.buscar_todas_sucursales_cdmx(estrategia='mixta')
```
- Combina búsqueda por alcaldías + códigos postales
- Máxima cobertura
- Recomendado para análisis profesional

## 📊 Archivos Generados

### 🗺️ **Mapas HTML Interactivos**
- `mapa_multibancos_cdmx.html`: Mapa principal con todos los bancos
- `mapa_alcaldias_comparativo.html`: Análisis comparativo por alcaldía

### 📁 **Datos Exportados**
- `multibancos_cdmx_YYYYMMDD_HHMM.json`: Datos completos en JSON
- `multibancos_cdmx_YYYYMMDD_HHMM.csv`: Datos para Excel/análisis
- `multibancos_cdmx_YYYYMMDD_HHMM.xlsx`: Excel con múltiples hojas de análisis
- `multibancos_cdmx_competencia_YYYYMMDD_HHMM.json`: Análisis de competencia

### 📈 **Hojas de Excel Incluidas**
- **Todas_Sucursales**: Datos completos de todas las sucursales
- **Santander/BBVA/Banorte**: Datos separados por banco
- **Dominancia_Zona**: Análisis de dominancia por alcaldía
- **Resumen_Alcaldia_Banco**: Estadísticas comparativas

## 🔍 Características del Mapa Interactivo

### 🏦 **Información por Sucursal**
Al hacer clic en cualquier marcador verás:
- **Datos básicos**: Nombre, dirección, teléfono, horarios
- **Calificaciones**: Rating con estrellas y total de reseñas  
- **Reseñas recientes**: Últimas 3 reseñas con texto completo
- **Análisis de competencia**: Competidores cercanos y distancias
- **Ventaja competitiva**: Diferencia de rating vs competencia

### 🎨 **Capas Disponibles**
- **Marcadores por banco**: Santander (rojo), BBVA (azul), Banorte (verde)
- **Mapas de calor**: Concentración por banco basada en ratings
- **Análisis de competencia**: Círculos mostrando zonas de alta competencia
- **Diferentes fondos**: OpenStreetMap, modo oscuro, modo claro

### 🎯 **Códigos de Color**
- **Verde oscuro**: Rating 4.5-5.0 ⭐⭐⭐⭐⭐
- **Verde**: Rating 4.0-4.4 ⭐⭐⭐⭐
- **Naranja**: Rating 3.5-3.9 ⭐⭐⭐
- **Rojo claro**: Rating 3.0-3.4 ⭐⭐
- **Rojo**: Rating < 3.0 ⭐

## 📊 Análisis de Competencia

### 🎯 **Métricas Calculadas**
- **Competidores cercanos**: Número de sucursales competidoras en 1km
- **Distancia al más cercano**: Distancia en metros al competidor más próximo
- **Ventaja en rating**: Diferencia de calificación vs competencia
- **Diferencia en reseñas**: Comparación de volumen de feedback

### 🏆 **Análisis por Zona**
- **Dominancia por alcaldía**: Qué banco tiene más presencia en cada zona
- **Ratings promedio**: Comparación de calidad de servicio por zona
- **Concentración**: Áreas con mayor/menor competencia bancaria

## ⚠️ Consideraciones Importantes

### 🕐 **Límites de API**
- Google Places API tiene límites de uso diario
- Se incluyen pausas automáticas para respetar rate limits
- Para uso intensivo, considera un plan de pago de Google Cloud

### 📍 **Precisión de Datos**
- Los datos dependen de la calidad de Google Places
- Algunas sucursales pueden no estar actualizadas
- Se filtran resultados para evitar duplicados

### 💾 **Rendimiento**
- Búsqueda completa puede tomar 30-60 minutos
- Los archivos HTML generados pueden ser grandes (>10MB)
- Se recomienda usar SSD para mejor rendimiento

## 🛠️ Personalización

### 🎨 **Modificar Colores de Bancos**
```python
mapper.banco_config['Santander']['color'] = 'purple'
mapper.banco_config['BBVA']['color'] = 'yellow'
```

### 📐 **Cambiar Radio de Competencia**
```python
competencia = mapper.calcular_distancias_competencia(radio_km=0.5)  # 500m
```

### 🗺️ **Agregar Nuevos Bancos**
```python
mapper.banco_config['Banamex'] = {
    'color': 'orange',
    'icon': 'university',
    'search_terms': ['Banamex', 'Citibanamex']
}
```

## 📞 Soporte

Si encuentras problemas:
1. Verifica que tu API Key tenga permisos para Places API
2. Revisa los límites de tu cuenta de Google Cloud
3. Asegúrate de tener las dependencias correctas instaladas

## 📄 Licencia

Este proyecto es de código abierto. Úsalo libremente para análisis comercial o académico.

---

🏦 **¡Analiza el mercado bancario de CDMX como nunca antes!** 📊 