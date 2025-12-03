# barrabinbarrabash
## Ejecución interfaz web
### Recomendado
```
cd ui/
python3 -m venv venv
pip3 install -r requirements.txt
```
Dentro de `ui/backend/`
```
uvicorn main:app --reload --port 5000
```
Dentro de `ui/frontend/`
```
python3 app.py
```
### Alternativamente usar script
Dentro de `ui/`
```
chmod +x run.sh
./run.sh
```
