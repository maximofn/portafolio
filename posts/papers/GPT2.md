# Language Models are Unsupervised Multitask Learners

## Resumen

Las tareas de procesamiento del lenguaje natural, como las respuestas a preguntas, la traducción automática, la comprensión lectora y la generación de resúmenes, suelen abordarse mediante el aprendizaje supervisado en conjuntos de datos específicos de la tarea. Demostramos que los modelos de lenguaje empiezan a aprender estas tareas sin ninguna supervisión explícita cuando se entrenan en un nuevo conjunto de datos de millones de páginas web llamado WebText. Cuando se condicionan a un documento más preguntas, las respuestas generadas por el modelo de lenguaje alcanzan 55 F1 en el conjunto de datos CoQA, igualando o superando el rendimiento de 3 de los 4 sistemas de referencia sin utilizar los más de 127.000 ejemplos de entrenamiento. La capacidad del modelo de lenguaje es esencial para el éxito de la transferencia de tareas de tiro cero y aumentarla mejora el rendimiento de forma logarítmica lineal en todas las tareas. Nuestro modelo más grande, GPT-2, es un Transformer de 1.5B de parámetros que alcanza resultados de vanguardia en 7 de los 8 conjuntos de datos de modelado lingüístico probados en un entorno de tiro cero, pero que sigue estando poco ajustado a WebText. Las muestras del modelo reflejan estas mejoras y contienen párrafos de texto coherentes. Estos hallazgos sugieren un camino prometedor hacia la construcción de sistemas de procesamiento del lenguaje que aprendan a realizar tareas a partir de sus demostraciones naturales.

## 1. Introducción

Los sistemas de aprendizaje automático destacan ahora (en expectativa) en las tareas para las que se entrenan mediante el uso de una combinación de grandes conjuntos de datos, modelos de alta capacidad y aprendizaje supervisado (Krizhevsky et al., 2012) (Sutskever et al., 2014) (Amodei et al., 2016). Sin embargo, estos sistemas son frágiles y sensibles a pequeños cambios en la distribución de los datos (Recht et al., 2018) y en la especificación de las tareas (Kirkpatrick et al., 2017). Los sistemas actuales se caracterizan mejor como expertos limitados que como generalistas competentes. Nos gustaría avanzar hacia sistemas más generales que puedan realizar muchas tareas, eventualmente sin necesidad de crear y etiquetar manualmente un conjunto de datos de entrenamiento para cada una de ellas.

El enfoque dominante para crear sistemas de ML es recopilar un conjunto de datos de ejemplos de entrenamiento que demuestren el comportamiento correcto para una tarea deseada, entrenar un sistema para que imite estos comportamientos y luego probar su rendimiento en ejemplos retenidos independientes e idénticamente distribuidos (IID). Esto ha servido para avanzar en los expertos limitados. Pero el comportamiento a menudo errático de los modelos de subtitulado (Lake et al., 2017), los sistemas de comprensión lectora (Jia & Liang, 2017) y los clasificadores de imágenes (Alcorn et al., 2018) sobre la diversidad y variedad de posibles entradas pone de manifiesto algunas de las deficiencias de este enfoque.

Nuestra sospecha es que la prevalencia del entrenamiento en una sola tarea en conjuntos de datos de un solo dominio es un factor que contribuye en gran medida a la falta de generalización que se observa en los sistemas actuales. Es probable que el progreso hacia sistemas robustos con las arquitecturas actuales requiera el entrenamiento y la medición del rendimiento en una amplia gama de dominios y tareas. Recientemente, se han propuesto varios bancos de pruebas como GLUE (Wang et al., 2018) y decaNLP (McCann et al., 2018) para empezar a estudiar esto.

El aprendizaje multitarea (Caruana, 1997) es un marco prometedor para mejorar el rendimiento general. Sin embargo, el entrenamiento multitarea en PNL es todavía incipiente. Trabajos recientes reportan modestas mejoras en el rendimiento (Yogatama et al., 2019) y los dos esfuerzos más ambiciosos hasta la fecha han entrenado en un total de 10 y 17 pares (conjunto de datos, objetivo) respectivamente (McCann et al., 2018) (Bowman et al., 2018). Desde una perspectiva de meta-aprendizaje, cada par (conjunto de datos, objetivo) es un único ejemplo de entrenamiento muestreado de la distribución de conjuntos de datos y objetivos. Los sistemas de ML actuales necesitan cientos o miles de ejemplos para inducir funciones que generalicen bien. Esto sugiere que el entrenamiento multitarea puede necesitar otros tantos pares de entrenamiento eficaces para hacer realidad su promesa con los enfoques actuales. Será muy difícil seguir escalando la creación de conjuntos de datos y el diseño de objetivos hasta el grado que puede ser necesario para forzar nuestro camino con las técnicas actuales. Esto motiva a explorar configuraciones adicionales para realizar el aprendizaje multitarea.

![Figura 1](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQfNBBS_nyeXZzfGENWasBbbitHzEpBk8-Emg&s)

Figura1. Rendimiento en la tarea cero de los LM de WebText en función del tamaño del modelo en muchas tareas de PNL. Los resultados de comprensión lectora son sobre CoQA (Reddy et al., 2018), traducción sobre WMT-14 Fr-En (Artetxe et al., 2017), resumen sobre CNN y Daily Mail (See et al., 2017) y respuesta a preguntas sobre Natural Questions (Kwiatkowski et al., 2019). La sección 3 contiene descripciones detalladas de cada resultado

Los sistemas que actualmente tienen un mejor rendimiento en las tareas lingüísticas utilizan una combinación de pre-entrenamiento y ajuste fino supervisado. Este enfoque tiene una larga historia con una tendencia hacia formas de transferencia más flexibles. Primero, se aprendieron vectores de palabras y se utilizaron como entradas para arquitecturas específicas de la tarea (Mikolov et al., 2013) (Collobert et al., 2011), luego se transfirieron las representaciones contextuales de las redes recurrentes (Dai & Le, 2015) (Peters et al., 2018), y trabajos recientes sugieren que las arquitecturas específicas de la tarea ya no son necesarias y que transferir muchos bloques de autoatención es suficiente (Radford et al., 2018) (Devlin et al., 2018).

Estos métodos siguen requiriendo un entrenamiento supervisado para realizar una tarea. Cuando sólo se dispone de datos supervisados mínimos o nulos, otra línea de trabajo ha demostrado la promesa de los modelos lingüísticos para realizar tareas específicas, como el razonamiento de sentido común (Schwartz et al., 2017) y el análisis de sentimientos (Radford et al., 2017).

