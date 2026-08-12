# Plan de mejora del **Proyecto_I** integrando la estrategia de inversión de los **"7 Bloques"**

**Autor del plan:** Javier Mauricio Sierra (asistido)
**Fecha:** 2026-05-13
**Versión:** 1.1 — universo **mixto USD+EUR** aprobado por el docente (2026-05-13)

---

## 0. Resumen ejecutivo

El **Proyecto_I** (curso *Python para APIs e IA* + *Teoría del Riesgo*, USTA 2026-I) ya tiene **Capas 1 y 2 implementadas y commiteadas** y **Capas 3, 4 y 5 con planes aprobados pero pendientes de ejecutar** (ver `Proyecto_I/PLAN_MEJORA_CAPA_3.md`, `_CAPA_4.md`, `_CAPA_5.md`).

El documento *"Análisis Integral y Evaluación Crítica de la Estrategia de los 7 Bloques"* propone una arquitectura de cartera que es un **caso de uso financiero excepcionalmente rico** para anclar el proyecto: ofrece selección concreta de activos (5 mínimos → cubrimos 7 bloques), problemas reales de riesgo (duración, contraparte, behavioral gap), y un protocolo de rebalanceo mecánico que da identidad a la sustentación oral.

Este plan **NO sustituye** los `PLAN_MEJORA_CAPA_*.md` existentes: los **enriquece y reorienta** convirtiendo los 7 Bloques en el **hilo narrativo** del backend, el dashboard y el informe ejecutivo.

> **Decisión de universo (aprobada por el docente)**: se trabaja con **mezcla USD + EUR**. Yahoo Finance da cobertura suficiente para tickers UCITS europeos (sufijos `.DE`, `.MC`, `.L`, `.MI`) y para los US estándar, así que se puede honrar la *letra* del análisis (iBonds EUR, Socimis, ETCs de oro europeos) **sin violar la restricción "datos vía API"** de la spec. La consecuencia técnica relevante: el sistema necesita una **tabla de tipos de cambio** y un mecanismo de **normalización a moneda base** (recomendado USD) para todos los cálculos agregados (VaR, frontera eficiente, rebalanceo).

---

## 1. Mapeo conceptual: 7 Bloques ↔ Capas del proyecto

| Bloque (análisis) | Peso | Proxy USD (Yahoo) | Alternativa EUR / UCITS (Yahoo) | Capa del Proyecto_I | Criterios |
|---|---|---|---|---|---|
| 1. Indexación pura | 35% | `VTI`, `VEA`, `VWO`, `IJR` | `EUNL.DE` (MSCI World), `IUSN.DE` (Small Caps), `EIMI.DE` (EM) | Capa 1 + Capa 2 (CAPM, Markowitz) | C1, C2, C4, C6 |
| 2. Value / Pricing Power | 20% | `MOAT`, `QUAL` | `IWMO.DE` (MSCI World Momentum), `IWQU.DE` (Quality) | Capa 2 + **Capa 4 (clasificador moat)** | C4, C11★★ |
| 3. Renta fija (Target Maturity) | 15% | `IEF`, `TLT` | **`IB26.DE` / `IB28.DE` / `IB30.DE`** (iBonds EUR Dec 2026/2028/2030) — *literalmente el ejemplo §3.4 del análisis* | **Capa 3 (NS, duración, bond ladder)** | C7★ |
| 4. Oro (lógica de contraparte) | 10% | `GLD`, `IAU` | `EGLN.L` o `4GLD.DE` (ETC físico EUR) | Capa 2 (correlación, VaR) + Capa 3 (stress) | C5, C9★ |
| 5. Inmuebles productivos | 10% | `VNQ`, `VNQI` | `IPRP.AS` (European Property REITs UCITS), o **Socimis directos**: `MRL.MC` (Merlin), `COL.MC` (Colonial) | Capa 2 + Capa 3 | C1, C5 |
| 6. Liquidez remunerada | 5% | `BIL`, `SHV` | `XEON.DE` (Xtrackers EUR Overnight) | Capa 1 + Capa 3 (curva FRED corta) | — |
| 7. Especulativo asimétrico | 5% | `BTC-USD`, `ARKK` | `BTCE.DE` (Bitcoin ETP EUR físico) | Capa 1 + Capa 2 (Cornish-Fisher) | C3★, C5 |

