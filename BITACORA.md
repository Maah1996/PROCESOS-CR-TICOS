# BITÁCORA — Análisis de Procesos Críticos

Registro de trabajo del sistema **Análisis de Procesos Críticos** (V División, Ejército de Chile).

- **Repositorio:** https://github.com/Maah1996/PROCESOS-CR-TICOS (rama `main`)
- **Publicado en:** https://maah1996.github.io/PROCESOS-CR-TICOS
- **Respaldo:** `C:\Users\gladi\OneDrive\0 PROGRA\11 ANALISIS PROEC.RIESGOS\index.html`
- **Firebase:** proyecto `mapa-plano-montichef`, colección `procesos_criticos`, documento `principal`

> Este archivo es la FUENTE. El `BITACORA.pdf` de esta misma carpeta se genera a partir
> de él con `generar_bitacora.py`. Para agregar una sesión: escribir aquí y regenerar.
>
> Vive en dos lugares, siempre idénticos: esta carpeta de OneDrive y el repositorio de
> GitHub. **El repositorio es público**: no escribir aquí contraseñas, correos de terceros,
> contenido clasificado ni debilidades de seguridad sin resolver.

---

## Sesión 1 — 21 de julio de 2026

### Punto de partida

Revisión completa del código (un solo archivo `index.html`, 1.785 líneas / 130 KB) para
detectar fallas y proponer mejoras.

### Fallas encontradas y corregidas

**1. La tabla se redibujaba mal (lentitud grave)**
El cuerpo de la tabla se armaba agregando una fila a la vez al HTML ya existente, lo que
obligaba al navegador a reinterpretar toda la tabla en cada fila.
*Medido con 60 procesos × 3 módulos:* **7.311 ms → 53 ms** (138 veces más rápido).

**2. 450 líneas de tabla muerta**
El archivo traía una tabla escrita a mano que el programa reemplazaba al cargar. Incluía
botones que llamaban a funciones inexistentes (`addSubCol`, `delSubCol`). Se eliminó.

**3. Datos desalineados mostraban "undefined"**
Al restaurar un respaldo, cargar un registro o bajar de la nube, no se verificaba que la
cantidad de puntajes coincidiera con la cantidad de columnas. Se agregó `normalizarEstado()`,
que recorta lo sobrante, rellena lo faltante y descarta valores inválidos.

**4. Un apóstrofo rompía el guardado de columnas**
Nombrar una columna con apóstrofo (ej. `EJ'TO`) rompía el código interno y esa columna
dejaba de guardarse.

**5. El teclado borraba puntajes mientras se escribía texto**
Con celdas de puntaje marcadas, presionar Retroceso mientras se editaba la Misión borraba
los puntajes; teclear un dígito rellenaba toda la selección. Además dos manejadores se
disputaban el portapapeles.

**6. Pegar bloques guardaba una vez por celda**
Pegar 540 celdas desde Excel generaba 540 guardados. Ahora hace **1**, y demora 35 ms.

**7. Guardados que fallaban en silencio**
Si el almacenamiento del navegador se llenaba, el botón decía "Guardado" sin guardar.
Ahora avisa. Igual con "Imprimir" cuando el navegador bloquea las ventanas emergentes.

**8. Anti-caché mal planteado**
Usaba la hora exacta, así que cada visita era una dirección distinta: la página nunca se
guardaba en caché, se descargaba entera siempre y se rompía el botón "atrás". Se reemplazó
por un número de versión (`APP_VER`).

**9. Comentario que contradecía al cálculo**
El comentario de `calcTot` decía "redondeado al entero más cercano", pero el código siempre
devolvió un decimal. Se corrigió el comentario; **el cálculo NO se tocó**.

### Seguridad — el hallazgo grave

La regla de Firestore era `allow read, write: if true` sobre `procesos_criticos`. Cualquier
persona en internet podía **leer, editar y borrar** la misión, las unidades y los procesos
de la División, sin ninguna credencial.

**Corregido:**
- Se agregó login de correo y contraseña sobre el mismo proyecto Firebase que usan FUF DS44
  y MAPA-PLANO (mismos usuarios). No se muestra nada hasta identificarse.
- Quién entra lo deciden las **reglas de Firestore**, no la página: si un correo no está
  autorizado, se le niega el acceso, se le avisa y se cierra la sesión.
- Al cerrar sesión se borra el respaldo local y se recarga, para no dejar datos
  institucionales en un equipo compartido.
- **Verificado:** lectura anónima al documento responde **403 PERMISSION_DENIED**.

### Trabajo compartido en vivo

Antes la nube se leía una sola vez al abrir: si dos personas trabajaban a la vez, la segunda
en guardar borraba el trabajo de la primera sin que ninguna se enterara.

Ahora la página escucha el documento compartido:
- Si no hay cambios sin guardar, la pantalla se actualiza sola e indica quién guardó.
- Si se estaba editando, **no se toca nada**: aparece un aviso para elegir entre ver los
  cambios del otro o conservar los propios.

### Tamaño de letra

- El control `Aa` quedó **solo en el primer módulo** y manda sobre todos: texto de las
  tareas fundamentales y números (puntajes, TOTAL y NIVEL) de todos los módulos y columnas,
  **incluidos los que se agreguen después**.
- El tamaño **se guarda solo** y viaja con la planilla (respaldo local, nube y registros de
  la Base de Datos). Antes vivía solo en el navegador y se perdía al sincronizar o cambiar
  de equipo — esa era la causa de que "se desconfigurara la letra".
- Se migra automáticamente lo que estuviera configurado con la versión anterior.
- Los registros guardados ahora conservan también títulos y anchos de columna.

### Estado al cierre de la sesión

- **Versión publicada:** 1.3.0
- **Commits:** `fa139bf` (correcciones), `5224382` (login + sincronización), `f72dc73` (letra)
- GitHub y la copia de OneDrive quedaron idénticos (misma huella `2eb9ca36…`).

### PENDIENTES

1. **Autorizar a las demás personas.** Hoy el único correo autorizado es
   `marcoaraya1973@gmail.com`. Los demás usuarios ven el login y no pueden entrar. Falta
   definir la lista de correos y que cada uno tenga cuenta creada (esta página no tiene
   auto-registro).
2. **Exigir correo verificado en la regla de acceso.** Agregar
   `&& request.auth.token.email_verified == true` a la condición. Antes de aplicarlo hay que
   confirmar en Firebase → Authentication que todas las cuentas autorizadas figuren como
   verificadas, o quedarían fuera. (El motivo se conversó directamente; no se detalla aquí
   porque este archivo se publica en un repositorio público.)
3. **Definir el redondeo de `calcTot`.** Confirmar con el Comité de Riesgo si el TOTAL debe
   ser decimal (como está) o entero. Cambiarlo altera la calificación de todos los procesos.
4. **Revisar el umbral del TOTAL.** La celda TOT se pinta roja con `>= 2`, mientras el
   criterio de criticidad del resto de la planilla es `>= 1.5`. Confirmar si es intencional.

### Recordatorios de operación

- Tras cada cambio, abrir con **Ctrl+Shift+R** la primera vez.
- Al publicar una versión nueva hay que **subir el número de `APP_VER`** en `index.html`.
- Cada subida a GitHub se copia también a esta carpeta (quedan idénticos).