En este trabajo, conectamos estas dos líneas de trabajo y continuamos la tendencia de métodos de transferencia más generales. Demostramos que los modelos lingüísticos pueden realizar tareas posteriores en un entorno de tiro cero, sin ninguna modificación de parámetros o arquitectura. Demostramos que este enfoque tiene potencial al destacar la capacidad de los modelos lingüísticos para realizar una amplia gama de tareas en un entorno de tiro cero. Conseguimos resultados prometedores, competitivos y de última generación en función de la tarea.

## 2. Enfoque

En el núcleo de nuestro enfoque está el modelado del lenguaje. El modelado del lenguaje suele enmarcarse como la estimación no supervisada de la distribución a partir de un conjunto de ejemplos (x1, x2, ..., xn), cada uno de ellos compuesto por secuencias de símbolos de longitud variable (s1, s2, ..., sn). Dado que el lenguaje tiene una ordenación secuencial natural, es habitual factorizar las probabilidades conjuntas sobre símbolos como el producto de probabilidades condicionales (Jelinek & Mercer, 1980) (Bengio et al., 2003):

p(x) = ∏_(i=1)^n p(s_n | s_1, ..., s_(n-1)) (1)

Este enfoque permite un muestreo y una estimación manejables de p(x), así como de cualquier condicional de la forma p(s_(n-k), ..., s_n | s_1, ..., s_(n-k-1)). En los últimos años, se han producido mejoras significativas en la expresividad de los modelos que pueden calcular estas probabilidades condicionales, como las arquitecturas de autoatención como el Transformer (Vaswani et al., 2017).

Aprender a realizar una única tarea puede expresarse en un marco probabilístico como la estimación de una distribución condicional p(salida|entrada). Dado que un sistema general debería ser capaz de realizar muchas tareas diferentes, incluso para la misma entrada, debería condicionar no sólo a la entrada sino también a la tarea a realizar. Es decir, debería modelar p(salida|entrada, tarea). Esto se ha formalizado de diversas maneras en entornos multitarea y de meta-aprendizaje. El condicionamiento de tareas suele implementarse a nivel arquitectónico, como los codificadores y decodificadores específicos de la tarea en (Kaiser et al., 2017) o a nivel algorítmico como el marco de optimización de bucle interno y externo de MAML (Finn et al., 2017). Pero como se ejemplifica en McCann et al. (2018), el lenguaje proporciona una forma flexible de especificar tareas, entradas y salidas, todo ello como una secuencia de símbolos. Por ejemplo, un ejemplo de entrenamiento de traducción puede escribirse como la secuencia (traducir al francés, texto en inglés, texto en francés). Del mismo modo, un ejemplo de entrenamiento de comprensión lectora puede escribirse como (responder a la pregunta, documento, pregunta, respuesta). McCann et al. (2018) demostraron que era posible entrenar un único modelo, el MQAN, para inferir y realizar muchas tareas diferentes en ejemplos con este tipo de formato.

El modelado del lenguaje también es capaz, en principio, de aprender las tareas de McCann et al. (2018) sin necesidad de una supervisión explícita de cuáles son los símbolos que se van a predecir. Dado que el objetivo supervisado es el mismo que el objetivo no supervisado, pero sólo se evalúa en un subconjunto de la secuencia, el mínimo global del objetivo no supervisado es también el mínimo global del objetivo supervisado. En este entorno ligeramente artificial, las preocupaciones con la estimación de la densidad como objetivo de entrenamiento basado en principios que se discuten en (Sutskever et al., 2015) se dejan de lado. El problema se convierte en cambio en si somos capaces, en la práctica, de optimizar el objetivo no supervisado hasta la convergencia. Experimentos preliminares confirmaron que los modelos de lenguaje suficientemente grandes son capaces de realizar un aprendizaje multitarea en esta configuración artificial, pero el aprendizaje es mucho más lento que en los enfoques explícitamente supervisados.

Si bien es un gran paso desde la configuración bien planteada descrita anteriormente hasta el desorden del "lenguaje en estado salvaje", Weston (2016) argumenta, en el contexto del diálogo, la necesidad de desarrollar sistemas capaces de aprender del lenguaje natural directamente y demostró una prueba de concepto: aprender una tarea de control de calidad sin una señal de recompensa mediante el uso de la predicción hacia adelante de las salidas de un profesor. Si bien el diálogo es un enfoque atractivo, nos preocupa que sea demasiado restrictivo. Internet contiene una gran cantidad de información que está disponible pasivamente sin necesidad de comunicación interactiva. Nuestra especulación es que un modelo de lenguaje con suficiente capacidad comenzará a aprender a inferir y realizar las tareas demostradas en secuencias de lenguaje natural con el fin de predecirlas mejor, independientemente de su método de obtención. Si un modelo de lenguaje es capaz de hacer esto, estará, en efecto, realizando un aprendizaje multitarea no supervisado. Comprobamos si este es el caso analizando el rendimiento de los modelos de lenguaje en un entorno de tiro cero en una amplia variedad de tareas.

# 2.1. Conjunto de datos de entrenamiento

La mayoría de los trabajos anteriores entrenaban los modelos lingüísticos en un único dominio de texto, como artículos de noticias (Jozefowicz et al., 2016), Wikipedia (Merity et al., 2016) o libros de ficción (Kiros et al., 2015). Nuestro enfoque motiva la construcción de un conjunto de datos lo más grande y diverso posible para recopilar demostraciones en lenguaje natural de tareas en dominios y contextos lo más variados posible.

Una fuente prometedora de texto diverso y casi ilimitado son los web scraping como Common Crawl. Aunque estos archivos son muchos órdenes de magnitud mayores que los conjuntos de datos de modelado lingüístico actuales, tienen importantes problemas de calidad de los datos. Trinh & Le (2018) utilizaron Common Crawl en su trabajo sobre el razonamiento de sentido común, pero observaron una gran cantidad de documentos "cuyo contenido es en su mayoría ininteligible". Observamos problemas de datos similares en nuestros experimentos iniciales con Common Crawl. Los mejores resultados de Trinh & Le (2018) se obtuvieron utilizando una pequeña submuestra de Common Crawl que incluía sólo los documentos más similares a su conjunto de datos objetivo, el Winograd Schema Challenge. Si bien este es un enfoque pragmático para mejorar el rendimiento en una tarea específica, queremos evitar hacer suposiciones sobre las tareas que se van a realizar con antelación.

