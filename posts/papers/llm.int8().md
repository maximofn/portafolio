# LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale

## Abstract

Los grandes modelos lingüísticos han sido ampliamente adoptados, pero requieren una cantidad significativa de memoria de GPU para la inferencia. Desarrollamos un procedimiento para la multiplicación de matrices Int8 para capas de proyección de atención y de alimentación hacia adelante en transformadores, que reducen a la mitad la memoria necesaria para la inferencia al tiempo que conservan el rendimiento de precisión total. Con nuestro método, un punto de control de 175 B de parámetros de 16/32 bits se puede cargar, convertir a Int8 y utilizar inmediatamente sin degradación del rendimiento. Esto es posible al comprender y trabajar en torno a las propiedades de las características emergentes altamente sistemáticas en los modelos de lenguaje de transformadores que dominan la atención y el rendimiento predictivo del transformador. Para hacer frente a estas características, desarrollamos un procedimiento de cuantificación en dos partes, LLM.int8(). Primero, utilizamos la cuantificación vectorial con constantes de normalización separadas para cada producto interno en la multiplicación de matrices, para cuantificar la mayoría de las características. Sin embargo, para los valores atípicos emergentes, también incluimos un nuevo esquema de descomposición de precisión mixta, que aísla las dimensiones de características atípicas en una multiplicación de matrices de 16 bits, mientras que más del 99,9% de los valores se multiplican en 8 bits. Usando LLM.int8(), mostramos empíricamente que es posible realizar inferencias en LLM con hasta 175 B de parámetros sin ninguna degradación del rendimiento. Este resultado hace que dichos modelos sean mucho más accesibles, por ejemplo, haciendo posible utilizar OPT-175B/BLOOM en un solo servidor con GPU de consumo. Liberamos nuestro software como código abierto.

## 1. Introducción

Los grandes modelos lingüísticos preentrenados se han adoptado ampliamente en PNL (Vaswani et al., 2017; Radford et al., 2019; Brown et al., 2020; Zhang et al., 2022), pero requieren una cantidad significativa de memoria para la inferencia. Para los grandes modelos lingüísticos transformer en y más allá de los 6,7B parámetros, las capas de proyección de atención y de alimentación hacia adelante y sus operaciones de multiplicación de matrices son responsables del 95% de los parámetros consumidos y del 65-85% de todos los cálculos (Ilharco et al., 2020). Una forma de reducir el tamaño de los parámetros es cuantificarlos a menos bits y usar la multiplicación de matrices de baja precisión de bits. Con este objetivo en mente, se han desarrollado métodos de cuantificación de 8 bits para transformers (Chen et al., 2020; Lin et al., 2020; Zafrir et al., 2019; Shen et al., 2020). Si bien estos métodos reducen el uso de memoria, degradan el rendimiento, por lo general requieren ajustar aún más la cuantificación después del entrenamiento y solo se han estudiado para modelos con menos de 350 millones de parámetros. La cuantificación sin degradación de hasta 350 millones de parámetros es poco conocida y la cuantificación de parámetros de miles de millones sigue siendo un desafío abierto.

En este artículo, presentamos el primer procedimiento de cuantificación Int8 a escala de miles de millones para transformers que no incurre en ninguna degradación del rendimiento. Nuestro procedimiento permite cargar un transformer de 175B parámetros con pesos de 16 o 32 bits, convertir las capas de proyección de atención y de alimentación hacia adelante a 8 bits y utilizar el modelo resultante inmediatamente para la inferencia sin ninguna degradación del rendimiento. Logramos este resultado al resolver dos desafíos clave: la necesidad de una mayor precisión de cuantificación a escalas superiores a 1B parámetros y la necesidad de representar explícitamente las características atípicas dispersas pero sistemáticas de gran magnitud que arruinan la precisión de la cuantificación una vez que emergen en todas las capas del transformer a partir de escalas de 6,7B parámetros. Esta pérdida de precisión se refleja en la perplejidad de la evaluación C4 (Sección 3), así como en la precisión de disparo cero tan pronto como emergen estas características atípicas, como se muestra en la Figura 1.

[Imagen de la Figura 1: Precisión media de disparo cero del modelo OPT para los conjuntos de datos WinoGrande, HellaSwag, PIQA y LAMBADA.]

Mostramos que con la primera parte de nuestro método, la cuantificación vectorial, es posible mantener el rendimiento a escalas de hasta 2,7B parámetros. Para la cuantificación vectorial, la multiplicación de matrices puede verse como una secuencia de productos internos independientes de vectores de fila y columna. Como tal, podemos usar una constante de normalización de cuantificación separada para cada producto interno para mejorar la precisión de la cuantificación. Podemos recuperar la salida de la multiplicación de matrices desnormalizando por el producto externo de las constantes de normalización de columna y fila antes de realizar la siguiente operación.

Para escalar más allá de los 6,7B parámetros sin degradación del rendimiento, es fundamental comprender la aparición de valores atípicos extremos en las dimensiones de las características de los estados ocultos durante la inferencia. Con este fin, proporcionamos un nuevo análisis descriptivo que muestra que las características grandes con magnitudes hasta 20 veces mayores que en otras dimensiones aparecen primero en aproximadamente el 25% de todas las capas del transformer y luego se extienden gradualmente a otras capas a medida que escalamos los transformers a 6B parámetros. Alrededor de los 6,7B parámetros, se produce un cambio de fase y todas las capas del transformer y el 75% de todas las dimensiones de la secuencia se ven afectadas por características de magnitud extrema. Estos valores atípicos son altamente sistemáticos: a escala de 6,7B, se producen 150.000 valores atípicos por secuencia, pero se concentran en solo 6 dimensiones de características en todo el transformer. Establecer estas dimensiones de características atípicas en cero disminuye la masa de probabilidad softmax de atención superior-1 en más del 20% y degrada la perplejidad de validación en un 600-1000%, a pesar de que solo representan alrededor del 0,1% de todas las características de entrada. Por el contrario, eliminar la misma cantidad de características aleatorias disminuye la probabilidad en un máximo del 0,3% y degrada la perplejidad en aproximadamente un 0,1%.

Para admitir una cuantificación eficaz con estos valores atípicos extremos, desarrollamos la descomposición de precisión mixta, la segunda parte de nuestro método. Realizamos la multiplicación de matrices de 16 bits para las dimensiones de características atípicas y la multiplicación de matrices de 8 bits para el otro 99,9% de las dimensiones. Llamamos a la combinación de cuantificación vectorial y descomposición de precisión mixta, LLM.int8(). Mostramos que al usar LLM.int8(), podemos realizar inferencias en LLM con hasta 175B parámetros sin ninguna degradación del rendimiento. Nuestro método no solo proporciona nuevos conocimientos sobre los efectos de estos valores atípicos en el rendimiento del modelo, sino que también permite, por primera vez, utilizar modelos muy grandes, por ejemplo, OPT-175B/BLOOM, en un solo servidor con GPU de consumo. Si bien nuestro trabajo se centra en hacer que los grandes modelos lingüísticos sean accesibles sin degradación, también mostramos en el Apéndice D que mantenemos el rendimiento del tiempo de ejecución de inferencia de un extremo a otro para modelos grandes, como BLOOM-176B y proporcionamos mejoras modestas en la velocidad de multiplicación de matrices para modelos GPT-3 de tamaño 6,7B parámetros o más. Abrimos el código de nuestro software y lanzamos una integración de Hugging Face Transformers (Wolf et al., 2019) que hace que nuestro método esté disponible para todos los modelos alojados de Hugging Face que tienen capas lineales.

## 2. Antecedentes

En este trabajo, llevamos las técnicas de cuantificación push hasta su punto de ruptura al escalar modelos transformer. Estamos interesados en dos preguntas: ¿a qué escala y por qué fallan las técnicas de cuantificación y cómo se relaciona esto con la precisión de la cuantificación? Para responder a estas preguntas, estudiamos la cuantificación asimétrica de alta precisión (cuantificación de punto cero) y la cuantificación simétrica (cuantificación máxima absoluta). Si bien la cuantificación de punto cero ofrece una alta precisión al usar el rango de bits completo del tipo de datos, rara vez se usa debido a restricciones prácticas. La cuantificación máxima absoluta es la técnica más utilizada.

