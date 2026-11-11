---
modulo: ../../7_Python_para_APIS_IA_Data_Validation.html
agenda: si
---

<!--
  Semana 7 · Validación avanzada de datos.
  Cubre los 60 min de exposición del reparto («Antes de empezar»): introducción 5,
  tipos 10, validadores 20, modelos anidados 12 y 422 13. La práctica guiada de
  180 min se presenta al final, no se desarrolla.
  Rehecha sobre el capítulo revisado a fondo (PR #12): cambiaron el ejemplo de iris,
  el tamaño mínimo de la sesión, los diagramas, los cuestionarios y la actividad.
  Código verificado con Python 3.11, FastAPI 0.141.1 y Pydantic 2.13.5
  (taller_corte2/build/venv).
-->

# Por qué validar antes de modelar {seccion=modulo-0}

> Con una edad de −5, su regresión no protesta: calcula. Devuelve coeficientes, *p*-valor e intervalo, con la misma cara de seguridad que si los datos fueran buenos.

???
5 minutos para toda la sección. Es la motivación del material, casi literal: dejarla caer y preguntar quién ha visto un modelo ajustado sobre datos que nadie revisó.

## Un modelo no sabe que le mintieron {.idea etiqueta="El problema de la semana"}

Un fallo ruidoso se ve. Una edad de −5 que entra se convierte en una conclusión que usted tendrá que defender en la sustentación **sin saber que está podrida**.

???
Es el lema del capítulo. La semana 4 enseñó a declarar que un campo es `int`; esta semana, a decir *qué* entero, con qué rango, dentro de qué estructura, y a explicar por qué se rechazó.

## En producción nadie mira los datos: las reglas van antes

::: flujo
1. **Ingesta** — llegan los registros: un JSON, un CSV, otra base
2. **Validación de esquema (Pydantic)** — tipo, formato y rango lógico, registro a registro; rechaza lo imposible, con su motivo
3. **Análisis estadístico** — compara cada dato con el resto de la muestra; lo raro se **marca**, no se expulsa
4. **Auditoría** — queda constancia de qué entró, qué se rechazó y por qué
5. **Almacenamiento** — los registros aceptados, con sus marcas de revisión
:::

???
Figura 2.1 del material (el diagrama anterior, un SVG de texto pequeño, se sustituyó por este flujo de cinco etapas). En el análisis exploratorio hay un analista mirando y decidiendo sobre la marcha; en un pipeline automático no: las reglas se fijan antes de ver los datos. La etapa 2 mira un registro a la vez; la 3 necesita la muestra entera. Un peso de 180 kg es raro pero posible: se marca. Si sobra tiempo, la primera pregunta del cuestionario de la sección 2: dos registros, edad = −5 y edad = 97; el −5 se rechaza en la etapa 2, el 97 pasa y se revisa en la 3.

# El tipo es el libro de códigos {seccion=modulo-1}

> Declarar un tipo es escribir el *codebook* de la encuesta antes de salir a campo.

???
10 minutos. La analogía del material: el codebook dice qué significa cada columna y qué valores admite; el tipo lo vuelve una regla que se cumple, no un comentario. Python no comprueba las anotaciones: es Pydantic quien las lee y rechaza, mientras el programa corre.

## `int` ya no alcanza: una edad y un número de encuesta son los dos enteros

| Anotación | Qué declara | En estadística |
|---|---|---|
| `list[float]` | Vector homogéneo | Una columna de la matriz de datos |
| `T \| None` | Valor o ausencia permitida | Una variable con no respuesta permitida |
| `Literal["a", "b"]` | Niveles cerrados | Una variable nominal con niveles cerrados |
| `Annotated[int, Field(ge=0, le=120)]` | Tipo **y** rango | Una variable con recorrido acotado |

Y solo una de las dos puede valer 40 000.

???
Tabla de 3.1.2 del material. Desde Python 3.10 se escribe `list[T]` y `T | None`; el código del capítulo todavía usa `List` y `Optional` en varios ejemplos, y significan lo mismo. `NDArray[np.float64]` queda para la lectura: documenta para mypy, y Pydantic no valida arreglos de NumPy (3.4).

## Tipo y rango van en la misma línea

```python ObservacionClinica {resaltar=2,4,5}
class ObservacionClinica(BaseModel):
    edad: Annotated[int, Field(ge=0, le=120, description="Edad en años")]

    presion_sistolica: Annotated[float, Field(ge=60.0, le=250.0)]
    tratamiento: Literal["placebo", "dosis_baja", "dosis_alta"]
```

`ge` y `le` son el rango; `Literal`, los niveles del factor. Lo que queda fuera no entra.

???
Solución del ejercicio 2 de 3.5, sin la `description` de la presión. Preguntar qué pasa con `tratamiento="dosis_media"`: 422, porque no está entre los niveles. Y con `"Placebo"`, con mayúscula: también 422 (`literal_error`); `Literal` distingue mayúsculas, y tolerarlas exige normalizar antes con un validador `before`. Ojo con `float`: acepta `NaN` e infinito por defecto; `allow_inf_nan=False` los rechaza (3.2).

## Admitir `None` no es lo mismo que poder no venir {columnas=1:1 .codigo-grande}

```python Ejercicio 1 de 3.5
cilindros: Literal[4, 6, 8] | None = None
```

|||

- `| None`: el `null` es un valor **legal**; sin él, se rechaza
- `= None`: el campo puede **no venir**; sin él, Pydantic v2 lo exige
- Pydantic nunca rellena con 0

???
Ejercicio 1 de 3.5. Comprobado con Pydantic 2.13: sin `= None`, un `float | None` que no llega da `missing`. Lo que hace opcional a un campo es el valor por defecto; `Optional` solo dice que `None` es un valor admitido (es la tercera pregunta del cuestionario de la sección 3). El 0 aparece después, si alguien hace `fillna(0)` en pandas; y al pasar a un DataFrame cada `None` de una columna numérica se vuelve `NaN` sin aviso. Decidir qué hacer con los faltantes (casos completos, imputación) sigue siendo del analista; el mecanismo MCAR, MAR o MNAR se ve en la sección 4. `Literal` no convierte: un `"6"` que llegue como texto se rechaza.

## ¿Su API acepta `"25"` en un campo `edad: int`? {.pregunta tipo=E2}

Un cliente envía `{"edad": "25"}`, con la edad **entre comillas**.

::: respuesta Sí, en el modo por defecto
Pydantic trabaja en modo **laxo**: convierte `"25"` en `25` y responde 200. Con `model_config = ConfigDict(strict=True)` el mismo JSON da 422, `int_type`.
:::

???
Es la pregunta 1 de sustentación (sección 9). Comprobado con FastAPI 0.141: modo laxo, 200; estricto, 422. La tabla de 4.1.2 compara los dos modos: el laxo convierte lo inequívoco (`"4"`, `4.0`, `" 4 "`) y rechaza lo que obligaría a adivinar (`4.5`, `"cuatro"`); no corrige erratas.

# Validadores: lo que no puede ser cierto {seccion=modulo-2}

> Una saturación de oxígeno de 104 % no puede ser cierta, igual que una edad negativa. El validador es la verificación que la rechaza antes de que entre a la base.

???
20 minutos, la sección más cargada de la exposición. Un validador de campo es como las verificaciones de consistencia del formulario de captura (*edit checks*): detecta lo que no puede ser cierto. No es un criterio de inclusión: excluir a un paciente de 17 años de un ensayo para adultos es una decisión de diseño que se toma y se reporta aparte (4.1.1). Ojo: la tabla de síntesis de la sección 7 del material todavía lo llama «criterio de inclusión o exclusión del protocolo», y eso contradice 4.1.1; en clase, seguir 4.1.1.

## Un validador deja pasar el valor o lo rechaza con un motivo

```python ObservacionIris {resaltar=1,5-6,10}
@field_validator('especie_taxonomica')
@classmethod
def validar_especie(cls, valor: str) -> str:
    valor_limpio = valor.strip().lower()
    if valor_limpio not in cls.ESPECIES_PERMITIDAS:
        raise ValueError(
            f"Especie no reconocida: '{valor}'. "
            f"Valores admitidos: {', '.join(cls.ESPECIES_PERMITIDAS)}."
        )
    return valor_limpio
```

`raise ValueError` **rechaza**; `return` deja pasar el valor, aquí ya normalizado.

???
Del ejemplo del dataset iris (4.3). Un nivel fantasma como «rosa» crearía, en un ANOVA, un grupo de una sola observación. El validador también normaliza (`strip().lower()`): valida y transforma a la vez, como pregunta la sustentación 6. El ejemplo simula 15 observaciones con tres errores sembrados y rechaza 3, los índices 3, 7 y 11: una tasa de exclusión del 20 %, deliberadamente alta. `validar_medida` atrapa el −5,1 (rango lógico) y el 85,0 (heurística de escala: probable registro en milímetros; según el material, un único umbral de 10 cm detecta 542 de las 600 medidas de Fisher pasadas a milímetros, así que para atraparlas todas el límite tiene que ser por variable). `@cronometrar` mide cuánto cuesta validar el lote; queda para la lectura.

## `before` limpia el formato; `after` comprueba la regla

::: flujo
1. **Dato crudo** — `"1,234.56"`, `"NA"`, `" 4 "`
2. **`mode='before'`** — limpia el formato: `"1,234.56"` → `"1234.56"`, `"NA"` → `None`
3. **Conversión y `Field`** — `"4"` → `4`; `ge`, `le`, `pattern`… o `ValidationError`
4. **`mode='after'`** — reglas de dominio, sobre el valor ya convertido
5. **Valor validado** — listo para el análisis
:::

???
Es la figura 4.1 del material (apartado 4.2), «Orden de ejecución de los validadores», que proyectada no se lee: aquí va como flujo. Dos detalles que la semana 4 no contó: las restricciones de `Field` se comprueban antes de cualquier `after` (si `ge=0` falla, los `after` ni corren), y los `before` corren en orden inverso al de definición. Un `before` limpia el formato, no arregla valores: un `"-25"` lo rechaza `ge=0` después. Cuidado con la coma: `"12,5"` en Colombia es doce coma cinco, y una regla que borre todas las comas lo vuelve 125 (4.1.3). La pregunta que sigue muestra qué pasa si se confunden.

## El rango 1–6 en `mode='before'`, y llega `"3"` {.pregunta tipo=E2}

Su validador de **estrato socioeconómico** comprueba que el valor esté entre 1 y 6. Lo declaró con `mode='before'`, y el JSON trae el estrato como el string `"3"`.

¿Qué responde la API?

::: respuesta Ni 200 ni 422: un error del servidor
En `before` el valor todavía es `"3"`, y `1 <= "3"` lanza **`TypeError`**. Pydantic no lo convierte en error de validación: sale como 500. La regla de rango va en `Field`, o en `after`, cuando ya es `int`.
:::

???
Pregunta 5 de sustentación. Comprobado con FastAPI 0.141: el `TypeError` sube tal cual y la respuesta es 500; con un 9, 422. Un validador solo produce 422 si lanza `ValueError` o `AssertionError` (4.2). Por eso los rangos simples van en `Field`, que actúa después de la conversión de tipos.

## ¿Qué está mal en este validador? {.pregunta tipo=E3}

```python
@field_validator('edad')
@classmethod
def validar_edad(cls, v: int) -> int:
    if v < 0:
        return abs(v)
    return v
```

::: respuesta Corrige en silencio
Convierte −25 en 25 y registra como observado un valor que nadie midió: el error desaparece de la bitácora. Rechace con un motivo: `raise ValueError(f"La edad no puede ser negativa; se recibió {v}. …")`.
:::

???
Ejercicio 2 de 4.6, sin los comentarios que delatan la respuesta. El material llama a esto «mutación silenciosa». Un −25 puede ser un error de signo, un 52 mal digitado o un código «no sabe»; si las edades negativas vienen de un mismo encuestador, el «arreglo» sesga ese subgrupo. Para un rango fijo bastaría `Field(ge=0)`. La alternativa de apartar el dato para revisarlo (*dead letter queue*) está en el mismo ejercicio.

## Un buen motivo dice campo, valor, regla y qué revisar

Lo lee otra persona, o un programa, que no ve su código.

| Mal | Bien |
|---|---|
| «Error» · «Valor fuera de rango» | `La medida debe ser un número finito mayor que 0 cm; se recibió -5.1.` |
| «Violación axiomática del dominio» | `Especie no reconocida: 'rosa'. Valores admitidos: setosa, versicolor, virginica.` |

???
Recuadro «Cómo se redacta un rechazo» (4.5): es lo que pide RF2 de la actividad. Tres reglas más: nombrar el campo en el mensaje si va a acabar en un registro (en `loc` ya va, pero un registro se lee sin él); nada de LaTeX ni de jerga; y no recortarlo al registrarlo (`msg[:50]`): el motivo es justo lo que se corta.

## Cuando la regla cruza campos, va en `model_validator`

```python Estancia {resaltar=1,3,8}
@model_validator(mode="after")
def alta_posterior_al_ingreso(self) -> "Estancia":
    if self.fecha_alta < self.fecha_ingreso:
        raise ValueError(
            f"fecha_alta ({self.fecha_alta}) es anterior a fecha_ingreso "
            f"({self.fecha_ingreso}); la duración de la "
            "estancia saldría negativa."
        )
    return self
```

Un `field_validator` ve un campo; `model_validator` ve el registro entero, y **solo corre si todos los campos pasaron**.

???
Apartado 4.4 del material, recortado a un método de la clase `Estancia`. Tres detalles: solo corre si los campos pasan (con `"9 de marzo"` sale el error del campo y el de modelo ni se ejecuta); no lleva `@classmethod` y devuelve `self` (si se olvida el `return self`, en FastAPI el endpoint recibe `None`); y su error no es de ningún campo: `loc` vacío y, en FastAPI, `["body"]`, por eso el mensaje tiene que nombrar los dos campos. Es el validador que pide RF2 para la escala de `RespuestaEncuesta`.

## El rango estadístico usa una referencia fija, no el lote

```python EntradaPrediccion {resaltar=1,5,12}
MEDIA_REF, DE_REF = 1.462, 0.1737   # 50 setosas de Fisher (1936)
Z_MAX = 3.0   # supone una distribución aproximadamente normal

# en el modelo: el rango lógico lo pone Field
petal_length: float = Field(gt=0, allow_inf_nan=False)

@field_validator('petal_length')
@classmethod
def en_rango_estadistico(cls, valor: float) -> float:
    z = (valor - MEDIA_REF) / DE_REF
    if abs(z) > Z_MAX:
        raise PydanticCustomError('fuera_de_rango_estadistico', …)
    return valor
```

El **rango lógico** se rechaza siempre; el **estadístico**, solo a la entrada de un modelo ya ajustado, donde evita extrapolar.

???
Apartado 4.5, recortado: el `raise` completo, con su mensaje (valor, referencia, límite y qué revisar), está en el material. Este es el patrón de RF3 de la actividad, que pesa el 25 %. Los parámetros de referencia son los de la muestra con que se ajustó el modelo, declarados como constantes con su fuente, nunca los del lote que llega: una petición sola no tiene lote, y en un lote los propios errores inflan la desviación con la que se los mide. Con la muestra de Fisher la regla |z| > 3 no rechaza ninguna de las 50 setosas y rechaza las 100 versicolor y virginica. `PydanticCustomError` da un `type` propio, que un programa puede distinguir de un error de formato.

## Al recoger datos, lo imposible se rechaza; lo raro pero real, se marca {.idea icono=fa-scale-balanced}

Rechazar las edades por encima de 100 elimina a los centenarios, que existen: el rechazo depende del propio valor (**MNAR**) y la muestra pierde sus extremos. Si se excluye más del 5 %, pregúntese por el mecanismo.

???
Recuadro «Atención» de 4.5 y «Para profundizar: MCAR, MAR y MNAR» de 4.3. Los rechazos de formato pueden ser MCAR solo si el error no depende de nada del estudio; si se concentran en una fuente (un hospital, un encuestador), ya no. La bitácora muestra dónde se concentran los rechazos, pero no demuestra el mecanismo: MAR y MNAR no se distinguen con los datos observados, así que se argumenta con lo que se sabe de cómo se recogieron. Al recoger datos, lo raro se acepta y se marca (un campo `revisar` o una entrada en la bitácora) y una persona decide después. Es la décima pregunta de sustentación.

# Modelos anidados: la forma del diseño {seccion=modulo-3}

> Si su dato tiene bloques y unidades, su modelo también debería tenerlos.

???
12 minutos. Si el tiempo aprieta, dar solo las tres primeras diapositivas y la pregunta. Cuidado con la analogía con las parcelas divididas: un modelo de Pydantic registra qué unidad pertenece a qué grupo, no cómo se asignaron los tratamientos ni qué efectos se estiman; un diseño *split-plot* además aleatoriza un factor en cada tamaño de unidad, y eso ningún modelo de Pydantic lo representa (5.1.1).

## Un modelo anidado registra qué unidad pertenece a qué grupo

```text Figura 5.1 del material, como árbol
SesionDinamometro                    NIVEL 2 · el grupo
├─ id_sesion_laboratorio             str
├─ marca_tiempo_prueba               datetime
├─ investigador_responsable          str
└─ ensayos_experimentales            List[EnsayoVehiculo], min_length=3
   ├─ [0] EnsayoVehiculo             NIVEL 1 · la unidad
   ├─ [1] EnsayoVehiculo
   └─ [2] EnsayoVehiculo             ← su error lleva el 2 en el loc
```

Datos agrupados: ensayos dentro de sesiones, pacientes dentro de hospitales.

???
Figura 5.1 del material, dibujada aquí como árbol: el diagrama original tiene texto de 10 px y no se lee proyectado; está en el material, con la ruta del error del tercer ensayo en rosa. «Datos agrupados» o «anidados» es como lo llama la estadística; los modelos multinivel (*mixed-effects*) trabajan con esa estructura.

## Anidar o aplanar: la ventaja del modelo anidado está en la validación

- Un modelo multinivel (`lme4`, `statsmodels`) se estima sobre una **tabla plana**, con una columna que identifica el grupo
- La estructura solo se pierde si se borra esa columna o se promedia por grupo
- En la tabla plana, los atributos del grupo se repiten en cada fila y **pueden contradecirse**
- En el modelo anidado se declaran una vez, cada nivel tiene sus reglas y el error señala la unidad exacta

???
Apartado 5.1.4. Corrige lo que a veces se dice: aplanar no destruye la correlación intraclase si se conserva la columna del grupo. El CCI, la fracción de la varianza total debida a diferencias entre grupos, está en el «Para profundizar» de la sección 5: si es alto, las unidades de un mismo grupo no son independientes, y analizarlas como si lo fueran suele subestimar los errores estándar. Con dos o tres sesiones el CCI entre sesiones apenas se puede estimar, por muchos vehículos que traiga cada una.

## Una sola línea anida el nivel micro dentro del macro

```python {resaltar=11}
# 1. Nivel inferior: el submodelo (la unidad de observación)
class EnsayoVehiculo(BaseModel):
    id_vehiculo: str = Field(min_length=2)
    cilindros_motor_cyl: int
    peso_wt: float = Field(gt=0.0, le=10.0)

# 2. Nivel superior: el modelo contenedor (el grupo)
class SesionDinamometro(BaseModel):
    id_sesion_laboratorio: str = Field(pattern=r'^SES-\d{4}-[A-Z]{2}$')
    investigador_responsable: str = Field(min_length=3)
    ensayos_experimentales: List[EnsayoVehiculo] = Field(min_length=3)
```

Cada elemento de la lista se valida con sus reglas; `min_length=3` exige tres vehículos. `SES-2024-CC`, con 2, sale `too_short`.

???
Recortado de 5.3: sin las `description`, sin `millas_por_galon_mpg` ni `caballos_fuerza_hp`, que repiten el patrón de `peso_wt`, y sin `validar_cilindros` (solo 4, 6 u 8) ni el validador de vehículos repetidos, que mira la lista entera. El error de la sesión CC es de la lista, no de ningún vehículo: `loc` `('ensayos_experimentales',)`, «List should have at least 3 items after validation, not 2». El tamaño mínimo ya no es un `field_validator`: es un argumento de `Field`.

## El tercer vehículo trae 5 cilindros {.pregunta tipo=E2}

Una sesión con tres ensayos; el tercero tiene `cilindros_motor_cyl = 5` (solo se admiten 4, 6 y 8).

¿Se rechaza solo ese vehículo o la sesión completa? ¿Qué dice el error?

::: respuesta La sesión completa, y el error dice dónde
```text
('ensayos_experimentales', 2, 'cilindros_motor_cyl')  value_error
```
Pydantic no construye objetos a medias: la lista solo es válida si lo son todos sus elementos.
:::

???
Ejercicio 1 de 5.4 y caso (a) de «Cómo se lee el `loc`»; el material usa el décimo vehículo, aquí el tercero (índice 2). Comprobado: la ruta del error incluye el índice. Estadísticamente las dos opciones tienen costo: rechazar la sesión pierde los vehículos buenos; quedarse con ellos y descartar el malo puede sesgar el análisis si los que fallan no son un subconjunto al azar. El ejercicio pide la alternativa que procesa sesiones parciales y registra cada exclusión: buen puente con la práctica.

## Las reglas de la lista esperan a que sus elementos sean válidos

La sesión `CC` trae solo 2 vehículos y, además, el segundo tiene un peso negativo.

```text
loc=('ensayos_experimentales', 1, 'peso_wt')  type=greater_than
```

- Se informa **un solo error**: el del vehículo
- `min_length`, el validador de la lista y cualquier `model_validator` no corren si falla un ensayo
- El cliente se entera del `too_short` cuando corrige ese error

???
Punto clave del apartado 5.3, casos (c) y (d). En (d), en cambio, salen los dos errores porque el investigador y la lista son campos hermanos y Pydantic valida todos los campos antes de responder. Es la pregunta 4 de sustentación («llega una encuesta con dos respuestas y el modelo exige tres: ¿por qué no aparece el de "al menos tres"?»). Comprobado con Pydantic 2.13: un solo error.

# El rechazo que explica su motivo {seccion=modulo-4}

> Si sus validadores solo saben decir «no», su API es tan difícil de usar como un formulario que se pone rojo sin decir dónde.

???
13 minutos. La frase es de la motivación del capítulo. Esta sección va de lo que llega a quien llama a la API: el código, el cuerpo del 422 y cómo hacerlo explicativo.

## El 422 es el código de lo que no cumple el contrato del modelo

| Código | Cuándo | Quién lo produce |
|---|---|---|
| **400** | No se puede interpretar la petición | Usted, con `HTTPException` |
| **422** | Los datos no cumplen el contrato: falta un campo, un tipo no corresponde, un valor está fuera de rango | FastAPI, solo: `RequestValidationError` |
| **409** | Petición válida que choca con lo que ya hay: el sujeto ya fue registrado | Usted, con `HTTPException` |

Un JSON sin llave de cierre da **422** (`json_invalid`), no 400.

???
Tabla de 6.1.2. La RFC 9110 define el 422 como «entiendo la petición, pero no puedo procesar su contenido»; FastAPI además responde 422 a un JSON mal formado, y pone en `loc` la posición del carácter donde se rompió. Hasta 2022 se llamaba *Unprocessable Entity* (RFC 4918): se verán los dos nombres. Comprobado con FastAPI 0.141: `{"id_sujeto": 9, "edad": 30` da 422, `json_invalid`, `["body", 27]`. Es la pregunta 13 de sustentación.

## El 422 por defecto dice dónde, qué regla y por qué {columnas=1:1}

- **`loc`** — dónde: `body` y el campo
- **`type`** — qué regla incumplió
- **`msg`** — el porqué; en inglés si la regla es de `Field`

Los errores llegan **juntos**, no de uno en uno.

|||

```json Respuesta de FastAPI a edad = 200
{"detail": [{
  "type": "less_than_equal",
  "loc": ["body", "edad"],
  "msg": "Input should be less than or equal to 120",
  "input": 200,
  "ctx": {"le": 120}
}, …]}
```

???
Del ejemplo de 6.2, recortado al primer error; el segundo (el municipio `'Medellín'`, que no es un código DIVIPOLA) llega en la misma respuesta. Cuando la regla es suya, `type` es `value_error` y `msg` es su texto con el prefijo «Value error, »; en ese caso `ctx` llega como `{"error": {}}`, porque FastAPI no sabe pasar la excepción a JSON. Lo que se escribe en el `raise ValueError(...)` es, literalmente, lo que lee quien llama a la API.

## Un manejador de `RequestValidationError` hace que el 422 se explique solo

```python rechazo_explicado {resaltar=9-12}
@app.exception_handler(RequestValidationError)
async def rechazo_explicado(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    rechazos = []
    for err in exc.errors():
        falta = err["type"] == "missing"
        rechazos.append({
            "campo": ".".join(str(parte) for parte in err["loc"]),
            "valor_recibido": None if falta else repr(err["input"]),
            "regla": err["type"],
            "motivo": err["msg"].removeprefix("Value error, "),
        })
    return JSONResponse(status_code=422, content={"rechazos": rechazos})
```

La regla sale como **código estable** y el valor, como texto: cabe cualquiera, también un `NaN`.

???
Apartado 6.3, recortado: sin la línea que deja cada rechazo en el registro del servidor (`bitacora.warning(...)`), que el material sí trae. Se registra al crear la aplicación, antes de la primera petición. `valor_recibido` va con `repr` porque con el manejador por defecto una petición con `NaN` termina en 500: Pydantic la rechaza bien (`finite_number`), pero el manejador copia el `NaN` en la respuesta y el JSON estándar no lo admite. Tampoco se copia `ctx`: en un `value_error` guarda la excepción, y devolver `exc.errors()` sin más también da 500. Es la pregunta 14 de sustentación y el RF4 de la actividad.

## Cada rechazo llega con campo, valor, regla y motivo

| `campo` | `valor_recibido` | `regla` | `motivo` |
|---|---|---|---|
| `body.edad` | `'200'` | `less_than_equal` | Input should be less than or equal to 120 |
| `body.municipio` | `'Medellín'` | `value_error` | municipio='Medellín' no es un código DIVIPOLA: se esperan 5 dígitos… |
| `body.ingreso_mensual` | `'nan'` | `finite_number` | Input should be a finite number |
| `body.27` | `'{}'` | `json_invalid` | JSON decode error |

El `NaN` y el JSON roto también salen en **422**, no en 500.

???
Salida de las tres peticiones de prueba de 6.3: (1) `edad` 200 y municipio `'Medellín'`; (2) un `NaN` en el ingreso y sin municipio, que además da un `missing` con `valor_recibido` `None`; (3) un JSON sin la llave de cierre, con `campo` igual a `body.27`, la posición del carácter. El motivo del municipio es el mensaje de su validador, que llega sin el prefijo «Value error, »; el texto completo termina en «Revisa si llegó el nombre en vez del código.» Los motivos de `Field` siguen en inglés; como `regla` es estable, el manejador puede traducirlos.

## ¿Qué pierde este código? {.pregunta tipo=E3}

```python
def procesar_datos(lista_datos):
    resultados = []
    for dato in lista_datos:
        try:
            resultado = Modelo.model_validate(dato)
            resultados.append(resultado)
        except Exception:
            pass
    return resultados
```

::: respuesta Todo rastro de lo que excluyó
`except Exception: pass` se traga los rechazos: no queda qué se excluyó ni por qué, no hay diagrama de flujo de participantes posible y los que sobreviven pueden sesgar el análisis. Capture `ValidationError` y registre cada exclusión.
:::

???
Ejercicio 2 de 6.5. Además atrapa errores que no son de validación: un fallo del propio código también desaparecería (si `Modelo` no estuviera definido, la función devolvería una lista vacía sin avisar).

## La bitácora alimenta el diagrama de flujo de participantes

::: tarjetas {columnas=3}
### Registrar
Momento, sujeto, campo, tipo de error, mensaje y valor rechazado
### Reportar
El flujo de participantes: CONSORT en ensayos, STROBE en estudios observacionales
### Diagnosticar
Fallas del instrumento y el mecanismo de pérdida: MCAR, MAR, MNAR
:::

???
Es la clase `BitacoraAuditoria` de 6.4: el ejemplo completo está en el material. Para el análisis, una observación rechazada es un dato faltante; la bitácora muestra dónde se concentran los rechazos, pero no demuestra el mecanismo. La tasa de exclusión cuenta sujetos rechazados, no errores: 5 de 6, el 83,3 %, con 6 filas de error porque el sujeto 1006 trae dos. Es la pregunta 15 de sustentación: el diagrama de flujo cuenta encuestas excluidas; los errores por regla dicen por qué.

# Cierre y práctica {seccion=modulo-6}

## Lo que se llevan hoy {.cierre}

- El tipo es el libro de códigos: `Annotated`, `Literal` y `| None` dicen **qué** valor entra
- Limpiar el formato en `before`; comprobar la regla en `after`
- Rechazar lo imposible sin corregirlo en silencio; lo raro pero real se marca
- Un modelo anidado registra qué unidad es de qué grupo; un error adentro rechaza el bloque
- El 422 explica: campo, valor, regla y motivo

???
Recordar que el capítulo es el más largo del curso: el material dice qué es de clase y qué de consulta, en «Antes de empezar».

## Práctica guiada: la puerta de entrada de un modelo ajustado

::: flujo
1. **Modelos anidados** — `Encuestado`, `RespuestaEncuesta` y `EncuestaCompleta`
2. **Rangos y validadores** — `Field` para lo simple; departamento, faltantes `before` y escala `model_validator`
3. **Rango estadístico** — rechazo justificado, con referencia declarada
4. **422 que se explica** — campo, valor, regla y motivo; sin 500 ante un `NaN`
5. **Dos endpoints** — `POST /encuestas` (201 o 422) y `GET /encuestas/resumen`
:::

::: info Sustentación
Puede usar IA, pero debe explicar y cambiar en vivo cualquier línea. Las 15 preguntas de la sección 9 guían la sustentación.
:::

???
Los 180 minutos de práctica: la actividad empieza en ella. El enunciado completo, con los requerimientos RF1 a RF5, la rúbrica (15, 20, 25, 15, 10 y 5 %, más 10 % de sustentación) y las seis evidencias, está en la sección 8 del material: proyectarlo desde ahí. El plazo, la plataforma y el peso los fija usted al abrir la actividad: en el material son campos por completar.
