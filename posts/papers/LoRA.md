# LoRA - lora low rank adaptation of large language models

## Abstract

## LORA: Adaptación de bajo rango para modelos lingüísticos de gran escala

Un paradigma importante en el procesamiento del lenguaje natural consiste en el entrenamiento a gran escala con datos de dominio general y la adaptación a tareas o dominios específicos. A medida que entrenamos modelos más grandes, el ajuste fino completo, que vuelve a entrenar todos los parámetros del modelo, se vuelve menos viable. Tomando como ejemplo GPT-3 175B, implementar instancias independientes de modelos ajustados finamente, cada uno con 175B parámetros, es prohibitivamente costoso. Proponemos la Adaptación de Bajo Rango, o LoRA, que congela los pesos del modelo preentrenado e inyecta matrices de descomposición de rango entrenables en cada capa de la arquitectura Transformer, reduciendo en gran medida la cantidad de parámetros entrenables para tareas posteriores. En comparación con GPT-3 175B ajustado finamente con Adam, LoRA puede reducir la cantidad de parámetros entrenables en 10,000 veces y el requisito de memoria de GPU en 3 veces. LoRA funciona igual o mejor que el ajuste fino en calidad de modelo en RoBERTa, DeBERTa, GPT-2 y GPT-3, a pesar de tener menos parámetros entrenables, un mayor rendimiento de entrenamiento y, a diferencia de los adaptadores, no tiene latencia adicional de inferencia. También proporcionamos una investigación empírica sobre la deficiencia de rango en la adaptación del modelo lingüístico, lo que arroja luz sobre la eficacia de LoRA. Lanzamos un paquete que facilita la integración de LoRA con los modelos de PyTorch y proporcionamos nuestras implementaciones y puntos de control del modelo para RoBERTa, DeBERTa y GPT-2 en https://github.com/microsoft/LoRA.

## 1. Introducción

Figura 1: Nuestra reparametrización. Solo entrenamos A y B.

Muchas aplicaciones en el procesamiento del lenguaje natural dependen de la adaptación de un modelo de lenguaje preentrenado a gran escala a múltiples aplicaciones posteriores. Dicha adaptación generalmente se realiza mediante el ajuste fino, que actualiza todos los parámetros del modelo preentrenado. La principal desventaja del ajuste fino es que el nuevo modelo contiene tantos parámetros como el modelo original. A medida que se entrenan modelos más grandes cada pocos meses, esto cambia de una mera "inconveniencia" para GPT-2 (Radford et al., b) o RoBERTa grande (Liu et al., 2019) a un desafío de implementación crítico para GPT-3 (Brown et al., 2020) con 175 mil millones de parámetros entrenables.1

Muchos buscaron mitigar esto adaptando solo algunos parámetros o aprendiendo módulos externos para nuevas tareas. De esta manera, solo necesitamos almacenar y cargar una pequeña cantidad de parámetros específicos de la tarea además del modelo preentrenado para cada tarea, lo que aumenta en gran medida la eficiencia operativa cuando se implementa. Sin embargo, las técnicas existentes a menudo introducen latencia de inferencia (Houlsby et al., 2019; Rebuffi et al., 2017) al extender la profundidad del modelo o reducir la longitud de secuencia utilizable del modelo (Li & Liang, 2021; Lester et al., 2021; Hambardzumyan et al., 2020; Liu et al., 2021) (Sección 3). Más importante aún, estos métodos a menudo no coinciden con los valores de referencia del ajuste fino, lo que plantea una compensación entre la eficiencia y la calidad del modelo.

Nos inspiramos en Li et al. (2018a); Aghajanyan et al. (2020) que muestran que los modelos sobreparametrizados aprendidos en realidad residen en una dimensión intrínseca baja. Hipótesis que el cambio en los pesos durante la adaptación del modelo también tiene un "rango intrínseco" bajo, lo que lleva a nuestro enfoque propuesto de Adaptación de Bajo Rango (LoRA). LoRA nos permite entrenar algunas capas densas en una red neuronal indirectamente optimizando matrices de descomposición de rango del cambio de las capas densas durante la adaptación, mientras mantenemos los pesos preentrenados congelados, como se muestra en la Figura 1. Tomando como ejemplo GPT-3 175B, mostramos que un rango muy bajo (es decir, r en la Figura 1 puede ser uno o dos) es suficiente incluso cuando el rango completo (es decir, d) es tan alto como 12,288, lo que hace que LoRA sea eficiente tanto en almacenamiento como en cómputo.

LoRA posee varias ventajas clave:
 + Un modelo preentrenado se puede compartir y utilizar para construir muchos módulos LoRA pequeños para diferentes tareas. Podemos congelar el modelo compartido y cambiar de tarea de manera eficiente reemplazando las matrices A y B en la Figura 1, lo que reduce significativamente el requisito de almacenamiento y la sobrecarga de cambio de tarea.
 + LoRA hace que el entrenamiento sea más eficiente y reduce la barrera de entrada de hardware hasta 3 veces cuando se utilizan optimizadores adaptativos, ya que no necesitamos calcular los gradientes ni mantener los estados del optimizador para la mayoría de los parámetros. En cambio, solo optimizamos las matrices de rango bajo inyectadas, mucho más pequeñas.
 + Nuestro sencillo diseño lineal nos permite fusionar las matrices entrenables con los pesos congelados cuando se implementa, sin introducir latencia de inferencia en comparación con un modelo completamente ajustado, por construcción.
LoRA es ortogonal a muchos métodos anteriores y se puede combinar con muchos de ellos, como el ajuste de prefijos. Proporcionamos un ejemplo en el Apéndice E.

**Terminología y convenciones**: Hacemos referencia frecuente a la arquitectura Transformer y usamos la terminología convencional para sus dimensiones. Llamamos a la dimensión de entrada y salida de una capa Transformer dmodel. Usamos Wq, Wk, Wv y Wo para referirnos a las matrices de proyección de consulta/clave/valor/salida en el módulo de autoatención. W o W0 se refiere a una matriz de pesos preentrenada y ∆W su actualización de gradiente acumulada durante la adaptación. Usamos r para denotar el rango de un módulo LoRA. Seguimos las convenciones establecidas por (Vaswani et al., 2017; Brown et al., 2020) y usamos Adam (Loshchilov & Hutter, 2019; Kingma & Ba, 2017) para la optimización del modelo y usamos una dimensión de avance MLP de Transformer dffn = 4× dmodel.

## 2. DECLARACIÓN DEL PROBLEMA

Si bien nuestra propuesta es agnóstica al objetivo de entrenamiento, nos centramos en el modelado de lenguaje como nuestro caso de uso motivador. A continuación, se muestra una breve descripción del problema del modelado de lenguaje y, en particular, la maximización de las probabilidades condicionales dado un indicador específico de la tarea.

Supongamos que nos dan un modelo de lenguaje autorregresivo preentrenado PΦ(y|x) parametrizado por Φ. Por ejemplo, PΦ(y|x) puede ser un aprendiz multitarea genérico como GPT (Radford et al., b; Brown et al., 2020) basado en la arquitectura Transformer (Vaswani et al., 2017). Considere adaptar este modelo preentrenado a tareas de generación de texto condicional posteriores, como la resumización, la comprensión de la lectura de máquina (MRC) y el lenguaje natural a SQL (NL2SQL). Cada tarea posterior se representa mediante un conjunto de datos de entrenamiento de pares contexto-objetivo: Z = {(xi, yi)}i=1,..,N, donde tanto xi como yi son secuencias de tokens. Por ejemplo, en NL2SQL, xi es una consulta de lenguaje natural e yi su comando SQL correspondiente; para la resumización, xi es el contenido de un artículo e yi su resumen.

Durante el ajuste fino completo, el modelo se inicializa a los pesos preentrenados Φ0 y se actualiza a Φ0 + ∆Φ repitiendo el seguimiento del gradiente para maximizar el objetivo de modelado de lenguaje condicional:

max Φ ∑ (x,y)∈Z |y|∑ t=1 log (PΦ(yt|x, y<t)) (1)

Uno de los principales inconvenientes del ajuste fino completo es que para cada tarea posterior, aprendemos un conjunto diferente de parámetros ∆Φ cuya dimensión |∆Φ| es igual a |Φ0|. Por lo tanto, si el modelo preentrenado es grande (como GPT-3 con |Φ0| ≈ 175 mil millones), almacenar e implementar muchas instancias independientes de modelos ajustados finamente puede ser un desafío, si es que es posible.

En este artículo, adoptamos un enfoque más eficiente en cuanto a parámetros, donde el incremento de parámetros específico de la tarea ∆Φ = ∆Φ(Θ) se codifica además mediante un conjunto de parámetros Θ de tamaño mucho más pequeño con |Θ| < |Φ0|. La tarea de encontrar ∆Φ se convierte entonces en optimizar sobre Θ:

max Θ ∑ (x,y)∈Z |y|∑ t=1 log ( pΦ0+∆Φ(Θ)(yt|x, y<t) ) (2)

En las secciones posteriores, proponemos utilizar una representación de bajo rango para codificar ∆Φ que sea eficiente tanto en cómputo como en memoria. Cuando el modelo preentrenado es GPT-3 175B, la cantidad de parámetros entrenables |Θ| puede ser tan pequeña como el 0.01% de |Φ0|.

## 3. ¿NO SON SUFICIENTEMENTE BUENAS LAS SOLUCIONES EXISTENTES?

El problema que nos proponemos abordar no es nuevo. Desde la aparición del aprendizaje por transferencia, decenas de trabajos han buscado hacer que la adaptación del modelo sea más eficiente en cuanto a parámetros y cómputo. Consulte la Sección 6 para una revisión de algunos de los trabajos más conocidos. Tomando como ejemplo el modelado de lenguaje, existen dos estrategias destacadas cuando se trata de adaptaciones eficientes: agregar capas de adaptador (Houlsby et al., 2019; Rebuffi et al., 2017; Pfeiffer et al., 2021; Rücklé et al., 2020) u optimizar algunas formas de las activaciones de la capa de entrada (Li & Liang, 2021; Lester et al., 2021; Hambardzumyan et al., 2020; Liu et al., 2021). Sin embargo, ambas estrategias tienen sus limitaciones, especialmente en un escenario de producción a gran escala y sensible a la latencia.

### Capas de adaptador introducen latencia de inferencia

Existen muchas variantes de adaptadores. Nos centramos en el diseño original de Houlsby et al. (2019) que tiene dos capas de adaptador por bloque Transformer y uno más reciente de Lin et al. (2020) que tiene solo uno por bloque pero con una LayerNorm adicional (Ba et al., 2016). Si bien se puede reducir la latencia general al podar capas o explotar configuraciones multitarea (Rücklé et al., 2020; Pfeiffer et al., 2021), no hay formas directas de evitar el cálculo adicional en las capas de adaptador. Esto parece un problema menor, ya que las capas de adaptador están diseñadas para tener pocos parámetros (a veces menos del 1% del modelo original) al tener una pequeña dimensión de cuello de botella, lo que limita los FLOPs que pueden agregar. Sin embargo, las redes neuronales grandes dependen del paralelismo de hardware para mantener la latencia baja, y las capas de adaptador deben procesarse secuencialmente. Esto hace una diferencia en la configuración de inferencia en línea donde el tamaño del lote suele ser tan pequeño como uno. En un escenario genérico sin paralelismo de modelo, como ejecutar la inferencia en GPT-2 (Radford et al., b) mediano en una sola GPU, vemos un aumento notable en la latencia cuando se utilizan adaptadores, incluso con una dimensión de cuello de botella muy pequeña (Tabla 1).

Este problema empeora cuando necesitamos dividir el modelo como se hace en Shoeybi et al. (2020); Lepikhin et al. (2020), porque la profundidad adicional requiere más operaciones síncronas de GPU como AllReduce y Broadcast, a menos que almacenemos los parámetros del adaptador de forma redundante muchas veces.

### Optimizar directamente el indicador es difícil

La otra dirección, como se ejemplifica en el ajuste de prefijos (Li & Liang, 2021), enfrenta un desafío diferente. Observamos que el ajuste de prefijos es difícil de optimizar y que su rendimiento cambia de forma no monótona en los parámetros entrenables, confirmando observaciones similares en el documento original. Más fundamentalmente, reservar una parte de la longitud de la secuencia para la adaptación reduce necesariamente la longitud de la secuencia disponible para procesar una tarea posterior, lo que sospechamos hace que el ajuste del indicador sea menos eficaz en comparación con otros métodos. Dejamos el estudio sobre el rendimiento de la tarea para la Sección 5.

Table 1

## 4. NUESTRO MÉTODO

Describimos el sencillo diseño de LoRA y sus beneficios prácticos. Los principios que se describen aquí se aplican a cualquier capa densa en modelos de aprendizaje profundo, aunque solo nos centramos en ciertos pesos en los modelos de lenguaje Transformer en nuestros experimentos como caso de uso motivador.

### 4.1 MATRICES DE ACTUALIZACIÓN PARAMETRIZADAS POR RANGO BAJO

Una red neuronal contiene muchas capas densas que realizan la multiplicación de matrices. Las matrices de pesos en estas capas normalmente tienen rango completo. Al adaptarse a una tarea específica, Aghajanyan et al. (2020) muestran que los modelos de lenguaje preentrenados tienen una "dimensión intrínseca" baja y aún pueden aprender de manera eficiente a pesar de una proyección aleatoria a un subespacio más pequeño. Inspirados por esto, hipotetizamos que las actualizaciones de los pesos también tienen un "rango intrínseco" bajo durante la adaptación. Para una matriz de pesos preentrenada W0 ∈ Rd×k, restringimos su actualización representando esta última con una descomposición de rango bajo W0 + ∆W = W0 + BA, donde B ∈ Rd×r, A ∈ Rr×k, y el rango r ≤ min(d, k). Durante el entrenamiento, W0 se congela y no recibe actualizaciones de gradiente, mientras que A y B contienen parámetros entrenables. Observe que tanto W0 como ∆W = BA se multiplican por la misma entrada, y sus respectivos vectores de salida se suman coordenada por coordenada. Para h = W0x, nuestro paso de avance modificado produce:

h = W0x+ ∆Wx = W0x+BAx (3)

Ilustramos nuestra reparametrización en la Figura 1. Usamos una inicialización gaussiana aleatoria para A y cero para B, por lo que ∆W = BA es cero al comienzo del entrenamiento. Luego, escalamos ∆Wx por α/√r, donde α es una constante en r. Al optimizar con Adam, ajustar α es aproximadamente lo mismo que ajustar la tasa de aprendizaje si escalamos la inicialización de forma adecuada. Como resultado, simplemente establecemos α al primer r que intentamos y no lo ajustamos. Esta escala ayuda a reducir la necesidad de volver a ajustar los hiperparámetros cuando variamos r (Yang & Hu, 2021).

#### Generalización del ajuste fino completo

Una forma más general del ajuste fino permite el entrenamiento de un subconjunto de los parámetros preentrenados. LoRA da un paso más allá y no requiere que la actualización de gradiente acumulada a las matrices de peso tenga rango completo durante la adaptación. Esto significa que al aplicar LoRA a todas las matrices de peso y entrenar todos los sesgos2, recuperamos aproximadamente la expresividad del ajuste fino completo estableciendo el rango LoRA r al rango de las matrices de peso preentrenadas. En otras palabras, a medida que aumentamos la cantidad de parámetros entrenables 3, el entrenamiento de LoRA converge aproximadamente al entrenamiento del modelo original, mientras que los métodos basados en adaptadores convergen a una MLP y los métodos basados en prefijos a un modelo que no puede tomar secuencias de entrada largas.

#### No hay latencia de inferencia adicional

Cuando se implementa en producción, podemos calcular y almacenar explícitamente W = W0 + BA y realizar la inferencia como de costumbre. Observe que tanto W0 como BA están en Rd×k. Cuando necesitamos cambiar a otra tarea posterior, podemos recuperar W0 restando BA y luego sumando un B′A′ diferente, una operación rápida con muy poca sobrecarga de memoria. Críticamente, esto garantiza que no introduzcamos ninguna latencia adicional durante la inferencia en comparación con un modelo ajustado finamente por construcción.

### 4.2 APLICANDO LORA A TRANSFORMER

En principio, podemos aplicar LoRA a cualquier subconjunto de matrices de peso en una red neuronal para reducir la cantidad de parámetros entrenables. En la arquitectura Transformer, hay cuatro matrices de peso en el módulo de autoatención (Wq, Wk, Wv, Wo) y dos en el módulo MLP. Tratamos Wq (o Wk, Wv) como una sola matriz de dimensión dmodel×dmodel, aunque la dimensión de salida generalmente se divide en cabezas de atención. Limitamos nuestro estudio a solo adaptar los pesos de atención para tareas posteriores y congelamos los módulos MLP (por lo que no se entrenan en tareas posteriores) tanto por simplicidad como por eficiencia de parámetros. Estudiamos además el efecto de adaptar diferentes tipos de matrices de peso de atención en un Transformer en la Sección 7.1. Dejamos la investigación empírica sobre la adaptación de las capas MLP, las capas LayerNorm y los sesgos para un trabajo futuro.

#### Beneficios y limitaciones prácticas