### 2.1 Tipos de datos de 8 bits y cuantificación

La cuantificación Absmax escala las entradas al rango de 8 bits [-127, 127] multiplicando por sxf16, que es 127 dividido por el máximo absoluto de todo el tensor. Esto es equivalente a dividir por la norma infinita y multiplicar por 127. Como tal, para una matriz de entrada FP16 Xf16 ∈ Rs×h, la cuantificación absmax Int8 viene dada por:

Xi8 = ⌊ 127 · Xf16 / max ij (|Xf16ij |) ⌉ = ⌊ 127 / ‖Xf16‖∞ Xf16 ⌉ = ⌊ sxf16 Xf16 ⌉ ,

donde be indica redondeo al entero más cercano.

La cuantificación de punto cero desplaza la distribución de entrada al rango completo [-127, 127] escalando con el rango dinámico normalizado ndx y luego desplazando por el punto cero zpx. Con esta transformación afín, cualquier tensor de entrada utilizará todos los bits del tipo de datos, lo que reducirá el error de cuantificación para distribuciones asimétricas. Por ejemplo, para salidas ReLU, en la cuantificación absmax no se utilizan todos los valores en [-127, 0), mientras que en la cuantificación de punto cero se utiliza el rango completo [-127, 127]. La cuantificación de punto cero viene dada por las siguientes ecuaciones:

ndxf16 = 2 · 127 / (max ij (Xij f16) - min ij (Xij f16)) (1)

zpxi16 = ⌊ Xf16 · min ij (Xij f16) ⌉ (2)

Xi8 = ⌊ ndxf16 Xf16 ⌉ (3)

Para usar la cuantificación de punto cero en una operación, alimentamos tanto el tensor Xi8 como el punto cero zpxi16 en una instrucción especial que suma zpxi16 a cada elemento de Xi8 antes de realizar una operación entera de 16 bits. Por ejemplo, para multiplicar dos números cuantificados de punto cero Ai8 y Bi8 junto con sus puntos cero zpai16 y zpbi16, calculamos:

Ci32 = multiplyi16(Azpai16, Bzpbi16) = (Ai8 + zpai16)(Bi8 + zpbi16) (4)

donde se requiere desenrollar si la instrucción multiplyi16 no está disponible, como en GPU o TPU:

Ci32 = Ai8Bi8 + Ai8zpbi16 + Bi8zpai16 + zpai16zpbi16, (5)

donde Ai8Bi8 se calcula con precisión Int8 mientras que el resto se calcula con precisión Int16/32. Como tal, la cuantificación de punto cero puede ser lenta si la instrucción multiplyi16 no está disponible. En ambos casos, las salidas se acumulan como un entero de 32 bits Ci32. Para des cuantificar Ci32, dividimos por las constantes de escala ndaf16 y ndbf16.

Multiplicación de matrices Int8 con entradas y salidas flotantes de 16 bits. Dados los estados ocultos Xf16 ∈ Rs×h y los pesos Wf16 ∈ Rh×o con dimensión de secuencia s, dimensión de característica h y dimensión de salida o, realizamos la multiplicación de matrices de 8 bits con entradas y salidas de 16 bits de la siguiente manera:

Xf16Wf16 = Cf16 ≈ 1 / (cxf16 cwf16) Ci32 = Sf16 · Ci32 ≈ Sf16 · Ai8Bi8 = Sf16 · Q(Af16) Q(Bf16), (6)

Donde Q(·) es cuantificación absmax o de punto cero y cxf16 y cwf16 son las constantes de escala tensoriales respectivas sx y sw para absmax o ndx y ndw para cuantificación de punto cero.

## 3 Multiplicación de matrices Int8 a escala

El principal desafío con los métodos de cuantificación que usan una sola constante de escala por tensor es que un solo valor atípico puede reducir la precisión de la cuantificación de todos los demás valores. Como tal, es deseable tener múltiples constantes de escala por tensor, como constantes por bloques (Dettmers et al., 2022), de modo que el efecto de esos valores atípicos se limite a cada bloque. Mejoramos una de las formas más comunes de cuantificación por bloques, la cuantificación por filas (Khudia et al., 2021), mediante el uso de la cuantificación vectorial, como se describe con más detalle a continuación.

Para manejar las características atípicas de gran magnitud que ocurren en todas las capas del transformer más allá de la escala de 6,7B, la cuantificación vectorial ya no es suficiente. Para ello, desarrollamos la descomposición de precisión mixta, donde el pequeño número de dimensiones de características de gran magnitud (≈ 0,1%) se representan con una precisión de 16 bits, mientras que el otro 99,9% de los valores se multiplican en 8 bits. Dado que la mayoría de las entradas todavía se representan con baja precisión, conservamos aproximadamente un 50% de reducción de memoria en comparación con los 16 bits. Por ejemplo, para BLOOM-176B, reducimos la huella de memoria del modelo en 1,96 veces.

La cuantificación vectorial y la descomposición de precisión mixta se muestran en la Figura 2. El método LLM.int8() es la combinación de cuantificación vectorial absmax y descomposición de precisión mixta.

[Imagen de la Figura 2: Esquema de LLM.int8().]

### 3.1 Cuantificación vectorial

Una forma de aumentar el número de constantes de escala para la multiplicación de matrices es ver la multiplicación de matrices como una secuencia de productos internos independientes. Dados los estados ocultos Xf16 ∈ Rb×h y la matriz de pesos Wf16 ∈ Rh×o, podemos asignar una constante de escala diferente cxf16 a cada fila de Xf16 y cw a cada columna de Wf16. Para des cuantificar, desnormalizamos cada resultado del producto interno por 1 / (cxf16 cwf16). Para toda la multiplicación de matrices, esto es equivalente a la desnormalización por el producto externo cxf16 ⊗ cwf16, donde cx ∈ Rs y cw ∈ Ro. Como tal, la ecuación completa para la multiplicación de matrices con constantes de fila y columna viene dada por:

Cf16 ≈ 1 / (cxf16 ⊗ cwf16) Ci32 = S · Ci32 = S · Ai8Bi8 = S · Q(Af16) Q(Bf16), (7)

que denominamos cuantificación vectorial para la multiplicación de matrices.

### 3.2 El núcleo de LLM.int8(): Descomposición de precisión mixta

En nuestro análisis, demostramos que un problema significativo para los transformers de 8 bits a escala de miles de millones es que tienen características (columnas) de gran magnitud, que son importantes para el rendimiento del transformer y requieren una cuantificación de alta precisión. Sin embargo, la cuantificación vectorial, nuestra mejor técnica de cuantificación, cuantifica cada fila para el estado oculto, lo que no es efectivo para las características atípicas. Afortunadamente, vemos que estas características atípicas son increíblemente escasas y sistemáticas en la práctica, constituyendo solo alrededor del 0,1% de todas las dimensiones de las características, lo que nos permite desarrollar una nueva técnica de descomposición que se centra en la multiplicación de alta precisión para estas dimensiones particulares.

Encontramos que dada la matriz de entrada Xf16 ∈ Rs×h, estos valores atípicos ocurren sistemáticamente para casi todas las dimensiones de secuencia s pero están limitados a dimensiones de características/ocultas h específicas. Como tal, proponemos la descomposición de precisión mixta para la multiplicación de matrices donde separamos las dimensiones de características atípicas en el conjunto O = {i | i ∈ Z, 0 ≤ i ≤ h}, que contiene todas las dimensiones de h que tienen al menos un valor atípico con una magnitud mayor que el umbral α. En nuestro trabajo, encontramos que α = 6.0 es suficiente para reducir la degradación del rendimiento del transformer cerca de cero. Usando la notación de Einstein donde todos los índices son superíndices, dada la matriz de pesos Wf16 ∈ Rh×o, la descomposición de precisión mixta para la multiplicación de matrices se define de la siguiente manera:

Cf16 ≈ ∑ h∈O Xh f16Wh f16 + Sf16 · ∑ h6∈O Xh i8Wh i8 (8)

donde Sf16 es el término de desnormalización para las matrices de entrada y peso Int8 Xi8 y Wi8.

Esta separación en 8 bits y 16 bits permite la multiplicación de alta precisión de valores atípicos mientras se utiliza la multiplicación de matrices con memoria eficiente con pesos de 8 bits de más del 99,9% de los valores. Dado que el número de dimensiones de características atípicas no es superior a 7 (|O| ≤ 7) para transformers de hasta 13B parámetros, esta operación de descomposición solo consume aproximadamente un 0,1% de memoria adicional.

### 3.3 Configuración experimental

Medimos la robustez de los métodos de cuantificación a medida que escalamos el tamaño de varios modelos lingüísticos preentrenados disponibles públicamente hasta 175B parámetros. La pregunta clave no es qué tan bien funciona un método de cuantificación para un modelo en particular, sino la tendencia de cómo funciona dicho método a medida que escalamos.

Usamos dos configuraciones para nuestros experimentos. Una se basa en la perplejidad del modelado lingüístico, que encontramos que es una medida muy sólida que es muy sensible a la degradación de la cuantificación. Usamos esta configuración para comparar diferentes líneas de base de cuantificación. Además, evaluamos la degradación de la precisión de disparo cero en los modelos OPT para una gama de diferentes tareas finales, donde comparamos nuestros métodos con una línea de base de 16 bits.

Para la configuración de modelado lingüístico, usamos transformers autorregresivos densos preentrenados en fairseq (Ott et al., 2019) que van desde 125 millones a 13 mil millones de parámetros. Estos transformers se han preentrenado en Libros (Zhu et al., 2015), Wikipedia en inglés, CC-News (Nagel, 2016), OpenWebText (Gokaslan y Cohen, 2019), CC-Stories (Trinh y Le, 2018) e inglés CC100 (Wenzek et al., 2020). Para obtener más información sobre cómo se entrenan estos modelos preentrenados, consulte Artetxe et al. (2021).

Para evaluar la degradación del modelado lingüístico después de la cuantificación Int8, evaluamos la perplejidad del transformer de 8 bits en los datos de validación del corpus C4 (Raffel et al., 2019), que es un subconjunto del corpus Common Crawl. Usamos GPU NVIDIA A40 para esta evaluación.

Para medir la degradación en el rendimiento de disparo cero, usamos modelos OPT (Zhang et al., 2022) y evaluamos estos modelos en el arnés de evaluación del modelo de lenguaje EleutherAI (Gao et al., 2021).

### 3.4 Resultados principales

Los principales resultados de la perplejidad del modelado lingüístico en los modelos Int8 de 125 millones a 13 mil millones evaluados en el corpus C4 se pueden ver en la Tabla 1. Vemos que la cuantificación absmax, por filas y de punto cero falla a medida que escalamos, donde los modelos después de 2,7 mil millones de parámetros funcionan peor que los modelos más pequeños. En cambio, la cuantificación de punto cero falla más allá de los 6,7B parámetros. Nuestro método, LLM.int8(), es el único método que preserva la perplejidad. Como tal, LLM.int8() es el único método con una tendencia de escala favorable.

Tabla 1: Perplejidades de validación C4 de métodos de cuantificación para diferentes tamaños de transformer que van desde 125 millones a 13 mil millones de parámetros. Vemos que la cuantificación absmax, por filas, de punto cero y vectorial conduce a una degradación significativa del rendimiento a medida que escalamos, particularmente en la marca de 13B donde la perplejidad de 13B de 8 bits es peor que la perplejidad de 6,7B de 8 bits. Si usamos LLM.int8(), recuperamos la perplejidad total a medida que escalamos. La cuantificación de punto cero muestra una ventaja debido a la cuantificación asimétrica, pero ya no es ventajosa cuando se usa con descomposición de precisión mixta.

@Parámetros @ 125M @ 1.3B @ 2.7B @ 6.7B @ 13B
------- @ -------- @ -------- @ -------- @ -------- @ --------
Float de 32 bits @ 25,65 @ 15,91 @ 14,43 @ 13,30 @ 12,45
Int8 absmax @ 87,76 @ 16,55 @ 15,11 @ 14,59 @ 19,08
Int8 punto cero @ 56,66 @ 16,24 @ 14,76 @ 13,49 @ 13,94
Int8 absmax por filas @ 30,93 @ 17,08 @ 15,24 @ 14,13 @ 16,49
Int8 absmax vectorial @ 35,84 @ 16,82 @ 14,98 @ 14,13 @ 16,48
Int8 punto cero vectorial @ 25,72 @ 15,94 @ 14,36 @ 13,38 @ 13,47
Int8 absmax por filas + descomposición @ 30,76 @ 16,19 @ 14,65 @ 13,25 @ 12,46
Absmax LLM.int8() (vectorial + descomposición) @ 25,83 @ 15,93 @ 14,44 @ 13,24 @ 12,45
Punto cero LLM.int8() (vectorial + descomposición) @ 25,69 @ 15,92 @ 14,43 @ 13,24 @ 12,45

Cuando observamos las tendencias de escala del rendimiento de disparo cero de los modelos OPT en el arnés de evaluación del modelo de lenguaje EleutherAI en la Figura 1, vemos que LLM.int8() mantiene el rendimiento completo de 16 bits a medida que escalamos de 125 millones a 175 mil millones de parámetros. Por otro lado, la línea de base, la cuantificación vectorial absmax de 8 bits, escala mal y degenera en un rendimiento aleatorio.

Aunque nuestro enfoque principal está en ahorrar memoria, también medimos el tiempo de ejecución de LLM.int8(). La sobrecarga de cuantificación puede ralentizar la inferencia para modelos con menos de 6,7B parámetros, en comparación con una línea de base FP16. Sin embargo, los modelos de 6,7B parámetros o menos caben en la mayoría de las GPU y la cuantificación es menos necesaria en la práctica. Los tiempos de ejecución de LLM.int8() son aproximadamente dos veces más rápidos para multiplicaciones de matrices grandes equivalentes a las de los modelos de 175B. El Apéndice D proporciona más detalles sobre estos experimentos.

## 4 Características emergentes de gran magnitud en Transformers a escala

A medida que escalamos los transformers, surgen características atípicas con grandes magnitudes que afectan fuertemente a todas las capas y su cuantificación. Dado un estado oculto X ∈ Rs×h donde s es la dimensión de la secuencia/token y h la dimensión oculta/característica, definimos una característica como una dimensión particular hi. Nuestro análisis analiza una dimensión de característica particular hi en todas las capas de un transformer dado.

Encontramos que las características atípicas afectan fuertemente la atención y el rendimiento predictivo general de los transformers. Si bien existen hasta 150 000 valores atípicos por secuencia de 2048 tokens para un modelo de 13B, estas características atípicas son altamente sistemáticas y solo representan como máximo 7 dimensiones de características hi únicas. Las ideas de este análisis fueron fundamentales para desarrollar la descomposición de precisión mixta. Nuestro análisis explica las ventajas de la cuantificación de punto cero y por qué desaparecen con el uso de la descomposición de precisión mixta y el rendimiento de la cuantificación de modelos pequeños frente a grandes.

### 4.1 Encontrar características atípicas

La dificultad con el análisis cuantitativo de los fenómenos emergentes es doble. Nuestro objetivo es seleccionar un pequeño subconjunto de características para el análisis de modo que los resultados sean inteligibles y no demasiado complejos, al tiempo que se capturan patrones probabilísticos y estructurados importantes. Usamos un enfoque empírico para encontrar estas restricciones. Definimos valores atípicos de acuerdo con los siguientes criterios: la magnitud de la característica es al menos 6.0, afecta al menos al 25% de las capas y afecta al menos al 6% de las dimensiones de la secuencia.

