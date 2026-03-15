#!/usr/bin/env python
"""
SCRIPT MAESTRO DE DESPLIEGUE
============================
Ejecuta TODOS los cambios de una sola vez.
Sin perder datos. Seguro. Automatizado.

Uso:
    python deploy_all.py [ambiente]
    
Ejemplos:
    python deploy_all.py development   (local)
    python deploy_all.py production    (pythonanywhere)
"""

import os
import sys
import subprocess
from datetime import datetime

class Deployer:
    """Gestor de despliegue automático"""
    
    def __init__(self, ambiente='development'):
        self.ambiente = ambiente
        self.inicio = datetime.now()
        self.pasos_completados = []
        self.errores = []
    
    def log(self, mensaje, tipo='INFO'):
        """Registrar mensaje con timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        emojis = {
            'INFO': '📝',
            'SUCCESS': '✅',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'STEP': '📍'
        }
        emoji = emojis.get(tipo, '•')
        print(f"{emoji} [{timestamp}] {mensaje}")
    
    def paso(self, numero, descripcion):
        """Mostrar paso actual"""
        self.log(f"PASO {numero}: {descripcion}", 'STEP')
    
    def ejecutar_comando(self, comando, descripcion):
        """Ejecutar comando y capturar resultado"""
        try:
            self.log(f"Ejecutando: {descripcion}...", 'INFO')
            resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
            
            if resultado.returncode == 0:
                self.log(f"✓ {descripcion} completado", 'SUCCESS')
                self.pasos_completados.append(descripcion)
                return True
            else:
                error_msg = resultado.stderr or resultado.stdout
                self.log(f"✗ Error en {descripcion}: {error_msg}", 'ERROR')
                self.errores.append(f"{descripcion}: {error_msg}")
                return False
        except Exception as e:
            self.log(f"✗ Excepción: {str(e)}", 'ERROR')
            self.errores.append(str(e))
            return False
    
    def deploy(self):
        """Ejecutar despliegue completo"""
        print("\n" + "="*70)
        print("🚀 SCRIPT MAESTRO DE DESPLIEGUE - INVENTARIO APP")
        print("="*70)
        print(f"Ambiente: {self.ambiente.upper()}")
        print(f"Inicio: {self.inicio.strftime('%d/%m/%Y %H:%M:%S')}")
        print("="*70 + "\n")
        
        try:
            # PASO 1: BACKUP
            self.paso(1, "CREAR BACKUP DE BASE DE DATOS")
            if not self.ejecutar_comando(
                "python backup_restore.py export",
                "Backup de datos"
            ):
                self.log("⚠️ El backup falló pero continuamos (precaución recomendada)", 'WARNING')
            
            # PASO 2: MIGRACIÓN SE_VENDE
            self.paso(2, "MIGRAR COLUMNA 'SE_VENDE' EN PRODUCTOS")
            if not self.ejecutar_comando(
                "python migrate_db.py",
                "Migración de productos"
            ):
                self.log("❌ Migración 1 falló - abortando despliegue", 'ERROR')
                return False
            
            # PASO 3: MIGRACIÓN PERMISOS
            self.paso(3, "MIGRAR COLUMNAS DE PERMISOS EN USUARIOS")
            if not self.ejecutar_comando(
                "python migrate_permisos.py",
                "Migración de usuarios"
            ):
                self.log("❌ Migración 2 falló - abortando despliegue", 'ERROR')
                return False
            
            # PASO 4: VERIFICACIÓN DE BASE DE DATOS
            self.paso(4, "VERIFICAR BASE DE DATOS")
            if not self._verificar_bd():
                self.log("⚠️ Verificación de BD con advertencias", 'WARNING')
            
            # PASO 5: LIMPIAR CACHÉ (si es pythonanywhere)
            if self.ambiente == 'production':
                self.paso(5, "RECARGAR APLICACIÓN EN PYTHONANYWHERE")
                self._recargar_pythonanywhere()
            else:
                self.paso(5, "VERIFICACIÓN LOCAL COMPLETADA")
            
            return True
            
        except Exception as e:
            self.log(f"Error en despliegue: {str(e)}", 'ERROR')
            self.errores.append(str(e))
            return False
    
    def _verificar_bd(self):
        """Verificar que la BD tenga los cambios"""
        try:
            from app import create_app, db
            app = create_app(self.ambiente)
            
            with app.app_context():
                inspector = db.inspect(db.engine)
                tablas = inspector.get_table_names()
                
                # Verificar tabla productos
                if 'productos' in tablas:
                    cols_prod = [col['name'] for col in inspector.get_columns('productos')]
                    if 'se_vende' in cols_prod:
                        self.log("✓ Columna 'se_vende' detectada en productos", 'SUCCESS')
                    else:
                        self.log("✗ Columna 'se_vende' NO detectada", 'ERROR')
                        return False
                
                # Verificar tabla usuarios
                if 'usuarios' in tablas:
                    cols_users = [col['name'] for col in inspector.get_columns('usuarios')]
                    if 'has_permisos' in cols_users and 'rol' in cols_users:
                        self.log("✓ Columnas de permisos detectadas en usuarios", 'SUCCESS')
                    else:
                        self.log("✗ Columnas de permisos NO detectadas", 'ERROR')
                        return False
                
                return True
        except Exception as e:
            self.log(f"Error verificando BD: {str(e)}", 'ERROR')
            return False
    
    def _recargar_pythonanywhere(self):
        """Instruir para recargar pythonanywhere"""
        print("\n" + "⚠️ "*20)
        print("ACCIÓN MANUAL REQUERIDA - PYTHONANYWHERE")
        print("⚠️ "*20)
        print("""
