# Improving Language Understanding by Generative Pre-Training

## Abstract

La comprensión del lenguaje natural abarca una amplia gama de tareas diversas, como la implicación textual, la respuesta a preguntas, la evaluación de la similitud semántica y la clasificación de documentos. Aunque abundan los corpus de texto sin etiquetar de gran tamaño, los datos etiquetados para el aprendizaje de estas tareas específicas son escasos, lo que dificulta que los modelos entrenados discriminativamente funcionen adecuadamente. Demostramos que se pueden obtener grandes mejoras en estas tareas mediante el preentrenamiento generativo de un modelo de lenguaje en un corpus diverso de texto sin etiquetar, seguido de un ajuste fino discriminativo en cada tarea específica. A diferencia de los enfoques anteriores, hacemos uso de transformaciones de entrada conscientes de la tarea durante el ajuste fino para lograr una transferencia efectiva al tiempo que se requieren cambios mínimos en la arquitectura del modelo. Demostramos la eficacia de nuestro enfoque en una amplia gama de puntos de referencia para la comprensión del lenguaje natural. Nuestro modelo agnóstico de tareas generales supera a los modelos entrenados discriminativamente que utilizan arquitecturas diseñadas específicamente para cada tarea, mejorando significativamente el estado del arte en 9 de las 12 tareas estudiadas. Por ejemplo, logramos mejoras absolutas del 8,9% en razonamiento de sentido común (Prueba de cierre de historias), del 5,7% en respuesta a preguntas (RACE) y del 1,5% en implicación textual (MultiNLI).


## 1. Introducción

La capacidad de aprender eficazmente del texto bruto es crucial para aliviar la dependencia del aprendizaje supervisado en el procesamiento del lenguaje natural (PNL). La mayoría de los métodos de aprendizaje profundo requieren cantidades sustanciales de datos etiquetados manualmente, lo que restringe su aplicabilidad en muchos dominios que sufren de una escasez de recursos anotados [61]. En estas situaciones, los modelos que pueden aprovechar la información lingüística de datos no etiquetados proporcionan una valiosa alternativa a la recopilación de más anotaciones, que puede llevar mucho tiempo y ser costosa. Además, incluso en los casos en los que se dispone de una supervisión considerable, aprender buenas representaciones de forma no supervisada puede proporcionar una mejora significativa del rendimiento. La evidencia más convincente de ello hasta ahora ha sido el uso extensivo de embeddings de palabras preentrenadas [10, 39, 42] para mejorar el rendimiento en una serie de tareas de PNL [8, 11, 26, 45].

Sin embargo, aprovechar más información que la de las palabras a partir de texto sin etiquetar es un reto por dos razones principales. En primer lugar, no está claro qué tipo de objetivos de optimización son más eficaces para aprender representaciones de texto que sean útiles para la transferencia. Investigaciones recientes han estudiado varios objetivos como el modelado del lenguaje [44], la traducción automática [38] y la coherencia del discurso [22], y cada método ha superado a los demás en diferentes tareas.1 En segundo lugar, no hay consenso sobre la forma más eficaz de transferir estas representaciones aprendidas a la tarea objetivo. Las técnicas existentes implican una combinación de realizar cambios específicos de la tarea en la arquitectura del modelo [43, 44], utilizar esquemas de aprendizaje intrincados [21] y añadir objetivos de aprendizaje auxiliares [50]. Estas incertidumbres han dificultado el desarrollo de enfoques de aprendizaje semisupervisado eficaces para el procesamiento del lenguaje.

En este artículo, exploramos un enfoque semisupervisado para las tareas de comprensión del lenguaje utilizando una combinación de preentrenamiento no supervisado y ajuste fino supervisado. Nuestro objetivo es aprender una representación universal que se transfiera con poca adaptación a una amplia gama de tareas. Asumimos el acceso a un gran corpus de texto sin etiquetar y a varios conjuntos de datos con ejemplos de entrenamiento anotados manualmente (tareas objetivo). Nuestra configuración no requiere que estas tareas objetivo estén en el mismo dominio que el corpus sin etiquetar. Empleamos un procedimiento de entrenamiento en dos etapas. En primer lugar, utilizamos un objetivo de modelado del lenguaje en los datos no etiquetados para aprender los parámetros iniciales de un modelo de red neuronal. Posteriormente, adaptamos estos parámetros a una tarea objetivo utilizando el objetivo supervisado correspondiente.