**Activos FX necesarios para la normalización**:

| Símbolo Yahoo | Uso |
|---|---|
| `EURUSD=X` | Conversión EUR→USD para agregar a moneda base |
| `GBPUSD=X` | Si se incluyen ETCs `.L` (London) |

**Total potencial**: ~22 tickers entre USD/EUR + 2 FX. Se recomienda **curar a 7–10 tickers cubriendo los 7 bloques** (con al menos uno EUR y uno USD por estética de tesis), para mantener costes de ingesta y testabilidad razonables. La spec exige mínimo 5 → cumplimos cómodamente.

> Referencias justificadoras:
> - *Análisis 7 Bloques*, §3 (descripción de cada bloque) y §3.4 (ejemplo literal del iBonds EUR Dec 2026, ISIN `IE000SIZJ2B2`, reproducido aquí como `IB26.DE`).
> - *Análisis 7 Bloques*, §5.4 (custodia bifurcada del oro → motiva incluir un ETC físico EUR junto al `GLD` USD).

---

## 2. Etapas del plan

> **Restricción temporal**: el plazo del proyecto es de **20 días calendario** (spec). Las etapas se diseñan para encajar **dentro** de la ejecución pendiente de Capas 3–5 y entregables finales, NO como trabajo adicional independiente.

### Etapa 1 — **Anclaje narrativo y selección de universo de activos** (días 1–2)

**Objetivo específico**
Convertir los 7 Bloques en el caso de uso oficial del proyecto: cerrar la lista de tickers (mezcla USD+EUR), documentar el mapeo bloque→proxy y dejar el universo cargado en la base SQLite con histórico ≥2 años vía Yahoo, **incluyendo serie diaria de tipos de cambio para normalización a moneda base**.

**Acciones concretas**
1. Crear `Proyecto_I/backend/app/domain/blocks.py` con:
   - `Enum Block` (7 valores).
   - `BLOCK_TICKERS: dict[Block, list[TickerSpec]]` donde `TickerSpec = (symbol, currency, market_calendar)`.
2. Añadir columnas en la tabla `Activo`:
   - `block: str` (FK suave al catálogo).
   - `currency: str` (`USD` | `EUR` | `GBP`).
   - `base_currency: str` (siempre `USD` en MVP).
3. Crear tabla nueva `TipoCambio` (fecha, par, rate) y poblarla con `EURUSD=X`, `GBPUSD=X` (si aplica) — todo vía la misma capa de ingesta.
4. Implementar **helper `to_base_currency(price, ticker_currency, date)`** que aplique el FX del día. *Centralizar aquí*: todos los cálculos agregados (Markowitz, VaR de portafolio, rebalanceo) consumen precios ya normalizados.
5. Ejecutar `seed_history` (ya existe tras T1.3) con la lista curada y validar que todos los tickers tengan ≥504 días hábiles de histórico **y que para cada fecha exista FX si el ticker no es USD**.
6. Documentar en `Proyecto_I/README.md` la **sección "Universo de inversión"** con: tabla bloque↔ticker, mezcla USD+EUR justificada, política de moneda base, y referencia al .docx fuente.

**Referencia explícita a las fuentes**
- *Análisis 7 Bloques*, §3.1–§3.8 (descripción de cada bloque).
- *Análisis 7 Bloques*, §5 (limitaciones del enfoque ETF/España → motiva proxies USD).
- *Spec Proyecto_I*, requisito "mínimo 5 activos, 2 años de histórico diario, datos vía API".

**Entregables esperados**
- `blocks.py` con tipos + tickers + pesos objetivo.
- Migración Alembic 0001 que añade `Activo.block`.
- Sección README "Universo de inversión" (≥1 página, con tabla).
- Histórico cargado en SQLite y verificado (consulta SQL anexa en el commit).