Más formalmente, dado un transformer con L capas y estado oculto Xl ∈ Rs×h, l = 0...L donde s es la dimensión de la secuencia y h la dimensión de la característica, definimos una característica como una dimensión particular hi en cualquiera de los estados ocultos Xli. Rastreamos las dimensiones hi, 0 ≤ i ≤ h, que tienen al menos un valor con una magnitud de α ≥ 6 y solo recopilamos estadísticas si estos valores atípicos ocurren en la misma dimensión de característica hi en al menos el 25% de las capas del transformer 0...L y aparecen en al menos el 6% de todas las dimensiones de secuencia s en todos los estados ocultos Xl. Dado que los valores atípicos de características solo ocurren en la proyección de atención (clave/consulta/valor/salida) y en la capa de expansión de la red de alimentación hacia adelante (primera subcapa), ignoramos la función de atención y la capa de contracción FFN (segunda subcapa) para este análisis.

Nuestro razonamiento para estos umbrales es el siguiente. Encontramos que al usar la descomposición de precisión mixta, la degradación de la perplejidad se detiene si tratamos cualquier característica con una magnitud de 6 o mayor como una característica atípica. Para la cantidad de capas afectadas por valores atípicos, encontramos que las características atípicas son sistemáticas en modelos grandes: ocurren en la mayoría de las capas o no ocurren en absoluto. Por otro lado, son probabilísticos en modelos pequeños: ocurren a veces en algunas capas para cada secuencia. Como tal, establecemos nuestro umbral para cuántas capas deben verse afectadas para detectar una característica atípica de tal manera que se limite la detección a un solo valor atípico en nuestro modelo más pequeño con 125 millones de parámetros. Este umbral corresponde a que al menos el 25% de las capas del transformer se ven afectadas por un valor atípico en la misma dimensión de característica. El segundo valor atípico más común ocurre en una sola capa (2% de las capas), lo que indica que este es un umbral razonable. Usamos el mismo procedimiento para encontrar el umbral de cuántas dimensiones de secuencia se ven afectadas por las características atípicas en nuestro modelo de 125 millones: los valores atípicos ocurren en al menos el 6% de las dimensiones de secuencia.

Probamos modelos hasta una escala de 13B parámetros. Para asegurarnos de que los fenómenos observados no se deban a errores en el software, evaluamos transformers que se entrenaron en tres marcos de software diferentes. Evaluamos cuatro modelos GPT-2 que utilizan software OpenAI, cinco modelos Meta AI que utilizan Fairseq (Ott et al., 2019) y un modelo EleutherAI GPT-J que utiliza Tensorflow-Mesh (Shazeer et al., 2018). Se pueden encontrar más detalles en el Apéndice C. También realizamos nuestro análisis en dos marcos de software de inferencia diferentes: Fairseq y Hugging Face Transformers (Wolf et al., 2019).

### 4.2 Medición del efecto de las características atípicas

Para demostrar que las características atípicas son esenciales para la atención y el rendimiento predictivo, establecemos las características atípicas en cero antes de alimentar los estados ocultos Xl en las capas de proyección de atención y luego comparamos la probabilidad softmax superior-1 con la probabilidad softmax regular con valores atípicos. Hacemos esto para todas las capas de forma independiente, lo que significa que reenviamos los valores de probabilidades softmax regulares para evitar errores en cascada y aislar los efectos debidos a las características atípicas. También informamos la degradación de la perplejidad si eliminamos la dimensión de la característica atípica (estableciéndola en cero) y propagamos estos estados ocultos alterados a través del transformer. Como control, aplicamos el mismo procedimiento para dimensiones de características aleatorias no atípicas y observamos la degradación de la atención y la perplejidad.

Nuestros principales resultados cuantitativos se pueden resumir en cuatro puntos principales.

[Imagen de la Figura 3: Porcentaje de capas y todas las dimensiones de secuencia afectadas por características atípicas de gran magnitud en todo el transformer por (a) tamaño del modelo o (b) perplejidad C4.]

[Imagen de la Figura 4: La magnitud media de la característica atípica más grande en (a) indica un cambio repentino en el tamaño del valor atípico.]

(1) Cuando se mide por el número de parámetros, la aparición de características de gran magnitud en todas las capas de un transformer ocurre repentinamente entre 6B y 6.7B parámetros, como se muestra en la Figura 3a, a medida que el porcentaje de capas afectadas aumenta del 65% al 100%. El número de dimensiones de secuencia afectadas aumenta rápidamente del 35% al 75%. Este cambio repentino coincide con el punto en el que la cuantificación comienza a fallar.

(2) Alternativamente, cuando se mide por perplejidad, la aparición de características de gran magnitud en todas las capas del transformer puede verse como emergiendo suavemente de acuerdo con una función exponencial de perplejidad decreciente, como se ve en la Figura 3b. Esto indica que no hay nada repentino en la aparición y que podríamos detectar características emergentes antes de que ocurra un cambio de fase al estudiar tendencias exponenciales en modelos más pequeños. Esto también sugiere que la aparición no se trata solo del tamaño del modelo, sino de la perplejidad, que está relacionada con múltiples factores adicionales, como la cantidad de datos de entrenamiento utilizados y la calidad de los datos (Hoffmann et al., 2022; Henighan et al., 2020).

(3) La magnitud media de la característica atípica aumenta rápidamente una vez que las características atípicas ocurren en todas las capas del transformer, como se muestra en la Figura 4a. La gran magnitud de las características atípicas y su distribución asimétrica interrumpen la precisión de la cuantificación Int8. Esta es la razón principal por la que los métodos de cuantificación fallan a partir de la escala de 6,7B: el rango de la distribución de cuantificación es demasiado grande, por lo que la mayoría de los contenedores de cuantificación están vacíos y los valores pequeños de cuantificación se cuantifican a cero, esencialmente extinguiendo la información. Tenemos la hipótesis de que, además de la inferencia Int8, el entrenamiento regular de coma flotante de 16 bits se vuelve inestable debido a valores atípicos más allá de la escala de 6,7B: es fácil superar el valor máximo de 16 bits 65535 por casualidad si se multiplica por vectores llenos de valores de magnitud 60.

(4) El número de características atípicas aumenta estrictamente monótonamente con respecto a la disminución de la perplejidad C4 como se muestra en la Figura 4b, mientras que una relación con el tamaño del modelo no es monótona. Esto indica que la perplejidad del modelo en lugar del mero tamaño del modelo determina el cambio de fase. Tenemos la hipótesis de que el tamaño del modelo es solo una covariable importante entre muchas que se requieren para alcanzar la aparición.

Estas características atípicas son altamente sistemáticas después de que se produjo el cambio de fase. Por ejemplo, para un transformer de 6,7B con una longitud de secuencia de 2048, encontramos alrededor de 150 000 características atípicas por secuencia para todo el transformer, pero estas características se concentran en solo 6 dimensiones ocultas diferentes.

Estos valores atípicos son fundamentales para el rendimiento del transformer. Si se eliminan los valores atípicos, la probabilidad softmax superior-1 media se reduce de aproximadamente un 40% a aproximadamente un 20%, y la perplejidad de validación aumenta en un 600-1000% aunque haya como máximo 7 dimensiones de características atípicas. Cuando eliminamos 7 dimensiones de características aleatorias, la probabilidad superior-1 disminuye solo entre 0.02-0.3% y la perplejidad aumenta en 0.1%. Esto resalta la naturaleza crítica de estas dimensiones de características. La precisión de la cuantificación para estas características atípicas es primordial, ya que incluso pequeños errores afectan en gran medida el rendimiento del modelo.

### 4.3 Interpretación del rendimiento de la cuantificación

Nuestro análisis muestra que los valores atípicos en dimensiones de características particulares son omnipresentes en los transformers grandes y estas dimensiones de características son fundamentales para el rendimiento del transformer. Dado que la cuantificación por filas y vectorial escala cada dimensión de secuencia de estado oculto s (filas) y debido a que los valores atípicos ocurren en la dimensión de característica h (columnas), ambos métodos no pueden manejar estos valores atípicos de manera efectiva. Es por eso que los métodos de cuantificación absmax fallan rápidamente después de la aparición.

