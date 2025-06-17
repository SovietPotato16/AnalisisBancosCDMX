#!/usr/bin/env python3
"""
Script de lanzamiento para el analizador de bancos CDMX
Maneja la instalación de dependencias y ejecuta la aplicación Streamlit
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Instala las dependencias requeridas"""
    print("🔧 Instalando dependencias...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencias instaladas exitosamente!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def check_data_files():
    """Verifica si existen archivos de datos"""
    data_files = list(Path(".").glob("multibancos_cdmx_*.csv"))
    if not data_files:
        print("⚠️  No se encontraron archivos de datos!")
        print("💡 Ejecuta primero V1Extractor.py para generar los datos")
        return False
    
    latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
    print(f"📊 Archivo de datos encontrado: {latest_file}")
    return True

def run_streamlit():
    """Ejecuta la aplicación Streamlit"""
    print("🚀 Iniciando aplicación Streamlit...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_analyzer.py"])
    except KeyboardInterrupt:
        print("\n👋 Aplicación cerrada por el usuario")
    except Exception as e:
        print(f"❌ Error ejecutando Streamlit: {e}")

def main():
    """Función principal"""
    print("🏦 Analizador Multi-Bancos CDMX")
    print("=" * 40)
    
    # Verificar archivos de datos
    if not check_data_files():
        response = input("\n¿Quieres ejecutar el extractor de datos primero? (y/n): ")
        if response.lower() == 'y':
            print("🔄 Ejecutando extractor de datos...")
            try:
                subprocess.run([sys.executable, "V1Extractor.py"])
            except Exception as e:
                print(f"❌ Error ejecutando extractor: {e}")
                return
        else:
            print("❌ No se puede continuar sin datos")
            return
    
    # Instalar dependencias
    if not install_requirements():
        return
    
    # Ejecutar Streamlit
    run_streamlit()

if __name__ == "__main__":
    main() 