Para la arquitectura de nuestro modelo, utilizamos el Transformer [62], que ha demostrado tener un buen rendimiento en diversas tareas como la traducción automática [62], la generación de documentos [34] y el análisis sintáctico [29]. Esta elección del modelo nos proporciona una memoria más estructurada para manejar las dependencias a largo plazo en el texto, en comparación con alternativas como las redes recurrentes, lo que da como resultado un rendimiento de transferencia robusto en diversas tareas. Durante la transferencia, utilizamos adaptaciones de entrada específicas de la tarea derivadas de enfoques de estilo transversal [52], que procesan la entrada de texto estructurado como una única secuencia contigua de tokens. Como demostramos en nuestros experimentos, estas adaptaciones nos permiten ajustar de forma efectiva con cambios mínimos en la arquitectura del modelo preentrenado.

Evaluamos nuestro enfoque en cuatro tipos de tareas de comprensión del lenguaje: inferencia del lenguaje natural, respuesta a preguntas, similitud semántica y clasificación de textos. Nuestro modelo agnóstico de tareas generales supera a los modelos entrenados discriminativamente que emplean arquitecturas diseñadas específicamente para cada tarea, mejorando significativamente el estado del arte en 9 de las 12 tareas estudiadas. Por ejemplo, logramos mejoras absolutas del 8,9% en razonamiento de sentido común (Prueba de cierre de historias) [40], del 5,7% en respuesta a preguntas (RACE) [30], del 1,5% en implicación textual (MultiNLI) [66] y del 5,5% en el recientemente introducido punto de referencia multitarea GLUE [64]. También analizamos los comportamientos de "disparo cero" del modelo preentrenado en cuatro entornos diferentes y demostramos que adquiere un conocimiento lingüístico útil para las tareas posteriores.

## 2 Trabajo relacionado

**Aprendizaje semisupervisado para el PNL** Nuestro trabajo se enmarca en la categoría del aprendizaje semisupervisado para el lenguaje natural. Este paradigma ha suscitado un gran interés, con aplicaciones a tareas como el etiquetado de secuencias [24, 33, 57] o la clasificación de textos [41, 70]. Los primeros enfoques utilizaban datos no etiquetados para calcular estadísticas a nivel de palabra o de frase, que luego se utilizaban como características en un modelo supervisado [33]. En los últimos años, los investigadores han demostrado los beneficios de utilizar embeddings de palabras [11, 39, 42], que se entrenan en corpus no etiquetados, para mejorar el rendimiento en una variedad de tareas [8, 11, 26, 45]. Sin embargo, estos enfoques transfieren principalmente información a nivel de palabra, mientras que nosotros pretendemos capturar la semántica de nivel superior.

Los enfoques recientes han investigado el aprendizaje y la utilización de más semántica que la de las palabras a partir de datos no etiquetados. Las embeddings a nivel de frase o de oración, que pueden entrenarse utilizando un corpus no etiquetado, se han utilizado para codificar el texto en representaciones vectoriales adecuadas para diversas tareas objetivo [28, 32, 1, 36, 22, 12, 56, 31].

**Preentrenamiento no supervisado** El preentrenamiento no supervisado es un caso especial de aprendizaje semisupervisado en el que el objetivo es encontrar un buen punto de inicialización en lugar de modificar el objetivo de aprendizaje supervisado. Los primeros trabajos exploraron el uso de la técnica en la clasificación de imágenes [20, 49, 63] y en tareas de regresión [3]. Investigaciones posteriores [15] demostraron que el preentrenamiento actúa como un esquema de regularización, permitiendo una mejor generalización en las redes neuronales profundas. En trabajos recientes, el método se ha utilizado para ayudar a entrenar redes neuronales profundas en diversas tareas como la clasificación de imágenes [69], el reconocimiento de voz [68], la desambiguación de entidades [17] y la traducción automática [48].

