CREATE TABLE Rol (
    id_rol INT PRIMARY KEY,
    nombre VARCHAR2(50) NOT NULL
);


CREATE TABLE Cliente (
    codigo_cliente INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    departamento VARCHAR(50),
    municipio VARCHAR(50),
    calle VARCHAR(100),
    direccion VARCHAR(150),
    email VARCHAR(100),
    contrasena VARCHAR(255) NOT NULL,
    id_rol INT,
    FOREIGN KEY (id_rol) REFERENCES Rol(id_rol)

);
CREATE TABLE Categoria (
    codigo_categoria INT PRIMARY KEY,
    iva DECIMAL(6,2) NOT NULL CHECK (iva >= 0),
    utilidad DECIMAL(12,2) NOT NULL CHECK (utilidad >= 0)
);
CREATE TABLE Producto (
    codigo INT PRIMARY KEY,
    descripcion VARCHAR(255),
    nombre VARCHAR(100) NOT NULL,
    valor_adquisicion DECIMAL(12,2) NOT NULL CHECK (valor_adquisicion >= 0),
    valor_venta DECIMAL(12,2),
    codigo_categoria INT NOT NULL,
    FOREIGN KEY (codigo_categoria) REFERENCES Categoria(codigo_categoria)
);

CREATE TABLE Venta (
    id_venta INT PRIMARY KEY,
    codigo_venta VARCHAR(20) NOT NULL,
    estado_venta VARCHAR(20) NOT NULL,
    fecha DATE NOT NULL,
    total_neto DECIMAL(12,2),
    estado_credito VARCHAR(20),
    tipo_venta VARCHAR(20) NOT NULL,
    total_bruto DECIMAL(12,2),
    iva_total DECIMAL(12,2),
    codigo_cliente INT NOT NULL,
    FOREIGN KEY (codigo_cliente) REFERENCES Cliente(codigo_cliente)
);


CREATE TABLE DetalleVentaProducto (
    id_venta INT NOT NULL,
    codigo_producto INT NOT NULL,
    PRIMARY KEY (id_venta, codigo_producto),
    FOREIGN KEY (id_venta) REFERENCES Venta(id_venta),
    FOREIGN KEY (codigo_producto) REFERENCES Producto(codigo)
);


CREATE TABLE Credito (
    id_credito INT PRIMARY KEY,
    cuota_inicial DECIMAL(12,2) NOT NULL CHECK (cuota_inicial >= 0),
    saldo_financiado DECIMAL(12,2) NOT NULL CHECK (saldo_financiado >= 0),
    interes DECIMAL(6,2) NOT NULL CHECK (interes >= 0),
    plazo_meses INT NOT NULL CHECK (plazo_meses > 0),
    id_venta INT UNIQUE NOT NULL,
    FOREIGN KEY (id_venta) REFERENCES Venta(id_venta)
);


CREATE TABLE Cuota (
    id_pago INT PRIMARY KEY,
    n_cuota INT NOT NULL CHECK (n_cuota > 0),
    estado VARCHAR(20) NOT NULL,
    valor_cuota DECIMAL(12,2) NOT NULL CHECK (valor_cuota >= 0),
    fecha_vencimiento DATE NOT NULL,
    id_credito INT NOT NULL,
    FOREIGN KEY (id_credito) REFERENCES Credito(id_credito)
);
CREATE TABLE Pago (
    codigo_pago INT PRIMARY KEY,
    fecha_pago DATE NOT NULL,
    estado VARCHAR(20) NOT NULL,
    valor DECIMAL(12,2) NOT NULL CHECK (valor >= 0),
    id_pago INT UNIQUE NOT NULL,
    FOREIGN KEY (id_pago) REFERENCES Cuota(id_pago)
);