**Acceptance criteria**
- [ ] `pytest tests/domain/test_blocks.py` pasa: validación de pesos suma 100%, todos los bloques tienen ≥1 ticker.
- [ ] `select count(*) from Precio where ticker in (...)` ≥ `n_tickers * 504`.
- [ ] Para cada precio en EUR/GBP existe un FX rate del mismo día (`LEFT JOIN` no devuelve nulos).
- [ ] `to_base_currency(100.0, "EUR", "2026-04-01")` retorna el USD equivalente y un test verifica el orden de magnitud (~1.05–1.15× según fecha).
- [ ] README muestra la tabla en el render markdown.

**Riesgos y mitigación**
| Riesgo | Mitigación |
|---|---|
| Yahoo cambia o limita un ticker (p.ej. `MOAT` con cobertura corta) | Validar `start_date` real al hacer seed; sustituir por equivalente UCITS si <2 años. |
| Mezclar BTC (24/7) con ETFs (días hábiles) rompe joins de retornos | Normalizar a calendario de NYSE (`pandas_market_calendars`); descartar fines de semana en BTC. |
| Tickers EUR `.DE` cierran 1h antes que NYSE → desfase intradía | Trabajar SIEMPRE con cierre diario (`Close`), no intradía; documentar. |
| FX faltante en festivos cruzados (p.ej. festivo US pero EU abierto) | Forward-fill del último FX disponible (≤3 días); test que valide gap máximo. |
| iBonds `IB26.DE` se *liquida* en dic-2026 (dentro del horizonte del proyecto) | Documentarlo explícitamente: a partir de la fecha de liquidación, el activo entra en "modo cash" — útil narrativamente para explicar §3.4 del análisis en la sustentación. |
| Currency exposure no controlada infla volatilidad | Reportar **dos** series: rendimiento "moneda local" y "moneda base USD"; explicar el dual en el informe. |

---

### Etapa 2 — **Capa 3 enriquecida: renta fija con bond ladder + stress macro** (días 3–7)

**Objetivo específico**
Ejecutar `PLAN_MEJORA_CAPA_3.md` extendiéndolo con dos refinamientos directamente inspirados en el análisis: **(a) Bond Ladder paramétrico** para evitar el riesgo de reinversión, y **(b) Stress testing por shocks macro narrativos** (petróleo >120 USD, CBDC, represión financiera).

**Acciones concretas**
1. **Ejecutar T3.1–T3.N** según el plan ya aprobado (Nelson-Siegel sobre FRED, duración, convexidad, Black-Scholes + Greeks).
2. **Añadir endpoint `/renta-fija/bond-ladder`** con parámetros:
   - `total_assignment: Decimal` (p.ej. 0.15 del patrimonio).
   - `rungs: int` (3–5 escalones).
   - `start_year: int`, `years_step: int`.
   - `instrument_set: Literal["synthetic", "ibonds_eur"]` — **`ibonds_eur` usa los tickers reales** (`IB26.DE`, `IB28.DE`, `IB30.DE`...) y demuestra la mecánica del análisis sobre instrumentos existentes; `synthetic` calcula peldaños desde Nelson-Siegel sobre la curva FRED.
   - Devuelve: lista de peldaños con cupón estimado, duración por peldaño y duración promedio ponderada, en **moneda base** (USD) con conversión FX explícita.
3. **Extender el endpoint `/stress`** con 3 *escenarios narrativos* nominados:
   - `oil_shock_120`: shock paralelo de +150 bps en curva + caída -15% renta variable (justifica con §1.2 del análisis: "petróleo >120 USD → +1.5 pp inflación").
   - `cbdc_capital_controls`: ampliación de spread corporativo +200 bps + caída -25% BTC (refleja §3.8: regulación CBDC).
   - `financial_repression`: tasas reales negativas (curva -100 bps) + oro +20%.
4. Tests unitarios + de integración en `tests/test_bond_ladder.py` y `tests/test_stress_scenarios.py`.
5. Documentar los 3 escenarios en `docs/stress_scenarios.md` con la cita a la sección correspondiente del .docx.

**Referencia explícita a las fuentes**
- *Análisis 7 Bloques*, §3.4 (Target Maturity ETFs, mecánica operativa).
- *Análisis 7 Bloques*, §5.3 (recomendación explícita de Bond Ladder por riesgo de reinversión).
- *Análisis 7 Bloques*, §1.2 (shock de petróleo y estanflación).
- *Spec Proyecto_I*, criterios C7★ (renta fija, 6%) y C9★ (stress testing, 3%).
- *PLAN_MEJORA_CAPA_3.md*, alcance original.