El beneficio más significativo proviene de la reducción en el uso de memoria y almacenamiento. Para un Transformer grande entrenado con Adam, reducimos ese uso de VRAM hasta en 2/3 si r ≤ dmodel, ya que no necesitamos almacenar los estados del optimizador para los parámetros congelados. En GPT-3 175B, reducimos el consumo de VRAM durante el entrenamiento de 1.2TB a 350GB. Con r = 4 y solo las matrices de proyección de consulta y valor siendo adaptadas, el tamaño del punto de control se reduce aproximadamente en 10,000× (de 350GB a 35MB)4. Esto nos permite entrenar con significativamente menos GPUs y evitar cuellos de botella de E/S. Otra ventaja es que podemos cambiar entre tareas mientras se implementa a un costo mucho menor simplemente intercambiando los pesos de LoRA en lugar de todos los parámetros. Esto permite la creación de muchos modelos personalizados que se pueden intercambiar sobre la marcha en máquinas que almacenan los pesos preentrenados en VRAM. También observamos una aceleración del 25% durante el entrenamiento en GPT-3 175B en comparación con el ajuste fino completo5, ya que no necesitamos calcular el gradiente para la gran mayoría de los parámetros.

LoRA también tiene sus limitaciones. Por ejemplo, no es sencillo agrupar entradas a diferentes tareas con diferentes A y B en un solo paso de avance, si uno elige absorber A y B en W para eliminar la latencia adicional de inferencia. Aunque es posible no fusionar los pesos y elegir dinámicamente los módulos LoRA que se utilizarán para las muestras en un lote para escenarios donde la latencia no es crítica.

## 5. EXPERIMENTOS EMPÍRICOS

Evaluamos el rendimiento de la tarea posterior de LoRA en RoBERTa (Liu et al., 2019), DeBERTa (He et al., 2021) y GPT-2 (Radford et al., b), antes de escalar a GPT-3 175B (Brown et al., 2020). Nuestros experimentos cubren una amplia gama de tareas, desde la comprensión del lenguaje natural (NLU) hasta la generación (NLG). Específicamente, evaluamos en el punto de referencia GLUE (Wang et al., 2019) para RoBERTa y DeBERTa. Seguimos la configuración de Li & Liang (2021) en GPT-2 para una comparación directa y agregamos WikiSQL (Zhong et al., 2017) (NL a consultas SQL) y SAMSum (Gliwa et al., 2019) (resumización de conversaciones) para experimentos a gran escala en GPT-3. Consulte el Apéndice C para obtener más detalles sobre los conjuntos de datos que usamos. Usamos NVIDIA Tesla V100 para todos los experimentos.

### 5.1 VALORES DE REFERENCIA

Para comparar con otros valores de referencia de forma amplia, replicamos las configuraciones utilizadas en trabajos anteriores y reutilizamos sus números reportados siempre que sea posible. Sin embargo, esto significa que algunos valores de referencia podrían aparecer solo en ciertos experimentos.

**Ajuste fino (FT)** es un enfoque común para la adaptación. Durante el ajuste fino, el modelo se inicializa a los pesos y sesgos preentrenados, y todos los parámetros del modelo se someten a actualizaciones de gradiente. Una variante simple es actualizar solo algunas capas mientras se congelan otras. Incluimos uno de esos valores de referencia reportados en trabajos anteriores (Li & Liang, 2021) en GPT-2, que adapta solo las dos últimas capas (FTTop2).

Table 2

**Ajuste de solo sesgo o BitFit** es un valor de referencia donde solo entrenamos los vectores de sesgo mientras congelamos todo lo demás. Contemporáneamente, este valor de referencia también ha sido estudiado por BitFit (Zaken et al., 2021).

**Ajuste de incrustación de prefijo (PreEmbed)** inserta tokens especiales entre los tokens de entrada. Estos tokens especiales tienen incrustaciones de palabras entrenables y generalmente no están en el vocabulario del modelo. Dónde colocar esos tokens puede tener un impacto en el rendimiento. Nos centramos en el "prefijo", que antepone esos tokens al indicador, y el "infijo", que anexa al indicador; ambos se discuten en Li & Liang (2021). Usamos lp (resp. li) para denotar la cantidad de tokens de prefijo (resp. infijo). La cantidad de parámetros entrenables es |Θ| = dmodel × (lp + li).

**Ajuste de capa de prefijo (PreLayer)** es una extensión del ajuste de incrustación de prefijo. En lugar de solo aprender las incrustaciones de palabras (o equivalentemente, las activaciones después de la capa de incrustación) para algunos tokens especiales, aprendemos las activaciones después de cada capa Transformer. Las activaciones calculadas a partir de capas anteriores simplemente se reemplazan por otras entrenables. La cantidad resultante de parámetros entrenables es |Θ| = L× dmodel × (lp + li), donde L es la cantidad de capas Transformer.

**Ajuste de adaptador** como se propuso en Houlsby et al. (2019) inserta capas de adaptador entre el módulo de autoatención (y el módulo MLP) y la conexión residual posterior. Hay dos capas totalmente conectadas con sesgos en una capa de adaptador con una no linealidad en el medio. Llamamos a este diseño original AdapterH. Recientemente, Lin et al. (2020) propusieron un diseño más eficiente con la capa de adaptador aplicada solo después del módulo MLP y después de una LayerNorm. Lo llamamos AdapterL. Esto es muy similar a otro diseño propuesto en Pfeiffer et al. (2021), que llamamos AdapterP. También incluimos otro valor de referencia llamado AdapterDrop (Rücklé et al., 2020) que elimina algunas capas de adaptador para una mayor eficiencia (AdapterD). Citamos números de trabajos anteriores siempre que sea posible para maximizar la cantidad de valores de referencia con los que comparamos; están en filas con un asterisco (*) en la primera columna. En todos los casos, tenemos |Θ| = L̂Adpt×(2×dmodel×r+r+dmodel)+2× L̂LN ×dmodel donde L̂Adpt es la cantidad de capas de adaptador y L̂LN la cantidad de LayerNorms entrenables (por ejemplo, en AdapterL).

**LoRA** agrega pares entrenables de matrices de descomposición de rango en paralelo a las matrices de peso existentes. Como se mencionó en la Sección 4.2, solo aplicamos LoRA a Wq y Wv en la mayoría de los experimentos por simplicidad. La cantidad de parámetros entrenables está determinada por el rango r y la forma de los pesos originales: |Θ| = 2× L̂LoRA× dmodel× r, donde L̂LoRA es la cantidad de matrices de peso a las que aplicamos LoRA.

Table 3

### 5.2 ROBERTA BASE/GRANDE

RoBERTa (Liu et al., 2019) optimizó la receta de preentrenamiento propuesta originalmente en BERT (Devlin et al., 2019a) y mejoró el rendimiento de la tarea de este último sin introducir muchos más parámetros entrenables. Si bien RoBERTa ha sido superada por modelos mucho más grandes en las tablas de clasificación de PNL, como el punto de referencia GLUE (Wang et al., 2019) en los últimos años, sigue siendo un modelo preentrenado competitivo y popular por su tamaño entre los profesionales. Tomamos la base RoBERTa preentrenada (125M) y RoBERTa grande (355M) de la biblioteca HuggingFace Transformers (Wolf et al., 2020) y evaluamos el rendimiento de diferentes enfoques de adaptación eficientes en tareas del punto de referencia GLUE. También replicamos Houlsby et al. (2019) y Pfeiffer et al. (2021) según su configuración. Para garantizar una comparación justa, realizamos dos cambios cruciales en la forma en que evaluamos LoRA cuando la comparamos con los adaptadores. Primero, usamos el mismo tamaño de lote para todas las tareas y usamos una longitud de secuencia de 128 para que coincida con los valores de referencia del adaptador. En segundo lugar, inicializamos el modelo al modelo preentrenado para MRPC, RTE y STS-B, no a un modelo ya adaptado a MNLI como el valor de referencia de ajuste fino. Las ejecuciones que siguen esta configuración más restringida de Houlsby et al. (2019) están etiquetadas con †. El resultado se presenta en la Tabla 2 (tres secciones superiores). Consulte la Sección D.1 para obtener detalles sobre los hiperparámetros utilizados.

### 5.3 DEBERTA XXL

DeBERTa (He et al., 2021) es una variante más reciente de BERT que se entrena a una escala mucho mayor y funciona de manera muy competitiva en puntos de referencia como GLUE (Wang et al., 2019) y SuperGLUE (Wang et al., 2020). Evaluamos si LoRA todavía puede coincidir con el rendimiento de un DeBERTa XXL (1.5B) completamente ajustado en GLUE. El resultado se presenta en la Tabla 2 (Sección inferior). Consulte la Sección D.2 para obtener detalles sobre los hiperparámetros utilizados.

### 5.4 GPT-2 MEDIANO/GRANDE

Habiendo demostrado que LoRA puede ser una alternativa competitiva al ajuste fino completo en NLU, esperamos responder si LoRA todavía prevalece en los modelos NLG, como GPT-2 mediano y grande (Radford et al., b). Mantenemos nuestra configuración lo más cercana posible a Li & Liang (2021) para una comparación directa. Debido a las limitaciones de espacio, solo presentamos nuestro resultado en el Desafío E2E NLG (Tabla 3) en esta sección. Consulte la Sección F.1 para obtener resultados en WebNLG (Gardent et al., 2017) y DART (Nan et al., 2020). Incluimos una lista de los hiperparámetros utilizados en la Sección D.3.

