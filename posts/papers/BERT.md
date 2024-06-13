# Pre-training of Deep Bidirectional Transformers for Language Understanding

Este documento presenta un nuevo modelo de representación lingüística llamado BERT, que significa "Bidirectional Encoder Representations from Transformers". A diferencia de los recientes modelos de representación lingüística (Peters et al., 2018a; Radford et al., 2018), BERT está diseñado para pre-entrenar representaciones bidireccionales profundas a partir de texto sin etiquetar condicionando conjuntamente en el contexto izquierdo y derecho en todas las capas. Como resultado, el modelo BERT pre-entrenado puede ser ajustado con solo una capa de salida adicional para crear modelos de última generación para una amplia gama de tareas, como la respuesta a preguntas y la inferencia lingüística, sin modificaciones sustanciales en la arquitectura específica de la tarea.
BERT es conceptualmente simple y empíricamente potente. Obtiene nuevos resultados de última generación en once tareas de procesamiento del lenguaje natural, incluyendo el aumento de la puntuación GLUE al 80.5% (7.7 puntos de mejora absoluta), la precisión MultiNLI al 86.7% (4.6% de mejora absoluta), el F1 de prueba de SQuAD v1.1 para la respuesta a preguntas al 93.2 (1.5 puntos de mejora absoluta) y el F1 de prueba de SQuAD v2.0 al 83.1 (5.1 puntos de mejora absoluta).

## 1. Introducción

El pre-entrenamiento de modelos de lenguaje ha demostrado ser efectivo para mejorar muchas tareas de procesamiento del lenguaje natural (Dai y Le, 2015; Peters et al., 2018a; Radford et al., 2018; Howard y Ruder, 2018). Estos incluyen tareas a nivel de oración como la inferencia del lenguaje natural (Bowman et al., 2015; Williams et al., 2018) y la paráfrasis (Dolan y Brockett, 2005), que apuntan a predecir las relaciones entre las oraciones analizándolas de forma holística, así como tareas a nivel de token como el reconocimiento de entidades nombradas y la respuesta a preguntas, donde los modelos deben producir una salida de grano fino a nivel de token (Tjong Kim Sang y De Meulder, 2003; Rajpurkar et al., 2016).

Hay dos estrategias existentes para aplicar representaciones lingüísticas pre-entrenadas a tareas posteriores: basadas en características y de ajuste fino. El enfoque basado en características, como ELMo (Peters et al., 2018a), utiliza arquitecturas específicas de la tarea que incluyen las representaciones pre-entrenadas como características adicionales. El enfoque de ajuste fino, como el Generative Pre-trained Transformer (OpenAI GPT) (Radford et al., 2018), introduce parámetros específicos de la tarea mínimos y se entrena en las tareas posteriores simplemente ajustando todos los parámetros pre-entrenados. Los dos enfoques comparten la misma función objetivo durante el pre-entrenamiento, donde utilizan modelos de lenguaje unidireccionales para aprender representaciones lingüísticas generales.

Argumentamos que las técnicas actuales restringen el poder de las representaciones pre-entrenadas, especialmente para los enfoques de ajuste fino. La limitación principal es que los modelos de lenguaje estándar son unidireccionales, y esto limita la elección de arquitecturas que se pueden utilizar durante el pre-entrenamiento. Por ejemplo, en OpenAI GPT, los autores utilizan una arquitectura de izquierda a derecha, donde cada token solo puede atender a tokens anteriores en las capas de autoatención del Transformer (Vaswani et al., 2017). Tales restricciones son subóptimas para tareas a nivel de oración y podrían ser muy perjudiciales al aplicar enfoques basados en el ajuste fino a tareas a nivel de token como la respuesta a preguntas, donde es crucial incorporar el contexto desde ambas direcciones.

En este documento, mejoramos los enfoques basados en el ajuste fino proponiendo BERT: Bidirectional Encoder Representations from Transformers. BERT alivia la restricción de unidireccionalidad mencionada anteriormente utilizando un objetivo de pre-entrenamiento de "modelo de lenguaje enmascarado" (MLM), inspirado en la tarea Cloze (Taylor, 1953). El modelo de lenguaje enmascarado enmascara aleatoriamente algunos de los tokens de la entrada, y el objetivo es predecir el identificador de vocabulario original de la palabra enmascarada basándose solo en su contexto. A diferencia del pre-entrenamiento del modelo de lenguaje de izquierda a derecha, el objetivo MLM permite que la representación fusione el contexto izquierdo y derecho, lo que nos permite pre-entrenar un Transformer bidireccional profundo. Además del modelo de lenguaje enmascarado, también utilizamos una tarea de "predicción de la oración siguiente" que pre-entrena conjuntamente representaciones de pares de texto. Las contribuciones de nuestro documento son las siguientes:

 * Demostramos la importancia del pre-entrenamiento bidireccional para las representaciones lingüísticas. A diferencia de Radford et al. (2018), que utiliza modelos de lenguaje unidireccionales para el pre-entrenamiento, BERT utiliza modelos de lenguaje enmascarados para permitir representaciones bidireccionales profundas pre-entrenadas. Esto también contrasta con Peters et al. (2018a), que utiliza una concatenación superficial de LMs de izquierda a derecha y de derecha a izquierda entrenados independientemente.
 * Mostramos que las representaciones pre-entrenadas reducen la necesidad de muchas arquitecturas específicas de la tarea altamente diseñadas. BERT es el primer modelo de representación basado en el ajuste fino que alcanza un rendimiento de última generación en un conjunto amplio de tareas a nivel de oración y token, superando a muchas arquitecturas específicas de la tarea.
 * BERT avanza el estado del arte para once tareas de PNL. El código y los modelos pre-entrenados están disponibles en https://github.com/ google-research/bert.

## 2. Trabajo Relacionado

Existe una larga historia de pre-entrenamiento de representaciones lingüísticas generales, y revisamos brevemente los enfoques más utilizados en esta sección.

### 2.1 Enfoques Basados en Características no Supervisados

Aprender representaciones de palabras ampliamente aplicables ha sido un área activa de investigación durante décadas, incluyendo métodos no neuronales (Brown et al., 1992; Ando y Zhang, 2005; Blitzer et al., 2006) y neuronales (Mikolov et al., 2013; Pennington et al., 2014). Las incrustaciones de palabras pre-entrenadas son una parte integral de los sistemas modernos de PNL, ofreciendo mejoras significativas con respecto a las incrustaciones aprendidas desde cero (Turian et al., 2010). Para pre-entrenar vectores de incrustación de palabras, se han utilizado objetivos de modelado del lenguaje de izquierda a derecha (Mnih y Hinton, 2009), así como objetivos para discriminar palabras correctas de incorrectas en el contexto izquierdo y derecho (Mikolov et al., 2013).

