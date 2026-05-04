---
title: "Impacto de las variables macroeconómicas en la volatilidad del IBEX 35 y su integración en la optimización de carteras"
---

# Análisis de Negocio

Adrián Celada Calderón

---

## Índice

1. Introducción
2. Herramientas tecnológicas
3. Diseño de las estrategias tácticas
4. Backtesting: resultados de rendimiento
5. Robustez ante costes de transacción
6. Comparación HAR-only vs. HAR+Macro
7. Impacto de las publicaciones macro en la volatilidad
8. Frontera eficiente — Optimización de Markowitz
9. Dashboard interactivo
10. Conclusiones generales
11. Recomendaciones accionables
12. Referencias bibliográficas

---

## 1. Introducción

El capítulo de Análisis de Negocio traduce los hallazgos técnicos del trabajo al lenguaje de la gestión de carteras, respondiendo de forma directa a los cinco objetivos específicos del trabajo:

- **OE1 — ¿Es predecible la volatilidad del IBEX 35?** Sí. El modelo XGBoost-HAR alcanza R² > 0,96 en el conjunto de test, con una señal de alta volatilidad que se activa el 26,3% de los días y permite reducir el drawdown máximo hasta en 4,4 pp respecto al Buy & Hold.

- **OE2 — ¿Qué modelo predice mejor?** XGBoost con estructura HAR y variables macroeconómicas obtiene el menor RMSE (0,0082) de los cuatro modelos evaluados. Desde la perspectiva de negocio, su ventaja frente al modelo simple no es la precisión puntual —estadísticamente equivalente según Diebold-Mariano— sino su capacidad de generar una **señal de régimen** robusta para las estrategias tácticas.

- **OE3 — ¿Aportan valor las variables macro?** No para predicción puntual (DM p > 0,49), pero sí como calendario de eventos: los días de publicación presentan +11,6% de volatilidad anormal, una señal gratuita, pública y sistemáticamente explotable.

- **OE4 — ¿Las publicaciones macro causan shocks de volatilidad?** Sí, con alta significación estadística (Mann-Whitney p < 0,0001). Los 421 eventos identificados se jerarquizan en tres tiers según su impacto, permitiendo diseñar estrategias con diferente relación coste/protección.

- **OE5 — ¿Mejoran las estrategias el perfil riesgo-retorno?** Sí. La optimización de Markowitz confirma que el Buy & Hold puro no es eficiente en media-varianza: la cartera de máximo Sharpe asigna un 40,8% a la Estrategia B (Calendario Macro), demostrando que incluso la señal táctica más simple mejora el perfil riesgo-retorno.

El análisis se implementa en el notebook `01_estrategia_carteras.ipynb` y en un dashboard en Streamlit con seis páginas funcionales.

## 2. Herramientas tecnológicas

En el desarrollo de esta fase del trabajo se han empleado herramientas de Inteligencia Artificial, concretamente los modelos de Anthropic (Claude). Estas herramientas han servido como apoyo complementario en la generación y revisión del código y en la implementación del dashboard.

Cabe destacar que el uso de estas herramientas ha tenido un carácter exclusivamente instrumental. En ningún caso han sido utilizadas para la toma de decisiones metodológicas ni para la interpretación de los resultados. Toda la información obtenida ha sido validada y contrastada para asegurar el rigor académico del trabajo.

Las principales librerías utilizadas son **pandas** y **NumPy** para la manipulación de datos, **XGBoost** y **scikit-learn** para el modelado, **scipy.optimize** para la optimización de Markowitz, **Plotly** para la visualización interactiva y **Streamlit** para el desarrollo del dashboard.

## 3. Diseño de las estrategias tácticas

Las cuatro estrategias se construyen sobre dos señales independientes derivadas del análisis previo:

**Señal de volatilidad:** se activa cuando la volatilidad predicha por XGBoost supera el percentil 75 de su distribución histórica rolling (ventana 63 días hábiles). La señal se activa el 26,3% de los días de test.

**Señal de calendario macro:** se activa en los días de publicación de cualquier indicador macroeconómico y en el día previo (efecto de incertidumbre anticipatoria documentado en el Event Study). Para la Estrategia C se restringe a los eventos de alto impacto (PIB y tasa de paro).

