-- Select para traer el saldo si se tiene una tarjeta

SELECT cu.cantidad_dinero 
FROM Cuenta cu, Tarjeta t
WHERE t.id_cuenta = cu.id_cuenta
AND t.id_cuenta = 1;

-- Update cantidad a retirar

UPDATE Cuenta cu
SET cu.cantidad_dinero = (cu.cantidad_dinero - 20000)
WHERE cu.id_cuenta = 1;

-- Query para insertar transaccion

INSERT INTO Transacciones (id_tarjeta, hora, fecha, tipo_transaccion, cant_dinero) VALUES (1, '6:00:00', '2017-02-05', 'Retiro', 20000)

-- Query para traer la transaccion id

SELECT t.id_transaccion FROM Transacciones t
WHERE t.id_tarjeta = 2;