Sin embargo, casi todos los valores atípicos tienen una distribución asimétrica estricta: son únicamente positivos o negativos (consulte el Apéndice C). Esto hace que la cuantificación de punto cero sea particularmente efectiva para estos valores atípicos, ya que la cuantificación de punto cero es un método de cuantificación asimétrico que escala estos valores atípicos en el rango completo [-127, 127]. Esto explica el sólido rendimiento en nuestro punto de referencia de escala de cuantificación en la Tabla 1. Sin embargo, a escala de 13B, incluso la cuantificación de punto cero falla debido a los errores de cuantificación acumulados y al rápido crecimiento de las magnitudes de los valores atípicos, como se ve en la Figura 4a.

Si usamos nuestro método LLM.int8() completo con descomposición de precisión mixta, la ventaja de la cuantificación de punto cero desaparece, lo que indica que las características descompuestas restantes son simétricas. Sin embargo, vectorial todavía tiene una ventaja sobre la cuantificación por filas, lo que indica que se necesita la precisión de cuantificación mejorada de los pesos del modelo para mantener el rendimiento predictivo de precisión total.

## 5 Trabajo Relacionado

Existe trabajo estrechamente relacionado con los tipos de datos de cuantización y la cuantización de transformadores, como se describe a continuación. El Apéndice B proporciona trabajo relacionado adicional sobre la cuantización de redes convolucionales.

Tipos de Datos de 8 bits.

Nuestro trabajo estudia las técnicas de cuantización que rodean al tipo de datos Int8, ya que actualmente es el único tipo de datos de 8 bits compatible con las GPU. Otros tipos de datos comunes son los de coma fija o coma flotante de 8 bits (FP8). Estos tipos de datos suelen tener un bit de signo y diferentes combinaciones de bits de exponente y fracción. Por ejemplo, una variante común de este tipo de datos tiene 5 bits para el exponente y 2 bits para la fracción (Wang et al., 2018; Sun et al., 2019; Cambier et al., 2020; Mellempudi et al., 2019) y utiliza o bien ninguna constante de escala o bien una escala de punto cero. Estos tipos de datos tienen grandes errores para valores de gran magnitud, ya que sólo tienen 2 bits para la fracción, pero proporcionan una gran precisión para valores de pequeña magnitud. Jin et al. (2022) proporcionan un excelente análisis de cuándo ciertas anchuras de bits de exponente/fracción de coma fija son óptimas para entradas con una desviación estándar particular. Creemos que los tipos de datos FP8 ofrecen un rendimiento superior en comparación con el tipo de datos Int8, pero actualmente ni las GPU ni las TPU admiten este tipo de datos.

Características Atípicas en Modelos de Lenguaje.

Las características atípicas de gran magnitud en los modelos de lenguaje se han estudiado con anterioridad (Timkey y van Schijndel, 2021; Bondarenko et al., 2021; Wei et al., 2022; Luo et al., 2021). Trabajos anteriores demostraron la relación teórica entre la aparición de valores atípicos en los transformadores y cómo se relaciona con la normalización por capas y la distribución de la frecuencia de tokens (Gao et al., 2019). Del mismo modo, Kovaleva et al. (2021) atribuyen la aparición de valores atípicos en la familia de modelos BERT a LayerNorm, y Puccetti et al. (2022) muestran empíricamente que la aparición de valores atípicos está relacionada con la frecuencia de los tokens en la distribución de entrenamiento. Nosotros ampliamos este trabajo mostrando cómo la escala de los modelos autorregresivos se relaciona con las propiedades emergentes de estas características atípicas, y mostrando cómo modelar adecuadamente los valores atípicos es crítico para una cuantización efectiva.

Cuantización de Transformadores a Escala de Multimillones.

Hay dos métodos que se desarrollaron paralelamente al nuestro: nuQmm (Park et al., 2022) y ZeroQuant (Yao et al., 2022). Ambos utilizan el mismo esquema de cuantización: cuantización group-wise, que tiene una granularidad de la constante de normalización de la cuantización aún más fina que la cuantización vector-wise. Este esquema ofrece una mayor precisión de cuantización, pero también requiere kernels CUDA personalizados. Tanto nuQmm como ZeroQuant pretenden acelerar la inferencia y reducir la huella de memoria, mientras que nosotros nos centramos en preservar el rendimiento predictivo bajo una huella de memoria de 8 bits. Los modelos más grandes que evalúan nuQmm y ZeroQuant son transformadores de 2,7B y 20B parámetros, respectivamente. ZeroQuant consigue un rendimiento sin degradación para la cuantización de 8 bits de un modelo de 20B. Nosotros demostramos que nuestro método permite la cuantización sin degradación de modelos de hasta 176B parámetros. Tanto nuQmm como ZeroQuant sugieren que una granularidad de cuantización más fina puede ser un medio eficaz para cuantizar modelos grandes. Estos métodos son complementarios con LLM.int8(). Otro trabajo paralelo es GLM-130B, que utiliza las ideas de nuestro trabajo para conseguir una cuantización de 8 bits sin degradación (Zeng et al., 2022). GLM-130B realiza una multiplicación de matrices con precisión total de 16 bits con un almacenamiento de pesos de 8 bits.

## 6 Discusión y Limitaciones

Hemos demostrado por primera vez que los transformadores de parámetros multimillonarios pueden cuantificarse a Int8 y utilizarse inmediatamente para la inferencia sin degradación del rendimiento. Lo conseguimos utilizando nuestras ideas del análisis de características emergentes de gran magnitud a escala para desarrollar una descomposición de precisión mixta para aislar las características atípicas en una multiplicación de matrices separada de 16 bits. En conjunción con la cuantización vector-wise que da como resultado nuestro método, LLM.int8(), que mostramos empíricamente que puede recuperar el rendimiento de inferencia completo de modelos con hasta 175B parámetros.

La principal limitación de nuestro trabajo es que nuestro análisis se basa únicamente en el tipo de datos Int8, y no estudiamos los tipos de datos de coma flotante de 8 bits (FP8). Dado que las GPU y TPU actuales no admiten este tipo de datos, creemos que es mejor dejarlo para trabajos futuros. Sin embargo, también creemos que muchas de las ideas de los tipos de datos Int8 se traducirán directamente a los tipos de datos FP8. Otra limitación es que sólo estudiamos modelos con hasta 175B parámetros. Si bien cuantificamos un modelo de 175B a Int8 sin degradación del rendimiento, es posible que surjan propiedades emergentes adicionales que perturben nuestros métodos de cuantización a escalas mayores.

Una tercera limitación es que no utilizamos la multiplicación Int8 para la función de atención. Dado que nuestro objetivo es reducir la huella de memoria y que la función de atención no utiliza ningún parámetro, no era estrictamente necesario. Sin embargo, una exploración inicial de este problema indicó que una solución requería métodos de cuantización adicionales a los aquí desarrollados, y lo dejamos para trabajo futuro.

Una última limitación es que nos centramos en la inferencia pero no estudiamos el entrenamiento o el ajuste fino. Ofrecemos un análisis inicial del ajuste fino y el entrenamiento Int8 a escala en el Apéndice E. El entrenamiento Int8 a escala requiere complejas compensaciones entre la precisión de la cuantización, la velocidad de entrenamiento y la complejidad de la ingeniería, y representa un problema muy difícil. De nuevo, lo dejamos para trabajo futuro.

## 7 Impactos Más Amplios

El principal impacto de nuestro trabajo es que permite el acceso a grandes modelos que antes no cabían en la memoria de la GPU. Esto permite la investigación y las aplicaciones que antes no eran posibles debido a la limitada memoria de la GPU, en particular para los investigadores con menos recursos. Véase la Tabla 3 para las combinaciones de modelo/GPU que ahora son accesibles sin degradación del rendimiento. Sin embargo, nuestro trabajo también permite a las organizaciones con muchos recursos y muchas GPU servir más modelos en el mismo número de GPU, lo que podría aumentar las disparidades entre las organizaciones ricas y pobres en recursos.

