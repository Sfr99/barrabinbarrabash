# Firewall UI

Interfaz web desarrollada en Flask para visualizar métricas del firewall, gestionar IPs baneadas y consultar eventos recientes. La aplicación funciona como un frontend independiente ubicado en la ruta `/ui` y requiere un backend que proporcione la información real mediante API REST.

---

## 1. Requisitos

- Python 3.9+
- Entorno virtual (`venv`)
- Dependencias incluidas en `requirements.txt`
- Servidor backend del firewall con API accesible

---

## 2. Instalación

1. Crear y activar un entorno virtual.  
2. Instalar dependencias mediante `pip install -r requirements.txt`.  
3. Ejecutar la aplicación con `python app.py` (modo desarrollo).

La interfaz quedará disponible en el host configurado, bajo la ruta `/ui`.

---

## 3. Funcionamiento general

La UI muestra:

- Contador de ataques del día  
- Lista de IPs baneadas y opción de desbaneo  
- Actividad reciente del firewall  
- Gráfico de eventos por minuto  
- Botón de reseteo del estado

En modo demo, la información procede de un estado local en memoria. En producción, la UI debe obtener todos los datos desde la API del backend.

---

## 4. Integración con el backend

El backend debe exponer endpoints REST que proporcionen:

- Datos agregados para el dashboard  
- Lista actual de IPs baneadas  
- Acción de desbaneo de una IP  
- Restablecimiento del estado del firewall  
- Últimos eventos registrados  
- Estadísticas por minuto para la gráfica  

La UI consume estas rutas únicamente para lectura y para las acciones de desbaneo y reseteo. La estructura de los datos devueltos debe incluir campos equivalentes a los utilizados en la plantilla (IP, motivo, fecha, acción, descripción, métricas temporales, etc.).

---

## 5. Estructura del proyecto

```

ui/
│
├─ app.py              # Lógica de la UI y llamadas previstas al backend
├─ templates/          # Plantillas Jinja2
├─ static/             # Recursos estáticos (CSS)
├─ requirements.txt
└─ README.md

```

---

## 6. Despliegue

Para producción se recomienda:

- Ejecutar Flask detrás de un servidor WSGI (Gunicorn, uWSGI, etc.).  
- Publicar la aplicación detrás de un proxy inverso que sirva la ruta `/ui`.  
- Mantener las dependencias aisladas en un entorno virtual o contenedor.

---

## 7. Notas adicionales

- La seguridad (autenticación, roles, integridad de datos) debe implementarse en el backend si la UI se utiliza en entornos reales.  
- Las rutas y estructura exacta de la API pueden ajustarse siempre que mantengan compatibilidad con los campos que la UI renderiza.
