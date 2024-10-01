create table ventas_contables(
	id serial primary key not null,
	id_pedido int not null,
	id_usuario int not null,
	fecha_creacion date not null,
	total numeric(10,2) not null
);

mysql, ventas:
ALTER TABLE pedidos ADD COLUMN registrado_en_contable BOOLEAN DEFAULT FALSE;