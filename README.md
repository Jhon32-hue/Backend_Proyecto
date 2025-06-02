# Como ejecutar el proyecto

## Requerimientos

- Python
- Postgresql
- Visual Studio Code

## Clonar repositorio

Se recomienda crear una carpeta vacía en algun directorio de tu computador en mi caso yo la creare en la carpeta documentos:


```bash
cd Documents
mkdir proyecto_final_diplomado
cd proyecto_final_diplomado
```

Clonamos el repositorio
```bash
git https://github.com/Jhon32-hue/Backend_Proyecto.git
```

Creamos y activamos un entorno virtual
```bash
python -m venv enviroment
#windows
.\enviroment\Scripts\activate
#Mac / Linux
source enviroment/bin/activate
```

## Instalamos dependencias
Ahora debemos instalar las dependencias del proyecto, para esto debemos primero ir a la carpeta que contiene el proyecto de django

```bash
cd backend
```

Ahora debemos ejecutar el comando para instalar las dependencias

```bash
pip install -r requirements.txt
```

## Configurar las variables de entorno
Crea un archivo .env en la raiz del proyecto de django, cosa que quede al mismo nivel que el archivo manage.py; para este archivo .env puedes tomar como referencia el archivo .env.example

```bash
touch .env
```


## Modifica el fixture de la aplicación de users
```bash
python manage.py loaddata users 
```