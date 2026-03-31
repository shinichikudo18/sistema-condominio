# Sistema de Gestión de Condominio

Sistema web para gestionar registro de visitas, encomiendas y estacionamiento de visitas en un edificio de condominio.

## Requisitos

- Python 3.8+
- pip

## Instalación

```bash
cd condominio
pip install -r requirements.txt
python app.py
```

## Acceso

Abrir en el navegador: `http://localhost:5000`

## Usuarios iniciales

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| admin | admin123 | Administrador |
| supervisor | super123 | Supervisor |
| conserje | conserje123 | Conserje |

## Funcionalidades

### Registro de Visitas
- Nombre del visitante
- DNI (opcional)
- Departamento que visita
- Motivo de la visita
- Fecha/hora de ingreso y salida

### Registro de Encomiendas
- Departamento destinatario
- Remitente
- Descripción del paquete
- Fecha recepción
- Registro de retiro (quien retira y fecha)

### Estacionamiento de Visitas
- Patente del vehículo
- Marca y color
- Departamento que visita
- Fecha/hora de ingreso y salida

## Gestión (solo Admin)

- Crear/modificar usuarios
- Gestionar departamentos

## Producción con Docker

```bash
docker-compose up -d
```

El sistema estará disponible en `http://localhost:5000`
