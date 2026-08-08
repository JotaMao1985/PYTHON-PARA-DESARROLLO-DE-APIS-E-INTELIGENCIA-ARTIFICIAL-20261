# Portada Moodle — Python para APIs e IA (USTA 2026-II)

Piezas gráficas del aula Moodle. Construidas en **dos capas**: la ilustración de fondo se
genera con ComfyUI y el texto, el sello y la paleta se componen encima en HTML/CSS. Cambiar
el título o el semestre **no exige regenerar la ilustración**: basta editar `banner.html` y
volver a lanzar `render.py`.

## Entregables

| Archivo | Medida | Uso |
|---|---|---|
| `banner_1920x480.png` | 1920×480 (4:1) | Cabecera de la página del curso |
| `portada_1600x900.png` | 1600×900 (16:9) | Imagen de resumen / tarjeta del curso |

Activos intermedios: `fondo_banner.png`, `fondo_card.png` (ilustraciones sin texto, por si
se quieren reutilizar como *hero* en el HTML del syllabus) y `logo_usta_sello.png` (sello
recortado con transparencia).

## Reproducir las ilustraciones

Modelo **Flux schnell** (`flux1-schnell-Q4_K_S.gguf`), 1216×832, 4 pasos, guidance 3.5.
Local en Apple Silicon vía MPS; ~80 s por imagen.

Prompt exacto (idéntico para ambas, solo cambia la semilla):

```
A three-dimensional network graph floating in deep navy blue space. Luminous indigo and violet filaments connect glowing spherical nodes, with a few nodes glowing warm magenta. Foreground nodes are softly out of focus while the mid-ground structure stays crisp, creating strong depth. The lower left fades into near-black empty space. Elegant restrained editorial technology illustration, cinematic lighting, no text.
```

| Semilla | Salida | Por qué se eligió |
|---|---|---|
| **303** | `fondo_banner.png` | Franja del título genuinamente oscura; la malla ocupa el centro-derecha sin invadirla y el sello respira. |
| **101** | `fondo_card.png` | Malla repartida por todo el encuadre: envuelve la composición centrada de la tarjeta sin dejar mitades vacías. |

```bash
python3 ~/.claude/skills/comfyui-image/scripts/comfy_generate.py --model flux --width 1216 --height 832 --seed 303 --prompt 'A three-dimensional network graph floating in deep navy blue space. Luminous indigo and violet filaments connect glowing spherical nodes, with a few nodes glowing warm magenta. Foreground nodes are softly out of focus while the mid-ground structure stays crisp, creating strong depth. The lower left fades into near-black empty space. Elegant restrained editorial technology illustration, cinematic lighting, no text.'
```

## Regenerar los PNG finales

```bash
python3 scripts/portada/prep_logo.py
python3 scripts/portada/render.py --formato banner --fondo assets/portada/fondo_banner.png
python3 scripts/portada/render.py --formato card --fondo assets/portada/fondo_card.png --pos "center 62%"
python3 scripts/portada/verificar.py
```

## Decisiones registradas

- **Paleta: morado `#3D008D` → magenta `#ED1E79` sobre azul `#001A4D`**, coherente con el
  syllabus y los 13 módulos HTML del curso. El sello USTA usa su propia identidad (azul
  `#00478C` + rojo `#DF040B`); la diferencia es deliberada y se lee como co-branding.
- **Tipografía: Avenir Next** (600 para el título, 500 para la bajada). Solo hace falta en
  el equipo que renderiza; el entregable es PNG.
- **Transparencia del sello por geometría, no por color.** El original `Logo_USTA.png` es
  RGB sin alfa y sus blancos distan solo ~25 del fondo `(236,242,246)`: cualquier keying
  cromático semitransparenta la cruz blanca y el sello se ve gris sobre navy. Se enmascara
  con un disco antialiaseado.
- **La «zona tranquila» del título la crea el velo CSS, no el prompt.** Los modelos ignoran
  de forma poco fiable las instrucciones de composición espacial; el degradado de contraste
  garantiza la legibilidad pase lo que pase en la ilustración.
- **«Vigilada Mineducación» va como texto HTML**, no como ráster: a tamaño de banner la
  leyenda del PNG original sería ilegible.

## Verificación

`verificar.py` comprueba medida exacta, peso y **contraste real bajo cada texto**. Mide
sobre un re-render `--sin-texto` (fondo aislado), porque medir sobre el PNG final daría
blanco contra blanco. Última corrida:

| Pieza | Título | Bajada | Vigilada |
|---|---|---|---|
| `banner_1920x480.png` | 16.18:1 | 11.41:1 | 12.18:1 |
| `portada_1600x900.png` | 14.46:1 | 12.40:1 | 9.24:1 |

Umbrales WCAG AA: 3.0 (texto grande), 4.5 (texto normal).
