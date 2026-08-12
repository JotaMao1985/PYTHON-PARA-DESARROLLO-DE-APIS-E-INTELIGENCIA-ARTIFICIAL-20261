/* Desborde horizontal a 375 px en TODOS los estados de un módulo.
 *
 * Cierra la limitación L2 del INFORME_AUDITORIA_TECNICA.md: medir sólo la vista
 * inicial no dice nada de un material que muestra una lección cada vez.
 *
 * Uso:
 *   1. python3 -m http.server 8123     (desde la raíz del repo)
 *   2. abrir el módulo, poner el viewport en 375 px
 *   3. pegar este archivo en la consola del navegador
 *
 * AVISO, y es la lección más cara de la Fase 1: **no fuerces `style.display` para
 * revelar secciones ocultas.** Saltarse la navegación del módulo produce un
 * layout que ningún usuario ve: en el módulo 7 daba 502 px de desborde falso,
 * y recorriendo el botón «Siguiente» el desborde real es 0. Mide siempre a
 * través de los controles de la propia página.
 */
(async () => {
  const de = document.documentElement;
  const pausa = ms => new Promise(r => setTimeout(r, ms));
  const medir = () => de.scrollWidth - de.clientWidth;

  const culpables = () => {
    const W = de.clientWidth, out = [];
    for (const el of document.querySelectorAll('body *')) {
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.right <= W + 1) continue;
      const cs = getComputedStyle(el);
      if (['auto', 'scroll'].includes(cs.overflowX)) continue;   // se desplaza solo
      let p = el.parentElement, tapado = false;
      while (p) {
        if (['auto', 'scroll', 'hidden'].includes(getComputedStyle(p).overflowX)) { tapado = true; break; }
        p = p.parentElement;
      }
      if (!tapado && out.length < 5) {
        out.push(el.tagName + '.' + (el.className || '').toString().slice(0, 45) +
                 ' →' + Math.round(r.right) + 'px');
      }
    }
    return out;
  };

  const seccionActiva = () => {
    const a = [...document.querySelectorAll('article')]
        .find(x => getComputedStyle(x).display !== 'none');
    return a ? (a.id || '(sin id)') : null;
  };

  const estados = [{estado: 'inicial', seccion: seccionActiva(), desborde: medir()}];

  // 1) Módulos por secciones: recorrer con el botón «Siguiente» del propio módulo
  for (let i = 0; i < 15; i++) {
    const sig = [...document.querySelectorAll('button, a')]
        .find(b => /Siguiente/i.test(b.innerText || '') && b.offsetParent !== null);
    if (!sig) break;
    sig.click();
    await pausa(160);
    estados.push({estado: 'siguiente ' + (i + 1), seccion: seccionActiva(), desborde: medir()});
  }

  // 2) Módulos SPA (React): recorrer los botones de lección
  const lecciones = [...document.querySelectorAll('button, [role="tab"]')]
      .filter(e => e.offsetParent !== null);
  for (let i = 0; i < Math.min(lecciones.length, 20); i++) {
    const etiqueta = (lecciones[i].innerText || lecciones[i].tagName).trim().slice(0, 30);
    try { lecciones[i].click(); } catch (e) { continue; }
    await pausa(120);
    estados.push({estado: etiqueta, desborde: medir()});
  }

  // 3) Plegables: abrirlos todos y volver a medir
  document.querySelectorAll('details').forEach(d => d.open = true);
  await pausa(150);
  estados.push({estado: 'todos los <details> abiertos', desborde: medir()});

  const peor = estados.reduce((a, b) => b.desborde > a.desborde ? b : a);
  const resultado = {
    titulo: document.title,
    ancho: de.clientWidth,
    estadosMedidos: estados.length,
    desbordeMaximo: peor.desborde,
    peorEstado: peor,
    conDesborde: estados.filter(e => e.desborde > 0),
    culpables: peor.desborde > 0 ? culpables() : []
  };
  console.log(resultado);
  return JSON.stringify(resultado);
})();