Estos enfoques se han generalizado a granularidades más gruesas, como incrustaciones de oraciones (Kiros et al., 2015; Logeswaran y Lee, 2018) o incrustaciones de párrafos (Le y Mikolov, 2014). Para entrenar representaciones de oraciones, el trabajo anterior ha utilizado objetivos para clasificar las oraciones siguientes candidatas (Jernite et al., 2017; Logeswaran y Lee, 2018), la generación de izquierda a derecha de las palabras de la oración siguiente dada una representación de la oración anterior (Kiros et al., 2015), o objetivos derivados de autoencoders de eliminación de ruido (Hill et al., 2016).

ELMo y su predecesor (Peters et al., 2017, 2018a) generalizan la investigación tradicional de incrustación de palabras a lo largo de una dimensión diferente. Extraen características sensibles al contexto de un modelo de lenguaje de izquierda a derecha y de derecha a izquierda. La representación contextual de cada token es la concatenación de las representaciones de izquierda a derecha y de derecha a izquierda. Al integrar incrustaciones de palabras contextuales con arquitecturas específicas de la tarea existentes, ELMo avanza el estado del arte para varios puntos de referencia importantes de PNL (Peters et al., 2018a) incluyendo la respuesta a preguntas (Rajpurkar et al., 2016), el análisis de sentimientos (Socher et al., 2013) y el reconocimiento de entidades nombradas (Tjong Kim Sang y De Meulder, 2003). Melamud et al. (2016) propusieron aprender representaciones contextuales a través de una tarea para predecir una sola palabra desde el contexto izquierdo y derecho utilizando LSTMs. De manera similar a ELMo, su modelo está basado en características y no es profundamente bidireccional. Fedus et al. (2018) muestra que la tarea Cloze se puede utilizar para mejorar la solidez de los modelos de generación de texto.

### 2.2 Enfoques de Ajuste Fino no Supervisados

Al igual que con los enfoques basados en características, los primeros trabajos en esta dirección solo pre-entrenaban parámetros de incrustación de palabras a partir de texto sin etiquetar (Collobert y Weston, 2008).

Más recientemente, los codificadores de oraciones o documentos que producen representaciones contextuales de tokens se han pre-entrenado a partir de texto sin etiquetar y se han ajustado finamente para una tarea posterior supervisada (Dai y Le, 2015; Howard y Ruder, 2018; Radford et al., 2018). La ventaja de estos enfoques es que se necesitan pocos parámetros para aprender desde cero. Al menos en parte debido a esta ventaja, OpenAI GPT (Radford et al., 2018) logró resultados previos de última generación en muchas tareas a nivel de oración del punto de referencia GLUE (Wang et al., 2018a). El modelado del lenguaje de izquierda a derecha y los objetivos de autocodificador se han utilizado para el pre-entrenamiento de estos modelos (Howard y Ruder, 2018; Radford et al., 2018; Dai y Le, 2015).

### 2.3 Aprendizaje por Transferencia a partir de Datos Supervisados

También ha habido trabajos que muestran una transferencia efectiva a partir de tareas supervisadas con conjuntos de datos grandes, como la inferencia del lenguaje natural (Conneau et al., 2017) y la traducción automática (McCann et al., 2017). La investigación en visión artificial también ha demostrado la importancia del aprendizaje por transferencia a partir de modelos grandes pre-entrenados, donde una receta efectiva es ajustar finamente los modelos pre-entrenados con ImageNet (Deng et al., 2009; Yosinski et al., 2014).

# 3. BERT

Presentamos BERT y su implementación detallada en esta sección. Hay dos pasos en nuestro marco: pre-entrenamiento y ajuste fino. Durante el pre-entrenamiento, el modelo se entrena en datos sin etiquetar en diferentes tareas de pre-entrenamiento. Para el ajuste fino, el modelo BERT se inicializa primero con los parámetros pre-entrenados, y todos los parámetros se ajustan finamente utilizando datos etiquetados de las tareas posteriores. Cada tarea posterior tiene modelos ajustados finamente separados, aunque se inicializan con los mismos parámetros pre-entrenados. El ejemplo de respuesta a preguntas en la Figura 1 servirá como ejemplo continuo para esta sección.

Una característica distintiva de BERT es su arquitectura unificada en diferentes tareas. Hay una diferencia mínima entre la arquitectura pre-entrenada y la arquitectura final posterior.

**Arquitectura del Modelo** La arquitectura del modelo de BERT es un codificador Transformer bidireccional de varias capas basado en la implementación original descrita en Vaswani et al. (2017) y lanzada en la biblioteca tensor2tensor.1 Debido a que el uso de Transformers se ha vuelto común y nuestra implementación es casi idéntica a la original, omitiremos una descripción exhaustiva de la arquitectura del modelo y remitiremos a los lectores a Vaswani et al. (2017) así como a excelentes guías como "The Annotated Transformer".2

En este trabajo, denotamos el número de capas (es decir, bloques Transformer) como L, el tamaño oculto como H y el número de cabezas de autoatención como A.3

Presentamos principalmente resultados en dos tamaños de modelo: BERTBASE (L=12, H=768, A=12, Parámetros Totales=110M) y BERTLARGE (L=24, H=1024, A=16, Parámetros Totales=340M).

BERTBASE fue elegido para tener el mismo tamaño de modelo que OpenAI GPT para fines de comparación. Sin embargo, es fundamental que el Transformer de BERT use autoatención bidireccional, mientras que el Transformer de GPT usa autoatención restringida donde cada token solo puede atender al contexto a su izquierda.4

1 https://github.com/tensorflow/tensor2tensor

2 http://nlp.seas.harvard.edu/2018/04/03/attention.html

3 En todos los casos, establecemos el tamaño de la red neuronal de avance / filtrado en 4H, es decir, 3072 para H = 768 y 4096 para H = 1024.

4 Observamos que en la literatura, el Transformer bidireccional a menudo se denomina "codificador Transformer", mientras que la versión de solo contexto izquierdo se denomina "decodificador Transformer" ya que se puede utilizar para la generación de texto.

**Representaciones de Entrada / Salida** Para que BERT maneje una variedad de tareas posteriores, nuestra representación de entrada puede representar inequívocamente tanto una sola oración como un par de oraciones (por ejemplo, 〈Pregunta, Respuesta〉) en una secuencia de tokens. A lo largo de este trabajo, una "oración" puede ser un tramo arbitrario de texto contiguo, en lugar de una oración lingüística real. Una "secuencia" se refiere a la secuencia de tokens de entrada a BERT, que puede ser una sola oración o dos oraciones empaquetadas juntas.