En particular, creemos que la publicación pública de grandes modelos preentrenados, por ejemplo, los recientes Open Pretrained Transformers (OPT) (Zhang et al., 2022), junto con nuestra nueva inferencia Int8 para el prompting zero-shot y few-shot, permitirá nuevas investigaciones para instituciones académicas que antes no eran posibles debido a limitaciones de recursos. Es probable que la accesibilidad generalizada de estos modelos a gran escala tenga efectos tanto beneficiosos como perjudiciales para la sociedad que son difíciles de predecir.

# Apéndices

## Apéndice A

### Uso de Memoria en Comparación con la Precisión de 16 bits.

La Tabla 3 compara la huella de memoria de la inferencia de 16 bits y LLM.int8() para diferentes modelos de código abierto. Podemos ver que LLM.int8() permite ejecutar los modelos de código abierto más grandes, OPT-175B y BLOOM-176B, en un único nodo equipado con GPU de calidad de consumidor.

Tabla 3: Diferentes configuraciones de hardware y qué métodos se pueden ejecutar con precisión de 16 bits frente a 8 bits. Podemos ver que nuestro método de 8 bits hace que muchos modelos sean accesibles cuando antes no lo eran, en particular OPT-175B/BLOOM.

@ Clase @ Hardware @ Memoria de la GPU @ 8 bits @ 16 bits @
@---|---|---|---|---|
@ Empresa @ 8x A100 @ 80 GB @ OPT-175B / BLOOM @ OPT-175B / BLOOM @
@ Empresa @ 8x A100 @ 40 GB @ OPT-175B / BLOOM @ OPT-66B @
@ Servidor Académico @ 8x RTX 3090 @ 24 GB @ OPT-175B / BLOOM @ OPT-66B @
@ Ordenador de Sobremesa Académico @ 4x RTX 3090 @ 24 GB @ OPT-66B @ OPT-30B @
@ Nube de Pago Colab Pro @ 15 GB @ OPT-13B @ GPT-J-6B @
@ Nube Gratuita Colab @ 12 GB @ T0/T5-11B @ GPT-2 1.3B @

## Apéndice B

### Trabajo Relacionado Adicional

#### Cuantización de Transformadores con Menos de 1.000 Millones de Parámetros.

La cuantización de transformadores se ha centrado en modelos de lenguaje enmascarados (MLM) con menos de 1.000 millones de parámetros, incluidos BERT (Devlin et al., 2018) y RoBERTa (Liu et al., 2019). Las versiones de BERT/RoBERTa de 8 bits incluyen Q8BERT (Zafrir et al., 2019), QBERT (Shen et al., 2020), cuantización de productos con ruido de cuantización (Fan et al., 2020), TernaryBERT (Zhang et al., 2020) y BinaryBERT (Bai et al., 2021). El trabajo de Zhao et al. (2021) realiza tanto la cuantización como la poda. Todos estos modelos requieren un ajuste fino con conocimiento de la cuantización o una cuantización posterior al entrenamiento para que el modelo pueda utilizarse con baja precisión. En contraste con nuestros métodos, el modelo puede utilizarse directamente sin degradación del rendimiento.

Si se considera la multiplicación de matrices como una convolución 1x1, la cuantización vector-wise equivale a la cuantización canal a canal para la convolución combinada con la cuantización por filas (Khudia et al., 2021). Para la multiplicación de matrices, esto fue utilizado por Wu et al. (2020) para transformadores del tamaño de BERT (350 millones de parámetros), mientras que nosotros somos los primeros en estudiar la cuantización vector-wise para modelos autorregresivos y a gran escala. El único otro trabajo que conocemos que cuantifica transformadores distintos de BERT es el de Chen et al. (2020), que utiliza la cuantización posterior al entrenamiento con cuantización de punto cero en la pasada hacia delante y cuantización de punto cero por filas en la pasada hacia atrás. Sin embargo, este trabajo sigue siendo para transformadores con menos de 1.000 millones de parámetros. Nosotros comparamos con la cuantización de punto cero y por filas en nuestras evaluaciones y no requerimos la cuantización posterior al entrenamiento.

#### Cuantización de Redes Convolucionales y de Baja Precisión.

Los trabajos que utilizan menos de 8 bits para los tipos de datos suelen ser para redes convolucionales (CNN) con el fin de reducir su huella de memoria y aumentar la velocidad de inferencia para dispositivos móviles, minimizando al mismo tiempo la degradación del modelo. Se han estudiado métodos para diferentes anchos de bits: métodos de 1 bit (Courbariaux y Bengio, 2016; Rastegari et al., 2016; Courbariaux et al., 2015), de 2 a 3 bits (Zhu et al., 2017; Choi et al., 2019), de 4 bits (Li et al., 2019), de más bits (Courbariaux et al., 2014), o de una cantidad variable de bits (Gong et al., 2019). Para trabajos relacionados adicionales, véase la revisión de Qin et al. (2020). Si bien creemos que es posible un ancho inferior a 8 bits con cierta degradación del rendimiento para los transformadores a escala de miles de millones, nosotros nos centramos en los transformadores de 8 bits que no degradan el rendimiento y que pueden beneficiarse de las GPU de uso común que aceleran la inferencia a través de los núcleos tensoriales Int8.

Otra línea de trabajo que se centra en la cuantización de redes convolucionales es la de aprender ajustes en el procedimiento de cuantización para mejorar los errores de cuantización. Por ejemplo, utilizando información Hessiana (Dong et al., 2019), cuantización del tamaño del paso (Esser et al., 2019), cuantización suave (Gong et al., 2019), precisión mixta mediante optimización por programación lineal (Yao et al., 2021) y otros métodos de cuantización aprendidos (Zhang et al., 2018; Gholami et al., 2021).

## Apéndice C

### Datos Detallados de Características Atípicas.

La Tabla 4 proporciona datos tabulados de nuestro análisis de características atípicas. Proporcionamos los cuartiles del valor atípico más común en cada transformador y el número de valores atípicos que son unilaterales, es decir, que tienen distribuciones asimétricas que no cruzan el cero.

Tabla 4: Estadísticas resumidas de valores atípicos con una magnitud de al menos 6 que ocurren en al menos el 25% de todas las capas y al menos el 6% de todas las dimensiones de secuencia. Podemos ver que cuanto menor es la perplejidad de validación de C4, más valores atípicos están presentes. Los valores atípicos suelen ser unilaterales, y sus cuartiles con rango máximo muestran que la magnitud del valor atípico es de 3 a 20 veces mayor que la mayor magnitud de otras dimensiones de características, que suelen tener un rango de [-3,5, 3,5]. Con el aumento de la escala, los valores atípicos son cada vez más comunes en todas las capas del transformador, y ocurren en casi todas las dimensiones de secuencia. Se produce una transición de fase a 6,7B parámetros cuando el mismo valor atípico ocurre en todas las capas en la misma dimensión de característica para aproximadamente el 75% de todas las dimensiones de secuencia (SDim). A pesar de que sólo representan alrededor del 0,1% de todas las características, los valores atípicos son esenciales para las grandes probabilidades softmax. La probabilidad media softmax top-1 se reduce aproximadamente un 20% si se eliminan los valores atípicos. Dado que los valores atípicos tienen distribuciones mayoritariamente asimétricas a través de la dimensión de secuencia s, estas dimensiones de valores atípicos interrumpen la cuantización absmax simétrica y favorecen la cuantización de punto cero asimétrica. Esto explica los resultados de nuestro análisis de perplejidad de validación. Estas observaciones parecen ser universales, ya que se producen en modelos entrenados en diferentes marcos de software (fairseq, OpenAI, Tensorflow-mesh), y se producen en diferentes marcos de inferencia (fairseq, Hugging Face Transformers). Estos valores atípicos también parecen robustos a ligeras variaciones en la arquitectura del transformador (incrustaciones rotativas, norma de incrustación, escalado residual, diferentes inicializaciones).

