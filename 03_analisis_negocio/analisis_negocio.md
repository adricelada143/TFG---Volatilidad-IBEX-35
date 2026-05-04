# Análisis de Negocio — Gestión Táctica de Carteras basada en Volatilidad y Calendario Macro

**TFG:** Impacto de las variables macroeconómicas en la volatilidad del IBEX 35
**Autor:** Adrián Celada Calderón
**Grado:** Business Analytics — Universidad Francisco de Vitoria (UFV), Madrid
**Curso:** 2025-26

---

## 1. Contextualización

El IBEX 35, principal índice bursátil del mercado español, es un termómetro de la salud económica de España y una referencia para miles de gestores de carteras, fondos de inversión y patrimonios familiares. En un contexto de creciente incertidumbre macroeconómica —tipos de interés del BCE en niveles históricamente volátiles, inflación persistente y tensiones geopolíticas— la gestión del riesgo se ha convertido en una necesidad estratégica, no un complemento.

La volatilidad, medida como la dispersión de los retornos, es el indicador clave del riesgo de mercado. Para un gestor de carteras, anticipar períodos de alta volatilidad permite adoptar posiciones defensivas que protejan el capital sin renunciar completamente a la exposición al mercado.

Este TFG aborda una pregunta práctica: **¿puede un gestor de carteras utilizar información macroeconómica pública para mejorar su gestión del riesgo en el IBEX 35?**

---

## 2. Objetivos y Preguntas de Negocio

### Objetivo General
Evaluar si las variables macroeconómicas aportan valor a la gestión táctica de carteras en el IBEX 35.

### Objetivos Específicos (OE)

| OE | Pregunta | Perspectiva |
|----|----------|-------------|
| OE1 | ¿Es predecible la volatilidad del IBEX 35? | Viabilidad técnica |
| OE2 | ¿Qué modelo predice mejor la volatilidad? | Selección de herramientas |
| OE3 | ¿Aportan las variables macro al poder predictivo? | Valor de la información |
| OE4 | ¿Las publicaciones macro causan shocks de volatilidad? | Gestión de carteras |

---

## 3. Respuestas a los Objetivos — Perspectiva de Negocio

### OE1: ¿Es predecible la volatilidad del IBEX 35?

**Respuesta: Sí, con modelos autorregresivos y machine learning.**

El modelo XGBoost con features HAR (Heterogeneous Autoregressive) logra un RMSE de 0.035 en validación cruzada temporal (5-fold). La clave es la **persistencia de la volatilidad**: la volatilidad de ayer es el mejor predictor de la volatilidad de hoy.

**Implicación para el gestor:** La volatilidad no es aleatoria. Un gestor puede anticipar regímenes de alta volatilidad con suficiente antelación para ajustar posiciones. En el backtesting, la señal de alta volatilidad se activa el 26.3% de los días, proporcionando una guía clara sobre cuándo reducir exposición.

### OE2: ¿Qué modelo predice mejor la volatilidad?

**Respuesta: XGBoost supera a los modelos lineales, pero la diferencia es marginal.**

La mejora de XGBoost sobre modelos más simples (Random Forest, Ridge) es estadísticamente marginal. Sin embargo, XGBoost captura mejor las **no linealidades** y las **interacciones** entre variables, lo que lo hace más robusto en regímenes extremos.

**Implicación para el gestor:** No es necesario un modelo excesivamente complejo. Un modelo XGBoost bien calibrado con features HAR básicas (volatilidad rezagada a 1, 5 y 21 días) proporciona una base sólida. La complejidad adicional de incluir docenas de variables macro no justifica su coste de mantenimiento.

### OE3: ¿Aportan valor las variables macro?

**Respuesta: No para predicción puntual, sí para gestión de riesgo.**

El test de Diebold-Mariano (p > 0.49) confirma que añadir variables macroeconómicas al modelo HAR no mejora significativamente la predicción de volatilidad. Esta comparación es ahora visible de forma interactiva en la **Página 5 (Predictor)** del dashboard, donde se muestran las métricas de ambos modelos (RMSE, MAE, R²) y el resultado del test DM. Sin embargo, este hallazgo negativo conduce a una conclusión positiva: **las variables macro aportan valor no como predictores, sino como señales de calendario**.

El análisis de event study demuestra que los días de publicación macroeconómica presentan un **+11.6% de volatilidad anormal** (Mann-Whitney, p ≈ 0). Este efecto es explotable porque el calendario de publicaciones es **público, gratuito y conocido con antelación**.

**Implicación para el gestor:** La mayor aportación de las variables macro a la gestión de carteras no es predictiva sino **organizacional**: saber cuándo se publican datos clave permite planificar la exposición con antelación.

### OE4: ¿Las publicaciones macro causan shocks de volatilidad?

**Respuesta: Sí, con impacto estadísticamente significativo.**

- **421 eventos macro** detectados en 20 años de datos (7.9% de los días de negociación)
- **81 eventos de alto impacto** (PIB y tasa de paro): 1.5% de los días
- La volatilidad anormal en días de publicación macro es significativamente mayor que en días normales
- Los eventos de mayor impacto son las publicaciones de **PIB interanual** y **tasa de paro**

**Implicación para el gestor:** Estos 421 días del año son predecibles y conocidos de antemano. Un gestor puede programar reducciones tácticas de exposición en esas fechas exactas sin necesidad de ningún modelo predictivo.

---