Utilizamos incrustaciones de WordPiece (Wu et al., 2016) con un vocabulario de 30,000 tokens. El primer token de cada secuencia es siempre un token de clasificación especial ([CLS]). El estado oculto final correspondiente a este token se utiliza como la representación de secuencia agregada para tareas de clasificación. Los pares de oraciones se empaquetan juntos en una sola secuencia. Diferenciamos las oraciones de dos maneras. Primero, las separamos con un token especial ([SEP]). Segundo, agregamos una incrustación aprendida a cada token que indica si pertenece a la oración A o a la oración B. Como se muestra en la Figura 1, denotamos la incrustación de entrada como E, el vector oculto final del token especial [CLS] como C ∈ RH y el vector oculto final para el i-ésimo token de entrada como Ti ∈ RH.

Para un token dado, su representación de entrada se construye sumando las incrustaciones correspondientes de token, segmento y posición. Una visualización de esta construcción se puede ver en la Figura 2.

### 3.1 Pre-entrenamiento de BERT

A diferencia de Peters et al. (2018a) y Radford et al. (2018), no usamos modelos de lenguaje tradicionales de izquierda a derecha o de derecha a izquierda para pre-entrenar BERT. En cambio, pre-entrenamos BERT utilizando dos tareas no supervisadas, descritas en esta sección. Este paso se presenta en la parte izquierda de la Figura 1.

**Tarea # 1: MLM** Intuitivamente, es razonable creer que un modelo bidireccional profundo es estrictamente más poderoso que un modelo de izquierda a derecha o la concatenación superficial de un modelo de izquierda a derecha y uno de derecha a izquierda. Desafortunadamente, los modelos de lenguaje condicionales estándar solo se pueden entrenar de izquierda a derecha o de derecha a izquierda, ya que el condicionamiento bidireccional permitiría que cada palabra "se viera" indirectamente, y el modelo podría predecir trivialmente la palabra objetivo en un contexto de varias capas.

Para entrenar una representación bidireccional profunda, simplemente enmascaramos un cierto porcentaje de los tokens de entrada al azar y luego predecimos esos tokens enmascarados. Nos referimos a este procedimiento como "MLM" ("masked LM"), aunque a menudo se denomina tarea Cloze en la literatura (Taylor, 1953). En este caso, los vectores ocultos finales correspondientes a los tokens enmascarados se alimentan a un softmax de salida sobre el vocabulario, como en un LM estándar. En todos nuestros experimentos, enmascaramos el 15% de todos los tokens de WordPiece en cada secuencia al azar. En contraste con los autoencoders de eliminación de ruido (Vincent et al., 2008), solo predecimos las palabras enmascaradas en lugar de reconstruir toda la entrada.

Aunque esto nos permite obtener un modelo pre-entrenado bidireccional, una desventaja es que estamos creando una discrepancia entre el pre-entrenamiento y el ajuste fino, ya que el token [MASK] no aparece durante el ajuste fino. Para mitigar esto, no siempre reemplazamos las palabras "enmascaradas" con el token [MASK] real. El generador de datos de entrenamiento elige aleatoriamente el 15% de las posiciones de los tokens para la predicción. Si se elige el i-ésimo token, reemplazamos el i-ésimo token con (1) el token [MASK] el 80% de las veces, (2) un token aleatorio el 10% de las veces, (3) el i-ésimo token sin cambios el 10% de las veces. Luego, Ti se utilizará para predecir el token original con la pérdida de entropía cruzada. Comparamos variaciones de este procedimiento en el Apéndice C.2.

**Tarea # 2: Predicción de la Oración Siguiente (NSP)** Muchas tareas posteriores importantes, como la respuesta a preguntas (QA) y la inferencia del lenguaje natural (NLI), se basan en la comprensión de la relación entre dos oraciones, lo que no se captura directamente mediante el modelado del lenguaje. Para entrenar un modelo que comprenda las relaciones de oración, pre-entrenamos para una tarea de predicción de la oración siguiente binarizada que se puede generar trivialmente a partir de cualquier corpus monolingüístico. Específicamente, al elegir las oraciones A y B para cada ejemplo de pre-entrenamiento, el 50% de las veces B es la oración siguiente real que sigue a A (etiquetada como IsNext), y el 50% de las veces es una oración aleatoria del corpus (etiquetada como NotNext). Como se muestra en la Figura 1, C se utiliza para la predicción de la oración siguiente (NSP).5 A pesar de su simplicidad, demostramos en la Sección 5.1 que el pre-entrenamiento hacia esta tarea es muy beneficioso tanto para QA como para NLI.6

5 El modelo final alcanza una precisión del 97% -98% en NSP.
6 El vector C no es una representación de oración significativa sin ajuste fino, ya que se entrenó con NSP.

La tarea NSP está estrechamente relacionada con los objetivos de aprendizaje de representación utilizados en Jernite et al. (2017) y Logeswaran y Lee (2018). Sin embargo, en trabajos anteriores, solo las incrustaciones de oraciones se transfieren a tareas posteriores, donde BERT transfiere todos los parámetros para inicializar los parámetros del modelo de la tarea final.

**Datos de Pre-entrenamiento** El procedimiento de pre-entrenamiento sigue en gran medida la literatura existente sobre el pre-entrenamiento de modelos de lenguaje. Para el corpus de pre-entrenamiento, usamos el BooksCorpus (800M palabras) (Zhu et al., 2015) y la Wikipedia en inglés (2,500M palabras). Para Wikipedia, solo extraemos los pasajes de texto e ignoramos las listas, las tablas y los encabezados. Es fundamental utilizar un corpus a nivel de documento en lugar de un corpus a nivel de oración barajado como el Billion Word Benchmark (Chelba et al., 2013) para extraer secuencias contiguas largas.

### 3.2 Ajuste Fino de BERT

El ajuste fino es sencillo ya que el mecanismo de autoatención en el Transformer permite que BERT modele muchas tareas posteriores, ya sea que involucren un solo texto o pares de texto, intercambiando las entradas y salidas apropiadas. Para aplicaciones que involucran pares de texto, un patrón común es codificar de forma independiente los pares de texto antes de aplicar la atención cruzada bidireccional, como Parikh et al. (2016); Seo et al. (2017). BERT en cambio utiliza el mecanismo de autoatención para unificar estas dos etapas, ya que codificar un par de texto concatenado con autoatención incluye efectivamente la atención cruzada bidireccional entre dos oraciones.