@ Frecuencia de Valores Atípicos @ Probabilidad Softmax Top-1 @
@ Modelo @ PPL↓ @ Params @ Cuenta @ Unilateral @ Capas @ SDims @ Cuartiles @ Con Valor Atípico @ Sin Valor Atípico @
@---|---|---|---|---|---|---|---|---|---|
@ GPT2 @ 33.5 @ 117M @ 1 @ 1 @ 25% @ 6% @ (-8, -7, -6) @ 45% @ 19% @
@ GPT2 @ 26.0 @ 345M @ 2 @ 1 @ 29% @ 18% @ (6, 7, 8) @ 45% @ 19% @
@ FSEQ @ 25.7 @ 125M @ 2 @ 2 @ 25% @ 22% @ (-40, -23, -11) @ 32% @ 24% @
@ GPT2 @ 22.6 @ 762M @ 2 @ 0 @ 31% @ 16% @ (-9, -6, 9) @ 41% @ 18% @
@ GPT2 @ 21.0 @ 1.5B @ 2 @ 1 @ 41% @ 35% @ (-11, -9, -7) @ 41% @ 25% @
@ FSEQ @ 15.9 @ 1.3B @ 4 @ 3 @ 64% @ 47% @ (-33, -21, -11) @ 39% @ 15% @
@ FSEQ @ 14.4 @ 2.7B @ 5 @ 5 @ 52% @ 18% @ (-25, -16, -9) @ 45% @ 13% @
@ GPT-J @ 13.8 @ 6.0B @ 6 @ 6 @ 62% @ 28% @ (-21, -17, -14) @ 55% @ 10% @
@ FSEQ @ 13.3 @ 6.7B @ 6 @ 6 @ 100% @ 75% @ (-44, -40, -35) @ 35% @ 13% @
@ FSEQ @ 12.5 @ 13B @ 7 @ 6 @ 100% @ 73% @ (-63, -58, -45) @ 37% @ 16% @

## Apéndice D

Aceleraciones y Desaceleraciones de la Inferencia

### D.1 Benchmarks de Multiplicación de Matrices.

Si bien nuestro trabajo se centra en la eficiencia de la memoria para hacer que los modelos sean accesibles, los métodos Int8 también se utilizan a menudo para acelerar la inferencia. Encontramos que la sobrecarga de cuantización y descomposición es significativa, y la multiplicación de matrices Int8 en sí misma sólo proporciona una ventaja si toda la GPU está bien saturada, lo que sólo ocurre en los LLM con una dimensión de modelo de 4096 o superior.

Los benchmarks detallados de la multiplicación de matrices sin procesar y las sobrecargas de cuantización se pueden ver en la Tabla 5. Vemos que la multiplicación de matrices Int8 sin procesar en cuBLASLt comienza a ser dos veces más rápida que cuBLAS con un tamaño de modelo de 5140 (tamaño oculto 20560). Si las entradas necesitan ser cuantizadas y las salidas descuantizadas -un requisito estricto si no se hace todo el transformador en Int8- entonces las aceleraciones en comparación con 16 bits se reducen a 1,6x con un tamaño de modelo de 5140. Los modelos con un tamaño de modelo de 2560 o inferior se ralentizan. Añadir la descomposición de precisión mixta ralentiza aún más la inferencia, por lo que sólo los modelos de 13B y 175B tienen aceleraciones.

Estos números podrían mejorarse significativamente con kernels CUDA optimizados para la descomposición de precisión mixta. Sin embargo, también vemos que los kernels CUDA personalizados existentes son mucho más rápidos que cuando utilizamos kernels predeterminados de PyTorch y proporcionados por NVIDIA para la cuantización que ralentizan todas las multiplicaciones de matrices, excepto para un modelo de 175B.

Tabla 5: Aceleraciones de inferencia en comparación con la multiplicación de matrices de 16 bits para la primera capa oculta en la alimentación hacia delante de transformadores GPT-3 de diferentes tamaños. La dimensión oculta es 4 veces la dimensión del modelo. Las aceleraciones de 8 bits sin sobrecarga asumen que no se realiza ninguna cuantización o descuantización. Los números inferiores a 1,0x representan ralentizaciones. La multiplicación de matrices Int8 acelera la inferencia sólo para modelos con grandes dimensiones de modelo y ocultas.

@ Tamaño de GPT-3 @ Pequeño @ Mediano @ Grande @ XL @ 2.7B @ 6.7B @ 13B @ 175B @
@ Dimensión del modelo @ 768 @ 1024 @ 1536 @ 2048 @ 2560 @ 4096 @ 5140 @ 12288 @
@ Línea base de 16 bits FP16 @ 1.00x @ 1.00x @ 1.00x @ 1.00x @ 1.00x @ 1.00x @ 1.00x @ 1.00x @
@ Int8 sin sobrecarga @ 0.99x @ 1.08x @ 1.43x @ 1.61x @ 1.63x @ 1.67x @ 2.13x @ 2.29x @
@ Absmax PyTorch+NVIDIA @ 0.25x @ 0.24x @ 0.36x @ 0.45x @ 0.53x @ 0.70x @ 0.96x @ 1.50x @
@ Vector-wise PyTorch+NVIDIA @ 0.21x @ 0.22x @ 0.33x @ 0.41x @ 0.50x @ 0.65x @ 0.91x @ 1.50x @
@ Vector-wise @ 0.43x @ 0.49x @ 0.74x @ 0.91x @ 0.94x @ 1.18x @ 1.59x @ 2.00x @
@ LLM.int8() (vector-wise+descomp) @ 0.14x @ 0.20x @ 0.36x @ 0.51x @ 0.64x @ 0.86x @ 1.22x @ 1.81x @

### D.2 Benchmarks de Extremo a Extremo.

Además de los benchmarks de multiplicación de matrices, también probamos la velocidad de inferencia de extremo a extremo de BLOOM-176B en Hugging Face. Hugging Face utiliza una implementación optimizada con valores de atención almacenados en caché. Dado que este tipo de inferencia es distribuida y, por tanto, dependiente de la comunicación, esperamos que la aceleración y la ralentización general debidas a la inferencia Int8 sean menores, ya que una gran parte del tiempo de ejecución total de la inferencia es la sobrecarga fija de comunicación.

Comparamos con 16 bits y probamos configuraciones que utilizan un tamaño de lote mayor o menos GPU en el caso de la inferencia Int8, ya que podemos ajustar el modelo más grande en menos dispositivos. Podemos ver los resultados de nuestro benchmark en la Tabla 6. En general, la inferencia Int8 es ligeramente más lenta, pero se acerca a la latencia de milisegundos por token en comparación con la inferencia de 16 bits.

Tabla 6: Estudio de ablación sobre el número de GPU utilizadas para ejecutar varios tipos de inferencias del modelo BLOOM-176B. Comparamos el número de GPU utilizadas por nuestro modelo BLOOM-176B cuantificado junto con el modelo BLOOM-176B nativo. También informamos de la velocidad de generación por token en milisegundos para diferentes tamaños de lote. Utilizamos nuestro método integrado en transformers (Wolf et al., 2019) impulsado por la biblioteca accelerate de HuggingFace para hacer frente a la inferencia multi-GPU. Nuestro método alcanza un rendimiento similar al del modelo nativo al caber en menos GPU que el modelo nativo.

@ Tamaño del Lote @ Hardware @ 1 @ 8 @ 32 @
@---|---|---|---|
@ Línea base de bfloat16 @ 8xA100 80GB @ 239 @ 32 @ 9.94 @
@ LLM.int8() @ 8xA100 80GB @ 253 @ 34 @ 10.44 @
@ LLM.int8() @ 4xA100 80GB @ 246 @ 33 @ 9.40 @
@ LLM.int8() @ 3xA100 80GB @ 247 @ 33 @ 9.11 @

## Apéndice E

### Resultados del Entrenamiento

Probamos el entrenamiento Int8 en una variedad de configuraciones de entrenamiento y lo comparamos con las líneas base de 32 bits. Probamos configuraciones separadas para ejecutar el transformador con redes de alimentación hacia delante de 8 bits con y sin proyecciones lineales de 8 bits en la capa de atención, así como en la propia atención en 8 bits y lo comparamos con el rendimiento de 32 bits. Probamos dos tareas: (1) modelado del lenguaje en parte del corpus RoBERTa incluyendo Libros (Zhu et al., 2015), CC-News (Nagel, 2016), OpenWebText (Gokaslan y Cohen, 2019), e Historias CC (Trinh y Le, 2018); y (2) traducción automática neuronal (NMT) (Ott et al., 2018) en WMT14+WMT16 (Macháček y Bojar, 2014; Sennrich et al., 2016).