---
"No soy el hombre más inteligente del mundo, pero como dicen en francés: Je ne suis pas un imbecile [No soy un tonto].

En un post ahora borrado del 16 de agosto, Soheil Eid, candidato tory en la circunscripción de Joliette, escribió en francés: "Mentez mentez, il en restera toujours quelque chose", que se traduce como "Miente miente y algo quedará siempre".

"Odio la palabra 'perfume'", dice Burr. "Es algo mejor en francés: 'parfum'".

Si se escucha con atención en el minuto 29:55, se puede escuchar una conversación entre dos chicos en francés: "-Comment on fait pour aller de l'autre côté? -Quel autre côté?", que significa "- ¿Cómo se llega al otro lado? - ¿Qué otro lado?".

Si esto suena un poco exagerado, consideremos esta pregunta en francés: As-tu aller au cinéma?, o ¿Fuiste al cine?, que literalmente se traduce como ¿Tienes que ir al cine/teatro?

"Brevet Sans Garantie Du Gouvernement", traducido al inglés: "Patentado sin garantía del gobierno".

---

Tabla 1. Ejemplos de demostraciones naturales de traducción del inglés al francés y del francés al inglés encontradas en el conjunto de entrenamiento de WebText.

En su lugar, creamos un nuevo web scraping que hace hincapié en la calidad del documento. Para ello, sólo rastreamos las páginas web que han sido curadas/filtradas por humanos. Filtrar manualmente un web scraping completo sería excepcionalmente caro, así que, como punto de partida, rastreamos todos los enlaces salientes de Reddit, una plataforma de redes sociales, que recibieron al menos 3 karma. Esto puede considerarse como un indicador heurístico de si otros usuarios encontraron el enlace interesante, educativo o simplemente divertido.

El conjunto de datos resultante, WebText, contiene el subconjunto de texto de estos 45 millones de enlaces. Para extraer el texto de las respuestas HTML utilizamos una combinación de los extractores de contenido Dragnet (Peters & Lecocq, 2013) y Newspaper1. Todos los resultados presentados en este documento utilizan una versión preliminar de WebText que no incluye los enlaces creados después de diciembre de 2017 y que, tras la eliminación de duplicados y alguna limpieza basada en heurística, contiene algo más de 8 millones de documentos para un total de 40 GB de texto. Eliminamos todos los documentos de Wikipedia de WebText, ya que es una fuente de datos común para otros conjuntos de datos y podría complicar el análisis debido a la superposición de los datos de entrenamiento con las tareas de evaluación de la prueba.

1 https://github.com/codelucas/newspaper

### 2.2. Representación de la entrada

Un modelo lingüístico (LM) general debería ser capaz de calcular la probabilidad de (y también de generar) cualquier cadena. Los LM a gran escala actuales incluyen pasos de preprocesamiento como la conversión a minúsculas, la tokenización y los tokens fuera de vocabulario que restringen el espacio de las cadenas modelables. Mientras que procesar las cadenas Unicode como una secuencia de bytes UTF-8 cumple con elegancia este requisito, como se ejemplifica en trabajos como el de Gillick et al. (2015), los LM actuales a nivel de byte no son competitivos con los LM a nivel de palabra en conjuntos de datos a gran escala como el One Billion Word Benchmark (Al-Rfou et al., 2018). Observamos una brecha de rendimiento similar en nuestros propios intentos de entrenar LM estándar a nivel de byte en WebText.

La codificación por pares de bytes (BPE) (Sennrich et al., 2015) es un término medio práctico entre el modelado lingüístico a nivel de carácter y a nivel de palabra que interpola eficazmente entre entradas a nivel de palabra para secuencias de símbolos frecuentes y entradas a nivel de carácter para secuencias de símbolos poco frecuentes. A pesar de su nombre, las implementaciones de BPE de referencia suelen operar en puntos de código Unicode y no en secuencias de bytes. Estas implementaciones requerirían la inclusión del espacio completo de símbolos Unicode para poder modelar todas las cadenas Unicode. Esto daría lugar a un vocabulario base de más de 130.000 antes de añadir cualquier token multisímbolo. Esto es prohibitivamente grande en comparación con los vocabularios de 32.000 a 64.000 tokens que se utilizan a menudo con BPE. En cambio, una versión de BPE a nivel de byte sólo requiere un vocabulario base de tamaño 256. Sin embargo, la aplicación directa de BPE a la secuencia de bytes da como resultado fusiones subóptimas debido a que BPE utiliza una heurística codiciosa basada en la frecuencia para construir el vocabulario de tokens. Observamos que BPE incluye muchas versiones de palabras comunes como perro, ya que se dan en muchas variaciones como perro. perro! perro? . Esto da lugar a una asignación subóptima de las ranuras de vocabulario limitadas y de la capacidad del modelo. Para evitarlo, impedimos que BPE se fusione entre categorías de caracteres para cualquier secuencia de bytes. Añadimos una excepción para los espacios, lo que mejora significativamente la eficiencia de la compresión al tiempo que añade una fragmentación mínima de las palabras en varios tokens de vocabulario.

Esta representación de la entrada nos permite combinar los beneficios empíricos de los LM a nivel de palabra con la generalidad de los enfoques a nivel de byte. Dado que nuestro enfoque puede asignar una probabilidad a cualquier cadena Unicode, esto nos permite evaluar nuestros LM en cualquier conjunto de datos, independientemente del preprocesamiento, la tokenización o el tamaño del vocabulario.

### 2.3. Modelo

Utilizamos una arquitectura basada en Transformer (Vaswani et al., 2017) para nuestros LM. El modelo sigue en gran medida los detalles del modelo OpenAI GPT (Radford et al., 2018) con un Parámetros Capas dmodel

|Parameters|Layers|d_model|
|---|---|---|
|117M| 12| 768|
| 345M| 24| 1024|
| 762M| 36| 1280|
| 1542M| 48| 1600|

Tabla 2. Hiperparámetros de arquitectura para los 4 tamaños de modelo.

pocas modificaciones. La normalización de la capa (Ba et al., 2016) se trasladó a la entrada de cada sub-bloque, de forma similar a una red residual de pre-activación (He et al., 2016) y se añadió una normalización de la capa adicional después del bloque de autoatención final. Se utiliza una inicialización modificada que tiene en cuenta la acumulación en la ruta residual con la profundidad del modelo. Escalamos los pesos de las capas residuales en la inicialización por un factor de 1/√N donde N es el número de capas residuales. El vocabulario se amplía a 50.257. También aumentamos el tamaño del contexto de 512 a 1024 tokens y se utiliza un tamaño de lote mayor de 512.