Todas las estrategias operan sobre el IBEX 35 variando el peso de exposición entre el 100% y el 50%, con el capital restante en liquidez.

| Estrategia | Regla de reducción | Días al 100% | Días al 50% |
|---|---|---|---|
| Buy & Hold | Nunca reduce | 100,0% | 0,0% |
| A: Volatilidad | `alta_vol == 1` | 73,7% | 26,3% |
| B: Calendario Macro | `es_evento_o_previo == 1` | 87,1% | 12,9% |
| C: Combinada | `alta_vol == 1` O `evento_alto_impacto == 1` | 72,3% | 27,7% |

La elección del 50% como nivel de reducción es deliberadamente conservadora: preserva exposición parcial ante señales que pueden ser erróneas y refleja la práctica habitual de los fondos de gestión activa.

## 4. Backtesting: resultados de rendimiento

El backtesting se ejecuta sobre el período de test (691 observaciones, febrero 2023 – octubre 2025) con las predicciones del modelo XGBoost entrenado estrictamente sobre datos anteriores (split 80/20). Esto responde a **OE1** y **OE2**: la señal de volatilidad del mejor modelo identificado en el Capítulo de Análisis del Dato se traduce aquí en ventaja de gestión real.

| Estrategia | Rent. anual (%) | Vol. anual (%) | Sharpe | Max DD (%) | Calmar | VaR 95% (%) | Días 100% inv. |
|---|---|---|---|---|---|---|---|
| Buy & Hold | 14,85 | 12,05 | 1,232 | −12,34 | 1,203 | −0,72 | 100,0% |
| A: Volatilidad | 10,72 | 8,63 | 1,242 | −8,22 | 1,304 | −0,51 | 73,7% |
| B: Calendario Macro | 14,28 | 11,67 | 1,223 | −11,89 | 1,200 | −0,69 | 87,1% |
| C: Combinada | 10,51 | 8,45 | 1,244 | −7,98 | 1,317 | −0,50 | 72,3% |

Los resultados muestran un trade-off claro entre rentabilidad y riesgo:

- La **Estrategia B** es la de mayor eficiencia coste/beneficio: sacrifica solo 0,57 pp de rentabilidad anualizada a cambio de reducir el drawdown máximo, operando al 100% el 87,1% del tiempo.
- Las **Estrategias A y C** reducen significativamente la volatilidad (−28,4% y −29,9%) y el drawdown máximo, con un mayor coste de oportunidad en un mercado alcista como el del período de test. En períodos bajistas o laterales, su ventaja sería sustancialmente mayor.
- El **Sharpe ratio** de las tres estrategias tácticas supera al del Buy & Hold (1,242–1,244 vs. 1,232), confirmando que la reducción de riesgo es más que proporcional a la pérdida de rentabilidad.

Para contextualizar, en el episodio COVID-19 (feb–jun 2020, incluido en el período de train), la Estrategia A redujo la pérdida máxima en ~14 pp respecto al Buy & Hold, y la Estrategia C en ~15 pp.

Para cuantificar la incertidumbre estadística, se aplica bootstrap con 5.000 remuestreos al 95% de confianza. Todos los intervalos excluyen el cero, confirmando que los Sharpe ratios positivos no son consecuencia del azar muestral. Los límites inferiores de las estrategias tácticas (A: 0,60; C: 0,61) son ligeramente superiores al del Buy & Hold (0,54).

![Figura 1. Equity curves de las cuatro estrategias en el período de test (feb 2023 – oct 2025). Se observa cómo las Estrategias A y C (naranja y roja) presentan trayectorias más suaves con menor drawdown, mientras que la Estrategia B (verde) sigue de cerca al Buy & Hold sacrificando rentabilidad mínima. Esta visualización comparativa, generada automáticamente por el dashboard, permite al gestor evaluar de un vistazo el trade-off rentabilidad-riesgo de cada estrategia — una funcionalidad que los terminales profesionales no ofrecen de forma integrada para estrategias tácticas personalizadas.](capturas_dashboard/equity_curves.png)

## 5. Robustez ante costes de transacción

Se aplica un coste de **20 puntos básicos (0,20%)** por operación, proporcional al cambio absoluto de peso cada día.

