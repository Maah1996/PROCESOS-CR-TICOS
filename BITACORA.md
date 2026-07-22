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

---

## Sesión 2 — 22 de julio de 2026

### Lo que se pidió

Una pantalla previa a la planilla donde cada departamento administre sus propios procesos
(unidad, código y nombre), los revise y recién entonces pueda pasar a la planilla general.

### Pantalla nueva: "Gestión de procesos por departamento"

Es ahora la **puerta de entrada**: después del login se abre esta pantalla, no la planilla.
Se pasa a la planilla con "Ir a la planilla general ▸" y se vuelve con el botón
"◂ Procesos por Depto." de la barra superior.

**Departamentos cargados:** I "Personal", II "Inteligencia", III "Operaciones",
IV "Logística", V "Planes y Políticas", VI "Mando y Control", VIII "Finanzas" y COMPRED.
El orden es romano de menor a mayor y **COMPRED siempre al final**, tanto en el desplegable
como al pasar a la planilla. El administrador puede agregar, renombrar y eliminar
departamentos; los nuevos se ordenan solos en su lugar.

**Cada jefe ve solo su departamento.** El desplegable le queda fijo en el suyo y no ve el
panel de administración. Si su departamento está vacío, la pantalla se lo dice y lo invita
a cargar sus procesos; si ya tiene, los revisa, agrega o modifica.

**El código se sugiere solo** siguiendo el correlativo del departamento (2.1, 2.2, 2.3…) y
avisa si se repite uno.

### Certificación (control de calidad antes de la planilla)

Nadie pasa a la planilla sin declarar que revisó sus procesos. La franja de certificación
queda verde con el correo, la fecha y la cantidad certificada.

Lo importante: la certificación guarda una **huella del contenido**. Si después se edita
cualquier proceso, la huella deja de coincidir, la certificación se anula sola y el paso se
bloquea de nuevo. Así la firma siempre corresponde a lo que está guardado.

El administrador pasa siempre (es quien consolida) y tiene un **tablero** con el estado de
los 8 departamentos: certificado por quién y cuándo, pendiente, o sin procesos cargados.

### Un documento por departamento

Cada departamento guarda en `procesos_deptos/<DEPTO>`, no en un documento compartido.
Dos razones: las reglas de Firestore pueden verificar **de verdad** que un jefe solo escriba
en el suyo (con un documento único el límite habría sido solo de pantalla, saltable desde la
consola del navegador), y dos jefes guardando a la misma hora no se pisan.

La lista de departamentos y los correos asignados viven en `procesos_criticos/catalogo`,
que solo escribe el administrador.

### Cargar el catálogo en la planilla

Lo hace solo el administrador. Sincroniza **conservando los puntajes**: los procesos que ya
existen se reconocen por UNIDAD + CÓDIGO y mantienen sus notas intactas, solo se actualizan
nombre y orden; los nuevos entran con las celdas vacías; los que se sacaron del catálogo se
listan antes y se decide si se eliminan o se conservan al final. Si hay departamentos sin
certificar, los nombra y pregunta antes de continuar.

También quedó "Importar desde la planilla", que arma el catálogo con los procesos que ya
están escritos, para no tipearlos de nuevo la primera vez.

### Reglas de Firestore

Se agregaron sin tocar las de FUF DS 44 ni las de `/users`. Detalle que importaba: las
reglas se **suman**, así que la regla comodín de `procesos_criticos/{doc}` se modificó para
excluir `catalogo` en escritura — agregar un bloque aparte no habría restringido nada.

`procesos_deptos/{depto}` deja escribir al administrador, o a quien tenga su correo asignado
a ese departamento en `procesos_criticos/catalogo`.

### Correcciones y mejoras de la misma sesión

**1.4.1 — La importación traía filas incompletas.**
Una fila de la planilla con la unidad puesta pero sin nombre de proceso entraba al catálogo
y aparecía como una línea en blanco (le pasó al Depto. V). Ahora solo se importan las filas
que tienen unidad **y** nombre, y el aviso previo dice cuántas se omiten.