## 3. Experimentos

Entrenamos y evaluamos cuatro LM con tamaños espaciados logarítmicamente de forma uniforme. Las arquitecturas se resumen en la Tabla 2. El modelo más pequeño es equivalente al GPT original, y el segundo más pequeño equivalente al modelo más grande de BERT (Devlin et al., 2018). Nuestro modelo más grande, al que llamamos GPT-2, tiene más de un orden de magnitud más parámetros que GPT. La tasa de aprendizaje de cada modelo se ajustó manualmente para obtener la mejor perplejidad en una muestra retenida del 5% de WebText. Todos los modelos siguen estando poco ajustados a WebText y la perplejidad retenida ha mejorado hasta ahora dado más tiempo de entrenamiento.

### 3.1. Modelado del lenguaje
Como primer paso hacia la transferencia de tareas de tiro cero, estamos interesados en comprender cómo se comportan los LM de WebText en la transferencia de dominio de tiro cero en la tarea principal para la que están entrenados: el modelado del lenguaje. Dado que nuestro modelo opera a nivel de byte y no requiere un preprocesamiento o tokenización con pérdida, podemos evaluarlo en cualquier punto de referencia de modelo de lenguaje. Los resultados en los conjuntos de datos de modelado lingüístico se suelen reportar en una cantidad que es una versión escalada o exponenciada de la probabilidad logarítmica negativa media por unidad de predicción canónica - normalmente un carácter, un byte o una palabra. Evaluamos la misma cantidad calculando la probabilidad logarítmica de un conjunto de datos según un LM de WebText y dividiendo por el número de unidades canónicas. Para muchos de estos conjuntos de datos, los LM de WebText se probarían significativamente fuera de la distribución, teniendo que predecir texto agresivamente estandarizado, artefactos de tokenización como puntuación y contracciones desconectadas, frases barajadas e incluso la cadena <UNK> que es extremadamente rara en WebText - que ocurre sólo 26 veces en 40 mil millones de bytes. Reportamos nuestros resultados principales en la Tabla 3 utilizando des-tokenizadores invertibles que eliminan tantos de estos artefactos de tokenización / preprocesamiento como sea posible. Dado que estos des-tokenizadores son invertibles, todavía podemos calcular la probabilidad logarítmica de un conjunto de datos y pueden considerarse como una forma simple de adaptación al dominio. Observamos ganancias de 2,5 a 5 de perplejidad para GPT-2 con estos des-tokenizadores.

|   |LAMBADA|LAMBADA|CBT-CN|CBT-NE|WikiText2|PTB  |enwik8|text8|WikiText103|1BW  |
|---|-------|-------|------|------|---------|-----|------|-----|-----------|-----|
|   |(PPL)  |(ACC)  |(ACC) |(ACC) |(PPL)    |(PPL)|(BPB) |(BPC)|(PPL)      |(PPL)|
|SOTA|99.8|59.23|85.7|82.3|39.14|46.54|0.99|1.08|18.3|21.8|
|117M|35.13|45.99|87.65|83.4|29.41|65.85|1.16|1.17|37.50|75.20|
|345M|15.60|55.48|92.35|87.1|22.76|47.33|1.01|1.06|26.37|55.72|
|762M|10.87|60.12|93.45|88.0|19.93|40.31|0.97|1.02|22.05|44.575|
|1542M|8.63|63.24|93.30|89.05|18.34|35.76|0.93|0.98|17.48|42.16|

Tabla 3. Resultados sin disparos en muchos conjuntos de datos. No se realizó ningún entrenamiento ni ajuste fino para ninguno de estos resultados. Los resultados de PTB y WikiText-2 proceden de (Gong et al., 2018). Los resultados de CBT proceden de (Bajgar et al., 2016). El resultado de precisión de LAMBADA es de (Hoang et al., 2018) y el resultado de perplejidad de LAMBADA es de (Grave et al., 2016). Otros resultados proceden de (Dai et al., 2019).

Los LM de WebText se transfieren bien a través de dominios y conjuntos de datos, mejorando el estado del arte en 7 de los 8 conjuntos de datos en un entorno de tiro cero. Se observan grandes mejoras en conjuntos de datos pequeños como Penn Treebank y WikiText-2, que sólo tienen entre 1 y 2 millones de tokens de entrenamiento. También se observan grandes mejoras en los conjuntos de datos creados para medir las dependencias a largo plazo como LAMBADA (Paperno et al., 2016) y el Children's Book Test (Hill et al., 2015). Nuestro modelo sigue siendo significativamente peor que los trabajos anteriores en el One Billion Word Benchmark (Chelba et al., 2013). Esto se debe probablemente a una combinación de que es el conjunto de datos más grande y que tiene algunos de los preprocesamientos más destructivos - la mezcla a nivel de frase de 1BW elimina toda la estructura de largo alcance.

### 3.2. Prueba del libro infantil