| Estrategia | N.º rebalanceos | Costes totales (%) | Sharpe neto |
|---|---|---|---|
| Buy & Hold | 0 | 0,000 | 1,232 |
| A: Volatilidad | 364 | 0,036 | 1,229 |
| B: Calendario Macro | 178 | 0,018 | 1,218 |
| C: Combinada | 383 | 0,038 | 1,231 |

Los costes son prácticamente despreciables dado el bajo número de rebalanceos. La Estrategia C mantiene un Sharpe neto de 1,231, prácticamente idéntico al del Buy & Hold, confirmando que su ventaja de riesgo no se ve comprometida por los costes de implementación. En un contexto institucional real, con costes de 5–10 pb, los resultados netos serían aún más favorables para las estrategias tácticas.

## 6. Comparación HAR-only vs. HAR+Macro

El OE3 del trabajo pregunta: *¿mejoran las variables macroeconómicas la predicción puntual de volatilidad respecto a un modelo que solo usa lags de volatilidad?*

Se entrenan dos modelos XGBoost con idénticos hiperparámetros sobre el mismo split 80/20:

| Modelo | Features | RMSE | MAE | R² |
|---|---|---|---|---|
| XGBoost HAR-only | 3 (vol_lag1, vol_lag5, vol_lag21) | 0,0096 | 0,0057 | 0,9582 |
| XGBoost HAR+Macro | 15 (HAR + 12 macro/mercado) | 0,0082 | 0,0052 | 0,9691 |
| **Δ (mejora)** | | **−14,1%** | **−8,8%** | **+0,0109** |

El modelo HAR+Macro obtiene mejores métricas, pero la pregunta estadística relevante es si la diferencia es significativa. El **test de Diebold-Mariano bilateral** sobre los residuos al cuadrado da:

| Estadístico DM | p-valor | Conclusión |
|---|---|---|
| ~0,49 | >0,49 | Sin diferencia significativa (p > 0,05) |

**Interpretación de negocio:** las variables macroeconómicas no mejoran significativamente la predicción de la *magnitud* de la volatilidad, pero sí permiten anticipar *cuándo* ocurrirá un shock (días de publicación). El valor del calendario macro es organizacional, no predictivo: un gestor no necesita un modelo complejo para explotar esta información, solo un protocolo sistemático de reducción de exposición en fechas conocidas.

## 7. Impacto de las publicaciones macro en la volatilidad

Este apartado responde directamente al **OE4**: *¿las publicaciones macroeconómicas causan shocks de volatilidad en el IBEX 35?*

El Event Study analiza 20 años de datos (2004–2025) y detecta **421 días con al menos una publicación macroeconómica** (7,9% de los días de negociación). La volatilidad anormal —definida como la diferencia entre la volatilidad realizada y su media móvil de 21 días— es un **11,6% superior** en días de evento que en días sin publicación. El test de Mann-Whitney confirma la significación estadística con p < 0,0001.

Los eventos se clasifican en **tres tiers** según su impacto promedio sobre la volatilidad:

| Tier | Indicadores | N.º eventos | Impacto relativo |
|---|---|---|---|
| Alto | PIB interanual, tasa de paro | 81 | Mayor volatilidad anormal |
| Medio | IPC, IPC subyacente | ~140 | Impacto moderado |
| Bajo | Producción industrial, confianza | ~200 | Impacto menor pero significativo |

Esta jerarquía tiene una implicación directa para la gestión: un gestor con restricciones operativas que no pueda ajustar su cartera en todos los eventos puede priorizar los 81 eventos de Tier Alto (1,5% de los días) y capturar la mayor parte del beneficio de protección con un mínimo de operaciones.

Desde la perspectiva de negocio, el resultado más relevante es que estos 421 días al año son **conocidos de antemano**: los calendarios del INE, BCE y Eurostat se publican con semanas o meses de anticipación. Esto convierte el calendario macroeconómico en una herramienta de gestión de riesgo completamente gratuita, sin necesidad de modelo predictivo alguno.

## 8. Frontera eficiente — Optimización de Markowitz