**Entregables esperados**
- 2 nuevos endpoints documentados en OpenAPI: `/renta-fija/bond-ladder`, `/stress` extendido.
- ≥6 tests nuevos (3 por endpoint, golden path + edge).
- `docs/stress_scenarios.md`.
- Commit-link en `cerebro/proyectos/capa-3-plan-mejora-rf-derivados.md`.

**Acceptance criteria**
- [ ] `GET /renta-fija/bond-ladder?rungs=3&start_year=2027` devuelve 3 peldaños con duraciones decrecientes-crecientes consistentes.
- [ ] Los 3 escenarios narrativos producen P&L plausibles (signo y orden de magnitud) sobre la cartera demo.
- [ ] Coverage de `app/services/bond_ladder.py` ≥85%.

**Riesgos y mitigación**
| Riesgo | Mitigación |
|---|---|
| El estudiante no puede defender la "ingeniería" del Bond Ladder en oral | Anexar diagrama en `docs/` + sección en el informe ejecutivo. |
| Stress macros vistos como "arbitrarios" | Cada escenario lleva en docstring la cita literal del .docx que lo justifica. |
| Duración + convexidad con NS dan inconsistencias en plazos cortos | Cap inferior 1m, cap superior 30y; tests de monotonicidad. |

---

### Etapa 3 — **Capa 4 enriquecida: ML del Pricing Power + alerta Behavioral Gap** (días 8–12)

**Objetivo específico**
Ejecutar `PLAN_MEJORA_CAPA_4.md` dando al pipeline ML un **propósito analítico no-trivial** alineado con el análisis: **clasificar la "fortaleza de moat" de un activo** (proxy del Bloque 2) y **emitir alertas de behavioral gap** cuando el comportamiento del usuario se desvía de la doctrina del rebalanceo del 20%.

**Acciones concretas**
1. **Ejecutar T4.1–T4.N** del plan aprobado (train → joblib → Singleton → `/predict`, `PredictionLog`).
2. **Definir el target del modelo "Moat Classifier"**:
   - Features: márgenes operativos rolling 8 trimestres (vía Alpha Vantage `OVERVIEW`), volatilidad de márgenes, persistencia de ROE, beta vs `SPY`.
   - Label: 3 clases (`NO_MOAT`, `NARROW_MOAT`, `WIDE_MOAT`) derivadas heurísticamente de membership en `MOAT`/`QUAL` ETFs holdings + reglas (margen >25% sostenido N trimestres).
   - Modelo: `RandomForestClassifier` o `GradientBoosting` (no LSTM en MVP; LSTM va a bonificación).
3. **Endpoint `/predict/moat?ticker=XXX`** que retorna clase + probabilidades + features usadas (para explicabilidad).
4. **Endpoint `/alertas/behavioral-gap`**:
   - Lee el `PortafolioSnapshot` actual del usuario.
   - Compara pesos vs objetivos por bloque.
   - Si algún bloque excede ±20% relativo → emite alerta con la **acción mecánica obligatoria** (vender ganador / comprar perdedor).
   - Log estructurado en `BehavioralAlert` (tabla nueva).
5. **Bonificación drift (+0.5)**: `PSI` (Population Stability Index) sobre features de moat, alerta si PSI>0.2.
6. Tests con datos sintéticos (no fallar si Alpha Vantage da rate-limit).

**Referencia explícita a las fuentes**
- *Análisis 7 Bloques*, §3.2 (Pricing Power, foso defensivo, métricas EBIT).
- *Análisis 7 Bloques*, §2.2 (Behavioral Gap / Dalbar, FOMO/pánico).
- *Análisis 7 Bloques*, §4.1 (Doctrina del Rebalanceo, Regla del 20%).
- *Análisis 7 Bloques*, §5.2 (Smart Beta Factor → motiva el clasificador como sustituto algorítmico del stock picking).
- *Spec Proyecto_I*, criterios C11★★ (ML pipeline, 7%) y bonificación drift (+0.5).

