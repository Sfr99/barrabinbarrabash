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

La UI consume datos a través de un backend REST. Para que las plantillas HTML funcionen correctamente, el backend debe devolver una serie de campos mínimos con nombres estables. No es necesario un formato exacto más allá de estos campos requeridos, pero sí deben existir con tipos compatibles.

### 4.1. Datos requeridos para el dashboard

El endpoint correspondiente debe proporcionar:

* **attacks_today**: número entero.
* **banned_ips**: lista de objetos con:

  * `ip`
  * `reason`
  * `since` (cadena formateada para mostrar en la tabla)
* **events**: lista ordenable por fecha con:

  * `timestamp` (cadena mostrable en la UI)
  * `ip`
  * `action`
  * `description`
* **chart_labels**: lista de etiquetas temporales para el gráfico.
* **chart_values**: lista de valores numéricos asociados a cada etiqueta.

### 4.2. Gestión de IPs baneadas

La UI espera que el backend permita:

* Obtener la lista de IPs baneadas.
* Eliminar el ban de una IP mediante una operación POST o similar.

### 4.3. Reinicio del estado

El backend debe permitir que la UI solicite:

* Reset del contador de ataques.
* Limpieza de listas de bans y eventos.

### 4.4. Requisitos de formato

* Todos los campos deben ser serializables por JSON.
* Las fechas deben enviarse en formato legible por la UI (por ejemplo, “YYYY-MM-DD HH:MM:SS”).
* El backend puede implementar cualquier lógica interna mientras respete los nombres de campos anteriores.