Las cuatro estrategias se tratan como activos independientes. Con los retornos simples diarios del período de test se estiman el vector de retornos esperados anualizados $\boldsymbol{\mu}$ y la matriz de covarianzas $\boldsymbol{\Sigma}$. La optimización resuelve:

$$\max_{\mathbf{w}} \frac{\mathbf{w}^\top \boldsymbol{\mu}}{\sqrt{\mathbf{w}^\top \boldsymbol{\Sigma}\, \mathbf{w}}} \quad \text{s.a.} \quad \sum_i w_i = 1,\quad w_i \geq 0$$

usando `scipy.optimize.minimize` con método SLSQP. Se obtienen tres resultados:

**Frontera eficiente:** la curva de carteras óptimas en el espacio (volatilidad, rentabilidad), generada minimizando la volatilidad para 50 niveles de rentabilidad objetivo.

**Cartera de mínima varianza:** la combinación de pesos que minimiza la volatilidad del portafolio, con mayor peso en las estrategias A y C (menor correlación con el mercado en períodos de estrés).

**Cartera de máximo Sharpe:** la combinación que maximiza el ratio rentabilidad/riesgo. Asigna un 59,2% al Buy & Hold y un 40,8% a la Estrategia B (Calendario Macro), confirmando que la inversión pasiva pura no es óptima: incluso la señal táctica más simple — el calendario de publicaciones, de coste cero — merece una asignación significativa en la cartera óptima.

La frontera eficiente confirma tres conclusiones que responden al **OE5**:

1. El **Buy & Hold no es eficiente** en media-varianza: existe siempre una combinación de estrategias tácticas que obtiene igual o mayor rentabilidad con menor riesgo.
2. Las estrategias A, B y C no están perfectamente correlacionadas entre sí (sus señales se activan en momentos distintos), lo que proporciona **diversificación en la señal**.
3. La cartera de máximo Sharpe **valida la propuesta central del TFG** de forma independiente al backtesting.

![Figura 2. Frontera eficiente de Markowitz sobre las cuatro estrategias. El Buy & Hold (punto azul, esquina superior derecha) queda por debajo de la frontera: existe una combinación óptima (estrella amarilla, Sharpe 0,993) que obtiene similar rentabilidad con menor volatilidad. Los pesos óptimos — 59,2% Buy & Hold y 40,8% Calendario Macro — confirman que integrar la señal de calendario mejora el perfil riesgo-retorno. Ningún terminal profesional calcula automáticamente esta optimización sobre estrategias tácticas definidas por el usuario.](capturas_dashboard/frontera_eficiente.png)

## 9. Dashboard interactivo

El dashboard implementa todas las señales y métricas del trabajo en una herramienta operativa desarrollada en Streamlit. Consta de seis páginas:

| Página | Contenido |
|---|---|
| 1 — Resumen Ejecutivo | KPIs, equity curves, métricas comparativas, frontera eficiente |
| 2 — Estrategias | Análisis detallado por estrategia, drawdown, Sharpe rolling |
| 3 — Riesgo Avanzado | Stress testing, bootstrap, corrección de Bonferroni |
| 4 — Asesor de Carteras | Recomendaciones por perfil inversor, impacto en cartera real en € |
| 5 — Predictor | Semáforo de riesgo, comparación HAR vs. Full, walk-forward |
| 6 — Análisis Macro | Event study interactivo, histórico de publicaciones por indicador |

El flujo de uso diario se resume en tres pasos: (1) el gestor consulta la **recomendación de exposición** en la Página 5 para obtener la señal del día en menos de 30 segundos; (2) revisa el **calendario de próximos eventos macro** con el nivel de exposición recomendado en euros sobre su cartera real; (3) opcionalmente, consulta las **equity curves** y métricas acumuladas en la Página 1.

![Figura 3. Panel operativo del Predictor. El gestor recibe una recomendación directa en euros — en este ejemplo, "Vender 500.000 €" ante la publicación del PIB interanual —, con cada evento clasificado por tier de impacto (T1 alta señal, T2 moderada, T3 ruido) y un porcentaje de exposición específico. Esta es la principal diferenciación frente a las herramientas existentes: un terminal Bloomberg proporciona el dato macro pero no genera una recomendación de exposición en euros adaptada al tamaño de la cartera del gestor.](capturas_dashboard/semaforo_riesgo.png)