En PythonAnywhere Dashboard:
1. Ve a la sección "Web"
2. Haz clic en el botón VERDE "Reload"
3. Espera 30-60 segundos a que reinicie
4. Verifica que la app funcione

O por SSH (si tienes acceso):
touch /var/www/azaerodiego_pythonanywhere_com_wsgi.py
        """)
    
    def resumen(self):
        """Mostrar resumen final"""
        duracion = datetime.now() - self.inicio
        
        print("\n" + "="*70)
        print("📊 RESUMEN DE DESPLIEGUE")
        print("="*70)
        print(f"Duración total: {duracion.total_seconds():.1f} segundos")
        print(f"Pasos completados: {len(self.pasos_completados)}")
        print(f"Errores encontrados: {len(self.errores)}")
        
        if self.pasos_completados:
            print("\n✅ COMPLETADOS:")
            for paso in self.pasos_completados:
                print(f"   ✓ {paso}")
        
        if self.errores:
            print("\n❌ ERRORES:")
            for error in self.errores:
                print(f"   ✗ {error}")
        
        print("\n" + "="*70)
        
        if not self.errores:
            print("🎉 ¡DESPLIEGUE EXITOSO! Todos los cambios aplicados correctamente.")
            print("\nPróximos pasos:")
            print("1. Verifica que la app esté funcionando")
            print("2. Abre Dashboard → Administración → Gestión de Usuarios")
            print("3. Prueba editar permisos de un usuario")
            print("4. Intenta registrar una venta (verifica columna 'Se Vende')")
        else:
            print("⚠️  Algunos pasos fallaron. Revisa los errores arriba.")
        
        print("="*70 + "\n")
        
        return len(self.errores) == 0

def main():
    """Función principal"""
    ambiente = sys.argv[1].lower() if len(sys.argv) > 1 else 'development'
    
    if ambiente not in ['development', 'production']:
        print("❌ Ambiente inválido. Usa 'development' o 'production'")
        sys.exit(1)
    
    deployer = Deployer(ambiente)
    
    # Confirmar antes de ejecutar
    print(f"\n⚠️  Iniciarás despliegue en ambiente: {ambiente.upper()}")
    print("Esto ejecutará:")
    print("  1. Backup de datos")
    print("  2. Migración de 'se_vende' en productos")
    print("  3. Migración de permisos en usuarios")
    print("  4. Verificación de BD")
    
    confirmacion = input("\n¿Continuar? (si/no): ").lower()
    if confirmacion not in ['si', 'yes', 's', 'y']:
        print("❌ Despliegue cancelado.")
        sys.exit(0)
    
    # Ejecutar despliegue
    exito = deployer.deploy()
    deployer.resumen()
    
    sys.exit(0 if exito else 1)

if __name__ == '__main__':
    main()