Para cada tarea, simplemente conectamos las entradas y salidas específicas de la tarea en BERT y ajustamos finamente todos los parámetros de extremo a extremo. En la entrada, la oración A y la oración B del pre-entrenamiento son análogas a (1) pares de oraciones en la paráfrasis, (2) pares de hipótesis-premisa en la inferencia, (3) pares de preguntas-pasajes en la respuesta a preguntas y (4) un par de texto-∅ degenerado en la clasificación de texto o la etiquetación de secuencias. En la salida, las representaciones de tokens se alimentan a una capa de salida para tareas a nivel de token, como la etiquetación de secuencias o la respuesta a preguntas, y la representación [CLS] se alimenta a una capa de salida para la clasificación, como la inferencia o el análisis de sentimientos.

En comparación con el pre-entrenamiento, el ajuste fino es relativamente económico. Todos los resultados del documento se pueden replicar en un máximo de 1 hora en un solo Cloud TPU, o en unas pocas horas en una GPU, comenzando desde el mismo modelo pre-entrenado.7 Describimos los detalles específicos de la tarea en las subsecciones correspondientes de la Sección 4. Se pueden encontrar más detalles en el Apéndice A.5.

## 4. Experimentos

En esta sección, presentamos los resultados del ajuste fino de BERT en 11 tareas de PNL.

### 4.1 GLUE

El punto de referencia General Language Understanding Evaluation (GLUE) (Wang et al., 2018a) es una colección de diversas tareas de comprensión del lenguaje natural. Se incluyen descripciones detalladas de los conjuntos de datos GLUE en el Apéndice B.1.

Para ajustar finamente en GLUE, representamos la secuencia de entrada (para una sola oración o pares de oraciones) como se describió en la Sección 3, y usamos el vector oculto final C ∈ RH correspondiente al primer token de entrada ([CLS]) como la representación agregada. Los únicos parámetros nuevos introducidos durante el ajuste fino son los pesos de la capa de clasificación W ∈ RK×H, donde K es el número de etiquetas. Calculamos una pérdida de clasificación estándar con C y W, es decir, log(softmax(CW T)).

7 Por ejemplo, el modelo BERT SQuAD se puede entrenar en unos 30 minutos en un solo Cloud TPU para lograr una puntuación Dev F1 del 91.0%.
8 Ver (10) en https://gluebenchmark.com/faq.

Utilizamos un tamaño de lote de 32 y ajustamos finamente durante 3 épocas sobre los datos para todas las tareas de GLUE. Para cada tarea, seleccionamos la mejor tasa de aprendizaje de ajuste fino (entre 5e-5, 4e-5, 3e-5 y 2e-5) en el conjunto Dev. Además, para BERTLARGE encontramos que el ajuste fino a veces era inestable en conjuntos de datos pequeños, por lo que realizamos varios reinicios aleatorios y seleccionamos el mejor modelo en el conjunto Dev. Con reinicios aleatorios, usamos el mismo punto de control pre-entrenado pero realizamos diferentes barajos de datos de ajuste fino e inicialización de la capa del clasificador.9

Los resultados se presentan en la Tabla 1. Tanto BERTBASE como BERTLARGE superan a todos los sistemas en todas las tareas por un margen sustancial, obteniendo una mejora de precisión promedio del 4.5% y el 7.0% respectivamente sobre el estado del arte anterior. Tenga en cuenta que BERTBASE y OpenAI GPT son casi idénticos en términos de arquitectura del modelo aparte del enmascaramiento de atención. Para la tarea GLUE más grande y ampliamente reportada, MNLI, BERT obtiene una mejora de precisión absoluta del 4.6%. En la tabla de clasificación oficial de GLUE10, BERTLARGE obtiene una puntuación de 80.5, en comparación con OpenAI GPT, que obtiene 72.8 a partir de la fecha de este escrito.

Encontramos que BERTLARGE supera significativamente a BERTBASE en todas las tareas, especialmente aquellas con muy pocos datos de entrenamiento. El efecto del tamaño del modelo se explora más a fondo en la Sección 5.2.

### 4.2 SQuAD v1.1

El Stanford Question Answering Dataset (SQuAD v1.1) es una colección de 100,000 pares de preguntas / respuestas creados por la multitud (Rajpurkar et al., 2016). Dada una pregunta y un pasaje de Wikipedia que contiene la respuesta, la tarea es predecir el intervalo de texto de respuesta en el pasaje.

Como se muestra en la Figura 1, en la tarea de respuesta a preguntas, representamos la pregunta y el pasaje de entrada como una sola secuencia empaquetada, con la pregunta usando la incrustación A y el pasaje usando la incrustación B. Solo introducimos un vector de inicio S ∈ RH y un vector de fin E ∈ RH durante el ajuste fino. La probabilidad de que la palabra i sea el inicio del intervalo de respuesta se calcula como un producto punto entre Ti y S seguido de un softmax sobre todas las palabras en el párrafo: Pi = eS·Ti∑ j eS·Tj.

Se utiliza la fórmula análoga para el final del intervalo de respuesta. La puntuación de un intervalo candidato desde la posición i hasta la posición j se define como S·Ti + E·Tj, y el intervalo de puntuación máxima donde j ≥ i se utiliza como predicción. El objetivo de entrenamiento es la suma de las verosimilitudes logarítmicas de las posiciones de inicio y final correctas. Ajustamos finamente durante 3 épocas con una tasa de aprendizaje de 5e-5 y un tamaño de lote de 32.

9 La distribución del conjunto de datos GLUE no incluye las etiquetas de prueba, y solo realizamos una única presentación al servidor de evaluación GLUE para cada uno de BERTBASE y BERTLARGE.
10 https://gluebenchmark.com/leaderboard

La Tabla 2 muestra las entradas principales de la tabla de clasificación, así como los resultados de los principales sistemas publicados (Seo et al., 2017; Clark y Gardner, 2018; Peters et al., 2018a; Hu et al., 2018). Los principales resultados de la tabla de clasificación de SQuAD no tienen descripciones de sistemas públicas actualizadas disponibles,11 y se les permite utilizar cualquier dato público al entrenar sus sistemas. Por lo tanto, usamos un aumento de datos modesto en nuestro sistema ajustando finamente primero en TriviaQA (Joshi et al., 2017) antes de ajustar finamente en SQuAD.

Nuestro sistema de mejor rendimiento supera al sistema principal de la tabla de clasificación en +1.5 F1 en el ensamblaje y +1.3 F1 como un solo sistema. De hecho, nuestro único modelo BERT supera al sistema de ensamblaje superior en términos de puntuación F1. Sin datos de ajuste fino de TriviaQA, solo perdemos 0.1-0.4 F1, superando a todos los sistemas existentes por un amplio margen.12

### 4.3 SQuAD v2.0

La tarea SQuAD 2.0 amplía la definición del problema SQuAD 1.1 al permitir la posibilidad de que no exista una respuesta corta en el párrafo proporcionado, lo que hace que el problema sea más realista.