Los resultados se muestran en la Tabla 7 y la Tabla 8. Podemos ver que para el entrenamiento, el uso de las proyecciones lineales de atención con tipos de datos Int8 y la cuantización vector-wise conduce a una degradación para NMT y para el modelo de lenguaje de 1.1B pero no para el modelado de lenguaje de 209M. Los resultados mejoran ligeramente si se utiliza la descomposición de precisión mixta, pero no es suficiente para recuperar el rendimiento completo en la mayoría de los casos. Esto sugiere que el entrenamiento con capas FFN de 8 bits es sencillo, mientras que otras capas requieren técnicas adicionales o tipos de datos diferentes a Int8 para realizar el entrenamiento de 8 bits a escala sin degradación del rendimiento.

Tabla 7: Resultados iniciales en el modelado del lenguaje a pequeña y gran escala. Hacer la atención en 8 bits degrada severamente el rendimiento y el rendimiento no puede recuperarse completamente con la descomposición de precisión mixta. Mientras que los modelos de lenguaje a pequeña escala están cerca del rendimiento de referencia tanto para las FFN de 8 bits como para los proyectos lineales de 8 bits en las capas de atención, el rendimiento se degrada a gran escala.

@ Es de 8 bits @ PPL @
@ Params @ FFN @ Lineal @ Atención @ Descomp @
@---|---|---|---|---|---|
@ 209M @ @ @ @ @ 16.74 @
@ 209M @ X @ @ @ @ 16.77 @
@ 209M @ X @ X @ @ @ 16.83 @
@ 209M @ X @ X @ @ 2% @ 16.78 @
@ 209M @ X @ X @ @ 5% @ 16.77 @
@ 209M @ X @ X @ @ 10% @ 16.80 @
@ 209M @ X @ X @ X @ 2% @ 24.33 @
@ 209M @ X @ X @ X @ 5% @ 20.00 @
@ 209M @ X @ X @ X @ 10% @ 19.00 @
@ 1.1B @ @ @ @ @ 9.99 @
@ 1.1B @ X @ @ @ @ 9.93 @
@ 1.1B @ X @ X @ @ @ 10.52 @
@ 1.1B @ X @ X @ @ 1% @ 10.41 @

Tabla 8: Resultados de traducción automática neuronal para capas FFN y de atención lineal de 8 bits para WMT14+16. Descomp indica el porcentaje que se calcula en multiplicación de matrices de 16 bits en lugar de 8 bits. La puntuación BLEU es la mediana de tres semillas aleatorias.

@ Es de 8 bits @ BLEU @
@ FFN @ Lineal @ Descomp @
@---|---|---|---|
@ @ @ @ 28.9 @
@ X @ @ @ 28.8 @
@ X @ X @ @ inestable @
@ X @ X @ 2% @ 28.0 @
@ X @ X @ 5% @ 27.6 @
@ X @ X @ 10% @ 27.5 @

## Apéndice F

También probamos el ajuste fino de 8 bits en RoBERTa-large ajustado fino en GLUE. Ejecutamos dos configuraciones diferentes: (1) comparamos con otros métodos Int8, y (2) comparamos la degradación del ajuste fino con capas FFN de 8 bits, así como capas de proyección de atención de 8 bits en comparación con 32 bits. Ajustamos con 5 semillas aleatorias e informamos el rendimiento medio.

La Tabla 9 se compara con diferentes métodos Int8 anteriores para el ajuste fino y muestra que la cuantización vectorial mejora con respecto a otros métodos. La Tabla 10 muestra el rendimiento de las proyecciones de atención FFN y/o lineales en 8 bits, así como las mejoras si se utiliza la descomposición de precisión mixta. Encontramos que las capas FFN de 8 bits no conducen a degradación, mientras que las proyecciones lineales de atención de 8 bits conducen a degradación si no se combinan con la descomposición de precisión mixta donde al menos las dimensiones de magnitud del 2% superior se calculan en 16 bits en lugar de 8 bits. Estos resultados destacan el papel fundamental de la descomposición de precisión mixta para el ajuste fino si se desea no degradar el rendimiento.

Tabla 9: Resultados de ajuste fino de GLUE para métodos de cuantización para la capa de retroalimentación en 8 bits, mientras que el resto está en 16 bits. No se utiliza la descomposición de precisión mixta. Podemos ver que la cuantización vectorial mejora con respecto a las líneas base.

| Método @ MNLI @ QNLI @ QQP @ RTE @ SST-2 @ MRPC @ CoLA @ STS-B @ Media |
| ------------- @ ----- @ ----- @ ----- @ ----- @ ----- @ ----- @ ----- @ ------ @ -------- |
| Línea base de 32 bits @ 90.4 @ 94.9 @ 92.2 @ 84.5 @ 96.4 @ 90.1 @ 67.4 @ 93.0 @ 88.61 |
| Replicación de 32 bits @ 90.3 @ 94.8 @ 92.3 @ 85.4 @ 96.6 @ 90.4 @ 68.8 @ 92.0 @ 88.83 |
| Q-BERT (Shen et al., 2020) @ 87.8 @ 93.0 @ 90.6 @ 84.7 @ 94.8 @ 88.2 @ 65.1 @ 91.1 @ 86.91 |
| Q8BERT (Zafrir et al., 2019) @ 85.6 @ 93.0 @ 90.1 @ 84.8 @ 94.7 @ 89.7 @ 65.0 @ 91.1 @ 86.75 |
| PSQ (Chen et al., 2020) @ 89.9 @ 94.5 @ 92.0 @ 86.8 @ 96.2 @ 90.4 @ 67.5 @ 91.9 @ 88.65 |
| Vectorial @ 90.2 @ 94.7 @ 92.3 @ 85.4 @ 96.4 @ 91.0 @ 68.6 @ 91.9 @ 88.81 |

Tabla 10: Desglose para la red de retroalimentación de 8 bits (FFN) y capas de atención lineal para GLUE. Las puntuaciones son la mediana de 5 semillas aleatorias. Decomp indica el porcentaje que se descompone en multiplicación de matriz de 16 bits. En comparación con la inferencia, el ajuste fino parece necesitar un porcentaje de descomposición mayor si las capas de atención lineal también se convierten a 8 bits.

| Es 8 bits @ @ @ MNLI @ QNLI @ QQP @ RTE @ SST-2 @ MRPC @ CoLA @ STS-B @ MEDIA |
| ------------- @ ------------- @ ----- @ ----- @ ----- @ ----- @ ----- @ ----- @ ----- @ ----- @ ------ @ -------- |
| FFN @ Lineal @ Decomp @ @ @ @ @ @ @ @ @ |
| 0% @ 90.4 @ 94.9 @ 92.2 @ 84.5 @ 96.4 @ 90.1 @ 67.4 @ 93.0 @ 88.6 @ @ |
| X @ 0% @ @ 90.2 @ 94.7 @ 92.3 @ 85.4 @ 96.4 @ 91.0 @ 68.6 @ 91.9 @ 88.8 @ |
| X @ X @ 0% @ 90.2 @ 94.4 @ 92.2 @ 84.1 @ 96.2 @ 89.7 @ 63.6 @ 91.6 @ 87.7 @ |
| X @ X @ 1% @ 90.0 @ 94.6 @ 92.2 @ 83.0 @ 96.2 @ 89.7 @ 65.8 @ 91.8 @ 87.9 @ |
| X @ X @ 2% @ 90.0 @ 94.5 @ 92.2 @ 85.9 @ 96.7 @ 90.4 @ 68.0 @ 91.9 @ 88.7 @ |
| X @ X @ 3% @ 90.0 @ 94.6 @ 92.2 @ 86.3 @ 96.4 @ 90.2 @ 68.3 @ 91.8 @ 88.7 @ |
