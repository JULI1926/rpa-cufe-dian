Resumen y ejecución
-------------------

Este repositorio contiene scripts Python usados por un flujo RPA diseñado originalmente en ElectroNeek.
El archivo `orquestador_neek.py` integra los pasos principales del flujo Neek y ejecuta los scripts existentes:

- `iniciocorreogmailelectronek.py` -> envía correo de inicio (invocado como subproceso)
- `filtrarexcel.py` -> filtra el Excel original (el script ya modifica `rutaradian`)
- `procesarpendientes.py` -> procesa facturas pendientes obtenidas desde el endpoint y llama a `navegaciondian.procesarfactura` por cada registro
- `fincorreogmailelectronek.py` -> envía correo de fin (invocado como subproceso)
- `enviocorreogmailerrorelectronek.py` -> envía correo de error (invocado con "ruta=cuerpo")

Cómo ejecutar (PowerShell)

1. Asegúrate de que `VariablesGlobales.json` está en `C:/Users/julia/Desktop/VALIDACIONES_DIAN/DIAN/VariablesGlobales.json` o pasa la ruta como argumento.
2. Ejecuta:

```powershell
# desde la carpeta DIAN
python .\orquestador_neek.py
# o pasando la ruta al JSON
python .\orquestador_neek.py "C:/ruta/a/VariablesGlobales.json"
```

Notas:
- El orquestador invoca `procesarpendientes.py` que a su vez llama a `navegaciondian.procesarfactura`.
- Los envíos de correo y logs están implementados en los scripts existentes y se llaman como subprocesos; revisar sus salidas si hay fallos.
- Si desea ejecutar todo desde Neek, configure los bloques de Neek para ejecutar `python orquestador_neek.py`.