**Entregables esperados**
- `app/ml/moat_classifier.py` + modelo `.joblib` versionado.
- Endpoints `/predict/moat`, `/alertas/behavioral-gap`.
- Migración Alembic 0002 → `BehavioralAlert`.
- Notebook `notebooks/03_moat_training.ipynb` reproducible.
- ≥15 tests (unit + integration + drift).

**Acceptance criteria**
- [ ] `cv_accuracy` ≥ 0.65 con datos reales (no sintéticos), o se justifica downgrade en el informe.
- [ ] `/alertas/behavioral-gap` dispara correctamente con un portafolio test desbalanceado al 130%.
- [ ] PSI test con datos shuffleados emite alerta drift.
- [ ] Singleton del modelo no se recarga entre requests (verificado con log).

**Riesgos y mitigación**
| Riesgo | Mitigación |
|---|---|
| Métricas fundamentales de Alpha Vantage limitadas (rate-limit 25/día free) | Snapshot cacheado offline en `data/fundamentals_snapshot.parquet`; refresh manual semanal. |
| Modelo trivial overfittea sobre features pobres | Stratified K-fold + `class_weight=balanced` + ablation study en notebook. |
| El "moat" no es un concepto observable directamente → label noisy | Documentar honestamente la heurística de labeling; presentar como **proxy supervisado**, no ground truth. |
| Behavioral Gap necesita historia de portafolio → no la hay al inicio | Sembrar 6 meses de `PortafolioSnapshot` sintéticos en seed para demo. |

---

### Etapa 4 — **Capa 5 + endpoint `/rebalanceo`: la regla del 20% como API ejecutable** (días 13–16)

**Objetivo específico**
Ejecutar `PLAN_MEJORA_CAPA_5.md` (infraestructura, Docker, Render, CI) **y** añadir el endpoint que **materializa** la doctrina central del análisis: el rebalanceo mecánico por umbral del 20%.

**Acciones concretas**
1. **Ejecutar T5.1–T5.N** del plan aprobado (pytest+TestClient, Docker multi-stage <200MB, Render deploy, GitHub Actions).
2. **Endpoint `POST /rebalanceo/calcular`**:
   - Body: `portfolio_id`, `threshold_pct: float = 20`.
   - Lógica: convierte todas las posiciones a **moneda base (USD)** usando el FX del último día disponible; compara pesos por bloque vs pesos objetivo; si desviación relativa >threshold → genera **órdenes simuladas** (qué vender, qué comprar, en cuánto).
   - Las órdenes se devuelven en moneda base y, para tickers no-USD, también en moneda nativa del activo (auxiliar para la UI).
   - Devuelve lista de `Trade` (ticker, action, qty, est_price_usd, est_price_native, currency, block_target_after).
3. **Endpoint `POST /rebalanceo/aplicar`**: ejecuta las órdenes simuladas (registra en `RebalanceLog`, actualiza posiciones).
4. **Bonificación Alembic (+0.5)**: todas las migraciones de este plan (`0001_block`, `0002_behavioral_alert`, `0003_rebalance_log`) bajo Alembic versionado.
5. **CI**: GitHub Actions corre lint (`ruff`) + tests + build Docker + push a `ghcr` (opcional).
6. **Deploy en Render**: el docente configura UI; el estudiante asegura `render.yaml` correcto y `Dockerfile` listo.

**Referencia explícita a las fuentes**
- *Análisis 7 Bloques*, §4.1 (Regla del 20% literal: "intervenir únicamente cuando un bloque se desvía más de un 20% en términos relativos").
- *Análisis 7 Bloques*, §2.2 (rebalanceo automatiza prudencia, neutraliza FOMO).
- *Spec Proyecto_I*, criterios C10★ (Backend, 10%), C12★ (Tests, 3%), C13★★ (Docker+deploy+CI, 6%) y bonificación Alembic.

**Entregables esperados**
- 2 endpoints documentados en OpenAPI con ejemplos.
- Migración Alembic 0003 → `RebalanceLog`.
- `.github/workflows/ci.yml` verde.
- URL pública en Render funcionando.
- ≥10 tests nuevos (cálculo, idempotencia, threshold edges).

