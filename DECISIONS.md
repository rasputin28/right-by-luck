# Decisiones de diseño — Paper 1 (Right by Luck)

## 2026-11-16 · Modelos: viejos a propósito
- Modelos (OpenRouter): `openai/gpt-4o-mini-2024-07-18`, `meta-llama/llama-3.3-70b-instruct`, `qwen/qwen-2.5-72b-instruct`.
- Por qué viejos: un modelo deja de acumular hechos en su corte de entrenamiento. Con cortes de 2023–2024, los hechos de Wikidata posteriores a marzo de 2026 son desconocidos con un margen de más de un año: el control de hechos frescos es estable y no hace falta una carrera contra el tiempo.
- La carrera contra el tiempo (regla 6 del protocolo) aplica a los modelos NUEVOS: cada evaluación debe usar hechos más recientes que el corte del modelo más nuevo evaluado.
- Cortes de entrenamiento: gpt-4o-mini = oct-2023 (documentación de OpenAI); Llama 3.3 70B = dic-2023 (model card de Meta); Qwen2.5 = sin fecha oficial, se usa su lanzamiento (sep-2024) como cota superior. VERIFICAR las tres fuentes antes de citarlas.
- Qwen2.5 se elige porque la etapa 2 usa Qwen2.5-7B-Instruct (tiene NLA publicado). La versión 7B no está en OpenRouter; se usa la 72B de la misma familia.
- Riesgo: OpenRouter enruta a varios proveedores, que pueden servir versiones cuantizadas, y la temperatura 0 no es del todo determinista entre proveedores. Mitigación: fijar el proveedor por modelo y guardar el proveedor de cada respuesta.
- Costo estimado: < 10 USD por las ~22,500 llamadas (prompts cortos; precios de OpenRouter consultados 2026-11-16).

## 2026-11-16 · Replicabilidad del servicio (OpenRouter)
- Por llamada se guarda: id del modelo, proveedor que respondió (campo `provider` de la respuesta), parámetros completos de la petición (temperature 0, top_p 1, max_tokens, seed si el proveedor lo admite), id de la respuesta, `system_fingerprint` si existe, y la hora UTC.
- Ruteo fijo por modelo: `provider.order=[<uno>]`, `allow_fallbacks=false`, precisión fija (`quantizations`) cuando el proveedor la declara. Verificar los nombres exactos de los parámetros en la documentación de OpenRouter antes de correr.
- Lo que NO controlamos: el hardware, el balanceo de carga y el tamaño de lote en el centro de datos del proveedor. Con temperatura 0 estos cambios pueden alterar la salida (aritmética de punto flotante no asociativa). Es un error irreducible para nosotros.
- No lo suponemos: lo MEDIMOS. 100 ítems repiten el prompt neutral idéntico 3 veces; el % de respuestas que cambian sin cambiar nada entra al piso de ruido junto con el control y el error del juez.
- Todo se publica (log por llamada) para que otros repliquen con el mismo rigor.