Utilizamos un enfoque simple para extender el modelo BERT SQuAD v1.1 para esta tarea. Tratamos las preguntas que no tienen respuesta como que tienen un intervalo de respuesta con inicio y final en el token [CLS]. El espacio de probabilidad para las posiciones del intervalo de respuesta de inicio y fin se extiende para incluir la posición del token [CLS]. Para la predicción, comparamos la puntuación del intervalo sin respuesta: snull = S·C + E·C con la puntuación del mejor intervalo no nulo

11 QANet se describe en Yu et al. (2018), pero el sistema ha mejorado sustancialmente después de la publicación.
12 Los datos de TriviaQA que utilizamos consisten en párrafos de TriviaQA-Wiki formados por los primeros 400 tokens en documentos, que contienen al menos una de las posibles respuestas proporcionadas.

ˆsi,j = maxj≥iS·Ti + E·Tj. Predecimos una respuesta no nula cuando ˆsi,j > snull + τ, donde el umbral τ se selecciona en el conjunto dev para maximizar F1. No usamos datos de TriviaQA para este modelo. Ajustamos finamente durante 2 épocas con una tasa de aprendizaje de 5e-5 y un tamaño de lote de 48.

Los resultados en comparación con las entradas anteriores de la tabla de clasificación y el mejor trabajo publicado (Sun et al., 2018; Wang et al., 2018b) se muestran en la Tabla 3, excluyendo los sistemas que usan BERT como uno de sus componentes. Observamos una mejora de +5.1 F1 sobre el sistema mejor anterior.

### 4.4 SWAG

El conjunto de datos Situations With Adversarial Generations (SWAG) contiene 113,000 ejemplos de finalización de pares de oraciones que evalúan la inferencia de sentido común fundamentada (Zellers et al., 2018). Dada una oración, la tarea es elegir la continuación más plausible entre cuatro opciones.

Al ajustar finamente el conjunto de datos SWAG, construimos cuatro secuencias de entrada, cada una de las cuales contiene la concatenación de la oración dada (oración A) y una posible continuación (oración B). Los únicos parámetros específicos de la tarea que se introducen son un vector cuyo producto punto con la representación del token [CLS] C denota una puntuación para cada opción, que se normaliza con una capa softmax.

Ajustamos finamente el modelo durante 3 épocas con una tasa de aprendizaje de 2e-5 y un tamaño de lote de 16. Los resultados se presentan en la Tabla 4. BERTLARGE supera al sistema de referencia ESIM+ELMo de los autores en +27.1% y a OpenAI GPT en 8.3%.

# 5. Estudios de Ablación

En esta sección, realizamos experimentos de ablación sobre una serie de facetas de BERT para comprender mejor su importancia relativa. Se pueden encontrar estudios de ablación adicionales en el Apéndice C.

### 5.1 Efecto de las Tareas de Pre-entrenamiento

Demostramos la importancia de la bidireccionalidad profunda de BERT evaluando dos objetivos de pre-entrenamiento utilizando exactamente los mismos datos de pre-entrenamiento, esquema de ajuste fino e hiperparámetros que BERTBASE:

**No NSP**: Un modelo bidireccional que se entrena utilizando el "modelo de lenguaje enmascarado" (MLM) pero sin la tarea de "predicción de la oración siguiente" (NSP).
LTR & No NSP: Un modelo de solo contexto izquierdo que se entrena utilizando un LM de izquierda a derecha (LTR) estándar, en lugar de un MLM. La restricción de solo izquierda también se aplicó durante el ajuste fino, porque eliminarla introdujo una discrepancia de pre-entrenamiento / ajuste fino que degradó el rendimiento posterior. Además, este modelo se pre-entrenó sin la tarea NSP. Esto es directamente comparable a OpenAI GPT, pero utilizando nuestro conjunto de datos de entrenamiento más grande, nuestra representación de entrada y nuestro esquema de ajuste fino.

Primero examinamos el impacto que aporta la tarea NSP. En la Tabla 5, mostramos que eliminar NSP perjudica el rendimiento significativamente en QNLI, MNLI y SQuAD 1.1. A continuación, evaluamos el impacto de entrenar representaciones bidireccionales comparando "No NSP" con "LTR & No NSP". El modelo LTR funciona peor que el modelo MLM en todas las tareas, con grandes caídas en MRPC y SQuAD.

Para SQuAD, es intuitivamente claro que un modelo LTR funcionará mal en las predicciones de tokens, ya que los estados ocultos a nivel de token no tienen contexto del lado derecho. Para hacer un intento de buena fe de fortalecer el sistema LTR, agregamos un BiLSTM inicializado aleatoriamente en la parte superior. Esto mejora significativamente los resultados en SQuAD, pero los resultados siguen siendo mucho peores que los de los modelos bidireccionales pre-entrenados. El BiLSTM perjudica el rendimiento en las tareas GLUE.

Reconocemos que también sería posible entrenar modelos LTR y RTL separados y representar cada token como la concatenación de los dos modelos, como lo hace ELMo. Sin embargo: (a) esto es el doble de costoso que un solo modelo bidireccional; (b) esto no es intuitivo para tareas como QA, ya que el modelo RTL no podría condicionar la respuesta a la pregunta; (c) esto es estrictamente menos poderoso que un modelo bidireccional profundo, ya que puede usar el contexto izquierdo y derecho en cada capa.

### 5.2 Efecto del Tamaño del Modelo

En esta sección, exploramos el efecto del tamaño del modelo en la precisión de la tarea de ajuste fino. Entrenamos una serie de modelos BERT con un número diferente de capas, unidades ocultas y cabezas de atención, mientras que de otro modo usamos los mismos hiperparámetros y procedimiento de entrenamiento que se describieron anteriormente.

Los resultados en las tareas GLUE seleccionadas se muestran en la Tabla 6. En esta tabla, informamos la precisión promedio del conjunto Dev a partir de 5 reinicios aleatorios del ajuste fino. Podemos ver que los modelos más grandes conducen a una mejora de precisión estricta en los cuatro conjuntos de datos, incluso para MRPC, que solo tiene 3,600 ejemplos de entrenamiento etiquetados y es sustancialmente diferente de las tareas de pre-entrenamiento. También es quizás sorprendente que podamos lograr mejoras tan significativas en modelos que ya son bastante grandes en relación con la literatura existente. Por ejemplo, el Transformer más grande explorado en Vaswani et al. (2017) es (L=6, H=1024, A=16) con 100M parámetros para el codificador, y el Transformer más grande que hemos encontrado en la literatura es (L=64, H=512, A=2) con 235M parámetros (Al-Rfou et al., 2018). Por el contrario, BERTBASE contiene 110M parámetros y BERTLARGE contiene 340M parámetros.

