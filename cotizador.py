import pandas as pd
from datetime import datetime

ARCHIVO_EXCEL = 'Lista_Precios_Octubre.xlsx'

def cargar_catalogo():
    # Lee la hoja 'Lista Completa' saltando el título de la fila 1
    df = pd.read_excel(ARCHIVO_EXCEL, sheet_name='Lista Completa', skiprows=1)
    # Limpiamos espacios extra por si acaso
    df['N°'] = df['N°'].astype(str).str.strip()
    return df

def generar_cotizacion():
    df = cargar_catalogo()
    pedido = []
    
    print("=== GENERADOR DE COTIZACIONES (ELECTRODOMÉSTICOS) ===")
    cliente = input("Nombre del cliente: ").strip()
    
    print("\nTipo de pago:")
    print("[1] Precio Efectivo")
    print("[2] Precio Tarjeta (3 Meses)")
    tipo_pago = input("Elige una opción (1 o 2): ").strip()
    
    es_tarjeta = (tipo_pago == '2')
    columna_precio = 'PRECIO T-3 MESES ($)' if es_tarjeta else 'PRECIO EFECTIVO ($)'
    etiqueta_pago = "Tarjeta (3 cuotas sin intereses)" if es_tarjeta else "Efectivo / Transferencia"

    while True:
        print("\n-----------------------------------------")
        accion = input("Escribe una palabra para buscar (ej. 'tv', 'indurama'), el N° de código, o 'fin' para terminar: ").strip()
        
        if accion.lower() == 'fin':
            break
            
        # Si escribe un número exacto que está en la columna N°
        if accion in df['N°'].values:
            fila = df[df['N°'] == accion].iloc[0]
            cantidad = int(input(f"Cantidad de '{fila['PRODUCTO / DESCRIPCIÓN']}' (${fila[columna_precio]:.2f} c/u): "))
            subtotal = fila[columna_precio] * cantidad
            pedido.append({
                'nombre': fila['PRODUCTO / DESCRIPCIÓN'],
                'cantidad': cantidad,
                'precio_unit': fila[columna_precio],
                'subtotal': subtotal
            })
            print(f"✅ Agregado: {cantidad}x {fila['PRODUCTO / DESCRIPCIÓN']}")
        else:
            # Buscar por coincidencia de texto en el nombre o categoría
            resultados = df[
                df['PRODUCTO / DESCRIPCIÓN'].str.contains(accion, case=False, na=False) |
                df['CATEGORÍA'].str.contains(accion, case=False, na=False)
            ]
            if resultados.empty:
                print("❌ No se encontraron productos con esa búsqueda.")
            else:
                print(f"\n🔍 Resultados para '{accion}':")
                for _, row in resultados.iterrows():
                    print(f"  [N° {row['N°']}] {row['PRODUCTO / DESCRIPCIÓN']} -> ${row[columna_precio]:.2f}")
                print("💡 Ahora ingresa el N° del producto que quieres agregar.")

    if not pedido:
        print("No agregaste productos. Saliendo...")
        return

    # Armar el texto final para WhatsApp
    fecha = datetime.now().strftime("%d/%m/%Y")
    total = sum(item['subtotal'] for item in pedido)
    
    mensaje = f"""*COTIZACIÓN COMERCIAL* 📄
*Fecha:* {fecha}
*Cliente:* {cliente}
*Forma de pago:* {etiqueta_pago}
-----------------------------------
*Detalle de productos:*
"""
    for item in pedido:
        mensaje += f"▪️ {item['cantidad']}x {item['nombre']} (${item['precio_unit']:.2f} c/u) = *${item['subtotal']:.2f}*\n"
        
    mensaje += f"""-----------------------------------
*TOTAL A PAGAR: ${total:.2f}*"""

    if es_tarjeta:
        cuota = total / 3
        mensaje += f"\n*(3 cuotas mensuales de ${cuota:.2f})*"

    mensaje += """

_Precios incluyen IVA. Cotización válida por 48 horas._
¡Quedo atento a tu confirmación para coordinar la entrega! 🤝"""

    print("\n" + "="*45)
    print("COPIA Y PEGA ESTO EN WHATSAPP:")
    print("="*45)
    print(mensaje)

if __name__ == "__main__":
    generar_cotizacion()