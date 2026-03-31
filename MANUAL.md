# Manual de Usuario - Sistema de Gestión de Condominio

## Acceso al Sistema

1. Abrir navegador e ir a: `http://192.168.22.205:5000`
2. Ingresar usuario y contraseña

## Roles y Permisos

| Rol | Descripción |
|-----|-------------|
| **Conserje** | Registra visitas, encomiendas y estacionamiento |
| **Supervisor** | Todo lo anterior + gestiona departamentos |
| **Admin** | Acceso total incluyendo gestión de usuarios |

---

## 1. Registro de Visitas

### Registrar nueva visita
1. Ir a **Visitas** en el menú
2. Click en **+ Nueva Visita**
3. Completar:
   - **Nombre completo**: Nombre del visitante
   - **DNI**: Número de documento (opcional)
   - **Departamento que visita**: Seleccionar de la lista
   - **Motivo**: Ej: Visita familiar, Delivery, etc.
4. Click en **Registrar Visita**

### Registrar salida
1. En la lista de visitas, buscar la visita activa
2. Click en **Registrar Salida**

### Filtrar visitas
- **Todas**: Ver todas las visitas
- **Activas**: Solo visitas dentro del edificio
- **Cerradas**: Visitas ya finalizadas

---

## 2. Registro de Encomiendas

### Registrar encomienda
1. Ir a **Encomiendas** en el menú
2. Click en **+ Nueva Encomienda**
3. Completar:
   - **Departamento destinatario**: Seleccionar
   - **Remitente**: Quién envía (opcional)
   - **Descripción**: Ej: Paquete mediano, sobre, caja
4. Click en **Registrar Encomienda**

### Registrar retiro
1. En la lista, buscar encomienda pendiente
2. Click en **Registrar Retiro**
3. Ingresar **quién retira** el paquete
4. La fecha/hora se registra automáticamente

### Filtrar encomiendas
- **Todas**: Ver todas
- **Pendientes**: No retiradas
- **Retiradas**: Ya retiradas

---

## 3. Estacionamiento de Visitas

### Registrar ingreso de vehículo
1. Ir a **Estacionamiento** en el menú
2. Click en **+ Nuevo Ingreso**
3. Completar:
   - **Patente**: Patente del vehículo
   - **Departamento que visita**: Seleccionar
   - **Marca**: Ej: Toyota, Ford (opcional)
   - **Color**: Ej: Rojo, Azul (opcional)
4. Click en **Registrar Ingreso**

### Registrar salida
1. En la lista, buscar vehículo activo
2. Click en **Registrar Salida**

### Filtrar
- **Todos**: Ver todos los registros
- **Ocupados**: Vehículos actualmente en el estacionamiento
- **Historial**: Registros finalizados

---

## 4. Dashboard (Panel Principal)

Muestra estadísticas en tiempo real:
- **Visitas Activas**: Visitantes dentro del edificio
- **Encomiendas Pendientes**: Paquetes por retirar
- **Autos Estacionados**: Vehículos en el lugar

Desde aquí se puede acceder rápidamente a:
- Nueva Visita
- Nueva Encomienda
- Estacionamiento

---

## 5. Gestión de Departamentos (Supervisor/Admin)

### Agregar departamento
1. Ir a **Departamentos**
2. Click en **+ Nuevo Departamento**
3. Completar:
   - **Número**: Ej: 101, A1
   - **Piso**: Número de piso
   - **Propietario**: Nombre del propietario

---

## 6. Gestión de Usuarios (Solo Admin)

### Crear usuario
1. Ir a **Usuarios**
2. Click en **+ Nuevo Usuario**
3. Completar:
   - **Nombre de usuario**: Login
   - **Contraseña**: Contraseña inicial
   - **Nombre completo**: Nombre real
   - **Rol**: conserje / supervisor / admin

---

## 7. Descargar Código Fuente (Solo Admin)

1. Click en **Descargar Código** (esquina superior derecha)
2. Se descarga archivo ZIP con todo el proyecto

---

## 8. Cerrar Sesión

Click en **Salir** en la esquina superior derecha.

---

## Tips

- La fecha y hora se registran automáticamente
- Todos los registros incluyen quién los creó
- Se puede filtrar por estado (activo/pendiente o completado)
- Las tablas muestran los últimos 100 registros por defecto