Se sabe desde hace mucho tiempo que aumentar el tamaño del modelo conducirá a mejoras continuas en tareas a gran escala, como la traducción automática y el modelado del lenguaje, lo que se demuestra mediante la perplejidad del LM de los datos de entrenamiento retenidos que se muestran en la Tabla 6. Sin embargo, creemos que este es el primer trabajo que demuestra de manera convincente que escalar a tamaños de modelo extremos también conduce a grandes mejoras en tareas de escala muy pequeña, siempre que el modelo se haya pre-entrenado lo suficiente. Peters et al. (2018b) presentaron resultados mixtos sobre el impacto de la tarea posterior de aumentar el tamaño del bi-LM pre-entrenado de dos a cuatro capas y Melamud et al. (2016) mencionaron de pasada que aumentar la dimensión oculta de 200 a 600 ayudó, pero aumentar aún más a 1,000 no trajo más mejoras. Ambos trabajos anteriores utilizaron un enfoque basado en características: nosotros suponemos que cuando el modelo se ajusta finamente directamente en las tareas posteriores y utiliza solo un número muy pequeño de parámetros adicionales inicializados aleatoriamente, los modelos específicos de la tarea pueden beneficiarse de las representaciones pre-entrenadas más grandes y expresivas, incluso cuando los datos de la tarea posterior son muy pequeños.

### 5.3 Enfoque Basado en Características con BERT

Todos los resultados de BERT presentados hasta ahora han utilizado el enfoque de ajuste fino, donde se agrega una capa de clasificación simple al modelo pre-entrenado, y todos los parámetros se ajustan finamente de forma conjunta en una tarea posterior. Sin embargo, el enfoque basado en características, donde se extraen características fijas del modelo pre-entrenado, tiene ciertas ventajas. Primero, no todas las tareas se pueden representar fácilmente mediante una arquitectura de codificador Transformer, y por lo tanto requieren que se agregue una arquitectura de modelo específica de la tarea. Segundo, existen importantes beneficios computacionales para precalcular una representación costosa de los datos de entrenamiento una vez y luego ejecutar muchos experimentos con modelos más baratos sobre esta representación.

En esta sección, comparamos los dos enfoques aplicando BERT a la tarea de Reconocimiento de Entidades Nombradas (NER) de CoNLL-2003 (Tjong Kim Sang y De Meulder, 2003). En la entrada a BERT, utilizamos un modelo WordPiece que conserva las mayúsculas, e incluimos el contexto máximo del documento proporcionado por los datos. Siguiendo la práctica estándar, formulamos esto como una tarea de etiquetado, pero no usamos una capa CRF en la salida. Utilizamos la representación del primer subtoken como entrada al clasificador a nivel de token sobre el conjunto de etiquetas NER.

Para ablacionar el enfoque de ajuste fino, aplicamos el enfoque basado en características extrayendo las activaciones de una o más capas sin ajustar finamente ningún parámetro de BERT. Estas incrustaciones contextuales se utilizan como entrada a un BiLSTM bidimensional de 768 dimensiones inicializado aleatoriamente antes de la capa de clasificación.

Los resultados se presentan en la Tabla 7. BERTLARGE funciona de manera competitiva con los métodos de última generación. El método de mejor rendimiento concatena las representaciones de tokens de las cuatro capas ocultas superiores del Transformer pre-entrenado, que solo tiene 0.3 F1 por detrás del ajuste fino de todo el modelo. Esto demuestra que BERT es efectivo tanto para los enfoques de ajuste fino como para los basados en características.

# 6. Conclusión

Las mejoras empíricas recientes debido al aprendizaje por transferencia con modelos de lenguaje han demostrado que el pre-entrenamiento rico y no supervisado es una parte integral de muchos sistemas de comprensión del lenguaje. En particular, estos resultados permiten que incluso las tareas de bajos recursos se beneficien de las arquitecturas unidireccionales profundas. Nuestra principal contribución es generalizar aún más estos hallazgos a las arquitecturas bidireccionales profundas, permitiendo que el mismo modelo pre-entrenado aborde con éxito una amplia gama de tareas de PNL.


# Apéndice para "BERT: Pre-entrenamiento de Transformers Bidireccionales Profundos para la Comprensión del Lenguaje"

Organizamos el apéndice en tres secciones:
 + Se presentan detalles de implementación adicionales para BERT en el Apéndice A;
 + Se presentan detalles adicionales para nuestros experimentos en el Apéndice B; y
 + Se presentan estudios de ablación adicionales en el Apéndice C.

Presentamos estudios de ablación adicionales para BERT incluyendo:
 + Efecto del Número de Pasos de Entrenamiento; y
 + Ablación para Diferentes Procedimientos de Enmascaramiento.

## A. Detalles Adicionales para BERT

### A.1 Ilustración de las Tareas de Pre-entrenamiento

Proporcionamos ejemplos de las tareas de pre-entrenamiento en lo siguiente.

**Modelo de Lenguaje Enmascarado y el Procedimiento de Enmascaramiento** Suponiendo que la oración sin etiquetar es my dog is hairy, y durante el procedimiento de enmascaramiento aleatorio elegimos el cuarto token (que corresponde a hairy), nuestro procedimiento de enmascaramiento se puede ilustrar aún más mediante

 * 80% de las veces: Reemplace la palabra con el token [MASK], por ejemplo, my dog is hairy → my dog is [MASK]
 * 10% de las veces: Reemplace la palabra con una palabra aleatoria, por ejemplo, my dog is hairy → my dog is apple
 * 10% de las veces: Mantenga la palabra sin cambios, por ejemplo, my dog is hairy → my dog is hairy. El propósito de esto es sesgar la representación hacia la palabra observada real.

La ventaja de este procedimiento es que el codificador Transformer no sabe qué palabras se le pedirá que prediga o cuáles se han reemplazado por palabras aleatorias, por lo que se ve obligado a mantener una representación contextual distributiva de cada token de entrada. Además, debido a que el reemplazo aleatorio solo ocurre para el 1.5% de todos los tokens (es decir, el 10% del 15%), esto no parece perjudicar la capacidad de comprensión del lenguaje del modelo. En la Sección C.2, evaluamos el impacto de este procedimiento.

En comparación con el entrenamiento del modelo de lenguaje estándar, el MLM solo realiza predicciones en el 15% de los tokens en cada lote, lo que sugiere que se pueden requerir más pasos de pre-entrenamiento para que el modelo converja. En la Sección C.1, demostramos que MLM converge marginalmente más lento que un modelo de izquierda a derecha (que predice cada token), pero las mejoras empíricas del modelo MLM superan con creces el costo de entrenamiento aumentado.

**Predicción de la Oración Siguiente** La tarea de predicción de la oración siguiente se puede ilustrar en los siguientes ejemplos.

Entrada = [CLS] the man went to [MASK] store [SEP] he bought a gallon [MASK] milk [SEP]

