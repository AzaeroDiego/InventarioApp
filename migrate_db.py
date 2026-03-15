#!/usr/bin/env python
"""
Script de migración para agregar columna 'se_vende' a productos existentes.
Sin perder datos, mantiene historial intacto.
"""

import os
import sys
from app import create_app, db
from app.models import Producto

def migrate_database():
    """Realizar migración de base de datos"""
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    
    with app.app_context():
        try:
            # Verificar si la columna ya existe
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('productos')]
            
            if 'se_vende' in columns:
                print("✅ La columna 'se_vende' ya existe en la tabla productos.")
                return True
            
            # Agregar la columna si no existe
            print("📝 Agregando columna 'se_vende' a la tabla productos...")
            
            # Ejecutar el ALTER TABLE
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            try:
                # SQLite
                cursor.execute("ALTER TABLE productos ADD COLUMN se_vende BOOLEAN DEFAULT 1")
                connection.commit()
                print("✅ Columna 'se_vende' agregada exitosamente.")
                print("   Todos los productos existentes están marcados como 'SE VENDE = SI'")
                
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("✅ La columna ya existe en la base de datos.")
                else:
                    # Intentar con sintaxis SQLite alternativa
                    try:
                        cursor.execute("""
                            ALTER TABLE productos 
                            ADD COLUMN se_vende BOOLEAN NOT NULL DEFAULT 1
                        """)
                        connection.commit()
                        print("✅ Columna 'se_vende' agregada exitosamente.")
                    except Exception as e2:
                        print(f"❌ Error: {str(e2)}")
                        connection.rollback()
                        return False
            finally:
                cursor.close()
                connection.close()
            
            return True
            
        except Exception as e:
            print(f"❌ Error durante la migración: {str(e)}")
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("MIGRACIÓN DE BASE DE DATOS - AGREGAR 'SE_VENDE'")
    print("=" * 60)
    print()
    
    if migrate_database():
        print()
        print("✅ Migración completada exitosamente.")
        print()
        print("PRÓXIMOS PASOS:")
        print("1. Ejecuta: python run.py")
        print("2. Ve a Editar Productos")
        print("3. Marca cuáles productos SE VENDEN y cuáles son INGREDIENTES")
        print()
        sys.exit(0)
    else:
        print()
        print("❌ Error en la migración.")
        sys.exit(1)