Table 4

### 5.5 ESCALADO A GPT-3 175B

Como prueba de esfuerzo final para LoRA, escalamos a GPT-3 con 175 mil millones de parámetros. Debido al alto costo de entrenamiento, solo informamos la desviación estándar típica para una tarea determinada sobre semillas aleatorias, en lugar de proporcionar una para cada entrada. Consulte la Sección D.4 para obtener detalles sobre los hiperparámetros utilizados.

Como se muestra en la Tabla 4, LoRA coincide o supera el valor de referencia de ajuste fino en los tres conjuntos de datos. Tenga en cuenta que no todos los métodos se benefician de forma monótona al tener más parámetros entrenables, como se muestra en la Figura 2. Observamos una disminución significativa del rendimiento cuando usamos más de 256 tokens especiales para el ajuste de incrustación de prefijos o más de 32 tokens especiales para el ajuste de capa de prefijos. Esto corrobora observaciones similares en Li & Liang (2021). Si bien una investigación exhaustiva de este fenómeno está fuera del alcance de este trabajo, sospechamos que tener más tokens especiales hace que la distribución de entrada se desplace más lejos de la distribución de datos de preentrenamiento. Por separado, investigamos el rendimiento de diferentes enfoques de adaptación en el régimen de datos bajos en la Sección F.3.

Figure 2

## 6. TRABAJOS RELACIONADOS

### Modelos de lenguaje Transformer

Transformer (Vaswani et al., 2017) es una arquitectura de secuencia a secuencia que hace un uso intensivo de la autoatención. Radford et al. (a) lo aplicaron al modelado de lenguaje autorregresivo utilizando una pila de decodificadores Transformer. Desde entonces, los modelos de lenguaje basados en Transformer han dominado la PNL, logrando el estado del arte en muchas tareas. Un nuevo paradigma surgió con BERT (Devlin et al., 2019b) y GPT-2 (Radford et al., b) – ambos son modelos de lenguaje Transformer grandes entrenados en una gran cantidad de texto – donde el ajuste fino en datos específicos de la tarea después del preentrenamiento en dominios generales proporciona una ganancia de rendimiento significativa en comparación con el entrenamiento en datos específicos de la tarea directamente. El entrenamiento de Transformers más grandes generalmente da como resultado un mejor rendimiento y sigue siendo una dirección de investigación activa. GPT-3 (Brown et al., 2020) es el modelo de lenguaje Transformer individual más grande entrenado hasta la fecha con 175B parámetros.

### Ingeniería de indicadores y ajuste fino

Si bien GPT-3 175B puede adaptar su comportamiento con solo unos pocos ejemplos de entrenamiento adicionales, el resultado depende en gran medida del indicador de entrada (Brown et al., 2020). Esto requiere un arte empírico de composición y formateo del indicador para maximizar el rendimiento de un modelo en una tarea deseada, lo que se conoce como ingeniería de indicadores o piratería de indicadores. El ajuste fino vuelve a entrenar un modelo preentrenado en dominios generales a una tarea específica Devlin et al. (2019b); Radford et al. (a). Las variantes de él incluyen aprender solo un subconjunto de los parámetros Devlin et al. (2019b); Collobert & Weston (2008), pero los profesionales a menudo vuelven a entrenar todos para maximizar el rendimiento posterior. Sin embargo, la enormidad de GPT-3 175B hace que sea un desafío realizar el ajuste fino de la manera habitual debido al gran punto de control que produce y la alta barrera de entrada de hardware, ya que tiene la misma huella de memoria que el preentrenamiento.

### Adaptación eficiente de parámetros

Muchos han propuesto insertar capas de adaptador entre las capas existentes en una red neuronal (Houlsby et al., 2019; Rebuffi et al., 2017; Lin et al., 2020). Nuestro método utiliza una estructura de cuello de botella similar para imponer una restricción de rango bajo a las actualizaciones de peso. La principal diferencia funcional es que nuestros pesos aprendidos se pueden fusionar con los pesos principales durante la inferencia, sin introducir ninguna latencia, lo que no es el caso de las capas de adaptador (Sección 3). Una extensión contemporánea del adaptador es COMPACTER (Mahabadi et al., 2021), que esencialmente parametriza las capas del adaptador utilizando productos de Kronecker con algún esquema de uso compartido de peso predeterminado. De manera similar, combinar LoRA con otros métodos basados en productos tensoriales podría potencialmente mejorar su eficiencia de parámetros, lo que dejamos para un trabajo futuro. Más recientemente, muchos han propuesto optimizar las incrustaciones de palabras de entrada en lugar del ajuste fino, similar a una generalización continua y diferenciable de la ingeniería de indicadores (Li & Liang, 2021; Lester et al., 2021; Hambardzumyan et al., 2020; Liu et al., 2021). Incluimos comparaciones con Li & Liang (2021) en nuestra sección de experimentos. Sin embargo, esta línea de trabajos solo puede escalar utilizando más tokens especiales en el indicador, que ocupan la longitud de la secuencia disponible para los tokens de tarea cuando se aprenden las incrustaciones posicionales.

### Estructuras de rango bajo en aprendizaje profundo

La estructura de rango bajo es muy común en el aprendizaje automático. Muchos problemas de aprendizaje automático tienen cierta estructura de rango bajo intrínseca (Li et al., 2016; Cai et al., 2010; Li et al., 2018b; Grasedyck et al., 2013). Además, se sabe que para muchas tareas de aprendizaje profundo, especialmente aquellas con una red neuronal fuertemente sobreparametrizada, la red neuronal aprendida disfrutará de propiedades de rango bajo después del entrenamiento (Oymak et al., 2019). Algunos trabajos anteriores incluso imponen explícitamente la restricción de rango bajo al entrenar la red neuronal original (Sainath et al., 2013; Povey et al., 2018; Zhang et al., 2014; Jaderberg et al., 2014; Zhao et al., 2016; Khodak et al., 2021; Denil et al., 2014); sin embargo, hasta donde sabemos, ninguno de estos trabajos considera la actualización de rango bajo a un modelo congelado para la adaptación a tareas posteriores. En la literatura teórica, se sabe que las redes neuronales superan otros métodos de aprendizaje clásicos, incluidos los núcleos de tangente neural (de ancho finito) correspondientes (Allen-Zhu et al., 2019; Li & Liang, 2018) cuando la clase de concepto subyacente tiene cierta estructura de rango bajo (Ghorbani et al., 2020; Allen-Zhu & Li, 2019; Allen-Zhu & Li, 2020a). Otro resultado teórico en Allen-Zhu & Li (2020b) sugiere que las adaptaciones de rango bajo pueden ser útiles para el entrenamiento adversarial. En resumen, creemos que nuestra actualización de adaptación de rango bajo propuesta está bien motivada por la literatura.

## 7. COMPRENDER LAS ACTUALIZACIONES DE RANGO BAJO

Dado la ventaja empírica de LoRA, esperamos explicar aún más las propiedades de la adaptación de rango bajo aprendida de las tareas posteriores. Tenga en cuenta que la estructura de rango bajo no solo reduce la barrera de entrada de hardware, lo que nos permite ejecutar múltiples experimentos en paralelo, sino que también proporciona una mejor interpretabilidad de cómo los pesos de actualización están correlacionados con los pesos preentrenados. Centramos nuestro estudio en GPT-3 175B, donde logramos la mayor reducción de parámetros entrenables (hasta 10,000×) sin afectar negativamente los rendimientos de las tareas.

Realizamos una secuencia de estudios empíricos para responder a las siguientes preguntas: 1) Dado una restricción de presupuesto de parámetros, ¿qué subconjunto de matrices de peso en un Transformer preentrenado deberíamos adaptar para maximizar el rendimiento posterior? 2) ¿Es la matriz de adaptación "óptima" ∆W realmente deficiente en rango? Si es así, ¿cuál es un buen rango para usar en la práctica? 3) ¿Cuál es la conexión entre ∆W y W? ¿∆W está altamente correlacionada con W? ¿Qué tan grande es ∆W en comparación con W?

Creemos que nuestras respuestas a las preguntas (2) y (3) arrojan luz sobre los principios fundamentales del uso de modelos de lenguaje preentrenados para tareas posteriores, que es un tema crítico en la PNL.

### 7.1 ¿QUÉ MATRICES DE PESO EN TRANSFORMER DEBERÍAMOS APLICAR LORA?