Etiqueta = IsNext

Entrada = [CLS] the man [MASK] to the store [SEP] penguin [MASK] are flight ##less birds [SEP]

Etiqueta = NotNext

### A.2 Procedimiento de Pre-entrenamiento

Para generar cada secuencia de entrada de entrenamiento, muestreamos dos tramos de texto del corpus, a los que nos referimos como "oraciones" aunque normalmente son mucho más largas que las oraciones simples (pero también pueden ser más cortas). La primera oración recibe la incrustación A y la segunda recibe la incrustación B. El 50% de las veces B es la oración siguiente real que sigue a A y el 50% de las veces es una oración aleatoria, lo que se hace para la tarea de "predicción de la oración siguiente". Se muestrean de modo que la longitud combinada sea ≤ 512 tokens. El enmascaramiento LM se aplica después de la tokenización de WordPiece con una tasa de enmascaramiento uniforme del 15%, y no se tiene en cuenta ningún consideración especial para las piezas de palabras parciales.

Entrenamos con un tamaño de lote de 256 secuencias (256 secuencias * 512 tokens = 128,000 tokens / lote) durante 1,000,000 pasos, que son aproximadamente 40 épocas sobre el corpus de 3.3 mil millones de palabras. Usamos Adam con una tasa de aprendizaje de 1e-4, β1 = 0.9, β2 = 0.999, decaimiento de peso L2 de 0.01, calentamiento de la tasa de aprendizaje durante los primeros 10,000 pasos y decaimiento lineal de la tasa de aprendizaje. Usamos una probabilidad de abandono de 0.1 en todas las capas. Usamos una activación gelu (Hendrycks y Gimpel, 2016) en lugar de la relu estándar, siguiendo OpenAI GPT. La pérdida de entrenamiento es la suma de la verosimilitud media del MLM enmascarado y la verosimilitud media de la predicción de la oración siguiente.

El entrenamiento de BERTBASE se realizó en 4 Cloud TPUs en configuración Pod (16 chips TPU en total).13 El entrenamiento de BERTLARGE se realizó en 16 Cloud TPUs (64 chips TPU en total). Cada pre-entrenamiento tardó 4 días en completarse.

Las secuencias más largas son desproporcionadamente costosas porque la atención es cuadrática a la longitud de la secuencia. Para acelerar el pre-entrenamiento en nuestros experimentos, pre-entrenamos el modelo con una longitud de secuencia de 128 para el 90% de los pasos. Luego, entrenamos el resto del 10% de los pasos de la secuencia de 512 para aprender las incrustaciones posicionales.

### A.3 Procedimiento de Ajuste Fino

Para el ajuste fino, la mayoría de los hiperparámetros del modelo son los mismos que en el pre-entrenamiento, con la excepción del tamaño del lote, la tasa de aprendizaje y el número de épocas de entrenamiento. La probabilidad de abandono siempre se mantuvo en 0.1. Los valores óptimos de hiperparámetros son específicos de la tarea, pero encontramos que el siguiente rango de valores posibles funcionó bien en todas las tareas:

 * **Tamaño del lote**: 16, 32
 * **Tasa de aprendizaje (Adam)**: 5e-5, 3e-5, 2e-5
 * **Número de épocas**: 2, 3, 4

13 https://cloudplatform.googleblog.com/2018/06/Cloud-TPU-now-offers-preemptible-pricing-and-global-availability.html

También observamos que los conjuntos de datos grandes (por ejemplo, más de 100,000 ejemplos de entrenamiento etiquetados) eran mucho menos sensibles a la elección de hiperparámetros que los conjuntos de datos pequeños. El ajuste fino suele ser muy rápido, por lo que es razonable simplemente ejecutar una búsqueda exhaustiva sobre los parámetros anteriores y elegir el modelo que funcione mejor en el conjunto de desarrollo.

### A.4 Comparación de BERT, ELMo y OpenAI GPT

Aquí estudiamos las diferencias en los recientes modelos populares de aprendizaje de representación, incluidos ELMo, OpenAI GPT y BERT. Las comparaciones entre las arquitecturas del modelo se muestran visualmente en la Figura 3. Tenga en cuenta que además de las diferencias de arquitectura, BERT y OpenAI GPT son enfoques de ajuste fino, mientras que ELMo es un enfoque basado en características.

El método de pre-entrenamiento existente más comparable a BERT es OpenAI GPT, que entrena un LM Transformer de izquierda a derecha en un corpus de texto grande. De hecho, muchas de las decisiones de diseño en BERT se tomaron intencionalmente para que fuera lo más similar posible a GPT, de modo que los dos métodos pudieran compararse mínimamente. El argumento central de este trabajo es que la bidireccionalidad y las dos tareas de pre-entrenamiento presentadas en la Sección 3.1 representan la mayoría de las mejoras empíricas, pero sí notamos que existen varias otras diferencias entre la forma en que se entrenaron BERT y GPT:

 * GPT se entrena en el BooksCorpus (800M palabras); BERT se entrena en el BooksCorpus (800M palabras) y Wikipedia (2,500M palabras).
 * GPT utiliza un separador de oraciones ([SEP]) y un token de clasificador ([CLS]) que solo se introducen en el momento del ajuste fino; BERT aprende [SEP], [CLS] e incrustaciones de oración A / B durante el pre-entrenamiento.
 * GPT se entrenó durante 1M pasos con un tamaño de lote de 32,000 palabras; BERT se entrenó durante 1M pasos con un tamaño de lote de 128,000 palabras.
 * GPT utilizó la misma tasa de aprendizaje de 5e-5 para todos los experimentos de ajuste fino; BERT elige una tasa de aprendizaje de ajuste fino específica de la tarea que funciona mejor en el conjunto de desarrollo.

Para aislar el efecto de estas diferencias, realizamos experimentos de ablación en la Sección 5.1, que demuestran que la mayoría de las mejoras provienen de hecho de las dos tareas de pre-entrenamiento y la bidireccionalidad que habilitan.

### A.5 Ilustraciones del Ajuste Fino en Diferentes Tareas

La ilustración del ajuste fino de BERT en diferentes tareas se puede ver en la Figura 4. Nuestros modelos específicos de la tarea se forman incorporando BERT con una capa de salida adicional, por lo que se necesita un número mínimo de parámetros para aprender desde cero. Entre las tareas, (a) y (b) son tareas a nivel de secuencia, mientras que (c) y (d) son tareas a nivel de token. En la figura, E representa la incrustación de entrada, Ti representa la representación contextual del token i, [CLS] es el símbolo especial para la salida de clasificación y [SEP] es el símbolo especial para separar secuencias de tokens no consecutivas.

## B. Configuración Experimental Detallada