**1.4.2 — Número de versión a la vista.**
Al lado del título de la pantalla aparece la versión (`v1.4.3`). Sin eso no había forma de
saber si el navegador ya había tomado la versión nueva o seguía con la del caché — problema
real: el anti-caché no sirve para el propio salto de versión, porque el archivo viejo no
sabe que existe uno nuevo. Ante la duda, **Ctrl+Shift+R** y mirar el número.

**1.4.3 — Diálogos propios.**
Los `alert`/`confirm`/`prompt` del navegador mostraban "maah1996.github.io dice…" y rompían
la presentación del documento. Se reemplazaron por un cuadro con el mismo tipo de letra y
colores del sistema. Tres mejoras de fondo, no solo de aspecto:

- **Los botones dicen lo que hacen.** "Aceptar / Cancelar" era derechamente peligroso en el
  mensaje de procesos fuera del catálogo ("Aceptar = eliminarlos, Cancelar = conservarlos").
  Ahora dicen "Eliminarlos" / "Conservarlos al final", "Certificar" / "Volver a revisar",
  "Reemplazar catálogo" / "Cancelar", "Cargar igual" / "Esperarlos". Los que borran algo van
  en rojo.
- **Las listas largas** (departamentos pendientes, procesos fuera del catálogo) van en un
  bloque aparte con su propio desplazamiento, en vez de estirar el cuadro fuera de pantalla.
- Enter acepta, Escape cancela.

También se corrigió el mensaje de departamento vacío, que le decía "usted no tiene procesos"
al administrador cuando miraba el departamento de otro.

### Estado al cierre de la sesión

- **Versión publicada:** 1.4.3
- **Commits:** `7ffb7a2` (pantalla + certificación), `46229e2` (filas incompletas),
  `9753eae` (versión a la vista), `346a481` (diálogos propios)
- Reglas de Firestore publicadas el 22 de julio de 2026.
- Verificado en navegador con una copia sin Firebase (sin tocar los datos reales): bloqueo
  del paso sin certificar, certificación, anulación al editar, estado vacío, carga a la
  planilla conservando los puntajes de los procesos existentes, y los diálogos nuevos.
- Nota de método: el archivo se probó servido por `http://127.0.0.1` con una copia sin
  Firebase. Abrirlo como `file://` no sirve — el panel de vista previa se queda pegado en
  la primera dirección y no recarga.

### PENDIENTES (además de los de la Sesión 1)

5. **Primer guardado del administrador.** La regla de los departamentos consulta
   `procesos_criticos/catalogo`. Mientras ese documento no exista, los jefes reciben
   "Sin permiso para guardar". Hay que entrar y usar "Asignar correos a un depto." una vez
   para crearlo, ANTES de avisar a los jefes.
6. **Cargar los correos de cada jefe.** Cada uno debe estar en dos lugares: en la lista
   `autorizadoPC()` de las reglas (para abrir la app) y asignado a su departamento desde la
   pantalla (para escribir en él).
7. **Repartir los procesos actuales.** Usar "Importar desde la planilla" una sola vez para
   que los procesos que hoy están en la planilla queden distribuidos por departamento.
   Quedó pendiente rehacerlo con la versión 1.4.1 o superior: la primera importación se hizo
   con la versión que traía las filas incompletas, así que el catálogo todavía tiene líneas
   en blanco y marca 36 procesos donde hay muchos menos reales.
8. **La mayoría de los departamentos no tiene procesos escritos.** En la planilla solo I, II
   y V tienen nombres; III, IV, VI y VIII tienen la unidad marcada en filas vacías. No es una
   falla: es justamente lo que la pantalla nueva viene a resolver, que cada jefe cargue los
   suyos.
9. **Diálogos de la planilla general (pantalla 2).** Siguen usando los cuadros del navegador.
   Se dejaron así a propósito, es otro módulo; queda ofrecido igualarlos en una pasada aparte.