**Acceptance criteria**
- [ ] Portfolio con desviación 19% NO dispara trades; con 21% sí (boundary test).
- [ ] La suma de USD vendidos = USD comprados ± fees simulados (conservación de capital).
- [ ] `docker build .` produce imagen <200 MB.
- [ ] CI corre en PR y bloquea merge si falla.
- [ ] Imagen desplegada en Render responde `/health` en producción.

**Riesgos y mitigación**
| Riesgo | Mitigación |
|---|---|
| Free-tier de Render duerme la app → cold start 30s | Documentar en README; mantener `/health` simple; ping cron opcional. |
| Rebalanceo con precios stale (último cierre) confunde al evaluador | Mostrar timestamp explícito en la respuesta; doc claro de "simulación, no broker real". |
| Bonificación Alembic se duplica con migraciones SQLAlchemy `metadata.create_all` | Eliminar el `create_all` y migrar todo (con `alembic upgrade head` en startup dev). |

---

### Etapa 5 — **Dashboard 7-Bloques + informe ejecutivo + sustentación** (días 17–20)

**Objetivo específico**
Cerrar los 3 entregables que aún quedan (frontend, informe PDF, sustentación oral 20–25 min) **usando la narrativa de los 7 Bloques como hilo conductor** y demostrando en vivo el flujo: ingesta → análisis clásico → renta fija/stress → ML/alerta → rebalanceo.

**Acciones concretas**
1. **Dashboard** (Streamlit recomendado por simplicidad — Dash si se quiere bonificar UX):
   - Pestaña 1: **"Mi cartera vs 7 Bloques"** (donut con pesos actuales vs objetivos).
   - Pestaña 2: **Volatilidad, VaR, CVaR, Kupiec** por activo y por bloque.
   - Pestaña 3: **Renta fija**: curva NS interactiva + bond ladder visual.
   - Pestaña 4: **Stress**: selector de los 3 escenarios narrativos + waterfall de P&L.
   - Pestaña 5: **ML Moat**: input ticker → predicción + probabilidades + SHAP-light (top features).
   - Pestaña 6: **Rebalanceo**: botón "Calcular" → tabla de trades → "Aplicar".
2. **Informe ejecutivo (≤5 páginas)** con estructura:
   - Marco macro y motivación (síntesis del §1 del análisis).
   - Arquitectura técnica (5 capas + diagrama).
   - Resultados financieros sobre el universo elegido.
   - Sección obligatoria "Uso de herramientas de IA".
   - Limitaciones (incluida la sustitución USD).
3. **Sustentación oral** (script de 22 min):
   - 3 min motivación (capítulo 1 del análisis).
   - 12 min demo en vivo (flujo 6 pestañas).
   - 4 min ML + rebalanceo (criterios de mayor peso).
   - 3 min Q&A preparada (incluye "¿por qué USD?", "¿qué tan robusto es el moat classifier?", "¿qué falla en el behavioral gap?").
4. **Buenas prácticas** (C15, 5%): pulir README, `.env.example`, `LICENSE`, badges CI.

**Referencia explícita a las fuentes**
- *Análisis 7 Bloques*, §1 (marco macro, hilo narrativo de apertura).
- *Análisis 7 Bloques*, §3 (tabla y descripción → estructura del dashboard).
- *Análisis 7 Bloques*, §5 (limitaciones → sección honesta del informe).
- *Spec Proyecto_I*, entregables 2, 4, 5, 6 + criterios C14 (3%), C15 (5%), C16 (15%).

**Entregables esperados**
- `Proyecto_I/frontend/app.py` (Streamlit) consumiendo backend público.
- `Proyecto_I/docs/Informe_Ejecutivo.pdf` (≤5 páginas).
- `Proyecto_I/docs/Sustentacion_Script.md` con timing + slides clave.
- README final con badges (CI verde, imagen Docker, URL Render).

**Acceptance criteria**
- [ ] El dashboard arranca con `streamlit run app.py` sin variables hardcodeadas.
- [ ] Cada pestaña conecta a su endpoint y muestra datos reales (no mocks).
- [ ] Demo completa en <12 min (ensayar con cronómetro).
- [ ] Informe revisado para que no exceda 5 páginas.