### B.1 Descripciones Detalladas para los Experimentos del Punto de Referencia GLUE.

Nuestros resultados de GLUE en la Tabla 1 se obtienen de https://gluebenchmark.com/ leaderboard y https://blog. openai.com/language-unsupervised. El punto de referencia GLUE incluye los siguientes conjuntos de datos, cuyas descripciones se resumieron originalmente en Wang et al. (2018a):

**MNLI** Multi-Genre Natural Language Inference es una tarea de clasificación de inferencia a gran escala basada en la multitud (Williams et al., 2018). Dado un par de oraciones, el objetivo es predecir si la segunda oración es una inferencia, una contradicción o neutral con respecto a la primera.

**QQP** Quora Question Pairs es una tarea de clasificación binaria donde el objetivo es determinar si dos preguntas hechas en Quora son semánticamente equivalentes (Chen et al., 2018).

**QNLI** Question Natural Language Inference es una versión del conjunto de datos de respuesta a preguntas de Stanford (Rajpurkar et al., 2016) que se ha convertido a una tarea de clasificación binaria (Wang et al., 2018a). Los ejemplos positivos son pares (pregunta, oración) que sí contienen la respuesta correcta, y los ejemplos negativos son (pregunta, oración) del mismo párrafo que no contiene la respuesta.

**SST-2** The Stanford Sentiment Treebank es una tarea de clasificación binaria de una sola oración que consiste en oraciones extraídas de reseñas de películas con anotaciones humanas de su sentimiento (Socher et al., 2013).

**CoLA** The Corpus of Linguistic Acceptability es una tarea de clasificación binaria de una sola oración, donde el objetivo es predecir si una oración en inglés es lingüísticamente "aceptable" o no (Warstadt et al., 2018).

**STS-B** The Semantic Textual Similarity Benchmark es una colección de pares de oraciones extraídas de titulares de noticias y otras fuentes (Cer et al., 2017). Se les asignó una puntuación de 1 a 5 que denota qué tan similares son las dos oraciones en términos de significado semántico.

**MRPC** Microsoft Research Paraphrase Corpus consiste en pares de oraciones extraídas automáticamente de fuentes de noticias en línea, con anotaciones humanas para determinar si las oraciones del par son semánticamente equivalentes (Dolan y Brockett, 2005).

**RTE** Recognizing Textual Entailment es una tarea de inferencia binaria similar a MNLI, pero con muchos menos datos de entrenamiento (Bentivogli et al., 2009).14

**WNLI** Winograd NLI es un pequeño conjunto de datos de inferencia del lenguaje natural (Levesque et al., 2011). La página web de GLUE señala que existen problemas con la construcción de este conjunto de datos,15 y cada sistema entrenado que se ha presentado a GLUE ha funcionado peor que la precisión de línea de base del 65.1 de predecir la clase mayoritaria. Por lo tanto, excluimos este conjunto para ser justos con OpenAI GPT. Para nuestra presentación de GLUE, siempre predijimos la clase mayoritaria.

14 Tenga en cuenta que solo informamos resultados de ajuste fino de una sola tarea en este documento. Un enfoque de ajuste fino multitarea podría potencialmente impulsar el rendimiento aún más. Por ejemplo, sí observamos mejoras sustanciales en RTE a partir del entrenamiento multitarea con MNLI.

15 https://gluebenchmark.com/faq

## C. Estudios de Ablación Adicionales

### C.1 Efecto del Número de Pasos de Entrenamientoç

La Figura 5 presenta la precisión de MNLI Dev después del ajuste fino a partir de un punto de control que se ha pre-entrenado durante k pasos. Esto nos permite responder las siguientes preguntas:

 1. Pregunta: ¿BERT realmente necesita una cantidad tan grande de pre-entrenamiento (128,000 palabras / lote * 1,000,000 pasos) para lograr una alta precisión de ajuste fino? Respuesta: Sí, BERTBASE logra casi un 1.0% de precisión adicional en MNLI cuando se entrena en 1M pasos en comparación con 500k pasos.
 2. Pregunta: ¿El pre-entrenamiento MLM converge más lento que el pre-entrenamiento LTR, ya que solo se predice el 15% de las palabras en cada lote en lugar de cada palabra? Respuesta: El modelo MLM sí converge ligeramente más lento que el modelo LTR. Sin embargo, en términos de precisión absoluta, el modelo MLM comienza a superar al modelo LTR casi de inmediato.

### C.2 Ablación para Diferentes Procedimientos de Enmascaramiento

En la Sección 3.1, mencionamos que BERT utiliza una estrategia mixta para enmascarar los tokens objetivo al pre-entrenar con el objetivo del modelo de lenguaje enmascarado (MLM). El siguiente es un estudio de ablación para evaluar el efecto de diferentes estrategias de enmascaramiento.

Tenga en cuenta que el propósito de las estrategias de enmascaramiento es reducir la discrepancia entre el pre-entrenamiento y el ajuste fino, ya que el símbolo [MASK] nunca aparece durante la etapa de ajuste fino. Informamos los resultados de Dev tanto para MNLI como para NER. Para NER, informamos tanto los enfoques de ajuste fino como los basados en características, ya que esperamos que la discrepancia se amplifique para el enfoque basado en características, ya que el modelo no tendrá la oportunidad de ajustar las representaciones.

|Tasa de Enmascaramiento Resultados del Conjunto Dev|
|MASK| SAME| RND| MNLI Fine-tune| NER Fine-tune| NER Basado en Características|
|---|---|---|---|---|---|
|80%| 10%| 10%| 84.2| 95.4| 94.9|
|100%| 0%| 0%| 84.3| 94.9| 94.0|
|80%| 0%| 20%| 84.1| 95.2| 94.6|
|80%| 20%| 0%| 84.4| 95.2| 94.7|
|0%| 20%| 80%| 83.7| 94.8| 94.6|
|0%| 0%| 100%| 83.6| 94.9| 94.6|

Tabla 8: Ablación sobre diferentes estrategias de enmascaramiento.

Los números en la parte izquierda de la tabla representan las probabilidades de las estrategias específicas utilizadas durante el pre-entrenamiento MLM (BERT utiliza 80%, 10%, 10%). La parte derecha del documento representa los resultados del conjunto Dev. Para el enfoque basado en características, concatenamos las últimas 4 capas de BERT como características, lo que se demostró que era el mejor enfoque en la Sección 5.3.

De la tabla se puede ver que el ajuste fino es sorprendentemente robusto a diferentes estrategias de enmascaramiento. Sin embargo, como se esperaba, usar solo la estrategia MASK fue problemático al aplicar el enfoque basado en características a NER. Curiosamente, usar solo la estrategia RND funciona mucho peor que nuestra estrategia también.