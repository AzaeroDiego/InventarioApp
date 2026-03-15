#!/usr/bin/env python
"""
Script de migración para agregar columnas de permisos a usuarios.
Agrega: has_permisos (Boolean), rol (String)
"""

import os
import sys
from app import create_app, db

def migrate_permisos():
    """Realizar migración de permisos en usuarios"""
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    
    with app.app_context():
        try:
            # Verificar si las columnas ya existen
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('usuarios')]
            
            has_permisos_exists = 'has_permisos' in columns
            rol_exists = 'rol' in columns
            
            if has_permisos_exists and rol_exists:
                print("✅ Las columnas de permisos ya existen en la tabla usuarios.")
                return True
            
            # Conexión a base de datos
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            try:
                # Agregar columna has_permisos si no existe
                if not has_permisos_exists:
                    print("📝 Agregando columna 'has_permisos' a la tabla usuarios...")
                    cursor.execute("""
                        ALTER TABLE usuarios 
                        ADD COLUMN has_permisos BOOLEAN DEFAULT 1 NOT NULL
                    """)
                    connection.commit()
                    print("✅ Columna 'has_permisos' agregada exitosamente.")
                    print("   Todos los usuarios existentes tienen permisos = SI")
                
                # Agregar columna rol si no existe
                if not rol_exists:
                    print("📝 Agregando columna 'rol' a la tabla usuarios...")
                    cursor.execute("""
                        ALTER TABLE usuarios 
                        ADD COLUMN rol VARCHAR(50) DEFAULT 'vendedor' NOT NULL
                    """)
                    connection.commit()
                    print("✅ Columna 'rol' agregada exitosamente.")
                    print("   Todos los usuarios existentes tienen rol = 'vendedor'")
                
                # Agregar columna fecha_actualizacion si no existe
                fecha_act = 'fecha_actualizacion' in columns
                if not fecha_act:
                    print("📝 Agregando columna 'fecha_actualizacion' a la tabla usuarios...")
                    cursor.execute("""
                        ALTER TABLE usuarios 
                        ADD COLUMN fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
                    """)
                    connection.commit()
                    print("✅ Columna 'fecha_actualizacion' agregada exitosamente.")
                
                return True
                
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("✅ Las columnas ya existen en la base de datos.")
                    return True
                else:
                    print(f"❌ Error: {str(e)}")
                    connection.rollback()
                    return False
            finally:
                cursor.close()
                connection.close()
            
        except Exception as e:
            print(f"❌ Error durante la migración: {str(e)}")
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("MIGRACIÓN DE PERMISOS - AGREGAR COLUMNAS DE USUARIOS")
    print("=" * 60)
    print()
    
    if migrate_permisos():
        print()
        print("✅ Migración de permisos completada exitosamente.")
        print()
        print("PRÓXIMOS PASOS:")
        print("1. Ejecuta: python run.py")
        print("2. Ve a Administración → Gestión de Usuarios")
        print("3. Verifica permisos de cada usuario (SI/NO)")
        print()
        sys.exit(0)
    else:
        print()
        print("❌ Error en la migración.")
        sys.exit(1)