**Riesgos y mitigación**
| Riesgo | Mitigación |
|---|---|
| Dashboard depende de Render dormido → demo lenta | Pre-calentar 10 min antes; tener captura como fallback. |
| El estudiante no sabe defender el moat classifier en oral | Ensayar Q&A; sección "Limitaciones" honesta en el informe. |
| Informe se infla más allá de 5 páginas | Tablas en lugar de párrafos; figuras compactas; revisión de longitud al 60%, 80%, 100%. |
| Política de IA: README sin sección obligatoria → pérdida fácil de puntos en C15 | Plantilla "Uso de IA" preparada desde el día 1. |

---

## 3. Cronograma consolidado (20 días)

| Días | Etapa | Capa(s) afectada(s) | Criterios principales en juego |
|---|---|---|---|
| 1–2 | Etapa 1: Anclaje narrativo | Capa 1 + dominio | — (base) |
| 3–7 | Etapa 2: Capa 3 + bond ladder + stress | Capa 3 | C7★, C9★ |
| 8–12 | Etapa 3: Capa 4 + moat + behavioral gap | Capa 4 | C11★★, +0.5 drift |
| 13–16 | Etapa 4: Capa 5 + `/rebalanceo` | Capa 5 + Capa 2 | C10★, C12★, C13★★, +0.5 Alembic |
| 17–20 | Etapa 5: Dashboard + informe + sustentación | Frontend + entregables | C14, C15, C16 |

> Si se atrasa 1–2 días, **sacrificar primero las bonificaciones** (drift PSI, Alembic), no la sustentación.

---

## 4. Checkpoints de verificación (no negociables)

| Checkpoint | Cuándo | Qué debe estar verde |
|---|---|---|
| **CP1: Universo cargado** | Fin día 2 | Tests Etapa 1 pasan; histórico ≥504 días en BD para todos los tickers. |
| **CP2: Renta fija + stress** | Fin día 7 | Endpoints `/renta-fija/bond-ladder` y `/stress` extendidos; tests verdes; doc en `docs/`. |
| **CP3: ML + behavioral** | Fin día 12 | Modelo entrenado con `cv_accuracy` reportado; `/alertas/behavioral-gap` funcional; PSI implementado. |
| **CP4: Backend completo** | Fin día 16 | API en Render; CI verde; rebalanceo end-to-end; coverage ≥80%. |
| **CP5: Listo para defender** | Fin día 19 | Demo grabada como backup; informe revisado por terceros; ensayo cronometrado <23 min. |

---

## 5. Riesgos transversales

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Equipo de 2 personas → coordinación de submódulo `Proyecto_I` | Media | Alto | Branch por integrante, PRs revisados, no commits directos a `main`. |
| Yahoo / Alpha Vantage caen durante demo en vivo | Baja | Alto | Cache local en SQLite con `last_known_good`; preferir datos en caché para la demo. |
| Sustentación: pregunta "¿defina behavioral gap?" sin preparación | Media | Alto | Sección §2.2 del análisis al pie del script de sustentación; ensayar respuesta de 30s. |
| Falta de tiempo → tentación de bypassar tests | Alta | Alto | Política dura: ningún commit a `main` sin tests pasando en CI; el plan invierte en testing temprano. |
| Mapeo bloque↔proxy se cuestiona como "no defendible" | Media | Medio | Tabla de justificación explícita en README; referencia a §5 del análisis (limitaciones del enfoque ETF). |
| El docente quiere instrumentos europeos | Baja | Alto | Plan B documentado: si se exige EUR, pivot a Stooq/Investpy + assumir penalización por API menos estándar. |

---

## 6. Dudas y sugerencias

### 6.1 Dudas concretas a resolver con el docente / cliente