## 4. Conclusiones Generales

### Conclusión 1: El calendario macro es una herramienta de gestión de riesgo gratuita y efectiva

La Estrategia B (Calendario Macro) reduce la exposición al 50% solo el 12.9% de los días — aquellos con publicación macro o el día previo — y mantiene un rendimiento prácticamente equivalente al Buy & Hold (39.81% vs. 41.80% en el período de test). El coste de oportunidad es mínimo (1.99 puntos porcentuales en 2.7 años) y la protección ante shocks de volatilidad es significativa.

### Conclusión 2: Los modelos de volatilidad son útiles como complemento, no como sustituto

La Estrategia A (Volatilidad) y la Estrategia C (Combinada) utilizan la señal del modelo XGBoost para reducir exposición en regímenes de alta volatilidad. Aunque reducen el riesgo, también sacrifican rentabilidad al estar fuera del mercado el 26-28% del tiempo. En un mercado alcista como el del período de test (2023-2025), el coste de oportunidad es alto.

### Conclusión 3: La combinación de señales ofrece la mejor relación protección/coste

La Estrategia C — que combina la señal de volatilidad con eventos de alto impacto (PIB + paro) — ofrece el enfoque más sofisticado. Para un gestor institucional con mandato de control de riesgo, esta estrategia proporciona una capa adicional de protección en los momentos más críticos.

### Conclusión 5: La frontera eficiente confirma la superioridad risk-return de las estrategias tácticas

La optimización de Markowitz sobre las 4 estrategias (tratadas como activos) genera una frontera eficiente visible en la **Página 1 (Resumen Ejecutivo)** del dashboard. La cartera de máximo Sharpe asigna un 59,2% al Buy & Hold y un 40,8% a la Estrategia B (Calendario Macro), confirmando que la inversión pasiva pura no es óptima: incluso la señal táctica más simple merece una asignación significativa en la cartera eficiente. La cartera de mínima varianza, por su parte, demuestra que es posible reducir significativamente el riesgo sin sacrificar rentabilidad. Esta evidencia respalda la viabilidad de implementar combinaciones óptimas de las estrategias propuestas en un entorno de gestión real.

### Conclusión 4: El dashboard como herramienta operativa viabiliza la implementación

La herramienta de gestión táctica desarrollada permite al gestor:
- Consultar cada mañana si hay publicación macro programada
- Ver el estado del modelo de volatilidad (semáforo verde/amarillo/rojo)
- Obtener una recomendación clara y justificada de exposición
- Explorar el histórico para justificar decisiones ante el comité de inversiones

---

## 5. Recomendaciones Accionables

### Recomendación 1: Implementar la Estrategia B como protocolo operativo estándar

**Para quién:** Gestores de carteras con exposición al IBEX 35.

**Qué hacer:** Programar una reducción automática de exposición al 50% los días de publicación de datos macroeconómicos y el día previo. Usar el calendario oficial del INE, BCE y Eurostat.

**Coste de implementación:** Prácticamente nulo. Solo requiere consultar el calendario de publicaciones macro al inicio de cada mes y programar las órdenes correspondientes.

**Beneficio esperado:** Reducción de la volatilidad anormal en cartera sin coste significativo en rentabilidad a largo plazo.

### Recomendación 2: Usar el dashboard como herramienta de decisión diaria

**Para quién:** Equipos de gestión y comités de inversión.

**Qué hacer:** Integrar la consulta del dashboard en la rutina matutina del equipo de gestión. El semáforo de riesgo proporciona una señal rápida y visual del estado del mercado.

**Evolución futura:** Conectar el dashboard a feeds de datos en tiempo real (Bloomberg, Reuters) y al calendario oficial de publicaciones para obtener señales actualizadas automáticamente.

### Recomendación 3: Extender el análisis a otros mercados e índices

**Para quién:** Equipos de investigación y desarrollo de producto.

**Qué hacer:** Replicar el análisis para el Euro Stoxx 50, DAX 40 y otros índices europeos. Si el efecto calendario se confirma en múltiples mercados, se podría diseñar un producto de gestión semi-pasiva que explote esta ineficiencia.

### Recomendación 4: Optimizar los parámetros de la estrategia

**Para quién:** Equipos cuantitativos.

**Qué hacer:** El umbral de reducción del 50% es conservador y arbitrario. Una optimización del peso de exposición (entre 0% y 100%) en función del tipo de evento y la volatilidad predicha podría mejorar significativamente los resultados. Además, incorporar el rendimiento del cash (Euríbor) haría la comparación más realista.

---

## 6. Limitaciones y Trabajo Futuro

| Limitación | Impacto | Mitigación propuesta |
|-----------|---------|---------------------|
| Período de test de 2.7 años | Resultados pueden no ser robustos en otros regímenes | Validar con walk-forward de 10+ años |
| Sin costes de transacción | Sobreestima ventaja de estrategias activas | Incluir comisiones de 0.1-0.5% por operación |
| Cash rinde 0% | Subestima rentabilidad de estrategias activas | Incluir Euríbor 3M como rendimiento de cash |
| Índice equiponderado | No replica exactamente el IBEX 35 real | Ponderar por capitalización |
| Umbral de reducción fijo (50%) | Puede no ser óptimo | Optimizar con grid search + validación |

---

*Este documento forma parte del capítulo de Análisis de Negocio del TFG "Impacto de las variables macroeconómicas en la volatilidad del IBEX 35".*