Dado un presupuesto limitado de parámetros, ¿qué tipos de pesos deberíamos adaptar con LoRA para obtener el mejor rendimiento en las tareas de downstream? Como se mencionó en la sección 4.2, solo consideramos matrices de peso en el módulo de autoatención. Fijamos un presupuesto de parámetros de 18M (aproximadamente 35 MB si se almacena en FP16) en GPT-3 175B, lo que corresponde a r = 8 si adaptamos un tipo de peso de atención o r = 4 si adaptamos dos tipos, para las 96 capas. El resultado se presenta en la tabla 5.

Tipo de Peso	Wq	Wk	Wv	Wo	Wq,Wk	Wq,Wv	Wq,Wk,Wv,Wo
Rango r	8	8	8	8	4	4	2
WikiSQL (±0.5%)	70.4	70.0	73.0	73.2	71.4	73.7	73.7
MultiNLI (±0.1%)	91.0	90.8	91.0	91.3	91.3	91.3	91.7

Tabla 5: Precisión de validación en WikiSQL y MultiNLI después de aplicar LoRA a diferentes tipos de pesos de atención en GPT-3, dado el mismo número de parámetros entrenables. Adaptar tanto Wq como Wv proporciona el mejor rendimiento en general. Descubrimos que la desviación estándar entre semillas aleatorias es consistente para un conjunto de datos dado, lo que informamos en la primera columna.

Nótese que colocar todos los parámetros en ∆Wq o ∆Wk produce un rendimiento significativamente menor, mientras que adaptar tanto Wq como Wv produce el mejor resultado. Esto sugiere que incluso un rango de cuatro captura suficiente información en ∆W para que sea preferible adaptar más matrices de peso que adaptar un solo tipo de peso con un rango mayor.

### 7.2 ¿Cuál es el Rango Óptimo r para LoRA?

Dirigimos nuestra atención al efecto del rango r en el rendimiento del modelo. Adaptamos {Wq,Wv}, {Wq,Wk,Wv,Wc} y solo Wq para una comparación.

Tipo de Peso	r = 1	r = 2	r = 4	r = 8	r = 64
WikiSQL(±0.5%)	Wq	68.8	69.6	70.5	70.4
Wq,Wv	73.4	73.3	73.7	73.8
Wq,Wk,Wv,Wo	74.1	73.7	74.0	74.0
MultiNLI (±0.1%)	Wq	90.7	90.9	91.1	90.7
Wq,Wv	91.3	91.4	91.3	91.6
Wq,Wk,Wv,Wo	91.2	91.7	91.7	91.5

Tabla 6: Precisión de validación en WikiSQL y MultiNLI con diferentes rangos r. Para nuestra sorpresa, un rango tan pequeño como uno es suficiente para adaptar tanto Wq como Wv en estos conjuntos de datos, mientras que entrenar solo Wq necesita un r mayor. Realizamos un experimento similar en GPT-2 en la sección H.2.

La tabla 6 muestra que, sorprendentemente, LoRA ya se desempeña de manera competitiva con un r muy pequeño (más para {Wq,Wv} que para solo Wq). Esto sugiere que la matriz de actualización ∆W podría tener un "rango intrínseco" muy pequeño. Para apoyar aún más este hallazgo, verificamos la superposición de los subespacios aprendidos por diferentes elecciones de r y por diferentes semillas aleatorias. Argumentamos que aumentar r no cubre un subespacio más significativo, lo que sugiere que una matriz de adaptación de rango bajo es suficiente.

**Similitud del Subespacio entre Diferentes r**. Dado Ar=8 y Ar=64, que son las matrices de adaptación aprendidas con rango r = 8 y 64 utilizando el mismo modelo preentrenado, realizamos la descomposición de valor singular y obtenemos las matrices unitarias singulares correctas UAr=8 y UAr=64. Esperamos responder: ¿cuánto del subespacio abarcado por los primeros i vectores singulares en UAr=8 (para 1 ≤ i ≤ 8) está contenido en el subespacio abarcado por los primeros j vectores singulares de UAr=64 (para 1 ≤ j ≤ 64)? Medimos esta cantidad con una similitud de subespacio normalizada basada en la distancia de Grassmann (ver Apéndice G para una discusión más formal)

φ(Ar=8, Ar=64, i, j) = ||U i>Ar=8 U jAr=64 ||2F min(i, j) ∈ [0, 1] (4)

donde U iAr=8 representa las columnas de UAr=8 correspondientes a los primeros i vectores singulares.

φ(·) tiene un rango de [0, 1], donde 1 representa una superposición completa de subespacios y 0 una separación completa. Vea la figura 3 para ver cómo cambia φ al variar i y j. Solo miramos la capa 48 (de 96) debido a la limitación de espacio, pero la conclusión se mantiene para otras capas también, como se muestra en la sección H.1.

[Imagen de la figura 3]

Figura 3: Similitud de subespacio entre vectores de columna de Ar=8 y Ar=64 para ambos ∆Wq y ∆Wv. La tercera y la cuarta figuras amplían el triángulo inferior izquierdo en las dos primeras figuras. Las direcciones superiores en r = 8 están incluidas en r = 64, y viceversa.

Hacemos una observación importante de la figura 3.

Las direcciones correspondientes al primer vector singular se superponen significativamente entre Ar=8 y Ar=64, mientras que otras no. Específicamente, ∆Wv (resp. ∆Wq) de Ar=8 y ∆Wv (resp. ∆Wq) de Ar=64 comparten un subespacio de dimensión 1 con similitud normalizada > 0.5, proporcionando una explicación de por qué r = 1 se desempeña bastante bien en nuestras tareas de downstream para GPT-3.

Dado que tanto Ar=8 como Ar=64 se aprenden utilizando el mismo modelo preentrenado, la figura 3 indica que las direcciones de vector singular superior de Ar=8 y Ar=64 son las más útiles, mientras que otras direcciones potencialmente contienen principalmente ruidos aleatorios acumulados durante el entrenamiento. Por lo tanto, la matriz de adaptación puede tener un rango muy bajo.

**Similitud del Subespacio entre Diferentes Semillas Aleatorias**. Confirmamos esto aún más trazando la similitud de subespacio normalizada entre dos ejecuciones con semillas aleatorias con r = 64, que se muestra en la figura 4. ∆Wq parece tener un "rango intrínseco" más alto que ∆Wv, ya que se aprenden más direcciones de valor singular comunes por ambas ejecuciones para ∆Wq, lo que está en línea con nuestra observación empírica en la tabla 6. A modo de comparación, también trazamos dos matrices gaussianas aleatorias, que no comparten ninguna dirección de valor singular común entre sí.

[Imagen de la figura 4]

Figura 4: Izquierda y Centro: Similitud de subespacio normalizada entre los vectores de columna de Ar=64 desde dos semillas aleatorias, para ambos ∆Wq y ∆Wv en la capa 48. Derecha: el mismo mapa de calor entre los vectores de columna de dos matrices gaussianas aleatorias. Vea la sección H.1 para otras capas.

### 7.3 ¿Cómo Se Compara la Matriz de Adaptación ∆W con W?

Investigamos aún más la relación entre ∆W y W. En particular, ¿∆W está altamente correlacionada con W? (O matemáticamente, ¿∆W está mayormente contenida en las direcciones singulares superiores de W?) Además, ¿qué tan "grande" es ∆W en comparación con sus direcciones correspondientes en W? Esto puede arrojar luz sobre el mecanismo subyacente para adaptar modelos de lenguaje preentrenados.

Para responder a estas preguntas, proyectamos W sobre el subespacio r-dimensional de ∆W calculando U>WV >, con U /V siendo la matriz de vector singular izquierdo/derecho de ∆W. Luego, comparamos la norma de Frobenius entre ‖U>WV >‖F y ‖W‖F. A modo de comparación, también calculamos ‖U>WV >‖F reemplazando U, V con los primeros r vectores singulares de W o una matriz aleatoria.

r = 4	r = 64	∆Wq	Wq	Aleatorio	∆Wq	Wq	Aleatorio
U>WqV >		F =	0.32	21.67	0.02
Wq		F =	61.95		
∆Wq		F =	6.91		

Tabla 7: La norma de Frobenius de U>WqV > donde U y V son las direcciones de vector singular superior izquierdo/derecho de (1) ∆Wq, (2) Wq o (3) una matriz aleatoria. Las matrices de peso se toman de la capa 48 de GPT-3.

Sacamos varias conclusiones de la tabla 7. Primero, ∆W tiene una correlación más fuerte con W en comparación con una matriz aleatoria, lo que indica que ∆W amplifica algunas características que ya están en W. Segundo, en lugar de repetir las direcciones singulares superiores de W, ∆W solo amplifica las direcciones que no están resaltadas en W. Tercero, el factor de amplificación es bastante grande: 21.5 ≈ 6.91/0.32 para r = 4. Vea la sección H.4 para ver por qué r = 64 tiene un factor de amplificación menor. También proporcionamos una visualización en la sección H.3 de cómo cambia la correlación a medida que incluimos más direcciones singulares superiores de Wq. Esto sugiere que la matriz de adaptación de rango bajo potencialmente amplifica las características importantes para tareas de downstream específicas que se aprendieron pero no se destacaron en el modelo de preentrenamiento general.