La línea de trabajo más cercana a la nuestra implica el preentrenamiento de una red neuronal utilizando un objetivo de modelado del lenguaje y luego su ajuste fino en una tarea objetivo con supervisión. Dai y otros [13] y Howard y Ruder [21] siguen este método para mejorar la clasificación de textos. Sin embargo, aunque la fase de preentrenamiento ayuda a capturar alguna información lingüística, su uso de modelos LSTM restringe su capacidad de predicción a un rango corto. En cambio, nuestra elección de las redes transformadoras nos permite capturar estructuras lingüísticas de mayor alcance, como demostramos en nuestros experimentos. Además, también demostramos la eficacia de nuestro modelo en una gama más amplia de tareas, incluyendo la inferencia del lenguaje natural, la detección de paráfrasis y la finalización de historias. Otros enfoques [43, 44, 38] utilizan representaciones ocultas de un modelo de lenguaje o de traducción automática preentrenado como características auxiliares mientras se entrena un modelo supervisado en la tarea objetivo. Esto implica una cantidad sustancial de nuevos parámetros para cada tarea objetivo separada, mientras que nosotros requerimos cambios mínimos en la arquitectura de nuestro modelo durante la transferencia.

**Objetivos de entrenamiento auxiliares** Añadir objetivos de entrenamiento auxiliares no supervisados es una forma alternativa de aprendizaje semisupervisado. Los primeros trabajos de Collobert y Weston [10] utilizaron una amplia variedad de tareas auxiliares de PNL como el etiquetado POS, la segmentación, el reconocimiento de entidades nombradas y el modelado del lenguaje para mejorar el etiquetado de roles semánticos. Más recientemente, Rei [50] añadió un objetivo auxiliar de modelado del lenguaje a su objetivo de tarea objetivo y demostró mejoras en el rendimiento de las tareas de etiquetado de secuencias. Nuestros experimentos también utilizan un objetivo auxiliar, pero como demostramos, el preentrenamiento no supervisado ya aprende varios aspectos lingüísticos relevantes para las tareas objetivo

## 3 Marco de trabajo

Nuestro procedimiento de entrenamiento consta de dos etapas. La primera etapa consiste en aprender un modelo de lenguaje de alta capacidad en un gran corpus de texto. A esto le sigue una etapa de ajuste fino, en la que adaptamos el modelo a una tarea discriminativa con datos etiquetados.

### 3.1 Preentrenamiento no supervisado

Dado un corpus no supervisado de tokens U = {u1, . . . , un}, utilizamos un objetivo estándar de modelado del lenguaje para maximizar la siguiente probabilidad:

L1(U) = ∑ᵢ logP(uᵢ|uᵢ₋ₖ, ..., uᵢ₋₁; Θ) (1)

donde k es el tamaño de la ventana de contexto, y la probabilidad condicional P se modela utilizando una red neuronal con parámetros Θ. Estos parámetros se entrenan utilizando el descenso de gradiente estocástico [51].

En nuestros experimentos, utilizamos un decodificador Transformer multicapa [34] para el modelo de lenguaje, que es una variante del Transformer [62]. Este modelo aplica una operación de autoatención multicabezal sobre los tokens de contexto de entrada, seguida de capas de alimentación hacia adelante posición por posición para producir una distribución de salida sobre los tokens objetivo:


h₀ = UWe + Wp
hₗ = transformer_block(hₗ₋₁) ∀i ∈ [1, n]    (2)
P(u) = softmax(hₙWᵀe)

donde U = (u−k, . . . , u−1) es el vector de contexto de tokens, n es el número de capas, We es la matriz de incrustación de tokens y Wp es la matriz de incrustación de posición.

### 3.2 Ajuste fino supervisado

Después de entrenar el modelo con el objetivo de la ecuación 1, adaptamos los parámetros a la tarea objetivo supervisada. Asumimos un conjunto de datos etiquetado C, donde cada instancia consiste en una secuencia de tokens de entrada, x1, . . . , xm, junto con una etiqueta y. Las entradas se pasan a través de nuestro modelo preentrenado para obtener la activación del bloque Transformer final hml , que luego se introduce en una capa de salida lineal añadida con parámetros Wy para predecir y:

P (y|x1, . . . , xm) = softmax(hml Wy). (3)

Esto nos da el siguiente objetivo a maximizar:

L2(C) = ∑ (x,y)logP (y|x1, . . . , xm). (4)

Además, descubrimos que la inclusión del modelado del lenguaje como objetivo auxiliar al ajuste fino ayudaba al aprendizaje al (a) mejorar la generalización del modelo supervisado, y (b) acelerar la convergencia. Esto está en línea con trabajos anteriores [50, 43], que también observaron una mejora del rendimiento con dicho objetivo auxiliar. Específicamente, optimizamos el siguiente objetivo (con peso λ):

L3(C) = L2(C) + λ ∗ L1(C) (5) 

En general, los únicos parámetros adicionales que requerimos durante el ajuste fino son W y y las embeddings para los tokens delimitadores (descritos más adelante en la sección 3.3).

