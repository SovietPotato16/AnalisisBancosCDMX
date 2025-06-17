#!/usr/bin/env python3
"""
Script completo de instalación y ejecución para el Analizador Multi-Bancos CDMX
Incluye manejo de entorno virtual, instalación de dependencias y ejecución de Streamlit
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def check_python_version():
    """Verifica la versión de Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor} detectado")
    return True

def setup_virtual_environment():
    """Configura el entorno virtual"""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print("🔧 Creando entorno virtual...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", "venv"])
            print("✅ Entorno virtual creado exitosamente!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creando entorno virtual: {e}")
            return False
    else:
        print("✅ Entorno virtual ya existe")
    
    return True

def get_venv_python():
    """Obtiene la ruta del Python del entorno virtual"""
    if platform.system() == "Windows":
        return Path("venv/Scripts/python.exe")
    else:
        return Path("venv/bin/python")

def get_venv_pip():
    """Obtiene la ruta del pip del entorno virtual"""
    if platform.system() == "Windows":
        return Path("venv/Scripts/pip")
    else:
        return Path("venv/bin/pip")

def install_requirements():
    """Instala las dependencias en el entorno virtual"""
    pip_path = get_venv_pip()
    
    print("📦 Instalando dependencias...")
    
    # Lista de paquetes críticos
    critical_packages = [
        "streamlit>=1.28.0",
        "pandas>=2.0.0",
        "plotly>=5.15.0",
        "folium>=0.15.0",
        "streamlit-folium>=0.13.0",
        "googlemaps>=4.10.0",
        "geopy>=2.4.0",
        "numpy>=1.25.0",
        "textblob>=0.17.1",
        "wordcloud>=1.9.2",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "openpyxl>=3.1.0"
    ]
    
    try:
        # Actualizar pip primero
        subprocess.check_call([str(pip_path), "install", "--upgrade", "pip"])
        
        # Instalar paquetes uno por uno para mejor control de errores
        for package in critical_packages:
            print(f"   📥 Instalando {package.split('>=')[0]}...")
            try:
                subprocess.check_call([str(pip_path), "install", package], 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️  Error instalando {package}: {e}")
                # Intentar versión más básica
                basic_package = package.split('>=')[0]
                print(f"   🔄 Intentando versión básica de {basic_package}...")
                subprocess.check_call([str(pip_path), "install", basic_package])
        
        print("✅ Todas las dependencias instaladas exitosamente!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def download_nltk_data():
    """Descarga datos necesarios para NLTK/TextBlob"""
    python_path = get_venv_python()
    
    print("📚 Descargando datos de procesamiento de lenguaje natural...")
    try:
        subprocess.check_call([
            str(python_path), "-c", 
            "import textblob; textblob.download_corpora()"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Datos de NLP descargados!")
    except:
        print("⚠️  Advertencia: No se pudieron descargar datos de NLP")

def check_data_files():
    """Verifica si existen archivos de datos"""
    data_files = list(Path(".").glob("multibancos_cdmx_*.csv"))
    if not data_files:
        print("⚠️  No se encontraron archivos de datos!")
        print("💡 Asegúrate de ejecutar V1Extractor.py primero para generar los datos")
        return False
    
    latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
    print(f"📊 Archivo de datos encontrado: {latest_file}")
    return True

def run_streamlit():
    """Ejecuta la aplicación Streamlit"""
    python_path = get_venv_python()
    
    print("🚀 Iniciando aplicación Streamlit...")
    print("📱 La aplicación se abrirá en tu navegador web")
    print("🌐 URL: http://localhost:8501")
    print("⚠️  Presiona Ctrl+C para detener la aplicación")
    print("-" * 50)
    
    try:
        subprocess.run([
            str(python_path), "-m", "streamlit", "run", 
            "streamlit_analyzer.py", 
            "--server.address", "localhost",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Aplicación cerrada por el usuario")
    except Exception as e:
        print(f"❌ Error ejecutando Streamlit: {e}")

def show_banner():
    """Muestra banner de inicio"""
    print("=" * 60)
    print("🏦 ANALIZADOR MULTI-BANCOS CDMX - INSTALADOR AUTOMÁTICO")
    print("=" * 60)
    print("📊 Dashboard avanzado con análisis de reseñas y competencia")
    print("🎯 Tema oscuro, visualizaciones interactivas y más")
    print("💫 Powered by Streamlit + Plotly + AI")
    print("-" * 60)

def main():
    """Función principal"""
    show_banner()
    
    # Verificar Python
    if not check_python_version():
        return
    
    # Configurar entorno virtual
    if not setup_virtual_environment():
        return
    
    # Instalar dependencias
    if not install_requirements():
        return
    
    # Descargar datos de NLP
    download_nltk_data()
    
    # Verificar archivos de datos
    if not check_data_files():
        response = input("\n¿Quieres ejecutar el extractor de datos primero? (y/n): ")
        if response.lower() == 'y':
            python_path = get_venv_python()
            print("🔄 Ejecutando extractor de datos...")
            try:
                subprocess.run([str(python_path), "V1Extractor.py"])
            except Exception as e:
                print(f"❌ Error ejecutando extractor: {e}")
                return
        else:
            print("❌ No se puede continuar sin datos")
            print("💡 Ejecuta V1Extractor.py para generar los datos necesarios")
            return
    
    # Ejecutar Streamlit
    print("\n🎉 ¡Todo listo!")
    input("Presiona Enter para iniciar la aplicación...")
    run_streamlit()

if __name__ == "__main__":
    main() 