## 8. CONCLUSIÓN Y TRABAJO FUTURO

Entrenar modelos de lenguaje enormes es prohibitivamente caro en términos del hardware requerido y el costo de almacenamiento/cambio para alojar instancias independientes para diferentes tareas. Proponemos LoRA, una estrategia de adaptación eficiente que no introduce latencia de inferencia ni reduce la longitud de la secuencia de entrada, mientras que conserva una alta calidad del modelo. Es importante destacar que permite un rápido cambio de tarea cuando se implementa como servicio al compartir la gran mayoría de los parámetros del modelo. Si bien nos enfocamos en modelos de lenguaje Transformer, los principios propuestos son generalmente aplicables a cualquier red neuronal con capas densas.

Existen muchas direcciones para trabajos futuros. 1) LoRA se puede combinar con otros métodos de adaptación eficientes, lo que potencialmente proporciona una mejora ortogonal. 2) El mecanismo detrás del entrenamiento fino o LoRA está lejos de estar claro: ¿cómo se transforman las características aprendidas durante el preentrenamiento para funcionar bien en las tareas de downstream? Creemos que LoRA hace que sea más fácil responder a esto que el entrenamiento fino completo. 3) Dependemos principalmente de la heurística para seleccionar las matrices de peso a las que se debe aplicar LoRA. ¿Existen formas más principales de hacerlo? 4) Finalmente, la deficiencia de rango de ∆W sugiere que W también podría ser deficiente en rango, lo que también puede ser una fuente de inspiración para trabajos futuros.

# Apéndices

## A MODELOS DE LENGUAJE GRANDES TODAVÍA NECESITAN ACTUALIZACIONES DE PARÁMETROS

El aprendizaje de pocos disparos, o la ingeniería de prompts, es muy ventajoso cuando solo tenemos un puñado de ejemplos de entrenamiento. Sin embargo, en la práctica, a menudo podemos permitirnos curar algunos miles o más ejemplos de entrenamiento para aplicaciones sensibles al rendimiento. Como se muestra en la tabla 8, el entrenamiento fino mejora drásticamente el rendimiento del modelo en comparación con el aprendizaje de pocos disparos en conjuntos de datos grandes y pequeños. Tomamos el resultado de pocos disparos de GPT-3 en RTE del artículo de GPT-3 (Brown et al., 2020). Para MNLI-coincidente, utilizamos dos demostraciones por clase y seis ejemplos en contexto en total.

Método	MNLI-m (Precisión de validación/%)	RTE (Precisión de validación/%)
GPT-3 de pocos disparos	40.6	69.0
GPT-3 Entrenado Fín	89.5	85.4

Tabla 8: El entrenamiento fino supera significativamente el aprendizaje de pocos disparos en GPT-3 (Brown et al., 2020).

## B LA LATENCIA DE INFERENCIA INTRODUCIDA POR LAS CAPAS DE ADAPTADOR

Las capas de adaptador son módulos externos agregados a un modelo preentrenado de forma secuencial, mientras que nuestra propuesta, LoRA, se puede ver como módulos externos agregados de forma paralela. En consecuencia, las capas de adaptador deben calcularse además del modelo base, lo que inevitablemente introduce latencia adicional. Si bien, como se señaló en Rücklé et al. (2020), la latencia introducida por las capas de adaptador se puede mitigar cuando el tamaño del lote del modelo y/o la longitud de la secuencia son lo suficientemente grandes como para utilizar completamente el paralelismo del hardware. Confirmamos su observación con un estudio de latencia similar en GPT-2 mediano y señalamos que hay escenarios, notablemente la inferencia en línea donde el tamaño del lote es pequeño, donde la latencia agregada puede ser significativa.

Medimos la latencia de una sola pasada hacia adelante en una NVIDIA Quadro RTX8000 promediando 100 ensayos. Variamos el tamaño del lote de entrada, la longitud de la secuencia y la dimensión de cuello de botella del adaptador r. Probamos dos diseños de adaptador: el original de Houlsby et al. (2019), que llamamos AdapterH, y una variante reciente, más eficiente de Lin et al. (2020), que llamamos AdapterL. Consulte la sección 5.1 para obtener más detalles sobre los diseños. Trazamos la ralentización en porcentaje en comparación con la línea base sin adaptador en la figura 5.

[Imagen de la figura 5]

Figura 5: Porcentaje de ralentización de la latencia de inferencia en comparación con la línea base sin adaptador (r = 0). La fila superior muestra el resultado para AdapterH y la fila inferior AdapterL. Un tamaño de lote y una longitud de secuencia más grandes ayudan a mitigar la latencia, pero la ralentización puede llegar a ser superior al 30 % en un escenario de longitud de secuencia corta en línea. Ajustamos el mapa de colores para una mejor visibilidad.

## C DETALLES DEL CONJUNTO DE DATOS

El conjunto de datos de GLUE es una amplia colección de tareas de comprensión del lenguaje natural. Incluye MNLI (inferencia, Williams et al. (2018)), SST-2 (análisis de sentimiento, Socher et al. (2013)), MRPC (detección de paráfrasis, Dolan & Brockett (2005)), CoLA (aceptabilidad lingüística, Warstadt et al. (2018)), QNLI (inferencia, Rajpurkar et al. (2018)), QQP8 (preguntas y respuestas), RTE (inferencia) y STS-B (similitud textual, Cer et al. (2017)). La amplia cobertura convierte al conjunto de datos de GLUE en una métrica estándar para evaluar modelos de PNL como RoBERTa y DeBERTa. Los conjuntos de datos individuales se publican bajo diferentes licencias permisivas.

WikiSQL se introdujo en Zhong et al. (2017) y contiene 56,355/8,421 ejemplos de entrenamiento/validación. La tarea consiste en generar consultas SQL a partir de preguntas de lenguaje natural y esquemas de tabla. Codificamos el contexto como x = {esquema de tabla, consulta} y el objetivo como y = {SQL}. El conjunto de datos se publica bajo la Licencia BSD de 3 cláusulas.

SAMSum se introdujo en Gliwa et al. (2019) y contiene 14,732/819 ejemplos de entrenamiento/prueba. Consiste en conversaciones de chat por etapas entre dos personas y resúmenes abstractos escritos por lingüistas. Codificamos el contexto como "
" concatenamos las expresiones seguidas de un "
", y el objetivo como y = {resumen}. El conjunto de datos se publica bajo la licencia no comercial: Creative Commons BY-NC-ND 4.0.

El conjunto de datos de E2E NLG Challenge se introdujo por primera vez en Novikova et al. (2017) como un conjunto de datos para entrenar sistemas de generación de lenguaje natural basados ​​en datos de extremo a extremo y se utiliza comúnmente para la evaluación de datos a texto. El conjunto de datos de E2E consta de aproximadamente 42,000 ejemplos de entrenamiento, 4,600 de validación y 4,600 de prueba del dominio de restaurantes. Cada tabla de origen utilizada como entrada puede tener varias referencias. Cada entrada de muestra (x, y) consta de una secuencia de pares de ranura-valor, junto con un texto de referencia de lenguaje natural correspondiente. El conjunto de datos se publica bajo Creative Commons BY-NC-SA 4.0.

DART es un conjunto de datos de datos a texto de dominio abierto descrito en Nan et al. (2020). Las entradas de DART están estructuradas como secuencias de triples ENTIDAD — RELACIÓN — ENTIDAD. Con 82K ejemplos en total, DART es una tarea de datos a texto significativamente más grande y compleja en comparación con E2E. El conjunto de datos se publica bajo la licencia MIT.

WebNLG es otro conjunto de datos comúnmente utilizado para la evaluación de datos a texto (Gardent et al., 2017). Con 22K ejemplos en total, WebNLG comprende 14 categorías distintas, nueve de las cuales se ven durante el entrenamiento. Dado que cinco de las 14 categorías totales no se ven durante el entrenamiento, pero están representadas en el conjunto de prueba, la evaluación suele desglosarse por categorías "vistas" (S), categorías "no vistas" (U) y "todas" (A). Cada ejemplo de entrada está representado por una secuencia de triples SUJETO — PROPIEDAD — OBJETO. El conjunto de datos se publica bajo Creative Commons BY-NC-SA 4.0.

## D HIPERPARÁMETROS UTILIZADOS EN LOS EXPERIMENTOS

### D.1 ROBERTA