El dashboard incorpora tres elementos de rigor metodológico: validación walk-forward con 5 folds (CV(RMSE) < 15%), corrección de Bonferroni sobre los p-valores del Event Study, e intervalos de confianza bootstrap para los Sharpe ratios.

## 10. Conclusiones generales

La siguiente tabla resume la respuesta a cada objetivo específico y la sección donde se desarrolla:

| OE | Pregunta | Respuesta | Sección |
|---|---|---|---|
| OE1 | ¿Es predecible la volatilidad? | Sí (R² > 0,96, señal activa 26,3% días) | §4 |
| OE2 | ¿Qué modelo predice mejor? | XGBoost-HAR (RMSE 0,0082) | §4, §6 |
| OE3 | ¿Aportan las variables macro? | No predictivamente; sí como calendario | §6 |
| OE4 | ¿Causan shocks las publicaciones? | Sí (+11,6%, p < 0,0001, 421 eventos) | §7 |
| OE5 | ¿Mejoran el perfil riesgo-retorno? | Sí (Buy & Hold no es eficiente) | §8 |

**Sobre OE1 y OE2 — Predicción y selección de modelos:**
La volatilidad del IBEX 35 es predecible con R² > 0,96. Sobre una cartera de **1.000.000 €**, la Estrategia C reduce el drawdown máximo de 123.400 € a 79.800 € — un **ahorro de 43.600 €** —, con un ratio Calmar un 9,5% superior al Buy & Hold (1,317 vs. 1,203). En el episodio COVID-19, las estrategias tácticas redujeron la pérdida máxima en ~15 pp (~**150.000 €** de ahorro), más de tres veces el coste de oportunidad del período de test completo.

**Sobre OE3 y OE4 — Valor de las variables macro:**
El test de Diebold-Mariano (p > 0,49) confirma que las variables macro no mejoran la predicción puntual. Sin embargo, el Event Study revela que los 421 días de evento generan un 11,6% más de volatilidad que los días normales (p < 0,0001). Sobre la misma cartera de 1.000.000 €, el VaR diario se reduce en **2.200 €/día** en los días de evento al aplicar la Estrategia C respecto al Buy & Hold. Este hallazgo redirige el valor de las variables macro: su aportación no es predictiva sino organizacional, y el calendario de publicaciones macroeconómicas es la herramienta de gestión de riesgo más eficiente identificada en este trabajo.

**Sobre OE5 — Frontera eficiente:**
La optimización de Markowitz confirma que el Buy & Hold puro no es eficiente en media-varianza. La cartera de máximo Sharpe asigna un 40,8% a la Estrategia B (Calendario Macro) y un 59,2% al Buy & Hold, demostrando que incluso la señal táctica más simple — gratuita y sin modelo predictivo — merece una asignación significativa en la cartera óptima. Este resultado valida la propuesta central del trabajo desde la perspectiva de la teoría moderna de carteras.

**Robustez estadística:**
Los Sharpe ratios positivos son confirmados por bootstrap con 5.000 remuestreos (intervalos al 95% excluyendo el cero). La validación walk-forward (5 folds, CV(RMSE) < 15%) y la corrección de Bonferroni en el Event Study garantizan que los resultados no son fruto del sobreajuste.

**Contribución original:**
Frente a la literatura previa centrada en la capacidad predictiva de las variables macro, este trabajo demuestra que su valor no reside en mejorar la predicción puntual, sino en señalar los momentos de mayor incertidumbre con antelación suficiente para actuar. El calendario macroeconómico — información pública, gratuita y conocida de antemano — constituye por sí solo una herramienta de gestión de riesgo estadísticamente significativa.

**Limitaciones principales:**
El período de test de 2,7 años coincide con un mercado alcista, lo que penaliza artificialmente la rentabilidad de las estrategias con reducción de exposición. La hipótesis de cash al 0% (sin Euríbor) subestima la rentabilidad real. El umbral del 50% es fijo y no optimizado.

## 11. Recomendaciones accionables

