# Política de tratamiento de Portes

## Regla oficial (Versión 1.0)

1. **Eliminación de línea PORTES**  
   - Cualquier línea de factura cuyo concepto sea “PORTES” o equivalente no se conserva como producto independiente.

2. **Reparto proporcional en bruto**  
   - El importe total de portes (Base + IVA) se reparte proporcionalmente entre las demás líneas de la factura.
   - El reparto se hace en función del **importe bruto** de cada línea (`Base_i × (1 + IVA_i)`), de modo que quien más pesa en la factura asume más parte de los portes.

3. **Descomposición según IVA propio**  
   - La parte de portes que le corresponde a cada línea se descompone según el IVA de esa línea:
     - `Base_prorrata_i = P_bruto_i / (1 + IVA_i)`
     - `IVA_prorrata_i  = P_bruto_i - Base_prorrata_i`
   - Luego se suman a los importes originales de la línea:
     - `Base_final_i = Base_original_i + Base_prorrata_i`
     - `IVA_final_i  = IVA_original_i + IVA_prorrata_i`

4. **Redondeo y ajuste**  
   - Todos los cálculos se redondean a 2 decimales.
   - Si el redondeo genera céntimos sobrantes o faltantes, el ajuste se hace en la línea de mayor base imponible.

5. **Flags de trazabilidad**  
   - En la columna `Observaciones` de cada línea que haya recibido parte de los portes se añade el flag:  
     - `PortesProrrateados`
   - Si hubo un ajuste de redondeo:  
     - `AjusteRedondeoPortes`

6. **Casos especiales**  
   - Si solo hay **una línea** en la factura: el porte completo se asigna a esa línea.  
   - Si hay **varias líneas PORTES**, se suman primero para formar un total único antes de repartir.

## Objetivo
- Garantizar que el **Total con IVA** de la factura procesada coincida exactamente con el original.  
- Evitar líneas artificiales de “PORTES” y distribuir su coste entre los artículos.

## Estado
- Esta política se aplicará en la CLI a partir de la implementación del módulo `portes_logic.py`.  
- Versión inicial documentada para su inclusión en el repositorio GitHub.