Entrenando usando AdamW con un programa de decaimiento de tasa de aprendizaje lineal. Barremos la tasa de aprendizaje, el número de épocas de entrenamiento y el tamaño del lote para LoRA. Siguiendo a Liu et al. (2019), inicializamos los módulos LoRA a nuestro mejor punto de control MNLI cuando nos adaptamos a MRPC, RTE y STS-B, en lugar de la inicialización habitual; el modelo preentrenado permanece congelado para todas las tareas. Informamos la mediana de 5 semillas aleatorias; el resultado de cada ejecución se toma de la mejor época. Para una comparación justa con la configuración de Houlsby et al. (2019) y Pfeiffer et al. (2021), restringimos la longitud de la secuencia del modelo a 128 y utilizamos un tamaño de lote fijo para todas las tareas. Es importante destacar que comenzamos con el modelo RoBERTa grande preentrenado cuando nos adaptamos a MRPC, RTE y STS-B, en lugar de un modelo ya adaptado a MNLI. Las ejecuciones con esta configuración restringida están marcadas con †. Vea los hiperparámetros utilizados en nuestras ejecuciones en la tabla 9.

| Método | Conjunto de datos | MNLI | SST-2 | MRPC | CoLA | QNLI | QQP | RTE | STS-B |
|---|---|---|---|---|---|---|---|---|
| Optimizador | AdamW | | | | | | | | |
| Proporción de calentamiento | 0.06 | | | | | | | | |
| Programa de tasa de aprendizaje | Lineal | | | | | | | | |
| RoBERTa base LoRA | | | | | | | | | |
| Tamaño del lote | 16 | 16 | 16 | 32 | 32 | 16 | 32 | 16 | |
| Número de épocas | 30 | 60 | 30 | 80 | 25 | 25 | 80 | 40 | |
| Tasa de aprendizaje | 5E-04 | 5E-04 | 4E-04 | 4E-04 | 4E-04 | 5E-04 | 5E-04 | 4E-04 | |
| Configuración de LoRA | rq = rv = 8 | | | | | | | | |
| LoRA α | 8 | | | | | | | | |
| Longitud máxima de la secuencia | 512 | | | | | | | | |
| RoBERTa grande LoRA | | | | | | | | | |
| Tamaño del lote | 4 | 4 | 4 | 4 | 4 | 4 | 8 | 8 | |
| Número de épocas | 10 | 10 | 20 | 20 | 10 | 20 | 20 | 30 | |
| Tasa de aprendizaje | 3E-04 | 4E-04 | 3E-04 | 2E-04 | 2E-04 | 3E-04 | 4E-04 | 2E-04 | |
| Configuración de LoRA | rq = rv = 8 | | | | | | | | |
| LoRA α | 16 | | | | | | | | |
| Longitud máxima de la secuencia | 128 | 128 | 512 | 128 | 512 | 512 | 512 | 512 | |
| RoBERTa grande LoRA† | | | | | | | | | |
| Tamaño del lote | 4 | | | | | | | | |
| Número de épocas | 10 | 10 | 20 | 20 | 10 | 20 | 20 | 10 | |
| Tasa de aprendizaje | 3E-04 | 4E-04 | 3E-04 | 2E-04 | 2E-04 | 3E-04 | 4E-04 | 2E-04 | |
| Configuración de LoRA | rq = rv = 8 | | | | | | | | |
| LoRA α | 16 | | | | | | | | |
| Longitud máxima de la secuencia | 128 | | | | | | | | |
| RoBERTa grande AdptP (3M)† | | | | | | | | | |
| Tamaño del lote | 32 | | | | | | | | |
| Número de épocas | 10 | 20 | 20 | 20 | 10 | 20 | 20 | 20 | |
| Tasa de aprendizaje | 3E-05 | 3E-05 | 3E-04 | 3E-04 | 3E-04 | 3E-04 | 3E-04 | 3E-04 | |
| Cuello de botella r | 64 | | | | | | | | |
| Longitud máxima de la secuencia | 128 | | | | | | | | |
| RoBERTa grande AdptP (0.8M)† | | | | | | | | | |
| Tamaño del lote | 32 | | | | | | | | |
| Número de épocas | 5 | 20 | 20 | 20 | 10 | 20 | 20 | 20 | |
| Tasa de aprendizaje | 3E-04 | 3E-04 | 3E-04 | 3E-04 | 3E-04 | 3E-04 | 3E-04 | 3E-04 | |
| Cuello de botella r | 16 | | | | | | | | |
| Longitud máxima de la secuencia | 128 | | | | | | | | |
| RoBERTa grande AdptH (6M)† | | | | | | | | | |
| Tamaño del lote | 32 | | | | | | | | |
| Número de épocas | 10 | 5 | 10 | 10 | 5 | 20 | 20 | 10 | |
| Tasa de aprendizaje | 3E-05 | 3E-04 | 3E-04 | 3E-04 | 3E-04 | 3E-04 | 3E-04 | 3E-04 | |
| Cuello de botella r | 64 | | | | | | | | |
| Longitud máxima de la secuencia | 128 | | | | | | | | |
| RoBERTa grande AdptH (0.8M)† | | | | | | | | | |
| Tamaño del lote | 32 | | | | | | | | |
| Número de épocas | 10 | 5 | 10 | 10 | 5 | 20 | 20 | 10 | |
| Tasa de aprendizaje | 3E-04 | 3E-04 | 3E-04 | 3E-04 | 3E-04 | 3E-04 | 3E-04 | 3E-04 | |
| Cuello de botella r | 8 | | | | | | | | |
| Longitud máxima de la secuencia | 128 | | | | | | | | |

Tabla 9: Los hiperparámetros que usamos para RoBERTa en el conjunto de datos de GLUE.

### D.2 DEBERTA

Nuevamente entrenamos usando AdamW con un programa de decaimiento de tasa de aprendizaje lineal. Siguiendo a He et al. (2021), sintonizamos la tasa de aprendizaje, la probabilidad de abandono, los pasos de calentamiento y el tamaño del lote. Usamos la misma longitud de secuencia del modelo que (He et al., 2021) para mantener nuestra comparación justa. Siguiendo a He et al. (2021), inicializamos los módulos LoRA a nuestro mejor punto de control MNLI cuando nos adaptamos a MRPC, RTE y STS-B, en lugar de la inicialización habitual; el modelo preentrenado permanece congelado para todas las tareas. Informamos la mediana de 5 semillas aleatorias; el resultado de cada ejecución se toma de la mejor época. Vea los hiperparámetros utilizados en nuestras ejecuciones en la tabla 10.

| Método | Conjunto de datos | MNLI | SST-2 | MRPC | CoLA | QNLI | QQP | RTE | STS-B |
|---|---|---|---|---|---|---|---|---|
| Optimizador | AdamW | | | | | | | | |
| Proporción de calentamiento | 0.1 | | | | | | | | |
| Programa de tasa de aprendizaje | Lineal | | | | | | | | |
| DeBERTa XXL LoRA | | | | | | | | | |
| Tamaño del lote | 8 | 8 | 32 | 4 | 6 | 8 | 4 | 4 | |
| Número de épocas | 5 | 16 | 30 | 10 | 8 | 11 | 11 | 10 | |
| Tasa de aprendizaje | 1E-04 | 6E-05 | 2E-04 | 1E-04 | 1E-04 | 1E-04 | 2E-04 | 2E-04 | |
| Decaimiento de peso | 0 | 0.01 | 0.01 | 0 | 0.01 | 0.01 | 0.01 | 0.1 | |
| Abandono de CLS | 0.15 | 0 | 0 | 0.1 | 0.1 | 0.2 | 0.2 | 0.2 | |
| Configuración de LoRA | rq = rv = 8 | | | | | | | | |
| LoRA α | 8 | | | | | | | | |
| Longitud máxima de la secuencia | 256 | 128 | 128 | 64 | 512 | 320 | 320 | 128 | |

Tabla 10: Los hiperparámetros para DeBERTa XXL en las tareas incluidas en el conjunto de datos de GLUE.

### D.3 GPT-2

Entrenando todos nuestros modelos GPT-2 usando AdamW (Loshchilov & Hutter, 2017) con un programa de tasa de aprendizaje lineal para 5 épocas. Usamos el tamaño del lote, la tasa de aprendizaje y el tamaño del haz de búsqueda por haz descrito en Li & Liang (2021). En consecuencia, también sintonizamos los hiperparámetros anteriores para LoRA. Informamos la media de 3 semillas aleatorias; el resultado de cada ejecución se toma de la mejor época. Los hiperparámetros utilizados para LoRA en GPT-2 se enumeran en la tabla 11. Para aquellos utilizados para otras líneas de base, consulte Li & Liang (2021).

Conjunto de datos	E2E	WebNLG	DART
Entrenamiento			
Optimizador	AdamW	AdamW	AdamW
Decaimiento de peso	0.01	0.01	0.01
Probabilidad de abandono	0.1	0.1	0.0
Tamaño del lote	8	8	8
Número de épocas	5	5	5
Pasos de calentamiento	500	500	500
Programa de tasa de aprendizaje	Lineal	Lineal	Lineal
Suavizado de etiquetas	0.1	0.1	0.0
Tasa de aprendizaje	0.0002	0.0002	0.0002
Adaptación	rq = rv = 4	rq = rv = 4	rq = rv = 4
LoRA α	32	32	32
Inferencia			
Tamaño del haz	10	10	10
Penalización de longitud	0.9	0.8	0.8
Tamaño del ngrama sin repetición	4	4	4