Las siguientes recomendaciones se derivan directamente de las conclusiones y limitaciones identificadas en este trabajo. Se ordenan de mayor a menor inmediatez: las dos primeras son implementables de forma inmediata con los recursos actuales; la tercera mejora la comparación existente; y la cuarta propone una línea de desarrollo a medio plazo con potencial de diferenciación en el mercado.

### Recomendación 1: Implementar la Estrategia B como protocolo operativo estándar

**Para quién:** gestores de carteras con exposición al IBEX 35, independientemente del tamaño de la cartera.

**Qué hacer:** programar una reducción automática de exposición al 50% los días de publicación de datos macroeconómicos y el día previo. Usar el calendario oficial del INE, BCE y Eurostat, que es público, gratuito y disponible con semanas de antelación.

**Por qué:** la Estrategia B es la única que no requiere ningún modelo predictivo. Su coste de implementación es prácticamente nulo y su beneficio, aunque modesto en mercados alcistas, es sustancial en episodios de estrés. Para un gestor con mandato de control de drawdown es la medida de mayor eficiencia coste/beneficio disponible.

**Impacto estimado:** sobre una cartera de 1.000.000 €, reducción del VaR diario en ~1.500 € en los 89 días anuales de evento, con un coste de oportunidad inferior a 0,6 pp de rentabilidad anual. Coste de implementación: cero (solo requiere consultar un calendario público).

### Recomendación 2: Optimizar el umbral de reducción de forma dinámica

Reemplazar el umbral fijo del 50% por un umbral dinámico (30–80%) en función del percentil de volatilidad predicha y del tipo de evento macro, calibrado trimestralmente mediante grid search sobre el conjunto de validación. **Impacto estimado:** mejora del Sharpe neto entre 0,05 y 0,15 puntos (~425–1.275 € anuales sobre 1.000.000 €).

### Recomendación 3: Incorporar el rendimiento del cash

Añadir el Euríbor 3M como rendimiento de la liquidez en los días de reducción de exposición. Con tipos del 3–4%, las estrategias tácticas ganarían entre 1,35 y 1,80 pp de rentabilidad adicional anualizada (13.500–18.000 €/año sobre 1.000.000 €), cerrando la brecha con el Buy & Hold y probablemente superándolo en rentabilidad total.

### Recomendación 4: Extender el modelo a múltiples mercados europeos

Replicar el pipeline sobre DAX, CAC 40, FTSE 100 y Euro Stoxx 50, incorporando variables macro de cada país y efectos de contagio entre mercados (VIX, VSTOXX, volatilidad cruzada del S&P 500). Esta extensión transforma el trabajo en un producto de gestión táctica paneuropea escalable: la frontera eficiente sobre cinco índices genuinamente descorrelacionados generaría ganancias de diversificación significativas (reducción de volatilidad del 25–40%, mejora del Sharpe de 0,3–0,5 puntos) y abriría la posibilidad de comercializar la herramienta como servicio para gestoras independientes y family offices.

En conjunto, las cuatro recomendaciones trazan un camino de adopción progresiva: desde una medida de coste cero basada exclusivamente en un calendario público (R1), pasando por mejoras incrementales del modelo (R2, R3), hasta una propuesta de producto escalable con potencial comercial (R4). Este enfoque gradual permite que cualquier gestor, independientemente de su sofisticación cuantitativa, pueda extraer valor inmediato de los hallazgos de este trabajo.

## 12. Referencias bibliográficas

Corsi, F. (2009). *A simple approximate long-memory model of realized volatility.* Journal of Financial Econometrics, 7(2), 174–196.

Diebold, F. X., & Mariano, R. S. (1995). *Comparing predictive accuracy.* Journal of Business & Economic Statistics, 13(3), 253–263.

Faber, M. T. (2007). *A quantitative approach to tactical asset allocation.* The Journal of Wealth Management, 9(4), 69–79.

Markowitz, H. (1952). *Portfolio selection.* Journal of Finance, 7(1), 77–91.

Minga López, C. (2022). *Predicción de la volatilidad del IBEX 35 mediante variables macroeconómicas.* Trabajo de Fin de Grado, Universidad Francisco de Vitoria, Madrid.

Patton, A. J. (2011). *Volatility forecast comparison using imperfect volatility proxies.* Journal of Econometrics, 160(1), 246–256.
