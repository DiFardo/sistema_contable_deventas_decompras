--ventas:
SELECT 
    dp.id_pedido,
    p.id_usuario,
    CASE 
        WHEN u.apellido IS NOT NULL AND u.apellido != '' 
            THEN CONCAT(u.nombre, ' ', u.apellido)
        ELSE u.nombre
    END AS usuario,
    u.tipo_documento,
    u.numero_documento,
    pa.fecha_pago AS fecha, 
    ROUND(SUM(dp.cantidad * pr.precio) / 1.18, 2) AS sub_sin_igv,
    ROUND(SUM(dp.cantidad * pr.precio) - (SUM(dp.cantidad * pr.precio) / 1.18), 2) AS igv,
    ROUND(SUM(dp.cantidad * pr.precio), 2) AS total_con_igv,
    cp.tipo_comprobante,
    cp.serie_comprobante,
    cp.numero_comprobante
FROM detalles_pedido dp
JOIN pedidos p ON dp.id_pedido = p.id_pedido
JOIN usuarios u ON p.id_usuario = u.id_usuario
JOIN productos pr ON dp.id_producto = pr.id_producto
JOIN pagos pa ON pa.id_pedido = p.id_pedido
JOIN comprobante_pago cp ON cp.id_pedido = p.id_pedido  
WHERE p.estado = 'pagado' AND p.registrado_en_contable = FALSE
GROUP BY cp.serie_comprobante, cp.numero_comprobante, dp.id_pedido, p.id_usuario, usuario, u.tipo_documento, u.numero_documento, pa.fecha_pago, cp.tipo_comprobante
ORDER BY pa.fecha_pago, cp.serie_comprobante, cp.numero_comprobante;

--compras:
SELECT 
    c.id_compra,
    c.id_usuario,
    CASE 
        WHEN u.apellido IS NOT NULL AND u.apellido != '' 
            THEN CONCAT(u.nombre, ' ', u.apellido)
        ELSE u.nombre
    END AS usuario,
    c.id_proveedor,
    p.nombre_proveedor,
    p.tipo_documento,
    p.numero_documento,
    c.fecha_compra AS fecha,
    ROUND(SUM(dc.cantidad * im.precio_unitario) / 1.18, 2) AS sub_sin_igv,
    ROUND(SUM(dc.cantidad * im.precio_unitario) - (SUM(dc.cantidad * im.precio_unitario) / 1.18), 2) AS igv,
    ROUND(SUM(dc.cantidad * im.precio_unitario), 2) AS subtotal,
    c.tipo_comprobante,
    c.serie_comprobante,
    c.numero_comprobante
FROM detalles_compra dc
JOIN compras c ON dc.id_compra = c.id_compra
JOIN usuarios u ON c.id_usuario = u.id_usuario
JOIN proveedores p ON c.id_proveedor = p.id_proveedor
JOIN insumos_materiales im ON dc.id_insumo = im.id_insumo
WHERE c.estado = 'pagado' AND c.registrado_en_contable = FALSE
GROUP BY c.id_compra, c.id_usuario, usuario, c.id_proveedor, p.nombre_proveedor, 
         p.tipo_documento, p.numero_documento, c.fecha_compra, 
         c.tipo_comprobante, c.serie_comprobante, c.numero_comprobante
ORDER BY c.fecha_compra, c.serie_comprobante, c.numero_comprobante;