Tabla 11: Los hiperparámetros para GPT-2 LoRA en E2E, WebNLG y DART.

### D.4 GPT-3

Para todos los experimentos de GPT-3, entrenamos usando AdamW (Loshchilov & Hutter, 2017) durante 2 épocas con un tamaño de lote de 128 muestras y un factor de decaimiento de peso de 0.1. Usamos una longitud de secuencia de 384 para WikiSQL (Zhong et al., 2017), 768 para MNLI (Williams et al., 2018) y 2048 para SAMSum (Gliwa et al., 2019). Sintonizamos la tasa de aprendizaje para todas las combinaciones de método-conjunto de datos. Consulte la sección D.4 para obtener más detalles sobre los hiperparámetros utilizados. Para el ajuste de incrustaciones de prefijo, encontramos que los lp y li óptimos son 256 y 8, respectivamente, con un total de 3.2M parámetros entrenables. Usamos lp = 8 y li = 8 para el ajuste de capa de prefijo con 20.2M parámetros entrenables para obtener el mejor rendimiento general. Presentamos dos presupuestos de parámetros para LoRA: 4.7M (rq = rv = 1 o rv = 2) y 37.7M (rq = rv = 8 o rq = rk = rv = ro = 2). Informamos el mejor rendimiento de validación de cada ejecución. Los hiperparámetros de entrenamiento utilizados en nuestros experimentos de GPT-3 se enumeran en la tabla 12.

Hiperparámetros	Entrenamiento fino	PreEmbed	PreLayer	BitFit	AdapterH	LoRA
Optimizador	AdamW	AdamW	AdamW	AdamW	AdamW	AdamW
Tamaño del lote	128	128	128	128	128	128
Número de épocas	2	2	2	2	2	2
Tokens de calentamiento	250,000	250,000	250,000	250,000	250,000	250,000
Programa de tasa de aprendizaje	Lineal	Lineal	Lineal	Lineal	Lineal	Lineal
Tasa de aprendizaje	5.00E-06	5.00E-04	1.00E-04	1.6E-03	1.00E-04	2.00E-04
Tabla 12: Los hiperparámetros de entrenamiento utilizados para diferentes métodos de adaptación de GPT-3. Usamos los mismos hiperparámetros para todos los conjuntos de datos después de ajustar la tasa de aprendizaje.

## E COMBINANDO LORA CON AJUSTE DE PREFIJO
LoRA se puede combinar naturalmente con los enfoques existentes basados ​​en prefijos. En esta sección, evaluamos dos combinaciones de LoRA y variantes de ajuste de prefijo en WikiSQL y MNLI.
LoRA+PrefixEmbed (LoRA+PE) combina LoRA con el ajuste de incrustación de prefijo, donde insertamos lp + li tokens especiales cuyas incrustaciones se tratan como parámetros entrenables. Para obtener más información sobre el ajuste de incrustación de prefijo, consulte la sección 5.1.
LoRA+PrefixLayer (LoRA+PL) combina LoRA con el ajuste de capa de prefijo. También insertamos lp + li tokens especiales; sin embargo, en lugar de dejar que las representaciones ocultas de estos tokens evolucionen naturalmente, los reemplazamos después de cada bloque Transformer con un vector agnóstico de entrada. Por lo tanto, tanto las incrustaciones como las activaciones del bloque Transformer subsiguientes se tratan como parámetros entrenables. Para obtener más información sobre el ajuste de capa de prefijo, consulte la sección 5.1.
En la tabla 15, mostramos los resultados de la evaluación de LoRA+PE y LoRA+PL en WikiSQL y MultiNLI. En primer lugar, LoRA+PE supera significativamente tanto a LoRA como al ajuste de incrustación de prefijo en WikiSQL, lo que indica que LoRA es algo ortogonal al ajuste de incrustación de prefijo. En MultiNLI, la combinación de LoRA+PE no funciona mejor que LoRA, posiblemente porque LoRA por sí solo ya alcanza un rendimiento comparable a la línea de base humana. En segundo lugar, notamos que LoRA+PL funciona ligeramente peor que LoRA incluso con más parámetros entrenables. Atribuimos esto al hecho de que el ajuste de capa de prefijo es muy sensible a la elección de la tasa de aprendizaje y, por lo tanto, dificulta la optimización de los pesos LoRA en LoRA+PL.
Método	Hiperparámetros	Número de parámetros entrenables	WikiSQL	MNLI-m
Entrenamiento fino	-	175B	73.8	89.5
PrefixEmbed	lp = 32, li = 8	0.4 M	55.9	84.9
lp = 64, li = 8	0.9 M	58.7	88.1
lp = 128, li = 8	1.7 M	60.6	88.0
lp = 256, li = 8	3.2 M	63.1	88.6
lp = 512, li = 8	6.4 M	55.9	85.8
PrefixLayer	lp = 2, li = 2	5.1 M	68.5	89.2
lp = 8, li = 0	10.1 M	69.8	88.2
lp = 8, li = 8	20.2 M	70.1	89.5
lp = 32, li = 4	44.1 M	66.4	89.6
lp = 64, li = 0	76.1 M	64.9	87.9
AdapterH	r = 1	7.1 M	71.9	89.8
r = 4	21.2 M	73.2	91.0
r = 8	40.1 M	73.2	91.5
r = 16	77.9 M	73.2	91.5
r = 64	304.4 M	72.6	91.5
LoRA	rv = 2	4.7 M	73.4	91.7
rq = rv = 1	4.7 M	73.4	91.3
rq = rv = 2	9.4 M	73.3	91.4
rq = rk = rv = ro = 1	9.4 M	74.1	91.2
rq = rv = 4	18.8 M	73.7	91.3
rq = rk = rv = ro = 2	18.8 M	73.7	91.7
rq = rv = 8	37.7 M	73.8	91.6
rq = rk = rv = ro = 4	37.7 M	74.0	91.7
rq = rv = 64	301.9 M	73.6	91.4
rq = rk = rv = ro = 64	603.8 M	73.9	91.4
LoRA+PE	rq = rv = 8, lp = 8, li = 4	37.8 M	75.0	91.4
rq = rv = 32, lp = 8, li = 4	151.1 M	75.9	91.1
rq = rv = 64, lp = 8, li = 4	302.1 M	76.2	91.3
LoRA+PL	rq = rv = 8, lp = 8, li = 4	52.8 M	72.9	90.2
Tabla 15: Análisis de hiperparámetros de diferentes enfoques de adaptación en WikiSQL y MNLI. Tanto el ajuste de incrustación de prefijo (PrefixEmbed) como el ajuste de capa de prefijo (PrefixLayer) funcionan peor a medida que aumentamos el número de parámetros entrenables, mientras que el rendimiento de LoRA se estabiliza. El rendimiento se mide en precisión de validación.
F EXPERIMENTOS EMPÍRICOS ADICIONALES
F.1 EXPERIMENTOS ADICIONALES EN GPT-2
También repetimos nuestro experimento en DART (Nan et al., 2020) y WebNLG (Gardent et al., 2017) siguiendo la configuración de Li & Liang (2021). El resultado se muestra en la tabla 13. Similar a nuestro resultado en E2E NLG Challenge, reportado en la sección 5, LoRA se desempeña mejor o al menos a la par con los enfoques basados ​​en prefijos dado el mismo número de parámetros entrenables.
Método	Número de parámetros entrenables	DART	BLEU↑	MET↑	TER↓
GPT-2 Medio Entrenamiento fino	354M		46.2	0.39	0.46
AdapterL	0.37M		42.4	0.36
AdapterL	11M		45.2	0.38
FTTop2	24M		41.0	0.34
PrefLayer	0.35M		46.4	0.38
LoRA	0.35M		47.1±.2	0.39
GPT-2 Grande Entrenamiento fino	774M		47.0	0.39	0.46
AdapterL	0.88M		45.7±.1	0.38
AdapterL	23M		47.1±.1	0.39
PrefLayer	0.77M		46.7	0.38
LoRA	0.77M		47.5±.1	0.39
Tabla 13: GPT-2 con diferentes métodos de adaptación en DART. Las variaciones de MET y TER son inferiores a 0.01 para todos los enfoques de adaptación.
Método	WebNLG	BLEU↑	MET↑	TER↓
U	S	A	U
GPT-2 Medio Entrenamiento fino (354M)		27.7	64.2	46.5
AdapterL (0.37M)		45.1	54.5
AdapterL (11M)		48.3	60.4
FTTop2 (