![Figura 1](https://production-media.paperswithcode.com/methods/Screen_Shot_2020-05-27_at_12.41.44_PM.png)
Figura 1: (izquierda) Arquitectura del Transformer y objetivos de entrenamiento utilizados en este trabajo. (derecha) Transformaciones de entrada para el ajuste fino en diferentes tareas. Convertimos todas las entradas estructuradas en secuencias de tokens para ser procesadas por nuestro modelo preentrenado, seguido de una capa lineal+softmax.

### 3.3 Transformaciones de entrada específicas de la tarea

Para algunas tareas, como la clasificación de textos, podemos ajustar directamente nuestro modelo como se ha descrito anteriormente. Otras tareas, como la respuesta a preguntas o la implicación textual, tienen entradas estructuradas, como pares de frases ordenadas o tripletes de documento, pregunta y respuestas. Dado que nuestro modelo preentrenado se entrenó en secuencias contiguas de texto, necesitamos algunas modificaciones para aplicarlo a estas tareas. Trabajos anteriores propusieron aprender arquitecturas específicas de la tarea sobre las representaciones transferidas [44]. Este enfoque reintroduce una cantidad significativa de personalización específica de la tarea y no utiliza el aprendizaje por transferencia para estos componentes arquitectónicos adicionales. En su lugar, utilizamos un enfoque de estilo de recorrido [52], en el que convertimos las entradas estructuradas en una secuencia ordenada que nuestro modelo preentrenado puede procesar. Estas transformaciones de entrada nos permiten evitar realizar cambios extensos en la arquitectura entre tareas. A continuación, ofrecemos una breve descripción de estas transformaciones de entrada y la Figura 1 proporciona una ilustración visual. Todas las transformaciones incluyen la adición de tokens de inicio y fin inicializados aleatoriamente (〈s〉, 〈e〉).

**Implicación textual** Para las tareas de implicación, concatenamos las secuencias de tokens de la premisa p y la hipótesis h, con un token delimitador ($) en medio.

**Similitud** Para las tareas de similitud, no hay un orden inherente de las dos frases que se comparan. Para reflejar esto, modificamos la secuencia de entrada para que contenga los dos posibles órdenes de las frases (con un delimitador en medio) y procesamos cada una de ellas de forma independiente para producir dos representaciones de secuencia hml que se suman elemento a elemento antes de ser introducidas en la capa de salida lineal.

**Respuesta a preguntas y razonamiento de sentido común** Para estas tareas, se nos da un documento de contexto z, una pregunta q y un conjunto de posibles respuestas {ak}. Concatenamos el contexto del documento y la pregunta con cada posible respuesta, añadiendo un token delimitador en medio para obtener [z; q; $; ak]. Cada una de estas secuencias se procesa de forma independiente con nuestro modelo y luego se normaliza mediante una capa softmax para producir una distribución de salida sobre las posibles respuestas.

## 4 Experimentos

### 4.1 Configuración

**Preentrenamiento no supervisado** Utilizamos el conjunto de datos BooksCorpus [71] para entrenar el modelo de lenguaje. Contiene más de 7.000 libros inéditos únicos de una variedad de géneros, incluyendo aventuras, fantasía y romance. Fundamentalmente, contiene largos tramos de texto contiguo, lo que permite al modelo generativo aprender a condicionar la información a largo plazo. Un conjunto de datos alternativo, el 1B Word Benchmark, que es utilizado por un enfoque similar, ELMo [44], tiene aproximadamente el mismo tamaño pero se baraja a nivel de frase, destruyendo la estructura a largo plazo. Nuestro modelo de lenguaje alcanza una perplejidad a nivel de token muy baja de 18,4 en este corpus.

Tabla 1: Una lista de las diferentes tareas y conjuntos de datos utilizados en nuestros experimentos.
|Tarea	|Conjuntos de datos|
|---|---|
|Inferencia del lenguaje natural	|SNLI [5], MultiNLI [66], Question NLI [64], RTE [4], SciTail [25]|
|Respuesta a preguntas	|RACE [30], Story Cloze [40]|
|Similitud de oraciones	|MSR Paraphrase Corpus [14], Quora Question Pairs [9], STS Benchmark [6]|
|Clasificación	|Stanford Sentiment Treebank-2 [54], CoLA [65]|

**Especificaciones del modelo** Nuestro modelo sigue en gran medida el trabajo original del transformer [62]. Entrenamos un transformer de solo decodificador de 12 capas con cabezas de autoatención enmascaradas (estados dimensionales 768 y 12 cabezas de atención). Para las redes de alimentación hacia adelante posición por posición, utilizamos estados internos de 3072 dimensiones. Utilizamos el esquema de optimización Adam [27] con una tasa de aprendizaje máxima de 2.5e-4. La tasa de aprendizaje se incrementó linealmente desde cero durante las primeras 2000 actualizaciones y se redujo a 0 utilizando un esquema de coseno. Entrenamos durante 100 épocas en minibloques de 64 secuencias contiguas de 512 tokens muestreadas aleatoriamente. Dado que la normalización de capas [2] se utiliza ampliamente en todo el modelo, una simple inicialización de pesos de N(0, 0.02) fue suficiente. Utilizamos un vocabulario de codificación de pares de bytes (BPE) con 40.000 fusiones [53] y abandonos residuales, de incrustación y de atención con una tasa de 0,1 para la regularización. También empleamos una versión modificada de la regularización L2 propuesta en [37], con w = 0,01 en todos los pesos no sesgados o de ganancia. Para la función de activación, utilizamos la unidad lineal de error gaussiano (GELU) [18]. Utilizamos embeddings de posición aprendidas en lugar de la versión sinusoidal propuesta en el trabajo original. Utilizamos la biblioteca ftfy2 para limpiar el texto bruto de BooksCorpus, estandarizar algunos signos de puntuación y espacios en blanco, y utilizar el tokenizador spaCy.3

**Detalles del ajuste fino** A menos que se especifique, reutilizamos la configuración de los hiperparámetros del preentrenamiento no supervisado. Añadimos un abandono al clasificador con una tasa de 0,1. Para la mayoría de las tareas, utilizamos una tasa de aprendizaje de 6.25e-5 y un tamaño de lote de 32. Nuestro modelo se ajusta rápidamente y 3 épocas de entrenamiento fueron suficientes para la mayoría de los casos. Utilizamos un esquema de decaimiento lineal de la tasa de aprendizaje con calentamiento durante el 0,2% del entrenamiento. λ se fijó en 0,5.

### 4.2 Ajuste fino supervisado

Realizamos experimentos en una variedad de tareas supervisadas que incluyen la inferencia del lenguaje natural, la respuesta a preguntas, la similitud semántica y la clasificación de textos. Algunas de estas tareas están disponibles como parte del punto de referencia multitarea GLUE recientemente publicado [64], que utilizamos. La Figura 1 ofrece una visión general de todas las tareas y conjuntos de datos.

**Inferencia del lenguaje natural** La tarea de inferencia del lenguaje natural (NLI), también conocida como reconocimiento de implicaciones textuales, consiste en leer un par de frases y juzgar la relación entre ellas a partir de una de implicación, contradicción o neutralidad. Aunque ha habido mucho interés recientemente [58, 35, 44], la tarea sigue siendo un reto debido a la presencia de una amplia variedad de fenómenos como la implicación léxica, la correferencia y la ambigüedad léxica y sintáctica. Evaluamos en cinco conjuntos de datos con diversas fuentes, incluyendo pies de foto de imágenes (SNLI), voz transcrita, ficción popular e informes gubernamentales (MNLI), artículos de Wikipedia (QNLI), exámenes de ciencias (SciTail) o artículos de noticias (RTE).

La Tabla 2 detalla varios resultados en las diferentes tareas de NLI para nuestro modelo y los enfoques anteriores del estado del arte. Nuestro método supera significativamente a las líneas de base en cuatro de los cinco conjuntos de datos, logrando mejoras absolutas de hasta un 1,5% en MNLI, un 5% en SciTail, un 5,8% en QNLI y un 0,6% en SNLI con respecto a los mejores resultados anteriores. Esto demuestra la capacidad de nuestro modelo para razonar mejor sobre múltiples frases y manejar aspectos de la ambigüedad lingüística. En RTE, uno de los conjuntos de datos más pequeños que evaluamos (2490 ejemplos), alcanzamos una precisión del 56%, lo que está por debajo del 61,7% reportado por un modelo BiLSTM multitarea. Dado el fuerte rendimiento de nuestro enfoque en conjuntos de datos NLI más grandes, es probable que nuestro modelo también se beneficie del entrenamiento multitarea, pero no lo hemos explorado actualmente.

2https://ftfy.readthedocs.io/en/latest/
3https://spacy.io/

Tabla 2: Resultados experimentales en tareas de inferencia del lenguaje natural, comparando nuestro modelo con los métodos actuales del estado del arte. 5x indica un conjunto de 5 modelos. Todos los conjuntos de datos utilizan la precisión como métrica de evaluación.
|Método	|MNLI-m	|MNLI-mm	|SNLI	|SciTail	|QNLI	|RTE|
|---|---|---|---|---|---|---|
|ESIM + ELMo [44] (5x)	|-	|-	|89.3	|-	|-	|-|
|CAFE [58] (5x)	|80.2	|79.0	|89.3	|-	|-	|-|
|Stochastic Answer Network [35] (3x)	|80.6	|80.1	|-	|-	|-	|-|
|CAFE [58]	|78.7	|77.9	|88.5	|83.3| | 	|
|GenSen [64]	|71.4	|71.3	|-	|-	|82.3	|59.2|
|Multi-task BiLSTM + Attn [64]	|72.2	|72.1	|-	|-	|82.1	|61.7|
|Finetuned Transformer LM (ours)	|82.1	|81.4	|89.9	|88.3	|88.1	|56.0|

**Respuesta a preguntas y razonamiento de sentido común** Otra tarea que requiere aspectos de razonamiento de una o varias frases es la respuesta a preguntas. Utilizamos el conjunto de datos RACE [30], recientemente publicado, que consiste en pasajes en inglés con preguntas asociadas de exámenes de secundaria y bachillerato. Se ha demostrado que este corpus contiene más preguntas de tipo razonamiento que otros conjuntos de datos como CNN [19] o SQuaD [47], lo que proporciona la evaluación perfecta para nuestro modelo, que está entrenado para manejar contextos de largo alcance. Además, evaluamos en la prueba Story Cloze [40], que consiste en seleccionar el final correcto para historias de varias frases entre dos opciones. En estas tareas, nuestro modelo vuelve a superar los mejores resultados anteriores por márgenes significativos: hasta un 8,9% en Story Cloze y un 5,7% en general en RACE. Esto demuestra la capacidad de nuestro modelo para manejar eficazmente contextos de largo alcance.

Tabla 3: Resultados en respuesta a preguntas y razonamiento de sentido común, comparando nuestro modelo con los métodos actuales del estado del arte. 9x significa un conjunto de 9 modelos.
|Método	|Story Cloze	|RACE-m	|RACE-h	|RACE|
|---|---|---|---|---|
|val-LS-skip [55]	|76.5	|-	|-	|-|
|Hidden Coherence Model [7]	|77.6	|-	|-	|-|
|Dynamic Fusion Net [67] (9x)	|-	|55.6	|49.4	|51.2|
|BiAttention MRU [59] (9x)	|-	|60.2	|50.3	|53.3|
|Finetuned Transformer LM (ours)	|86.5	|62.9	|57.4	|59.0|

**Similitud semántica** Las tareas de similitud semántica (o detección de paráfrasis) implican predecir si dos frases son semánticamente equivalentes o no. Los retos residen en reconocer la reformulación de conceptos, comprender la negación y manejar la ambigüedad sintáctica. Utilizamos tres conjuntos de datos para esta tarea: el corpus de paráfrasis de Microsoft (MRPC) [14] (recopilado de fuentes de noticias), el conjunto de datos de pares de preguntas de Quora (QQP) [9] y el punto de referencia de similitud textual semántica (STS-B) [6]. Obtenemos resultados de última generación en dos de las tres tareas de similitud semántica (Tabla 4) con una ganancia absoluta de 1 punto en STS-B. La diferencia de rendimiento en QQP es significativa, con una mejora absoluta del 4,2% con respecto a Single-task BiLSTM + ELMo + Attn.

**Clasificación** Por último, también evaluamos en dos tareas diferentes de clasificación de textos. El Corpus of Linguistic Acceptability (CoLA) [65] contiene juicios de expertos sobre si una frase es gramatical o no, y pone a prueba el sesgo lingüístico innato de los modelos entrenados. El Stanford Sentiment Treebank (SST-2) [54], por otro lado, es una tarea estándar de clasificación binaria. Nuestro modelo obtiene una puntuación de 45,4 en CoLA, lo que supone un salto especialmente grande con respecto al mejor resultado anterior de 35,0, lo que demuestra el sesgo lingüístico innato aprendido por nuestro modelo. El modelo también alcanza una precisión del 91,3% en SST-2, lo que es competitivo con los resultados del estado del arte. También alcanzamos una puntuación global de 72,8 en el punto de referencia GLUE, que es significativamente mejor que la mejor anterior de 68,9.

Tabla 4: Resultados de similitud semántica y clasificación, comparando nuestro modelo con los métodos actuales del estado del arte. Todas las evaluaciones de las tareas de esta tabla se realizaron utilizando el punto de referencia GLUE. (mc= correlación de Mathews, acc=Precisión, pc=correlación de Pearson)

|Método	                               |Clasificación| |Similitud semántica|	|GLUE||
|--------------------------------------|------|------|------|------|------|-----|
|                                      |CoLA (mc) | SST2 (acc) | MRPC (F1) | STSB (pc) | QQP (F1) | |
|Sparse byte mLSTM [16]                | -    | 93.2 | -    | -    | -    | -   |
|TF-KLD [23]                           | -    | -    | 86.0 | -    | -    | -   |
|ECNU (mixed ensemble) [60]            | -    | -    | -    | 81.0 | -    | -   |
|Single-task BiLSTM + ELMo + Attn [64] | 35.0 | 90.2 | 80.2 | 55.5 | 66.1 | 64.8|
|Multi-task BiLSTM + ELMo + Attn [64]  | 18.9 | 91.6 | 83.5 | 72.8 | 63.3 | 68.9|
|Finetuned Transformer LM (ours)       | 45.4 | 91.3 | 82.3 | 82.0 | 70.3 | 72.8|

En general, nuestro enfoque logra nuevos resultados de última generación en 9 de los 12 conjuntos de datos que evaluamos, superando a los conjuntos en muchos casos. Nuestros resultados también indican que nuestro enfoque funciona bien en conjuntos de datos de diferentes tamaños, desde conjuntos de datos más pequeños como STS-B (≈5,7k ejemplos de entrenamiento) - hasta el más grande - SNLI (≈550k ejemplos de entrenamiento).

# 5 Análisis

**Impacto del número de capas transferidas** Observamos el impacto de transferir un número variable de capas del preentrenamiento no supervisado a la tarea objetivo supervisada. La Figura 2 (izquierda) ilustra el rendimiento de nuestro enfoque en MultiNLI y RACE en función del número de capas transferidas. Observamos el resultado estándar de que la transferencia de embeddings mejora el rendimiento y que cada capa del transformer proporciona beneficios adicionales de hasta un 9% para la transferencia completa en MultiNLI. Esto indica que cada capa en el modelo preentrenado contiene una funcionalidad útil para resolver las tareas objetivo.

![Figure 2](https://d3i71xaburhd42.cloudfront.net/cd18800a0fe0b668a1cc19f2ec95b5003d0a5035/7-Figure2-1.png)
Figura 2: (izquierda) Efecto de transferir un número creciente de capas del modelo de lenguaje preentrenado en RACE y MultiNLI. (derecha) Gráfico que muestra la evolución del rendimiento de disparo cero en diferentes tareas en función de las actualizaciones de preentrenamiento del LM. El rendimiento por tarea se normaliza entre una línea de base de conjetura aleatoria y el estado del arte actual con un solo modelo.

**Comportamientos de disparo cero** Nos gustaría comprender mejor por qué el preentrenamiento del modelo de lenguaje de los transformadores es eficaz. Una hipótesis es que el modelo generativo subyacente aprende a realizar muchas de las tareas que evaluamos para mejorar su capacidad de modelado del lenguaje y que cuanto más estructurado

Tabla 5: Análisis de varias ablaciones del modelo en diferentes tareas. La puntuación media es una media no ponderada de todos los resultados. (mc= correlación de Mathews, acc=Precisión, pc=correlación de Pearson)

|Método	|Puntuación media	|CoLA (mc)	|SST2 (acc)	|MRPC (F1)	|STSB (pc)	|QQP (F1)	|MNLI (acc)	|QNLI (acc)	|RTE (acc)|
|---|---|---|---|---|---|---|---|---|---|
|Transformer w/ aux LM (full)	|74.7 | 45.4 | 91.3 | 82.3 | 82.0 | 70.3 | 81.8 | 88.1 | 56.0 |
|Transformer w/o pre-training	|59.9 | 18.9 | 84.0 | 79.4 | 30.9 | 65.5 | 75.7 | 71.2 | 53.8 |
|Transformer w/o aux LM	|75.0 | 47.9 | 92.0 | 84.9 | 83.2 | 69.8 | 81.1 | 86.9 | 54.4 | |
|LSTM w/ aux LM	|69.1 | 30.3 | 90.5 | 83.2 | 71.8 | 68.1 | 73.7 | 81.1 | 54.6 | | |

la memoria atencional del transformer ayuda a la transferencia en comparación con los LSTM. Diseñamos una serie de soluciones heurísticas que utilizan el modelo generativo subyacente para realizar tareas sin ajuste fino supervisado. Visualizamos la eficacia de estas soluciones heurísticas a lo largo del preentrenamiento generativo en la figura 2 (derecha). Observamos que el rendimiento de estas heurísticas es estable y aumenta constantemente a lo largo del entrenamiento, lo que sugiere que el preentrenamiento generativo apoya el aprendizaje de una amplia variedad de funcionalidades relevantes para la tarea. También observamos que el LSTM exhibe una mayor varianza en su rendimiento de disparo cero, lo que sugiere que el sesgo inductivo de la arquitectura del Transformer ayuda a la transferencia.

Para CoLA (aceptabilidad lingüística), los ejemplos se puntúan como la probabilidad logarítmica media de token que el modelo generativo asigna y las predicciones se hacen mediante umbrales. Para SST-2 (análisis de sentimientos), añadimos el token very a cada ejemplo y restringimos la distribución de salida del modelo de lenguaje sólo a las palabras positivo y negativo y adivinamos el token al que asigna mayor probabilidad como predicción. Para RACE (respuesta a preguntas), elegimos la respuesta a la que el modelo generativo asigna la mayor probabilidad logarítmica media de token cuando está condicionado al documento y a la pregunta. Para DPRD [46] (esquemas de Winograd), sustituimos el pronombre definido por los dos posibles referentes y predecimos la resolución a la que el modelo generativo asigna mayor probabilidad logarítmica media del resto de la secuencia tras la sustitución.

**Estudios de ablación** Realizamos tres estudios de ablación diferentes (Tabla 5). En primer lugar, examinamos el rendimiento de nuestro método sin el objetivo auxiliar de LM durante el ajuste fino. Observamos que el objetivo auxiliar ayuda en las tareas de NLI y QQP. En general, la tendencia sugiere que los conjuntos de datos más grandes se benefician del objetivo auxiliar, pero los más pequeños no. En segundo lugar, analizamos el efecto del Transformer comparándolo con un LSTM de una sola capa y 2048 unidades utilizando el mismo marco. Observamos una caída de la puntuación media de 5,6 cuando se utiliza el LSTM en lugar del Transformer. El LSTM sólo supera al Transformer en un conjunto de datos: MRPC. Por último, también comparamos con nuestra arquitectura de transformadores entrenada directamente en tareas objetivo supervisadas, sin preentrenamiento. Observamos que la falta de preentrenamiento perjudica el rendimiento en todas las tareas, lo que resulta en una disminución del 14,8% en comparación con nuestro modelo completo.

# 6 Conclusión

Hemos introducido un marco para lograr una sólida comprensión del lenguaje natural con un único modelo agnóstico de tareas a través del preentrenamiento generativo y el ajuste fino discriminativo. Al realizar el preentrenamiento en un corpus diverso con largos tramos de texto contiguo, nuestro modelo adquiere un importante conocimiento del mundo y la capacidad de procesar dependencias de largo alcance que luego se transfieren con éxito a la resolución de tareas discriminativas como la respuesta a preguntas, la evaluación de la similitud semántica, la determinación de la implicación y la clasificación de textos, mejorando el estado del arte en 9 de los 12 conjuntos de datos que estudiamos. Utilizar el entrenamiento (pre)supervisado para mejorar el rendimiento en tareas discriminativas ha sido durante mucho tiempo un objetivo importante de la investigación en aprendizaje automático. Nuestro trabajo sugiere que de hecho es posible lograr ganancias significativas en el rendimiento, y ofrece indicios sobre qué modelos (Transformers) y conjuntos de datos (texto con dependencias de largo alcance) funcionan mejor con este enfoque. Esperamos que esto ayude a impulsar nuevas investigaciones sobre el aprendizaje no supervisado, tanto para la comprensión del lenguaje natural como para otros dominios, mejorando aún más nuestra comprensión de cómo y cuándo funciona el aprendizaje no supervisado.