![Figure2](https://img-blog.csdnimg.cn/direct/b4b62e1296ec46e9a4675a93c04618d4.png)

Figura 2. Rendimiento en el Test del Libro Infantil en función de la capacidad del modelo. El rendimiento humano procede de Bajgar et al. (2016), en lugar de las estimaciones mucho más bajas del documento original.

La prueba del libro infantil (CBT) (Hill et al., 2015) se creó para examinar el rendimiento de los LM en diferentes categorías de palabras: entidades nombradas, sustantivos, verbos y preposiciones. En lugar de informar de la perplejidad como métrica de evaluación, el CBT informa de la precisión en una prueba de cierre construida automáticamente en la que la tarea consiste en predecir cuál de las 10 opciones posibles para una palabra omitida es la correcta. Siguiendo el enfoque LM introducido en el trabajo original, calculamos la probabilidad de cada opción y el resto de la frase condicionada a esta opción según el LM, y predecimos la que tiene la mayor probabilidad. Como se observa en la Figura 2, el rendimiento mejora constantemente a medida que aumenta el tamaño del modelo y se cierra la mayor parte de la brecha con el rendimiento humano en esta prueba. El análisis de superposición de datos mostró que uno de los libros del conjunto de prueba del CBT, El libro de la selva de Rudyard Kipling, está en WebText, por lo que informamos de los resultados en el conjunto de validación que no tiene superposición significativa. GPT-2 consigue nuevos resultados de vanguardia del 93,3% en sustantivos comunes y del 89,1% en entidades nombradas. Se aplicó un des-tokenizador para eliminar los artefactos de tokenización de estilo PTB del CBT.

### 3.3. LAMBADA

El conjunto de datos LAMBADA (Paperno et al., 2016) pone a prueba la capacidad de los sistemas para modelar dependencias de largo alcance en el texto. La tarea consiste en predecir la última palabra de frases que requieren al menos 50 tokens de contexto para que un humano las prediga con éxito. GPT-2 mejora el estado del arte de 99,8 (Grave et al., 2016) a 8,6 de perplejidad y aumenta la precisión de los LM en esta prueba del 19% (Dehghani et al., 2018) al 52,66%. Al investigar los errores de GPT-2 se observó que la mayoría de las predicciones son continuaciones válidas de la frase, pero no son palabras finales válidas. Esto sugiere que el LM no está utilizando la restricción adicional útil de que la palabra debe ser la final de la frase. Añadir un filtro de palabras de parada como aproximación a esto aumenta aún más la precisión hasta el 63,24%, mejorando el estado del arte general en esta tarea en un 4%. El estado del arte anterior (Hoang et al., 2018) utilizaba un entorno de predicción restringido diferente en el que las salidas del modelo estaban limitadas sólo a las palabras que aparecían en el contexto. Para GPT-2, esta restricción es más perjudicial que útil, ya que el 19% de las respuestas no están en contexto. Utilizamos una versión del conjunto de datos sin preprocesamiento.

### 3.4. Reto del esquema Winograd

![Figure3](https://blog.kakaocdn.net/dn/cbgVsF/btq9DvZmYMu/stnJZ6kp7BCkxoMfL6qsjk/img.png)

Figura 3. Rendimiento en el Winograd Schema Challenge en función de la capacidad del modelo

El reto del esquema Winograd (Levesque et al., 2012) se construyó para medir la capacidad de un sistema para realizar razonamientos de sentido común midiendo su capacidad para resolver ambigüedades en el texto. Recientemente, Trinh & Le (2018) demostraron un progreso significativo en este reto utilizando LM, al predecir la resolución de la ambigüedad con mayor probabilidad. Seguimos su formulación del problema y visualizamos el rendimiento de nuestros modelos con técnicas de puntuación completa y parcial en la Figura 3. GPT-2 mejora la precisión del estado del arte en un 7%, alcanzando el 70,70%. El conjunto de datos es bastante pequeño, con sólo 273 ejemplos, por lo que recomendamos leer Trichelair et al. (2018) para ayudar a contextualizar este resultado.

### 3.5. Comprensión lectora

El conjunto de datos de respuestas a preguntas de conversación (CoQA) Reddy et al. (2018) consiste en documentos de 7 dominios diferentes emparejados con diálogos en lenguaje natural entre un preguntador y un respondedor sobre el documento. CoQA pone a prueba las capacidades de comprensión lectora y también la capacidad de los modelos para responder a preguntas que dependen del historial de la conversación (como "¿Por qué?").

| |R-1|R-2|R-L|R-AVG|
|--|---|---|---|---|
|Bottom-Up Sum|41.22|18.68|38.34|32.75|
|Lede-3|40.38|17.66|36.62|31.55|
|Seq2Seq + Attn|31.33|11.81|28.83|23.99|
|GPT-2 TL;DR:|29.34|8.27|26.58|21.40|
|Random-3|28.78|8.63|25.52|20.98|
|GPT-2 no hint|21.58|4.03|19.47|15.03|

Tabla 4. Rendimiento de resumen medido por la métrica ROUGE F1 en los conjuntos de datos CNN y Daily Mail. Bottom-Up Sum es el modelo SOTA de (Gehrmann et al., 2018).

La decodificación codiciosa de GPT-2 cuando se condiciona a un documento, al historial de la conversación asociada y a un token final A: alcanza 55 F1 en el conjunto de desarrollo. Esto iguala o supera el rendimiento de 3 de los 4 sistemas de referencia sin utilizar los más de 127.000 pares de preguntas y respuestas recopilados manualmente en los que se entrenaron esos sistemas de referencia. El SOTA supervisado, un sistema basado en BERT (Devlin et al., 2018), se está acercando al rendimiento de 89 F1 de los humanos. Aunque el rendimiento de GPT-2 es emocionante para un sistema sin ningún tipo de entrenamiento supervisado, una inspección de sus respuestas y errores sugiere que GPT-2 a menudo utiliza heurísticas simples basadas en la recuperación, como responder con un nombre del documento a una pregunta de quién.

### 3.6. Resumen

Probamos la capacidad de GPT-2 para realizar resúmenes en el conjunto de datos de CNN y Daily Mail (Nallapati et al., 2016). Para inducir el comportamiento de resumen, añadimos el texto TL;DR: después del artículo y generamos 100 tokens con muestreo aleatorio Top-k (Fan et al., 2018) con k = 2, lo que reduce la repetición y fomenta resúmenes más abstractos que la decodificación codiciosa. Utilizamos las 3 primeras frases generadas en estos 100 tokens como resumen. Mientras que cualitativamente las generaciones se asemejan a resúmenes, como se muestra en la Tabla 14, a menudo se centran en el contenido reciente del artículo o confunden detalles específicos como cuántos coches estuvieron involucrados en un accidente o si un logotipo estaba en una gorra o camisa. En las métricas comúnmente reportadas ROUGE 1,2,L los resúmenes generados sólo comienzan a acercarse al rendimiento de las líneas de base neuronales clásicas y apenas superan la selección de 3 frases aleatorias del artículo. El rendimiento de GPT-2 cae 6,4 puntos en la métrica agregada cuando se elimina la pista de la tarea, lo que demuestra la capacidad de invocar un comportamiento específico de la tarea en un modelo de lenguaje con lenguaje natural.

### 3.7. Traducción

Probamos si GPT-2 ha empezado a aprender a traducir de un idioma a otro. Para ayudarle a inferir que esta es la tarea deseada, condicionamos el modelo de lenguaje a un contexto de pares de ejemplos del formato frase en inglés = frase en francés y luego, después de una indicación final de frase en inglés =, tomamos muestras del modelo con decodificación codiciosa y utilizamos la primera frase generada como traducción. En el conjunto de prueba WMT-14 inglés-francés, GPT-2 obtiene 5 BLEU, lo que es ligeramente peor que una sustitución palabra por palabra con un léxico bilingüe inferido en trabajos anteriores sobre traducción automática no supervisada (Conneau et al., 2017b). En el conjunto de prueba WMT-14 francés-inglés, GPT-2 es capaz de aprovechar su potente modelo de lenguaje inglés para obtener un rendimiento significativamente mejor, alcanzando los 11,5 BLEU. Esto supera a varias líneas de base de traducción automática no supervisada de (Artetxe et al., 2017) y (Lample et al., 2017), pero sigue siendo mucho peor que los 33,5 BLEU del mejor enfoque actual de traducción automática no supervisada (Artetxe et al., 2019). El rendimiento en esta tarea nos sorprendió, ya que eliminamos deliberadamente las páginas web no inglesas de WebText como paso de filtrado. Para confirmarlo, ejecutamos un detector de idioma a nivel de bytes2 en WebText que detectó sólo 10 MB de datos en francés, lo que es aproximadamente 500 veces menos que el corpus monolingüe francés común en las investigaciones previas sobre traducción automática no supervisada.

|Question | Generated Answer | Correct | Probability|
|------- | -------- | -------- | --------|
|Who wrote the book the origin of species? | Charles Darwin | ✓ | 83.4%|
|Who is the founder of the ubuntu project? | Mark Shuttleworth | ✓ | 82.0%|
|Who is the quarterback for the green bay packers? | Aaron Rodgers | ✓ | 81.1%|
|Panda is a national animal of which country? | China | ✓ | 76.8%|
|Who came up with the theory of relativity? | Albert Einstein | ✓ | 76.4%|
|When was the first star wars film released? | 1977 | ✓ | 71.4%|
|What is the most common blood type in sweden? | A | X | 70.6%|
|Who is regarded as the founder of psychoanalysis? | Sigmund Freud | ✓ | 69.3%|
|Who took the first steps on the moon in 1969? | Neil Armstrong | ✓ | 66.8%|
|Who is the largest supermarket chain in the uk? | Tesco | ✓ | 65.3%|
|What is the meaning of shalom in english? | peace | ✓ | 64.0%|
|Who was the author of the art of war? | Sun Tzu | ✓ | 59.6%|
|Largest state in the us by land mass? | California | X | 59.2%|
|Green algae is an example of which type of reproduction? | parthenogenesis | X | 56.5%|
|Vikram samvat calender is official in which country? | India | ✓ | 55.6%|
|Who is mostly responsible for writing the declaration of independence? | Thomas Jefferson | ✓ | 53.3%|
|What us state forms the western boundary of montana? | Montana | X | 52.3%|
|Who plays ser davos in game of thrones? | Peter Dinklage | X | 52.1%|
|Who appoints the chair of the federal reserve system? | Janet Yellen | X | 51.5%|
|State the process that divides one nucleus into two genetically identical nuclei? | mitosis | ✓ | 50.7%|
|Who won the most mvp awards in the nba? | Michael Jordan | X | 50.2%|
|What river is associated with the city of rome? | the Tiber | ✓ | 48.6%|
|Who is the first president to be impeached? | Andrew Johnson | ✓ | 48.3%|
|Who is the head of the department of homeland security 2017? | John Kelly | ✓ | 47.0%|
|What is the name given to the common currency to the european union? | Euro | ✓ | 46.8%|
|What was the emperor name in star wars? | Palpatine | ✓ | 46.5%|
|Do you have to have a gun permit to shoot at a range? | No | ✓ | 46.4%|
|Who proposed evolution in 1859 as the basis of biological development? | Charles Darwin | ✓ | 45.7%|
|Nuclear power plant that blew up in russia? | Chernobyl | ✓ | 45.7%|
|Who played john connor in the original terminator? | Arnold Schwarzenegger | X | 45.2%|

Tabla 5. Las 30 respuestas más seguras generadas por GPT-2 en el conjunto de desarrollo de Preguntas Naturales ordenadas por su probabilidad según GPT-2. Ninguna de estas preguntas aparece en WebText según el procedimiento descrito en la sección 4.

### 3.8. Respuesta a preguntas

Una forma potencial de probar qué información contiene un modelo de lenguaje es evaluar con qué frecuencia genera la respuesta correcta a preguntas de estilo factoide. En anteriores presentaciones de este comportamiento en sistemas neuronales en los que toda la información se almacena en parámetros como A Neural Conversational Model (Vinyals & Le, 2015) se reportaron resultados cualitativos debido a la falta de conjuntos de datos de evaluación de alta calidad. El conjunto de datos Natural Questions, recientemente introducido (Kwiatkowski et al., 2019), es un recurso prometedor para probar esto de forma más cuantitativa. Al igual que en la traducción, el contexto del modelo de lenguaje se siembra con pares de preguntas y respuestas de ejemplo, lo que ayuda al modelo a inferir el estilo de respuesta corta del conjunto de datos. GPT-2 responde correctamente al 4,1% de las preguntas cuando se evalúa mediante la métrica de coincidencia exacta que se utiliza habitualmente en los conjuntos de datos de comprensión lectora como SQUAD.3 Como punto de comparación, el modelo más pequeño no supera la precisión del 1,0% de una línea de base increíblemente simple que devuelve la respuesta más común para cada tipo de pregunta (quién, qué, dónde, etc.). GPT-2 responde 5,3 veces más preguntas correctamente, lo que sugiere que la capacidad del modelo ha sido un factor importante en el bajo rendimiento de los sistemas neuronales en este tipo de tareas hasta ahora. La probabilidad que GPT-2 asigna a sus respuestas generadas está bien calibrada y GPT-2 tiene una precisión del 63,1% en el 1% de las preguntas en las que tiene más confianza. Las 30 respuestas más seguras generadas por GPT-2 en las preguntas del conjunto de desarrollo se muestran en la Tabla 5. El rendimiento de GPT-2 sigue siendo mucho, mucho, peor que el rango del 30 al 50% de los sistemas de respuesta a preguntas de dominio abierto que hibridan la recuperación de información con la respuesta a preguntas de documentos extractivos (Alberti et al., 2019).

2 https://github.com/CLD2Owners/cld2

3 Alec, que antes se consideraba bueno en las trivias aleatorias, respondió correctamente a 17 de 100 ejemplos muestreados aleatoriamente cuando se le probó en el mismo entorno que GPT-2. En realidad sólo acertó 14, pero debería haber acertado las otras 3.

|PTB | WikiText-2 | enwik8 | text8 | Wikitext-103 | 1BW|
|------- | -------- | -------- | -------- | -------- | --------|
|Dataset train | 2.67% | 0.66% | 7.50% | 2.34% | 9.09% | 13.19%|
|WebText train | 0.88% | 1.63% | 6.31% | 3.94% | 2.42% | 3.75%|

Tabla 6. Porcentaje de solapamiento del conjunto de prueba 8 gramos con los conjuntos de entrenamiento

## 4. Generalización vs Memorización

Trabajo reciente en visión artificial ha demostrado que datasets de imágenes comunes contienen una cantidad no trivial de imágenes casi duplicadas. Por ejemplo, CIFAR-10 tiene un 3.3% de superposición entre las imágenes de entrenamiento y prueba (Barz & Denzler, 2019). Esto resulta en una sobrestimación del rendimiento de generalización de los sistemas de aprendizaje automático. A medida que el tamaño de los datasets aumenta, este problema se vuelve cada vez más probable, lo que sugiere que un fenómeno similar podría estar sucediendo con WebText. Por lo tanto, es importante analizar cuánto de los datos de prueba también aparece en los datos de entrenamiento.

Para estudiar esto, creamos filtros Bloom que contienen 8-gramas de tokens del conjunto de entrenamiento de WebText. Para mejorar la recuperación, las cadenas se normalizaron para que solo contuvieran palabras alfanuméricas en minúsculas con un solo espacio como delimitador. Los filtros Bloom se construyeron de modo que la tasa de falsos positivos estuviera limitada superiormente por 1/10⁸. Verificamos además la baja tasa de falsos positivos generando 1M cadenas, de las cuales ninguna fue encontrada por el filtro.

Estos filtros Bloom nos permiten calcular, dado un dataset, el porcentaje de 8-gramas de ese dataset que también se encuentran en el conjunto de entrenamiento de WebText. La Tabla 6 muestra este análisis de superposición para los conjuntos de prueba de los benchmarks de LM comunes. Los conjuntos de prueba de datasets de LM comunes tienen entre un 1% y un 6% de superposición con WebText train, con un promedio de superposición del 3.2%. Algo sorprendente es que muchos datasets tienen superposiciones más grandes con sus propias divisiones de entrenamiento, con un promedio de 5.9% de superposición.

Nuestro enfoque optimiza la recuperación, y aunque la inspección manual de las superposiciones muestra muchas frases comunes, hay muchas coincidencias más largas que se deben a datos duplicados. Esto no es exclusivo de WebText. Por ejemplo, descubrimos que el conjunto de prueba de WikiText-103 tiene un artículo que también está en el conjunto de entrenamiento. Como solo hay 60 artículos en el conjunto de prueba, hay al menos una superposición del 1.6%.⁴ Posiblemente más preocupante, 1BW tiene una superposición de casi 13.2% con su propio conjunto de entrenamiento según nuestro procedimiento.

Para el Winograd Schema Challenge, encontramos solo 10 esquemas que tenían alguna superposición de 8-gramas con el conjunto de entrenamiento de WebText. De estos, 2 fueron coincidencias espurias. De los 8 restantes, solo 1 esquema apareció en cualquier contexto que diera la respuesta.

Para CoQA, alrededor del 15% de los documentos en el dominio de las noticias ya están en WebText y el modelo tiene un rendimiento de aproximadamente 3 F1 mejor en estos. La métrica del conjunto de desarrollo de CoQA informa el rendimiento promedio en 5 dominios diferentes y medimos una ganancia de aproximadamente 0.5-1.0 F1 debido a la superposición en los diversos dominios. Sin embargo, ninguna pregunta o respuesta de entrenamiento real se encuentra en WebText, ya que CoQA se lanzó después de la fecha límite para los enlaces en WebText.

En LAMBADA, la superposición promedio es del 1.2%. GPT-2 tiene un rendimiento de aproximadamente 2 puntos de perplexity mejor en los ejemplos con una superposición superior al 15%. Recalcular las métricas al excluir todos los ejemplos con cualquier superposición cambia los resultados de 8.6 a 8.7 puntos de perplexity y reduce la precisión del 63.2% al 62.9%. Este cambio muy pequeño en los resultados generales probablemente se deba a que solo 1 de cada 200 ejemplos tiene una superposición significativa.

En general, nuestro análisis sugiere que la superposición de datos entre los datos de entrenamiento de WebText y datasets de evaluación específicos proporciona un beneficio pequeño pero constante a los resultados informados. Sin embargo, para la mayoría de los datasets no notamos superposiciones significativamente mayores que las que ya existen entre los conjuntos de entrenamiento y prueba estándar, como destaca la Tabla 6.

Comprender y cuantificar cómo el texto altamente similar impacta el rendimiento es una pregunta de investigación importante. Las técnicas de desduplicación mejoradas, como la coincidencia difusa escalable, también podrían ayudar a responder mejor estas preguntas. Por ahora, recomendamos el uso de la desduplicación basada en la superposición de n-gramas como un paso de verificación importante y una verificación de cordura durante la creación de divisiones de entrenamiento y prueba para nuevos datasets de PNL.

Otra forma potencial de determinar si el rendimiento de los modelos de LM de WebText se debe a la memorización es inspeccionar su rendimiento en su propio conjunto reservado. Como se muestra en la Figura 4, el rendimiento tanto en el conjunto de entrenamiento como en el de prueba de WebText es similar y mejora juntos a medida que aumenta el tamaño del modelo. Esto sugiere que incluso GPT-2 todavía está subajustado en WebText en muchos aspectos.

GPT-2 también es capaz de escribir artículos de noticias sobre el descubrimiento de unicornios parlantes. Un ejemplo se proporciona en la Tabla 13.

## 5. Trabajo Relacionado

Una parte importante de este trabajo midió el rendimiento de modelos de lenguaje más grandes entrenados en datasets más grandes. Esto es similar al trabajo de Jozefowicz et al. (2016) que escaló modelos de lenguaje basados en RNN en el One Billion Word Benchmark. Bajgar et al. (2016) también mejoraron previamente los resultados en el Children's Book Test creando un dataset de entrenamiento mucho más grande a partir de Project Gutenberg para complementar el dataset de entrenamiento estándar. Hestness et al. (2017) realizaron un análisis exhaustivo de cómo el rendimiento de varios modelos de aprendizaje profundo cambia en función tanto de la capacidad del modelo como del tamaño del dataset. Nuestros experimentos, aunque mucho más ruidosos entre tareas, sugieren que tendencias similares se mantienen para las subtareas de un objetivo y continúan en el régimen de 1B+ parámetros.

![Figure 4](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS_ra5mF9smqnnlHHj0q8Dx3WKBIrua76HeKA&s)

Figura 4. Rendimiento de los LM Rendimiento de los LM entrenados con WebText en función del tamaño del modelo



Se ha documentado anteriormente una funcionalidad aprendida interesante en modelos generativos, como las células en un modelo de lenguaje RNN que realizan el seguimiento del ancho de línea y la detección de citas/comentarios Karpathy et al. (2015). Más inspirador para nuestro trabajo fue la observación de Liu et al. (2018) de que un modelo entrenado para generar artículos de Wikipedia también aprendió a traducir nombres entre idiomas.

El trabajo anterior ha explorado enfoques alternativos para filtrar y construir un gran corpus de texto de páginas web, como el iWeb Corpus (Davies, 2018).

Ha habido un extenso trabajo en métodos de preentrenamiento para tareas de lenguaje. Además de los mencionados en la introducción, GloVe (Pennington et al., 2014) escaló el aprendizaje de representación de vectores de palabras a todo Common Crawl. Un trabajo influyente temprano sobre aprendizaje de representación profunda para texto fue Skip-thought Vectors (Kiros et al., 2015). McCann et al. (2017) exploraron el uso de representaciones derivadas de modelos de traducción automática y Howard & Ruder (2018) mejoraron los enfoques de ajuste fino basados en RNN de (Dai & Le, 2015). (Conneau et al., 2017a) estudiaron el rendimiento de transferencia de las representaciones aprendidas por modelos de inferencia de lenguaje natural y (Subramanian et al., 2018) exploraron el entrenamiento multitarea a gran escala.

(Ramachandran et al., 2016) demostraron que los modelos seq2seq se benefician de ser inicializados con modelos de lenguaje preentrenados como codificadores y decodificadores. El trabajo más reciente ha demostrado que el preentrenamiento de LM es útil cuando se ajusta finamente para tareas de generación difíciles como el diálogo de charla informal y los sistemas de preguntas y respuestas basados en el diálogo también (Wolf et al., 2019) (Dinan et al., 2018).

## 6. Discusión

Mucha investigación se ha dedicado a aprender (Hill et al., 2016), comprender (Levy & Goldberg, 2014) y evaluar críticamente (Wieting & Kiela, 2019) las representaciones de los métodos de preentrenamiento tanto supervisados como no supervisados. Nuestros resultados sugieren que el aprendizaje de tareas no supervisado es un área de investigación adicional prometedora para explorar. Estos hallazgos potencialmente ayudan a explicar el amplio éxito de las técnicas de preentrenamiento para las tareas de PNL posteriores, ya que mostramos que, en el límite, una de estas técnicas de preentrenamiento comienza a aprender a realizar tareas directamente sin necesidad de adaptación o modificación supervisada.

En la comprensión lectora, el rendimiento de GPT-2 es competitivo con los modelos base supervisados en un entorno de cero disparos. Sin embargo, en otras tareas, como la resumización, aunque realiza la tarea cualitativamente, su rendimiento sigue siendo solo rudimentario según las métricas cuantitativas. Aunque es sugestivo como resultado de investigación, en términos de aplicaciones prácticas, el rendimiento de cero disparos de GPT-2 todavía está lejos de ser utilizable.

Hemos estudiado el rendimiento de cero disparos de los modelos de LM de WebText en muchas tareas canónicas de PNL, pero hay muchas tareas adicionales que podrían evaluarse. Sin duda, hay muchas tareas prácticas donde el rendimiento de GPT-2 todavía no es mejor que el azar. Incluso en las tareas comunes que evaluamos, como la resumización y la traducción, los modelos de lenguaje solo comienzan a superar los modelos base triviales cuando tienen suficiente capacidad.

Si bien el rendimiento de cero disparos establece una línea de base del rendimiento potencial de GPT-2 en muchas tareas, no está claro dónde está el límite con el ajuste fino. En algunas tareas, la salida totalmente abstracta de GPT-2 es una desviación significativa de las salidas basadas en la red de punteros extractiva (Vinyals et al., 2015) que actualmente son las mejores en muchos datasets de comprensión lectora y preguntas y respuestas. Dado el éxito anterior del ajuste fino de GPT, planeamos investigar el ajuste fino en benchmarks como decaNLP y GLUE, especialmente porque no está claro si los datos de entrenamiento y la capacidad adicionales de GPT-2 son suficientes para superar las ineficiencias de las representaciones unidireccionales demostradas por BERT (Devlin et al., 2018).

## 7. Conclusión

Cuando un modelo de lenguaje grande se entrena en un dataset lo suficientemente grande y diverso, es capaz de funcionar bien en muchos dominios y datasets. GPT-2 alcanza un rendimiento de vanguardia de cero disparos en 7 de los 8 datasets de modelado de lenguaje probados. La diversidad de tareas que el modelo puede realizar en un entorno de cero disparos sugiere que los modelos de alta capacidad entrenados para maximizar la probabilidad de un corpus de texto lo suficientemente variado comienzan a aprender a realizar una cantidad sorprendente de tareas sin necesidad de supervisión explícita.⁵

Notas:

⁴ Una parte importante de la superposición adicional se debe a que los editores reutilizan algunos párrafos en varios artículos con un tema compartido, como varias batallas en la Guerra de Corea.

⁵ El código preliminar para descargar y usar el modelo pequeño está disponible en https://github.com/openai/gpt-2.

## Agradecimientos

Gracias a todos los que escribieron el texto, compartieron los enlaces y votaron a favor del contenido en WebText. Millones de personas participaron en la creación de los datos en los que se entrenó GPT-2. También gracias a todos los Googlers que nos ayudaron con la infraestructura de entrenamiento, incluyendo a Zak Stone, JS Riehl, Jonathan Hseu, Russell Power, Youlong Cheng, Noam Shazeer, Solomon Boulos, Michael Banfield, Aman Gupta, Daniel Sohn y muchos más. Por último, gracias a las personas que dieron comentarios sobre los borradores del artículo: Jacob Steinhardt, Sam Bowman, Geoffrey Irving y Madison May.