1. ~~¿Acepta el docente la sustitución USD?~~ **RESUELTO (2026-05-13)**: el docente aprueba **mezcla USD+EUR**. Se honra la letra del análisis (iBonds EUR, Socimis, ETCs físicos europeos) y se añade una capa de FX para normalización a moneda base USD. Consecuencias incorporadas en §1 (tabla con columna EUR), Etapa 1 (tabla `TipoCambio` + helper `to_base_currency`) y Etapa 4 (rebalanceo en moneda base).
2. **¿La rúbrica admite "ampliación de scope" como bonificación o solo lo listado (LSTM, JWT, websockets, drift, Alembic)?** Si admite más, el endpoint `/rebalanceo` por sí solo podría puntuar como bonificación adicional.
3. **¿El frontend obligatorio es Streamlit, Shiny o Dash?** La spec dice "uno de los tres"; este plan recomienda Streamlit por velocidad pedagógica.
4. **¿"Mínimo 5 activos" significa 5 tickers o 5 clases de activo?** Este plan asume 5 tickers (interpretación más exigente).
5. **¿Se permite que el modelo ML use snapshot offline de fundamentales** (por rate-limit de Alpha Vantage free) **mientras los precios sí sean live**? Este plan lo asume, pero conviene confirmar para defender el criterio "datos vía API, no estáticos".

### 6.2 Sugerencias adicionales para el éxito

- **Versionar el dataset**: cada experimento ML debe escribir un `MANIFEST.json` con hash del dataset usado, fecha, métricas. Es trivial y blinda la defensa oral.
- **Tablero financiero ≠ tablero técnico**: la sustentación valdrá más si el dashboard *cuenta una historia* (un usuario invierte → ve su cartera vs 7 bloques → recibe alerta → ejecuta rebalanceo) en lugar de exponer 16 endpoints sueltos.
- **No sobre-vender el moat classifier**: ser explícito en el informe sobre que es un **proxy supervisado por reglas heurísticas**, no un oráculo. Esto convierte una potencial debilidad en una muestra de honestidad metodológica (suma puntos en C16).
- **Aprovechar `cerebro/proyectos/`**: las notas vivas del vault Obsidian son material excelente para nutrir las secciones del informe; conectarlas con `[[wikilinks]]` antes de cerrar el PDF.
- **Test del informe**: dárselo a leer a un compañero ajeno al proyecto antes de entregar. Si entiende el flujo en 10 minutos, está listo.

### 6.3 Carencias de información que el plan ha tenido que asumir

- **Estado real del trabajo de equipo**: el plan asume que el estudiante trabajará solo o que el compañero está sincronizado; no se sabe la distribución actual de tareas.
- **Capacidad de ML en máquina docente**: la memoria menciona que el modelo se reentrenará "en máquina docente para datos reales"; este plan asume que esa máquina existe y está disponible al menos los días 10–11.
- **Plazo exacto de entrega**: la memoria dice "20 días"; este plan asume que arrancan hoy (2026-05-13) y entregan el 2026-06-02.
- **Disponibilidad de API keys**: Alpha Vantage y FRED requieren keys; el plan asume que están en `.env` y funcionan.
- **Render free tier**: el plan asume que sigue siendo gratuito y permite Docker; si cambió la política, hay que pivotar a Fly.io o Railway.

---

## 7. Trazabilidad: este plan vs documentos de origen

| Sección de este plan | Inspirada por (origen) |
|---|---|
| §1 Mapeo bloques↔capas | *Análisis 7 Bloques*, §3 + *Spec Proyecto_I*, arquitectura de 5 capas |
| Etapa 1 (universo) | *Análisis*, §3.1–§3.8 + *Spec*, "mínimo 5 activos" |
| Etapa 2 (bond ladder) | *Análisis*, §3.4 + §5.3 |
| Etapa 2 (stress narrativo) | *Análisis*, §1.2, §3.8 |
| Etapa 3 (moat classifier) | *Análisis*, §3.2 + §5.2 |
| Etapa 3 (behavioral gap) | *Análisis*, §2.2 + §4.1 |
| Etapa 4 (regla del 20%) | *Análisis*, §4.1 (literal) |
| Etapa 4 (Alembic / Docker / CI) | *Spec Proyecto_I*, C13★★ + `PLAN_MEJORA_CAPA_5.md` |
| Etapa 5 (dashboard + informe) | *Spec Proyecto_I*, entregables 2, 5, 6 |
| §6 Dudas y sugerencias | Política del skill `planning-and-task-breakdown` (Surface assumptions) |

---

**Próximo paso recomendado:**
revisar este plan con el docente, confirmar los 5 puntos de §6.1, y si todo está bien, **arrancar la Etapa 1** mañana lunes con la creación de `blocks.py` y la migración Alembic 0001.
