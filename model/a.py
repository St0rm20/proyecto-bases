"""
Script de diagnóstico para verificar el estado de créditos y cuotas
"""

from model.credito import Credito
from model.cuota import Cuota
from model.venta import Venta


def diagnosticar_creditos():
    """Verifica el estado actual de los créditos en la base de datos"""

    credito_controller = Credito()
    cuota_controller = Cuota()
    venta_controller = Venta()

    print("=" * 80)
    print("DIAGNÓSTICO DE CRÉDITOS")
    print("=" * 80)

    # 1. Verificar todos los créditos
    print("\n1. TODOS LOS CRÉDITOS EN LA BASE DE DATOS:")
    print("-" * 80)

    sql_todos = """
                SELECT c.id_credito, \
                       c.id_venta, \
                       v.codigo_venta,
                       v.estado_venta, \
                       v.estado_credito, \
                       v.tipo_venta
                FROM Credito c
                         INNER JOIN Venta v ON c.id_venta = v.id_venta
                ORDER BY c.id_credito \
                """

    todos_creditos = credito_controller.db.execute_query(sql_todos)

    if not todos_creditos:
        print("❌ No hay créditos en la base de datos")
    else:
        for credito in todos_creditos:
            id_cred, id_venta, cod_venta, est_venta, est_credito, tipo_venta = credito
            print(f"\nCrédito ID: {id_cred}")
            print(f"  └─ Venta: {cod_venta} (ID: {id_venta})")
            print(f"  └─ Tipo Venta: {tipo_venta}")
            print(f"  └─ Estado Venta: {est_venta}")
            print(f"  └─ Estado Crédito: {est_credito or 'NULL ⚠️'}")

            # Verificar cuotas
            sql_cuotas = """
                         SELECT COUNT(*)                                              as total,
                                SUM(CASE WHEN estado = 'Pagada' THEN 1 ELSE 0 END)    as pagadas,
                                SUM(CASE WHEN estado = 'Pendiente' THEN 1 ELSE 0 END) as pendientes
                         FROM Cuota
                         WHERE id_credito = :id_credito \
                         """
            cuotas_info = credito_controller.db.execute_query(
                sql_cuotas,
                {'id_credito': id_cred}
            )

            if cuotas_info and cuotas_info[0]:
                total, pagadas, pendientes = cuotas_info[0]
                print(f"  └─ Cuotas: {pagadas or 0}/{total or 0} pagadas, {pendientes or 0} pendientes")

                if pendientes and pendientes > 0 and est_credito != 'Activo':
                    print(f"  └─ ⚠️ PROBLEMA: Tiene cuotas pendientes pero estado_credito es '{est_credito}'")
            else:
                print(f"  └─ ⚠️ No tiene cuotas registradas")

    # 2. Verificar créditos que el sistema considera "activos"
    print("\n\n2. CRÉDITOS QUE EL SISTEMA CONSIDERA ACTIVOS:")
    print("-" * 80)

    creditos_activos = credito_controller.obtener_creditos_activos()

    if not creditos_activos:
        print("❌ No se encontraron créditos activos")
    else:
        print(f"✅ Se encontraron {len(creditos_activos)} crédito(s) activo(s):")
        for credito in creditos_activos:
            print(f"  - Crédito ID: {credito.id_credito}, Venta ID: {credito.id_venta}")

    # 3. Sugerencias de corrección
    print("\n\n3. SUGERENCIAS DE CORRECCIÓN:")
    print("-" * 80)

    sql_problemas = """
                    SELECT c.id_credito, c.id_venta, v.codigo_venta, v.estado_credito
                    FROM Credito c
                             INNER JOIN Venta v ON c.id_venta = v.id_venta
                    WHERE EXISTS (SELECT 1 \
                                  FROM Cuota cu \
                                  WHERE cu.id_credito = c.id_credito \
                                    AND cu.estado != 'Pagada')
                      AND (v.estado_credito IS NULL OR v.estado_credito != 'Activo') \
                    """

    creditos_problema = credito_controller.db.execute_query(sql_problemas)

    if creditos_problema:
        print("⚠️ Créditos con cuotas pendientes pero sin estado_credito = 'Activo':")
        for cred in creditos_problema:
            id_cred, id_venta, cod_venta, est_credito = cred
            print(f"\n  Crédito #{id_cred} (Venta: {cod_venta})")
            print(f"    Estado actual: {est_credito or 'NULL'}")
            print(f"    SQL para corregir:")
            print(f"    UPDATE Venta SET estado_credito = 'Activo' WHERE id_venta = {id_venta};")
    else:
        print("✅ No se encontraron problemas de estado_credito")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    diagnosticar_creditos()