import googlemaps
import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
import json
from datetime import datetime
import time
import webbrowser
import os
import math
from geopy.distance import geodesic
import numpy as np

class MultiBankCDMXMapper:
    def __init__(self, api_key):
        """
        Inicializa el extractor y mapeador para múltiples bancos en CDMX
        """
        self.gmaps = googlemaps.Client(key=api_key)
        # Resultados separados por banco
        self.results = {
            'Santander': [],
            'BBVA': [],
            'Banorte': []
        }
        self.processed_places = set()
        
        # Configuración de colores y marcadores por banco
        self.banco_config = {
            'Santander': {
                'color': 'red',
                'icon': 'university',
                'search_terms': ['Banco Santander', 'Santander']
            },
            'BBVA': {
                'color': 'blue', 
                'icon': 'university',
                'search_terms': ['BBVA', 'Banco BBVA']
            },
            'Banorte': {
                'color': 'green',
                'icon': 'university', 
                'search_terms': ['Banorte', 'Banco Banorte']
            }
        }
        
        # Colores para los marcadores según calificación
        self.rating_colors = {
            5: 'darkgreen',
            4: 'green', 
            3: 'orange',
            2: 'lightred',
            1: 'red'
        }
    
    def buscar_todas_sucursales_cdmx(self, estrategia='alcaldias', bancos=None, **kwargs):
        """
        Busca sucursales de múltiples bancos usando diferentes estrategias
        
        Args:
            estrategia: 'alcaldias', 'grid', 'mixta'
            bancos: Lista de bancos a buscar ['Santander', 'BBVA', 'Banorte']
            **kwargs: Parámetros adicionales según estrategia
        """
        if bancos is None:
            bancos = ['Santander', 'BBVA', 'Banorte']
            
        print(f"Iniciando búsqueda de {bancos} con estrategia: {estrategia}")
        
        for banco in bancos:
            print(f"\n=== Buscando sucursales de {banco} ===")
            self.banco_actual = banco
            
            if estrategia == 'alcaldias':
                self._buscar_por_alcaldias(banco)
            elif estrategia == 'grid':
                radio = kwargs.get('radio', 2000)
                tam_celda = kwargs.get('tam_celda', 3)
                self._buscar_por_grid(banco, radio=radio, tam_celda=tam_celda)
            elif estrategia == 'mixta':
                self._buscar_por_alcaldias(banco)
                self._buscar_por_cp_principales(banco)
                
        return self.results
    
    def _buscar_por_alcaldias(self, banco):
        """
        Busca en cada alcaldía de CDMX para un banco específico
        """
        alcaldias = [
            "Álvaro Obregón, CDMX",
            "Azcapotzalco, CDMX", 
            "Benito Juárez, CDMX",
            "Coyoacán, CDMX",
            "Cuajimalpa, CDMX",
            "Cuauhtémoc, CDMX",
            "Gustavo A. Madero, CDMX",
            "Iztacalco, CDMX",
            "Iztapalapa, CDMX",
            "Magdalena Contreras, CDMX",
            "Miguel Hidalgo, CDMX",
            "Milpa Alta, CDMX",
            "Tláhuac, CDMX",
            "Tlalpan, CDMX", 
            "Venustiano Carranza, CDMX",
            "Xochimilco, CDMX"
        ]
        
        search_terms = self.banco_config[banco]['search_terms']
        
        for i, alcaldia in enumerate(alcaldias):
            print(f"Buscando {banco} en {alcaldia} ({i+1}/{len(alcaldias)})")
            
            for term in search_terms:
                try:
                    results = self.gmaps.places(
                        query=f'{term} sucursal en {alcaldia}',
                        type='bank'
                    )
                    self._procesar_resultados(results.get('results', []), banco)
                    
                    # Manejar paginación
                    while 'next_page_token' in results:
                        time.sleep(2)
                        results = self.gmaps.places(
                            page_token=results['next_page_token']
                        )
                        self._procesar_resultados(results.get('results', []), banco)
                        
                except Exception as e:
                    print(f"Error en {alcaldia} para {banco}: {e}")
                
                time.sleep(0.5)  # Pausa entre términos de búsqueda
            
            time.sleep(1)  # Pausa entre alcaldías

    def _buscar_por_grid(self, banco, radio=2000, tam_celda=3):
        """
        Busca usando una cuadrícula para un banco específico
        """
        # Límites de CDMX
        bounds = {
            'north': 19.593, 'south': 19.048,
            'east': -98.960, 'west': -99.365
        }
        
        # Generar puntos de búsqueda
        puntos = []
        lat = bounds['south']
        lat_step = tam_celda / 111
        lng_step = tam_celda / 85  # Aproximado para esta latitud
        
        while lat <= bounds['north']:
            lng = bounds['west']
            while lng <= bounds['east']:
                puntos.append((lat, lng))
                lng += lng_step
            lat += lat_step
        
        print(f"Buscando {banco} en {len(puntos)} puntos con radio {radio}m")
        search_terms = self.banco_config[banco]['search_terms']
        
        for i, punto in enumerate(puntos):
            if i % 10 == 0:
                print(f"Progreso {banco}: {i}/{len(puntos)}")
            
            for term in search_terms:
                try:
                    results = self.gmaps.places_nearby(
                        location=punto,
                        radius=radio,
                        keyword=f'{term} banco',
                        type='bank'
                    )
                    self._procesar_resultados(results.get('results', []), banco)
                except Exception as e:
                    print(f"Error en punto {punto} para {banco}: {e}")
                
                time.sleep(0.3)

    def _buscar_por_cp_principales(self, banco):
        """
        Busca en códigos postales principales de CDMX para un banco específico
        """
        # Códigos postales principales de CDMX por alcaldía
        cp_principales = [
            # Centro histórico y áreas comerciales importantes
            "06000", "06010", "06020", "06030",  # Cuauhtémoc
            "11000", "11010", "11020", "11030",  # Miguel Hidalgo
            "03100", "03200", "03300", "03400",  # Benito Juárez
            "04000", "04100", "04200", "04300",  # Coyoacán
            "01000", "01100", "01200", "01300",  # Álvaro Obregón
            "07000", "07100", "07200", "07300",  # Gustavo A. Madero
            "08000", "08100", "08200", "08300",  # Iztacalco
            "09000", "09100", "09200", "09300",  # Iztapalapa
            "16000", "16100", "16200", "16300",  # Xochimilco
            "13000", "13100", "13200", "13300",  # Tláhuac
            "14000", "14100", "14200", "14300",  # Tlalpan
            "10000", "10100", "10200", "10300",  # Magdalena Contreras
            "05000", "05100", "05200", "05300",  # Cuajimalpa
            "15000", "15100", "15200", "15300",  # Venustiano Carranza
            "02000", "02100", "02200", "02300",  # Azcapotzalco
            "12000", "12100", "12200", "12300"   # Milpa Alta
        ]
        
        search_terms = self.banco_config[banco]['search_terms']
        
        for i, cp in enumerate(cp_principales):
            print(f"Buscando {banco} en CP {cp} ({i+1}/{len(cp_principales)})")
            
            for term in search_terms:
                try:
                    results = self.gmaps.places(
                        query=f'{term} sucursal {cp} CDMX',
                        type='bank'
                    )
                    self._procesar_resultados(results.get('results', []), banco)
                    
                    # Manejar paginación
                    while 'next_page_token' in results:
                        time.sleep(2)
                        results = self.gmaps.places(
                            page_token=results['next_page_token']
                        )
                        self._procesar_resultados(results.get('results', []), banco)
                        
                except Exception as e:
                    print(f"Error en CP {cp} para {banco}: {e}")
                
                time.sleep(0.5)
            
            time.sleep(0.8)  # Pausa entre códigos postales

    def _procesar_resultados(self, places, banco):
        """
        Procesa y filtra resultados para un banco específico
        """
        search_terms = self.banco_config[banco]['search_terms']
        
        for place in places:
            place_id = place.get('place_id')
            nombre = place.get('name', '').lower()
            
            # Verificar si es del banco correcto
            es_banco_correcto = any(term.lower() in nombre for term in search_terms)
            
            if es_banco_correcto and place_id not in self.processed_places:
                self.processed_places.add(place_id)
                details = self._obtener_detalles(place_id, banco)
                if details:
                    self.results[banco].append(details)
                    print(f"✓ {banco}: {details['nombre']}")
    
    def _obtener_detalles(self, place_id, banco):
        """
        Obtiene información detallada de una sucursal
        """
        try:
            result = self.gmaps.place(
                place_id=place_id,
                fields=['name', 'formatted_address', 'geometry', 'rating',
                       'user_ratings_total', 'reviews', 'opening_hours',
                       'formatted_phone_number', 'website'],
                language='es'
            )['result']
            
            # Extraer alcaldía
            direccion = result.get('formatted_address', '')
            alcaldia = self._extraer_alcaldia(direccion)
            
            # Procesar reseñas con más detalles
            reviews = []
            for review in result.get('reviews', []):
                reviews.append({
                    'autor': review.get('author_name', ''),
                    'rating': review.get('rating', 0),
                    'texto': review.get('text', ''),
                    'fecha': review.get('relative_time_description', ''),
                    'fecha_timestamp': review.get('time', 0)
                })
            
            return {
                'place_id': place_id,
                'banco': banco,
                'nombre': result.get('name', ''),
                'direccion': direccion,
                'alcaldia': alcaldia,
                'lat': result.get('geometry', {}).get('location', {}).get('lat'),
                'lng': result.get('geometry', {}).get('location', {}).get('lng'),
                'rating': result.get('rating', 0),
                'total_reviews': result.get('user_ratings_total', 0),
                'telefono': result.get('formatted_phone_number', ''),
                'website': result.get('website', ''),
                'horarios': result.get('opening_hours', {}).get('weekday_text', []),
                'reviews': reviews
            }
            
        except Exception as e:
            print(f"Error obteniendo detalles: {e}")
            return None
    
    def _extraer_alcaldia(self, direccion):
        """
        Identifica la alcaldía desde la dirección
        """
        alcaldias = [
            'Álvaro Obregón', 'Azcapotzalco', 'Benito Juárez', 'Coyoacán',
            'Cuajimalpa', 'Cuauhtémoc', 'Gustavo A. Madero', 'Iztacalco',
            'Iztapalapa', 'Magdalena Contreras', 'Miguel Hidalgo', 'Milpa Alta',
            'Tláhuac', 'Tlalpan', 'Venustiano Carranza', 'Xochimilco'
        ]
        
        for alcaldia in alcaldias:
            if alcaldia.lower() in direccion.lower():
                return alcaldia
        return 'No identificada'

    def calcular_distancias_competencia(self, radio_km=1.0):
        """
        Calcula distancias entre sucursales de diferentes bancos
        y identifica competencia cercana
        """
        print(f"Analizando competencia en radio de {radio_km} km...")
        
        analisis_competencia = []
        
        # Combinar todas las sucursales
        todas_sucursales = []
        for banco, sucursales in self.results.items():
            for sucursal in sucursales:
                sucursal_copy = sucursal.copy()
                sucursal_copy['banco'] = banco
                todas_sucursales.append(sucursal_copy)
        
        # Analizar cada sucursal
        for i, sucursal_base in enumerate(todas_sucursales):
            competidores_cercanos = []
            
            for j, otra_sucursal in enumerate(todas_sucursales):
                if i != j and sucursal_base['banco'] != otra_sucursal['banco']:
                    # Calcular distancia
                    coord1 = (sucursal_base['lat'], sucursal_base['lng'])
                    coord2 = (otra_sucursal['lat'], otra_sucursal['lng'])
                    distancia = geodesic(coord1, coord2).kilometers
                    
                    if distancia <= radio_km:
                        competidores_cercanos.append({
                            'banco_competidor': otra_sucursal['banco'],
                            'nombre_competidor': otra_sucursal['nombre'],
                            'distancia_km': round(distancia, 3),
                            'rating_competidor': otra_sucursal['rating'],
                            'reviews_competidor': otra_sucursal['total_reviews'],
                            'diferencia_rating': round(sucursal_base['rating'] - otra_sucursal['rating'], 2),
                            'diferencia_reviews': sucursal_base['total_reviews'] - otra_sucursal['total_reviews']
                        })
            
            if competidores_cercanos:
                # Ordenar por distancia
                competidores_cercanos.sort(key=lambda x: x['distancia_km'])
                
                analisis_competencia.append({
                    'sucursal_base': sucursal_base,
                    'competidores': competidores_cercanos,
                    'total_competidores': len(competidores_cercanos),
                    'competidor_mas_cercano': competidores_cercanos[0]['distancia_km'],
                    'promedio_rating_competencia': np.mean([c['rating_competidor'] for c in competidores_cercanos]),
                    'ventaja_rating': round(sucursal_base['rating'] - np.mean([c['rating_competidor'] for c in competidores_cercanos]), 2)
                })
        
        return analisis_competencia

    def crear_mapa_interactivo_multibancos(self, archivo='mapa_multibancos_cdmx.html', incluir_analisis_competencia=True):
        """
        Crea un mapa interactivo con todas las sucursales de múltiples bancos
        """
        print("Creando mapa interactivo multi-bancos...")
        
        # Análisis de competencia si se solicita
        competencia = []
        if incluir_analisis_competencia:
            competencia = self.calcular_distancias_competencia()
        
        # Crear mapa base centrado en CDMX
        mapa = folium.Map(
            location=[19.4326, -99.1332],
            zoom_start=11,
            tiles='OpenStreetMap'
        )
        
        # Agregar capas de tiles adicionales
        folium.TileLayer('CartoDB dark_matter', name='Modo Oscuro').add_to(mapa)
        folium.TileLayer('CartoDB positron', name='Modo Claro').add_to(mapa)
        
        # Crear grupos de marcadores por banco
        grupos_bancos = {}
        clusters_bancos = {}
        
        for banco in self.results.keys():
            if self.results[banco]:  # Solo si hay resultados
                config = self.banco_config[banco]
                grupos_bancos[banco] = folium.FeatureGroup(name=f'{banco} ({len(self.results[banco])} sucursales)')
                clusters_bancos[banco] = MarkerCluster(name=f'Cluster {banco}').add_to(grupos_bancos[banco])
        
        # Agregar marcadores para cada banco
        for banco, sucursales in self.results.items():
            if not sucursales:
                continue
                
            config = self.banco_config[banco]
            
            for sucursal in sucursales:
                # Crear popup con información completa incluyendo reseñas
                popup_html = self._crear_popup_completo(sucursal, banco, competencia)
                
                # Color según rating
                rating = sucursal.get('rating', 0)
                if rating >= 4.5:
                    color = 'darkgreen'
                elif rating >= 4.0:
                    color = 'green'
                elif rating >= 3.5:
                    color = 'orange'
                elif rating >= 3.0:
                    color = 'lightred'
                else:
                    color = 'red'
                
                # Agregar marcador
                folium.Marker(
                    location=[sucursal['lat'], sucursal['lng']],
                    popup=folium.Popup(popup_html, max_width=400),
                    icon=folium.Icon(
                        color=color, 
                        icon=config['icon'], 
                        prefix='fa'
                    ),
                    tooltip=f"{banco} - {sucursal['nombre']} - {rating}⭐"
                ).add_to(clusters_bancos[banco])
        
        # Agregar grupos al mapa
        for grupo in grupos_bancos.values():
            grupo.add_to(mapa)
        
        # Agregar mapas de calor por banco
        self._agregar_mapas_calor_multibancos(mapa)
        
        # Agregar análisis de competencia como capa
        if competencia:
            self._agregar_capa_competencia(mapa, competencia)
        
        # Agregar controles
        folium.LayerControl(collapsed=False).add_to(mapa)
        
        # Guardar mapa
        mapa.save(archivo)
        print(f"Mapa multi-bancos guardado como: {archivo}")
        
        # Abrir en navegador
        webbrowser.open(f'file://{os.path.abspath(archivo)}')
        
        return mapa

    def _crear_popup_completo(self, sucursal, banco, competencia):
        """
        Crea popup completo con reseñas y análisis de competencia
        """
        # Buscar análisis de competencia para esta sucursal
        comp_info = ""
        for comp in competencia:
            if comp['sucursal_base']['place_id'] == sucursal['place_id']:
                comp_info = f"""
                <hr>
                <h5>🏆 Análisis de Competencia</h5>
                <p><b>Competidores cercanos:</b> {comp['total_competidores']}</p>
                <p><b>Más cercano:</b> {comp['competidor_mas_cercano']} km</p>
                <p><b>Ventaja en rating:</b> {comp['ventaja_rating']} ⭐</p>
                <details>
                    <summary>Ver competidores cercanos</summary>
                    <ul style="margin: 5px 0; padding-left: 20px; font-size: 0.9em;">
                """
                for comp_det in comp['competidores'][:3]:  # Solo los 3 más cercanos
                    comp_info += f"""
                        <li>{comp_det['banco_competidor']} - {comp_det['distancia_km']}km 
                            (⭐{comp_det['rating_competidor']})</li>
                    """
                comp_info += "</ul></details>"
                break
        
        # Preparar reseñas para mostrar
        reviews_html = ""
        if sucursal.get('reviews'):
            reviews_html = """
            <hr>
            <h5>💬 Reseñas Recientes</h5>
            <div style="max-height: 200px; overflow-y: auto;">
            """
            
            # Mostrar hasta 3 reseñas más recientes
            for review in sucursal['reviews'][:3]:
                stars = '⭐' * int(review['rating'])
                reviews_html += f"""
                <div style="border-bottom: 1px solid #eee; margin: 5px 0; padding: 5px 0;">
                    <p style="margin: 2px 0; font-weight: bold;">{review['autor']}</p>
                    <p style="margin: 2px 0;">{stars} ({review['rating']}/5) - {review['fecha']}</p>
                    <p style="margin: 2px 0; font-size: 0.9em; font-style: italic;">
                        "{review['texto'][:150]}{'...' if len(review['texto']) > 150 else ''}"
                    </p>
                </div>
                """
            reviews_html += "</div>"
        
        # Popup completo
        popup_html = f"""
        <div style="font-family: Arial; width: 380px;">
            <h4 style="color: {self.banco_config[banco]['color']}; margin: 0 0 10px 0;">
                🏦 {sucursal['nombre']}
            </h4>
            
            <div style="background: #f8f9fa; padding: 8px; border-radius: 5px; margin: 5px 0;">
                <p style="margin: 2px 0;"><b>🏛️ Banco:</b> {banco}</p>
                <p style="margin: 2px 0;"><b>📍 Dirección:</b> {sucursal['direccion']}</p>
                <p style="margin: 2px 0;"><b>🗺️ Alcaldía:</b> {sucursal['alcaldia']}</p>
            </div>
            
            <div style="background: #e7f3ff; padding: 8px; border-radius: 5px; margin: 5px 0;">
                <p style="margin: 2px 0;"><b>⭐ Rating:</b> {'⭐' * int(sucursal.get('rating', 0))} {sucursal.get('rating', 0)}/5</p>
                <p style="margin: 2px 0;"><b>📊 Total reseñas:</b> {sucursal.get('total_reviews', 0)}</p>
                <p style="margin: 2px 0;"><b>📞 Teléfono:</b> {sucursal.get('telefono', 'No disponible')}</p>
            </div>
            
            <details style="margin: 5px 0;">
                <summary><b>🕒 Horarios de Atención</b></summary>
                <ul style="margin: 5px 0; padding-left: 20px; font-size: 0.9em;">
                    {''.join([f"<li>{h}</li>" for h in sucursal.get('horarios', [])[:7]])}
                </ul>
            </details>
            
            {comp_info}
            {reviews_html}
        </div>
        """
        
        return popup_html

    def _agregar_mapas_calor_multibancos(self, mapa):
        """
        Agrega mapas de calor separados por banco
        """
        for banco, sucursales in self.results.items():
            if not sucursales:
                continue
                
            heat_data = []
            for sucursal in sucursales:
                # Peso basado en rating y número de reseñas
                weight = sucursal.get('rating', 0) * (1 + sucursal.get('total_reviews', 0)/1000)
                heat_data.append([sucursal['lat'], sucursal['lng'], weight])
            
            if heat_data:
                HeatMap(
                    heat_data,
                    name=f'Mapa de Calor {banco}',
                    radius=20,
                    blur=15,
                    max_zoom=13,
                    show=False  # Oculto por defecto
                ).add_to(mapa)

    def _agregar_capa_competencia(self, mapa, competencia):
        """
        Agrega capa de análisis de competencia
        """
        grupo_competencia = folium.FeatureGroup(name='Análisis de Competencia', show=False)
        
        for comp in competencia:
            sucursal = comp['sucursal_base']
            
            # Círculo mostrando zona de competencia
            folium.Circle(
                location=[sucursal['lat'], sucursal['lng']],
                radius=1000,  # 1km de radio
                popup=f"""
                <div style="font-family: Arial;">
                    <h5>{sucursal['banco']} - {sucursal['nombre']}</h5>
                    <p><b>Competidores en 1km:</b> {comp['total_competidores']}</p>
                    <p><b>Ventaja en rating:</b> {comp['ventaja_rating']} ⭐</p>
                </div>
                """,
                color='purple',
                fill=True,
                fillOpacity=0.1,
                weight=2
            ).add_to(grupo_competencia)
        
        grupo_competencia.add_to(mapa)

    def analizar_competencia_por_zona(self):
        """
        Genera análisis detallado de competencia por alcaldía
        """
        print("Generando análisis de competencia por zona...")
        
        # Combinar todas las sucursales con información de banco
        todas_sucursales = []
        for banco, sucursales in self.results.items():
            for sucursal in sucursales:
                sucursal_info = sucursal.copy()
                sucursal_info['banco'] = banco
                todas_sucursales.append(sucursal_info)
        
        df_completo = pd.DataFrame(todas_sucursales)
        
        if df_completo.empty:
            print("No hay datos para analizar")
            return None
        
        # Análisis por alcaldía
        analisis_alcaldia = df_completo.groupby(['alcaldia', 'banco']).agg({
            'nombre': 'count',
            'rating': ['mean', 'std'],
            'total_reviews': ['sum', 'mean']
        }).round(2)
        
        # Análisis de dominancia por zona
        dominancia = df_completo.groupby('alcaldia')['banco'].value_counts().unstack(fill_value=0)
        dominancia['total'] = dominancia.sum(axis=1)
        dominancia['banco_dominante'] = dominancia[['Santander', 'BBVA', 'Banorte']].idxmax(axis=1)
        
        return {
            'analisis_por_alcaldia': analisis_alcaldia,
            'dominancia_por_zona': dominancia,
            'dataframe_completo': df_completo
        }

    def guardar_datos_multibancos(self, prefijo='multibancos_cdmx'):
        """
        Guarda los datos de múltiples bancos en diferentes formatos
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        # Combinar todos los resultados
        todos_datos = []
        for banco, sucursales in self.results.items():
            for sucursal in sucursales:
                sucursal_copy = sucursal.copy()
                sucursal_copy['banco'] = banco
                todos_datos.append(sucursal_copy)
        
        if not todos_datos:
            print("No hay datos para guardar")
            return
        
        # JSON completo
        with open(f'{prefijo}_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump({
                'resultados_por_banco': self.results,
                'timestamp': timestamp,
                'total_sucursales': len(todos_datos)
            }, f, ensure_ascii=False, indent=2)
        
        # DataFrame para análisis
        df = pd.DataFrame(todos_datos)
        
        # CSV
        df.to_csv(f'{prefijo}_{timestamp}.csv', index=False, encoding='utf-8-sig')
        
        # Excel con múltiples hojas de análisis
        with pd.ExcelWriter(f'{prefijo}_{timestamp}.xlsx') as writer:
            # Datos completos
            df.to_excel(writer, sheet_name='Todas_Sucursales', index=False)
            
            # Por banco
            for banco in self.results.keys():
                if self.results[banco]:
                    df_banco = df[df['banco'] == banco]
                    df_banco.to_excel(writer, sheet_name=banco, index=False)
            
            # Análisis por alcaldía
            if not df.empty:
                analisis_zona = self.analizar_competencia_por_zona()
                if analisis_zona:
                    analisis_zona['dominancia_por_zona'].to_excel(writer, sheet_name='Dominancia_Zona')
                    
                    # Resumen por alcaldía y banco
                    resumen = df.groupby(['alcaldia', 'banco']).agg({
                        'nombre': 'count',
                        'rating': 'mean',
                        'total_reviews': 'sum'
                    }).round(2)
                    resumen.to_excel(writer, sheet_name='Resumen_Alcaldia_Banco')
        
        # Análisis de competencia
        competencia = self.calcular_distancias_competencia()
        if competencia:
            with open(f'{prefijo}_competencia_{timestamp}.json', 'w', encoding='utf-8') as f:
                json.dump(competencia, f, ensure_ascii=False, indent=2)
        
        print(f"Datos multi-bancos guardados con prefijo: {prefijo}_{timestamp}")
        print(f"Total de sucursales encontradas: {len(todos_datos)}")
        for banco, sucursales in self.results.items():
            print(f"  - {banco}: {len(sucursales)} sucursales")

    def crear_mapa_alcaldias_comparativo(self, archivo='mapa_alcaldias_comparativo.html'):
        """
        Crea mapa con análisis comparativo por alcaldía entre bancos
        """
        print("Creando mapa comparativo por alcaldías...")
        
        # Combinar todas las sucursales
        todas_sucursales = []
        for banco, sucursales in self.results.items():
            for sucursal in sucursales:
                sucursal_copy = sucursal.copy()
                sucursal_copy['banco'] = banco
                todas_sucursales.append(sucursal_copy)
        
        if not todas_sucursales:
            print("No hay datos para crear el mapa")
            return None
            
        df = pd.DataFrame(todas_sucursales)
        
        # Crear mapa
        mapa = folium.Map(location=[19.4326, -99.1332], zoom_start=11)
        
        # Análisis por alcaldía
        stats_alcaldia = df.groupby(['alcaldia', 'banco']).agg({
            'nombre': 'count',
            'rating': 'mean',
            'total_reviews': 'sum'
        }).round(2)
        
        # Obtener centro de cada alcaldía
        centros_alcaldia = df.groupby('alcaldia')[['lat', 'lng']].mean()
        
        # Agregar marcadores por alcaldía con estadísticas comparativas
        for alcaldia in centros_alcaldia.index:
            if alcaldia == 'No identificada':
                continue
                
            lat_center = centros_alcaldia.loc[alcaldia, 'lat']
            lng_center = centros_alcaldia.loc[alcaldia, 'lng']
            
            # Estadísticas por banco en esta alcaldía
            stats_bancos = []
            total_sucursales = 0
            
            for banco in ['Santander', 'BBVA', 'Banorte']:
                try:
                    stats = stats_alcaldia.loc[(alcaldia, banco)]
                    sucursales = int(stats['nombre'])
                    rating = stats['rating']
                    reviews = int(stats['total_reviews'])
                    total_sucursales += sucursales
                    
                    stats_bancos.append(f"""
                    <tr style="color: {self.banco_config[banco]['color']};">
                        <td><b>{banco}</b></td>
                        <td>{sucursales}</td>
                        <td>{rating:.2f}</td>
                        <td>{reviews}</td>
                    </tr>
                    """)
                except KeyError:
                    stats_bancos.append(f"""
                    <tr style="color: gray;">
                        <td>{banco}</td>
                        <td>0</td>
                        <td>-</td>
                        <td>0</td>
                    </tr>
                    """)
            
            # Crear popup con estadísticas comparativas
            popup_html = f"""
            <div style="font-family: Arial; width: 350px;">
                <h3>🏛️ {alcaldia}</h3>
                <p><b>Total de sucursales bancarias:</b> {total_sucursales}</p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
                    <thead>
                        <tr style="background-color: #f0f0f0;">
                            <th style="padding: 5px; border: 1px solid #ddd;">Banco</th>
                            <th style="padding: 5px; border: 1px solid #ddd;">Sucursales</th>
                            <th style="padding: 5px; border: 1px solid #ddd;">Rating</th>
                            <th style="padding: 5px; border: 1px solid #ddd;">Reseñas</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(stats_bancos)}
                    </tbody>
                </table>
            </div>
            """
            
            # Agregar círculo proporcional al número total de sucursales
            folium.Circle(
                location=[lat_center, lng_center],
                radius=total_sucursales * 150,
                popup=folium.Popup(popup_html, max_width=350),
                color='navy',
                fill=True,
                fillOpacity=0.2,
                weight=2
            ).add_to(mapa)
            
            # Agregar marcador central con nombre de alcaldía
            folium.Marker(
                location=[lat_center, lng_center],
                popup=alcaldia,
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 12px; color: navy; font-weight: bold;">{alcaldia}</div>',
                    icon_size=(100, 20),
                    icon_anchor=(50, 10)
                )
            ).add_to(mapa)
        
        mapa.save(archivo)
        print(f"Mapa comparativo por alcaldías guardado como: {archivo}")
        return mapa

# Ejemplo de uso completo
if __name__ == "__main__":
    # PASO 1: Configurar API key de Google Maps
    API_KEY = "TU_API_KEY_AQUI"
    
    # PASO 2: Crear instancia del mapeador multi-bancos
    mapper = MultiBankCDMXMapper(API_KEY)
    
    # PASO 3: Buscar sucursales de múltiples bancos (elige una estrategia)
    
    # Opción A: Solo Santander (original)
    mapper.buscar_todas_sucursales_cdmx(
        estrategia='alcaldias',
        bancos=['Santander']
    )
    
    # Opción B: Todos los bancos por alcaldías (recomendado)
    # mapper.buscar_todas_sucursales_cdmx(
    #     estrategia='alcaldias',
    #     bancos=['Santander', 'BBVA', 'Banorte']
    # )
    
    # Opción C: Por cuadrícula (más exhaustivo)
    # mapper.buscar_todas_sucursales_cdmx(
    #     estrategia='grid',
    #     bancos=['Santander', 'BBVA', 'Banorte'],
    #     radio=1500,      # Radio de búsqueda en metros
    #     tam_celda=2      # Tamaño de celda en km
    # )
    
    # Opción D: Estrategia mixta (más completo)
    # mapper.buscar_todas_sucursales_cdmx(
    #     estrategia='mixta',
    #     bancos=['Santander', 'BBVA', 'Banorte']
    # )
    
    # PASO 4: Crear mapas interactivos con nuevas funcionalidades
    print("\n🗺️ Creando mapas interactivos...")
    
    # Mapa principal con análisis de competencia y reseñas completas
    mapper.crear_mapa_interactivo_multibancos(
        archivo='mapa_multibancos_cdmx.html',
        incluir_analisis_competencia=True
    )
    
    # Mapa comparativo por alcaldías
    mapper.crear_mapa_alcaldias_comparativo(
        archivo='mapa_alcaldias_comparativo.html'
    )
    
    # PASO 5: Análisis de competencia detallado
    print("\n📊 Realizando análisis de competencia...")
    competencia = mapper.calcular_distancias_competencia(radio_km=1.0)
    
    if competencia:
        print(f"Encontradas {len(competencia)} sucursales con competencia cercana")
        # Mostrar las 5 zonas con mayor competencia
        competencia_sorted = sorted(competencia, key=lambda x: x['total_competidores'], reverse=True)
        print("\n🏆 Top 5 zonas con mayor competencia:")
        for i, comp in enumerate(competencia_sorted[:5]):
            sucursal = comp['sucursal_base']
            print(f"{i+1}. {sucursal['banco']} - {sucursal['nombre']}")
            print(f"   Competidores: {comp['total_competidores']}, Ventaja rating: {comp['ventaja_rating']}")
    
    # PASO 6: Análisis por zona
    print("\n🏛️ Generando análisis por zona...")
    analisis_zona = mapper.analizar_competencia_por_zona()
    
    if analisis_zona:
        dominancia = analisis_zona['dominancia_por_zona']
        print("\nDominancia por alcaldía:")
        print(dominancia[['Santander', 'BBVA', 'Banorte', 'banco_dominante']])
    
    # PASO 7: Guardar todos los datos y análisis
    print("\n💾 Guardando datos...")
    mapper.guardar_datos_multibancos()
    
    # PASO 8: Mostrar resumen final
    print(f"\n=== RESUMEN FINAL ===")
    total_todas = sum(len(sucursales) for sucursales in mapper.results.values())
    print(f"Total de sucursales encontradas: {total_todas}")
    
    for banco, sucursales in mapper.results.items():
        if sucursales:
            print(f"  - {banco}: {len(sucursales)} sucursales")
            df_banco = pd.DataFrame(sucursales)
            print(f"    Rating promedio: {df_banco['rating'].mean():.2f}")
            print(f"    Alcaldía con más sucursales: {df_banco['alcaldia'].value_counts().index[0]}")
    
    print("\n✅ Proceso completado. Revisa los archivos HTML generados para ver los mapas interactivos.")