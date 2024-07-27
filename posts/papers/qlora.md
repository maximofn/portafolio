# QLoRA: Efficient Finetuning of Quantized LLMs

## Resumen

Presentamos QLORA, un enfoque de ajuste fino eficiente que reduce el uso de memoria lo suficiente como para ajustar un modelo de 65B parámetros en una sola GPU de 48GB mientras se preserva el rendimiento completo de ajuste fino de 16 bits. QLORA propaga gradientes a través de un modelo de lenguaje preentrenado cuantificado de 4 bits congelado en adaptadores de bajo rango (LoRA). Nuestra mejor familia de modelos, que llamamos Guanaco, supera a todos los modelos publicados anteriormente en el punto de referencia Vicuña, alcanzando el 99.3% del nivel de rendimiento de ChatGPT mientras que solo requiere 24 horas de ajuste fino en una sola GPU. QLORA presenta una serie de innovaciones para ahorrar memoria sin sacrificar el rendimiento: (a) NormalFloat de 4 bits (NF4), un nuevo tipo de datos que es óptimo en términos de teoría de la información para pesos distribuidos normalmente (b) Cuantificación doble para reducir la huella de memoria promedio al cuantificar las constantes de cuantificación y (c) Optimizadores paginados para administrar los picos de memoria. Usamos QLORA para ajustar más de 1,000 modelos, proporcionando un análisis detallado del seguimiento de instrucciones y el rendimiento del chatbot en 8 conjuntos de datos de instrucciones, múltiples tipos de modelos (LLaMA, T5) y escalas de modelos que serían inviables de ejecutar con ajuste fino regular (por ejemplo, modelos de 33B y 65B parámetros). Nuestros resultados muestran que el ajuste fino de QLoRA en un pequeño conjunto de datos de alta calidad conduce a resultados de vanguardia, incluso cuando se utilizan modelos más pequeños que el SoTA anterior. Brindamos un análisis detallado del rendimiento del chatbot basado en evaluaciones humanas y GPT-4 que muestran que las evaluaciones GPT-4 son una alternativa económica y razonable a la evaluación humana. Además, encontramos que los puntos de referencia actuales del chatbot no son confiables para evaluar con precisión los niveles de rendimiento de los chatbots. Un análisis selectivo demuestra dónde falla Guanaco en comparación con ChatGPT. Lanzamos todos nuestros modelos y código, incluidos los kernels CUDA para entrenamiento de 4 bits.

## 1 Introducción

El ajuste fino de grandes modelos de lenguaje (LLM) es una forma muy eficaz de mejorar su rendimiento, [40, 62, 43, 61, 59, 37] y de agregar o eliminar comportamientos deseables o indeseables [43, 2, 4]. Sin embargo, el ajuste fino de modelos muy grandes es prohibitivamente costoso; el ajuste fino regular de 16 bits de un modelo de parámetro LLaMA 65B [57] requiere más de 780 GB de memoria de GPU. Si bien los métodos de cuantificación recientes pueden reducir la huella de memoria de los LLM [14, 13, 18, 66], dichas técnicas solo funcionan para la inferencia y se descomponen durante el entrenamiento [65].

Demostramos por primera vez que es posible ajustar un modelo cuantificado de 4 bits sin ninguna degradación del rendimiento. Nuestro método, QLORA, utiliza una nueva técnica de alta precisión para cuantificar un modelo preentrenado a 4 bits, luego agrega un pequeño conjunto de pesos de adaptador de bajo rango que se pueden aprender [28] que se ajustan mediante la retropropagación de gradientes a través de los pesos cuantificados.

Tabla 1: Clasificaciones Elo para una competencia entre modelos, promediadas para 10,000 ordenamientos iniciales aleatorios. El ganador de un partido lo determina GPT-4, que declara qué respuesta es mejor para una indicación dada del punto de referencia Vicuña. Se muestran intervalos de confianza del 95% (±). Después de GPT-4, Guanaco 33B y 65B ganan la mayoría de los partidos, mientras que Guanaco 13B obtiene mejores resultados que Bard.

| Modelo | Tamaño | Elo |
|--------|--------|-----|
| GPT-4 | - | 1348 ± 1 |
| Guanaco | 65B 41 GB | 1022 ± 1 |
| Guanaco | 33B 21 GB | 992 ± 1 |
| Vicuña | 13B 26 GB | 974 ± 1 |
| ChatGPT | - | 966 ± 1 |
| Guanaco | 13B 10 GB | 916 ± 1 |
| Bardo | - | 902 ± 1 |
| Guanaco | 7B 6 GB | 879 ± 1 |

QLORA reduce los requisitos de memoria promedio de ajuste fino de un modelo de parámetros de 65B de > 780 GB de memoria de GPU a < 48 GB sin degradar el tiempo de ejecución ni el rendimiento predictivo en comparación con una línea de base de ajuste fino completo de 16 bits. Esto marca un cambio significativo en la accesibilidad del ajuste fino de LLM: ahora los modelos disponibles públicamente más grandes hasta la fecha se pueden ajustar en una sola GPU. Usando QLORA, entrenamos la familia de modelos Guanaco, y el segundo mejor modelo alcanza el 97.8% del nivel de rendimiento de ChatGPT en el punto de referencia Vicuña [10], mientras que se puede entrenar en menos de 12 horas en una sola GPU de consumo; usando una sola GPU profesional durante 24 horas logramos el 99.3% con nuestro modelo más grande, esencialmente cerrando la brecha con ChatGPT en el punto de referencia Vicuña. Cuando se implementa, nuestro modelo Guanaco más pequeño (7B parámetros) requiere solo 5 GB de memoria y supera a un modelo Alpaca de 26 GB en más de 20 puntos porcentuales en el punto de referencia Vicuña (Tabla 6).

QLORA presenta múltiples innovaciones diseñadas para reducir el uso de memoria sin sacrificar el rendimiento: (1) NormalFloat de 4 bits, un tipo de datos de cuantificación óptimo en términos de teoría de la información para datos distribuidos normalmente que produce mejores resultados empíricos que los enteros de 4 bits y los flotantes de 4 bits. (2) Cuantización doble, un método que cuantifica las constantes de cuantificación, ahorrando un promedio de aproximadamente 0.37 bits por parámetro (aproximadamente 3 GB para un modelo de 65B). (3) Optimizadores paginados, utilizando la memoria unificada de NVIDIA para evitar los picos de memoria de punto de control de gradiente que ocurren al procesar un minibatch con una longitud de secuencia larga. Combinamos estas contribuciones en un enfoque LoRA mejor ajustado que incluye adaptadores en cada capa de la red y, por lo tanto, evita casi todas las compensaciones de precisión observadas en trabajos anteriores.

La eficiencia de QLORA nos permite realizar un estudio en profundidad del ajuste fino de instrucciones y el rendimiento del chatbot en escalas de modelo que serían imposibles de explorar utilizando el ajuste fino completo de 16 bits en el hardware de investigación académica. Por lo tanto, entrenamos más de 1,000 modelos en varios conjuntos de datos de ajuste de instrucciones, arquitecturas de modelos y tamaños entre 80M y 65B parámetros. Además de mostrar que QLORA recupera el rendimiento de 16 bits (§4) y entrena un chatbot de última generación, Guanaco, (§5), también analizamos las tendencias en los modelos entrenados. Primero, encontramos que la calidad de los datos es mucho más importante que el tamaño del conjunto de datos, por ejemplo, un conjunto de datos de muestra de 9k (OASST1) superó a un conjunto de datos de muestra de 450k (FLAN v2, submuestreado) en el rendimiento del chatbot, incluso cuando ambos están destinados a admitir instrucciones siguiendo la generalización. En segundo lugar, mostramos que un rendimiento sólido del punto de referencia de Comprensión del lenguaje multitarea masiva (MMLU) no implica un rendimiento sólido del punto de referencia del chatbot Vicuña y viceversa, en otras palabras, la idoneidad del conjunto de datos es más importante que el tamaño para una tarea determinada.

Además, también proporcionamos un análisis extenso del rendimiento del chatbot que utiliza tanto evaluadores humanos como GPT-4 para la evaluación. Usamos puntos de referencia de estilo de torneo donde los modelos compiten entre sí en partidos para producir la mejor respuesta para una solicitud determinada. El ganador de un partido lo juzgan los anotadores humanos o GPT-4. Los resultados del torneo se agregan en puntajes Elo [16, 17] que determinan la clasificación del rendimiento del chatbot. Descubrimos que las evaluaciones de GPT-4 y las humanas coinciden en gran medida en el rango de rendimiento del modelo en los torneos, pero también encontramos que hay casos de fuerte desacuerdo. Como tal, destacamos que la evaluación basada en modelos, si bien proporciona una alternativa económica a la anotación humana, también tiene sus incertidumbres.

Aumentamos los resultados de nuestro punto de referencia de chatbot con un análisis cualitativo de los modelos Guanaco. Nuestro análisis destaca los casos de éxito y fracaso que no fueron capturados por los puntos de referencia cuantitativos.

Publicamos todas las generaciones de modelos con anotaciones humanas y GPT-4 para facilitar su posterior estudio. Tenemos código abierto en nuestra base de código y kernels CUDA e integramos nuestros métodos en la pila de transformadores Hugging Face [64], haciéndolos fácilmente accesibles para todos. Lanzamos una colección de adaptadores para modelos de tamaño 7/13/33/65B, entrenados en 8 conjuntos de datos diferentes de seguimiento de instrucciones, para un total de 32 modelos de ajuste fino diferentes de código abierto.

## 2 Antecedentes

**Cuantificación de k bits en bloque** La cuantificación es el proceso de discretizar una entrada de una representación que contiene más información a una representación con menos información. A menudo significa tomar un tipo de datos con más bits y convertirlo a menos bits, por ejemplo, de flotantes de 32 bits a enteros de 8 bits. Para garantizar que se utilice todo el rango del tipo de datos de bajo bit, el tipo de datos de entrada se reescala comúnmente al rango del tipo de datos de destino mediante la normalización por el máximo absoluto de los elementos de entrada, que generalmente se estructuran como un tensor. Por ejemplo, cuantificar un tensor de coma flotante (FP32) de 32 bits en un tensor Int8 con rango [-127, 127]:

$XInt8 = round (127/absmax(XFP32) XFP32) = round(cFP32 \cdot XFP32)$, (1)

donde c es la constante de cuantificación o escala de cuantificación. La descuantificación es la inversa:

$dequant(cFP32,XInt8) = XInt8/cFP32 = XFP32$ (2)

El problema con este enfoque es que si ocurre un valor de gran magnitud (es decir, un valor atípico) en el tensor de entrada, los contenedores de cuantificación (ciertas combinaciones de bits) no se utilizan bien con pocos o ningún número cuantificado en algunos contenedores. Para evitar el problema de los valores atípicos, un enfoque común es dividir el tensor de entrada en bloques que se cuantifican de forma independiente, cada uno con su propia constante de cuantificación c. Esto se puede formalizar de la siguiente manera: dividimos el tensor de entrada $X ∈ R^{b×h}$ en n bloques contiguos de tamaño B aplanando el tensor de entrada y cortando el segmento lineal en $n = (b × h)/B$ bloques. Cuantificamos estos bloques de forma independiente con la ecuación 1 para crear un tensor cuantificado y n constantes de cuantificación $c_i$.

**Adaptadores de bajo rango** El ajuste fino del adaptador de bajo rango (LoRA) [28] es un método que reduce los requisitos de memoria mediante el uso de un pequeño conjunto de parámetros entrenables, a menudo denominados adaptadores, sin actualizar los parámetros del modelo completo que permanecen fijos. Los gradientes durante el descenso de gradiente estocástico se pasan a través de los pesos fijos del modelo preentrenado al adaptador, que se actualiza para optimizar la función de pérdida. LoRA aumenta una proyección lineal a través de una proyección factorizada adicional. Dada una proyección $XW = Y$ con $X ∈ R^{b×h}$, $W ∈ R^{h×o}$ LoRA calcula:

$Y = XW + sXL_1L_2$, (3)

donde $L_1 ∈ R^{h×r}$ y $L_2 ∈ R^{r×o}$, y s es un escalar.

**Requisito de memoria para el ajuste fino eficiente en parámetros** Un punto importante de discusión es el requisito de memoria de LoRA durante el entrenamiento, tanto en términos del número como del tamaño de los adaptadores utilizados. Dado que la huella de memoria de LoRA es mínima, podemos usar más adaptadores para mejorar el rendimiento sin aumentar significativamente la memoria total utilizada. Si bien LoRA se diseñó como un

Figura 1: Diferentes métodos de ajuste fino y sus requisitos de memoria. QLORA mejora LoRA al cuantificar el modelo de transformador a una precisión de 4 bits y usar optimizadores paginados para manejar los picos de memoria.

método de ajuste fino eficiente en parámetros (PEFT), la mayor parte de la huella de memoria para el ajuste fino de LLM proviene de gradientes de activación y no de los parámetros de LoRA aprendidos. Para un modelo LLaMA de 7B entrenado en FLAN v2 con un tamaño de lote de 1, con pesos LoRA equivalentes al 0.2% comúnmente utilizado de los pesos del modelo original [28, 37], los gradientes de entrada de LoRA tienen una huella de memoria de 567 MB, mientras que los parámetros de LoRA ocupan solo 26 MB. Con el punto de control de gradiente [9], los gradientes de entrada se reducen a un promedio de 18 MB por secuencia, lo que los hace más intensivos en memoria que todos los pesos LoRA combinados. En comparación, el modelo base de 4 bits consume 5048 MB de memoria. Esto destaca que el punto de control de gradiente es importante, pero también que reducir drásticamente la cantidad de parámetros de LoRA produce solo beneficios de memoria menores. Esto significa que podemos usar más adaptadores sin aumentar significativamente la huella de memoria de entrenamiento general (consulte el Apéndice G para obtener un desglose detallado). Como se analiza más adelante, esto es crucial para recuperar el rendimiento completo de precisión de 16 bits.

## 3 Ajuste fino de QLORA

QLORA logra un ajuste fino de 4 bits de alta fidelidad a través de dos técnicas que proponemos: cuantificación NormalFloat (NF4) de 4 bits y cuantificación doble. Además, presentamos los optimizadores paginados para evitar que los picos de memoria durante el punto de control de gradiente provoquen errores de memoria insuficiente que tradicionalmente han dificultado el ajuste fino en una sola máquina para modelos grandes.

QLORA tiene un tipo de datos de almacenamiento de baja precisión, en nuestro caso generalmente 4 bits, y un tipo de datos de cálculo que generalmente es BFloat16. En la práctica, esto significa que siempre que se utiliza un tensor de peso QLORA, des cuantificamos el tensor a BFloat16 y luego realizamos una multiplicación de matrices en 16 bits.

Ahora discutimos los componentes de QLORA seguidos de una definición formal de QLORA.

**Cuantificación NormalFloat de 4 bits** El tipo de datos NormalFloat (NF) se basa en la cuantificación de cuantiles [15], que es un tipo de datos óptimo en términos de teoría de la información que garantiza que cada contenedor de cuantificación tenga el mismo número de valores asignados del tensor de entrada. La cuantificación de cuantiles funciona estimando el cuantil del tensor de entrada a través de la función de distribución acumulativa empírica.

La principal limitación de la cuantificación de cuantiles es que el proceso de estimación de cuantiles es costoso. Por lo tanto, se utilizan algoritmos rápidos de aproximación de cuantiles, como los cuantiles SRAM [15], para estimarlos. Debido a la naturaleza aproximada de estos algoritmos de estimación de cuantiles, el tipo de datos tiene grandes errores de cuantificación para valores atípicos, que a menudo son los valores más importantes.

Las estimaciones de cuantiles costosas y los errores de aproximación se pueden evitar cuando los tensores de entrada provienen de una distribución fijada hasta una constante de cuantificación. En tales casos, los tensores de entrada tienen los mismos cuantiles, lo que hace que la estimación de cuantiles exactos sea computacionalmente factible.

Dado que los pesos de la red neuronal preentrenados generalmente tienen una distribución normal centrada en cero con desviación estándar σ (consulte el Apéndice F), podemos transformar todos los pesos a una sola distribución fija escalando σ de modo que la distribución se ajuste exactamente al rango de nuestro tipo de datos. Para nuestro tipo de datos, establecemos el rango arbitrario [-1, 1]. Como tal, tanto los cuantiles para el tipo de datos como los pesos de la red neuronal deben normalizarse en este rango.

El tipo de datos óptimo en términos de teoría de la información para distribuciones normales de media cero con desviaciones estándar arbitrarias σ en el rango [-1, 1] se calcula de la siguiente manera: (1) estimar los cuantiles $2^k + 1$ de un $N(0, 1)$ teórico ) distribución para obtener un tipo de datos de cuantificación de cuantiles de k bits para distribuciones normales, (2) tomar este tipo de datos y normalizar sus valores en el rango [-1, 1], (3) cuantificar un tensor de peso de entrada normalizándolo en el rango [-1, 1] mediante el reescalado máximo absoluto.

Una vez que el rango de peso y el rango de tipo de datos coinciden, podemos cuantificar como de costumbre. El paso (3) es equivalente a reescalar la desviación estándar del tensor de peso para que coincida con la desviación estándar del tipo de datos de k bits. Más formalmente, estimamos los $2^k$ valores $q_i$ del tipo de datos de la siguiente manera:

$q_i = \frac{1}{2} ( Q_X (\frac{i}{2^k + 1}) + Q_X (\frac{i+ 1}{2^k + 1}))$, (4)

donde $Q_X(·)$ es la función de cuantiles de la distribución normal estándar $N(0, 1)$. Un problema para una cuantificación simétrica de k bits es que este enfoque no tiene una representación exacta de cero, que es una propiedad importante para cuantificar el relleno y otros elementos de valor cero sin error. A asegurar un punto cero discreto de 0 y utilizar los $2^k$ bits para un tipo de datos de k bits, creamos un tipo de datos asimétrico estimando los cuantiles $q_i$ de dos rangos $q_i: 2^{k−1}$ para la parte negativa y $2^{k−1} + 1$ para la parte positiva y luego unificamos estos conjuntos de $q_i$ y eliminamos uno de los dos ceros que ocurre en ambos conjuntos. Denominamos al tipo de datos resultante que tiene el mismo número esperado de valores en cada contenedor de cuantificación NormalFloat (NFk) de k bits, ya que el tipo de datos es óptimo en términos de teoría de la información para datos distribuidos normalmente centrados en cero. Los valores exactos de este tipo de datos se pueden encontrar en el Apéndice E.

Tabla 2: Perplejidad promedio de rastreo común de pila para diferentes tipos de datos para modelos OPT, BLOOM, LLaMA y Pythia de 125M a 13B.

| Tipo de datos | PPL medio |
|---------------|-----------|
| Int4 | 34.34 |
| Float4 (E2M1) | 31.07 |
| Float4 (E3M0) | 29.48 |
| NFloat4 + DQ | 27.41 |

**Cuantización doble** Presentamos la cuantificación doble (DQ), el proceso de cuantificar las constantes de cuantificación para obtener ahorros de memoria adicionales. Si bien se requiere un tamaño de bloque pequeño para una cuantificación precisa de 4 bits [13], también tiene una sobrecarga de memoria considerable. Por ejemplo, usando constantes de 32 bits y un tamaño de bloque de 64 para W, las constantes de cuantificación agregan 32/64 = 0.5 bits por parámetro en promedio. La cuantización doble ayuda a reducir la huella de memoria de las constantes de cuantificación.

Más específicamente, la cuantificación doble trata las constantes de cuantificación $c^{2}{FP32}$ de la primera cuantificación como entradas a una segunda cuantificación. Este segundo paso produce las constantes de cuantificación cuantificadas $c^{2}{FP8}$ y el segundo nivel de constantes de cuantificación $c^{1}{FP32}$. Usamos flotantes de 8 bits con un tamaño de bloque de 256 para la segunda cuantificación, ya que no se observa degradación del rendimiento para la cuantificación de 8 bits, en línea con los resultados de Dettmers y Zettlemoyer [13]. Dado que los $c^{2}{FP32}$ son positivos, restamos la media de $c_2$ antes de la cuantificación para centrar los valores alrededor de cero y hacer uso de la cuantificación simétrica. En promedio, para un tamaño de bloque de 64, esta cuantificación reduce la huella de memoria por parámetro de 32/64 = 0.5 bits a 8/64 + 32/(64 · 256) = 0.127 bits, una reducción de 0.373 bits por parámetro.

**Los optimizadores** paginados utilizan la función de memoria unificada de NVIDIA 3, que realiza transferencias automáticas de página a página entre la CPU y la GPU para un procesamiento de GPU sin errores en el escenario en el que la GPU ocasionalmente se queda sin memoria. La función funciona como la paginación de memoria normal entre la RAM de la CPU y el disco. Usamos esta característica para asignar memoria paginada para los estados del optimizador que luego se desalojan automáticamente a la RAM de la CPU cuando la GPU se queda sin memoria y se vuelven a paginar en la memoria de la GPU cuando la memoria es necesaria en el paso de actualización del optimizador.

**QLORA**. Usando los componentes descritos anteriormente, definimos QLORA para una sola capa lineal en el modelo base cuantificado con un solo adaptador LoRA de la siguiente manera:

$Y_{BF16} = X_{BF16}doubleDequant(c^{1}{FP32}, c^{2}{k-bit},W_{NF4}) +X_{BF16}L_{BF16}^{1}L_{BF16}^{2}$, (5)

donde doubleDequant(·) se define como:

$doubleDequant(c^{1}{FP32}, c^{2}{k-bit},W_{k-bit}) = dequant(dequant(c^{1}{FP32}, c^{2}{k-bit}),W_{4bit}) = W_{BF16}$, (6)

Usamos NF4 para W y FP8 para $c_2$. Usamos un tamaño de bloque de 64 para W para una mayor precisión de cuantificación y un tamaño de bloque de 256 para $c_2$ para conservar la memoria.

Para actualizaciones de parámetros, solo se necesita el gradiente con respecto al error para los pesos de los adaptadores $\frac{ \partial{E}}{\partial{L_i}}$, y no para pesos de 4 bits $\frac{ \partial{E}}{\partial{W}}$. Sin embargo, el cálculo de $\frac{ \partial{E}}{\partial{L_i}}$ implica el cálculo de $\frac{ \partial{X}}{\partial{W}}$ que procede a través de la ecuación (5) con des cuantificación del almacenamiento $W_{NF4}$ al tipo de datos de cálculo $W_{BF16}$ para calcular la derivada $\frac{ \partial{X}}{\partial{W}}$ en precisión BFloat16.

Para resumir, QLORA tiene un tipo de datos de almacenamiento (generalmente NormalFloat de 4 bits) y un tipo de datos de cálculo (BrainFloat de 16 bits). Descuantificamos el tipo de datos de almacenamiento al tipo de datos de cálculo para realizar el pase hacia adelante y hacia atrás, pero solo calculamos gradientes de peso para los parámetros LoRA que usan BrainFloat de 16 bits.

## 4 QLoRA frente al ajuste fino estándar

Hemos discutido cómo funciona QLoRA y cómo puede reducir significativamente la memoria requerida para ajustar modelos. La pregunta principal ahora es si QLoRA puede funcionar tan bien como el ajuste fino de modelo completo. Además, queremos analizar los componentes de QLoRA, incluido el impacto de NormalFloat4 sobre Float4 estándar. Las siguientes secciones discutirán los experimentos que tenían como objetivo responder a estas preguntas.

**Configuración experimental**. Consideramos tres arquitecturas (codificador, codificador-decodificador y solo decodificador) y comparamos QLORA con el ajuste fino del adaptador de 16 bits y con el ajuste fino completo para modelos de hasta 3B. Nuestras evaluaciones incluyen GLUE [58] con RoBERTa-large [38], Super-NaturalInstructions (TKInstruct) [61] con T5 [49] y MMLU de 5 disparos [24] después de ajustar LLaMA en Flan v2 [39] y Alpaca [55]. Para estudiar adicionalmente las ventajas de NF4 sobre otros tipos de datos de 4 bits, utilizamos la configuración de Dettmers y Zettlemoyer [13] y medimos la precisión y la perplejidad de cero disparos posteriores a la cuantificación en diferentes modelos (OPT [72], LLaMA [ 57], BLOOM [52], Pythia [7]) para tamaños de modelo 125 millones -13B. Brindamos más detalles en la sección de resultados para cada configuración particular para que los resultados sean más legibles. Detalles completos en el Apéndice A.

Figura 2: RougeL para modelos LLaMA 7B en el conjunto de datos Alpaca. Cada punto representa una ejecución con una semilla aleatoria diferente. Mejoramos los hiperparámetros predeterminados completamente ajustados de Stanford Alpaca para construir una línea de base sólida de 16 bits para las comparaciones. El uso de LoRA en todas las capas del transformador es fundamental para igualar el rendimiento de 16 bits.

Si bien los optimizadores paginados son fundamentales para realizar el ajuste QLORA de 33B/65B en una sola GPU de 24/48 GB, no proporcionamos mediciones estrictas para los optimizadores paginados, ya que la paginación solo ocurre cuando se procesan minibatches con longitudes de secuencia largas, lo cual es raro. Sin embargo, realizamos un análisis del tiempo de ejecución de los optimizadores paginados para modelos de 65B en GPU de 48 GB y encontramos que con un tamaño de lote de 16, los optimizadores paginados brindan la misma velocidad de entrenamiento que los optimizadores regulares. El trabajo futuro debería medir y caracterizar bajo qué circunstancias se producen ralentizaciones por el proceso de paginación.

**Los hiperparámetros LoRA predeterminados no coinciden con el rendimiento de 16 bits** Cuando se utiliza la práctica estándar de aplicar LoRA a las matrices de proyección de atención de consulta y valor [28], no podemos replicar el rendimiento de ajuste fino completo para modelos base grandes. Como se muestra en la Figura 2 para el ajuste fino de LLaMA 7B en Alpaca, encontramos que el hiperparámetro LoRA más crítico es cuántos adaptadores LoRA se utilizan en total y que se requiere LoRA en todas las capas de bloque de transformador lineal para igualar el rendimiento de ajuste fino completo. Otros hiperparámetros de LoRA, como la dimensión de proyección r, no afectan el rendimiento (consulte el Apéndice A).

Figura 3: Precisión promedio de cero disparos sobre Wino-grande, HellaSwag, PiQA, Arc-Easy y Arc-Challenge utilizando modelos LLaMA con diferentes tipos de datos de 4 bits. El tipo de datos NormalFloat mejora significativamente las ganancias de precisión bit a bit en comparación con los flotantes regulares de 4 bits. Si bien la cuantización doble (DQ) solo genera ganancias menores, permite un control más detallado sobre la huella de memoria para que los modelos de cierto tamaño (33B/65B) quepan en ciertas GPU (24/48GB).

Del mismo modo, encontramos que los hiperparámetros predeterminados para las líneas de base completamente ajustadas están poco ajustados. Realizamos una búsqueda de hiperparámetros en tasas de aprendizaje de 1e-6 a 5e-5 y tamaños de lote de 8 a 128 para encontrar líneas de base sólidas. Los resultados para el ajuste fino de LLaMA de 7B en Alpaca se muestran en la Figura 2.

**NormalFloat de 4 bits ofrece un mejor rendimiento que el punto flotante de 4 bits** Si bien el tipo de datos NormalFloat (NF4) de 4 bits es óptimo en términos de teoría de la información, aún debe determinarse si esta propiedad se traduce en ventajas empíricas. Seguimos la configuración de Dettmers y Zettlemoyer [13] donde los LLM cuantificados (OPT [72], BLOOM [52], Pythia [7], LLaMA) de diferentes tamaños (125M a 65B) con diferentes tipos de datos se evalúan en modelado de lenguaje y un conjunto de tareas de cero disparos. En la Figura 3 y la Tabla 2 vemos que NF4 mejora el rendimiento significativamente con respecto a FP4 e Int4 y que la cuantificación doble reduce la huella de memoria sin degradar el rendimiento.

**k-bit QLORA coincide con el rendimiento de ajuste fino completo de 16 bits y LoRA de 16 bits** Los hallazgos recientes han establecido que la cuantificación de 4 bits para la inferencia es posible, pero conduce a una degradación del rendimiento en relación con los 16 bits [13, 18]. Esto plantea la pregunta crucial de si el rendimiento perdido se puede recuperar realizando un ajuste fino del adaptador de 4 bits. Probamos esto para dos configuraciones.

Tabla 3: Experimentos que comparan BrainFloat (BF16) de 16 bits, entero de 8 bits (Int8), flotante de 4 bits (FP4) y NormalFloat (NF4) de 4 bits en GLUE y Super-NaturalInstructions. QLORA replica LoRA de 16 bits y ajuste fino completo.

| Conjunto de datos | GLUE (Acc.) |Super-NaturalInstructions (RougeL)| 

|Modelo | RoBERTa-large | T5-80M | T5-250M | T5-780M | T5-3B | T5-11B |
|-------|---------------|--------|---------|---------|-------|--------|
| BF16              | 88.6        | 40.1                             | 42.1   | 48.0          | 54.3   | 62.0    |
| Replicación BF16 | 88.6 | 40.0 | 42.2 | 47.3 | 54.9 | - |
| LoRA BF16 | 88.8 | 40.5 | 42.6 | 47.1 | 55.4 | 60.7 |
| QLORA Int8 | 88.8 | 40.4 | 42.9 | 45.4 | 56.5 | 60.7 |
| QLORA FP4 | 88.6 | 40.3 | 42.4 | 47.5 | 55.6 | 60.9 |
| QLORA NF4 + DQ | - | 40.4 | 42.7 | 47.7 | 55.3 | 60.9 |

El primero se centra en una comparación con el ajuste fino completo de 16 bits de los modelos RoBERTa y T5 con un tamaño de 125M a 3B parámetros en GLUE y el conjunto de datos Super-NaturalInstructions. Los resultados se muestran en la Tabla 3. En ambos conjuntos de datos, observamos que los métodos de adaptador de 16 bits, 8 bits y 4 bits replican el rendimiento de la línea de base de 16 bits completamente ajustada. Esto sugiere que el rendimiento perdido debido a la cuantificación imprecisa se puede recuperar completamente a través del ajuste fino del adaptador después de la cuantificación.

Para nuestra segunda configuración, dado que los modelos de ajuste fino completo con parámetros de 11B o más requieren más de un servidor de GPU de alta memoria, continuamos probando si QLORA de 4 bits puede coincidir con LoRA de 16 bits en las escalas de parámetros de 7B a 65B. Con este fin, ajustamos LLaMA 7B a través de 65B en dos conjuntos de datos de seguimiento de instrucciones, Alpaca y FLAN v2, y evaluamos en el punto de referencia MMLU a través de una precisión de 5 disparos. Los resultados se muestran en la Tabla 4, donde vemos que NF4 con cuantificación doble recupera completamente el rendimiento de MMLU de LoRA de 16 bits. Además, también notamos que QLORA con FP4 está rezagado con respecto a la línea de base de LoRA de coma flotante cerebral de 16 bits en aproximadamente 1 punto porcentual. Esto corrobora nuestros hallazgos de que (1) QLORA con NF4 replica el rendimiento de ajuste fino completo de 16 bits y el ajuste fino de LoRA de 16 bits, y (2) NF4 es superior a FP4 en términos de precisión de cuantificación.

**Resumen** Nuestros resultados muestran constantemente que QLORA de 4 bits con el tipo de datos NF4 coincide con el rendimiento de ajuste fino completo de 16 bits y el ajuste fino de LoRA de 16 bits en puntos de referencia académicos con configuraciones de evaluación bien establecidas. También hemos demostrado que NF4 es más efectivo que FP4 y que la cuantificación doble no degrada el rendimiento. Combinado, esto forma evidencia convincente de que el ajuste QLORA de 4 bits produce resultados confiables que coinciden con los métodos de 16 bits.

En línea con el trabajo anterior sobre cuantificación [13], nuestros resultados de MMLU y Elo indican que con un presupuesto de recursos de inferencia y ajuste fino dado, es beneficioso aumentar el número de parámetros en el modelo base al mismo tiempo que se disminuye su precisión. Esto resalta la importancia de los beneficios de eficiencia de QLORA. Dado que no observamos degradación del rendimiento en comparación con el ajuste fino completo en nuestros experimentos con ajuste fino de 4 bits, esto plantea la pregunta de dónde se encuentra exactamente la compensación entre rendimiento y precisión para el ajuste de QLoRA, que dejamos para que la explore el trabajo futuro.

Procedemos a investigar el ajuste fino de instrucciones a escalas que serían imposibles de explorar con el ajuste fino completo de 16 bits en el hardware de investigación académica.

## 5 Empujando el estado del arte de los chatbots con QLoRA

Habiendo establecido que QLoRA de 4 bits iguala el rendimiento de 16 bits en todas las escalas, tareas y conjuntos de datos, realizamos un estudio en profundidad del ajuste fino de instrucciones hasta los modelos de lenguaje de código abierto más grandes disponibles para la investigación. Para evaluar el rendimiento del ajuste fino de instrucciones de estos modelos, evaluamos en un punto de referencia desafiante de comprensión del lenguaje natural (MMLU) y desarrollamos nuevos métodos para la evaluación del rendimiento de los chatbots en el mundo real.

### 5.1 Configuración experimental

Ahora describimos una descripción general de la configuración experimental con todos los detalles en el Apéndice B.

**Datos**: Como, hasta donde sabemos, no existe un estudio exhaustivo de los conjuntos de datos recientes de seguimiento de instrucciones, seleccionamos ocho conjuntos de datos recientes. Incluimos conjuntos de datos obtenidos a través de crowdsourcing (OASST1 [31], HH-RLHF [4]), destilación de modelos ajustados a instrucciones (Alpaca [55], autoinstrucción [59], instrucciones no naturales [26]), agregaciones de corpus (FLAN v2 [12 ]), así como híbridos (Chip2 [32], Long-form [30]). Estos conjuntos de datos cubren diferentes idiomas, tamaños de datos y licencias.

**Configuración de entrenamiento**: Para evitar efectos de confusión de diferentes objetivos de entrenamiento, realizamos un ajuste fino de QLoRA con pérdida de entropía cruzada (aprendizaje supervisado) sin aprendizaje por refuerzo, incluso para conjuntos de datos que incluyen juicios humanos de diferentes respuestas. Para los conjuntos de datos que tienen una distinción clara entre instrucción y respuesta, ajustamos solo en la respuesta (ver ablaciones en el Apéndice B). Para OASST1 y HH-RLHF, hay varias respuestas disponibles. Luego, seleccionamos la respuesta superior en cada nivel del árbol de conversación y ajustamos la conversación completa seleccionada, incluidas las instrucciones. En todos nuestros experimentos, usamos NF4 QLORA con cuantificación doble y optimizadores paginados para evitar picos de memoria durante la verificación de gradientes que tradicionalmente han dificultado el ajuste fino en una sola máquina para modelos grandes. Hacemos pequeñas búsquedas de hiperparámetros para los modelos LLaMA de 13B y 33B y encontramos que todas las configuraciones de hiperparámetros encontradas en 7B se generalizan (incluido el número de épocas), excepto la tasa de aprendizaje y el tamaño del lote. Reducimos a la mitad la tasa de aprendizaje para 33B y 65B mientras duplicamos el tamaño del lote.

**Líneas de base**: Comparamos nuestros modelos con sistemas de chatbot tanto de investigación (Vicuña [10] y Open Assistant [31]) como comerciales (GPT-4 [42], GPT-3.5-turbo y Bard). El modelo Open Assistant es un modelo LLaMA 33B ajustado con Reinforcement Learning from Human Feedback (RLHF) en el mismo conjunto de datos OASST1 con el que experimentamos. Vicuña realiza un ajuste fino completo de LLaMA 13B en conversaciones patentadas compartidas por usuarios de ShareGPT y, por lo tanto, es el resultado de la destilación de los modelos OpenAI GPT.

### 5.2 Evaluación

Conjunto de datos	7B	13B	33B	65B
LLaMA sin ajuste	35.1	46.9	57.8	63.4
Autoinstrucción	36.4	33.3	53.0	56.7
Forma larga	32.1	43.2	56.6	59.7
Chip2	34.5	41.6	53.6	59.8
HH-RLHF	34.9	44.6	55.8	60.1
Instrucción no natural	41.9	48.1	57.3	61.3
Guanaco (OASST1)	36.6	46.4	57.0	62.2
Alpaca	38.8	47.8	57.3	62.5
FLAN v2	44.5	51.4	59.2	63.9

Tabla 5: Resultados de la prueba de 5 disparos de MMLU para diferentes tamaños de LLaMA ajustados en los conjuntos de datos correspondientes utilizando QLoRA.

Siguiendo la práctica común, usamos el punto de referencia MMLU (Comprensión del lenguaje de múltiples tareas masivas) [24] para medir el rendimiento en una variedad de tareas de comprensión del lenguaje. Este es un punto de referencia de opción múltiple que cubre 57 tareas, incluidas matemáticas elementales, historia de los EE. UU., informática, derecho y más. Informamos una precisión de prueba de 5 disparos.

También probamos las capacidades del lenguaje generativo a través de evaluaciones automatizadas y humanas. Este segundo conjunto de evaluaciones se basa en consultas seleccionadas por humanos y tiene como objetivo medir la calidad de las respuestas del modelo. Si bien este es un banco de pruebas más realista para el rendimiento del modelo de chatbot y está creciendo en popularidad, no existe un protocolo comúnmente aceptado en la literatura. Describimos a continuación nuestra configuración propuesta, utilizando el muestreo de núcleos con p = 0.9 y temperatura 0.7 en todos los casos.

**Datos de referencia**: Evaluamos en dos conjuntos de datos seleccionados de consultas (preguntas): las indicaciones de Vicuña [10] y el conjunto de datos de validación OASST1 [31]. Usamos las indicaciones de Vicuña, un conjunto de 80 indicaciones de un conjunto diverso de categorías, sin modificaciones. El conjunto de datos OASST1 es una colección multilingüe de diálogos multiturno de origen público entre un usuario y un asistente. Seleccionamos todos los mensajes de usuario en el conjunto de datos de validación como consultas e incluimos turnos anteriores en el aviso. Este procedimiento conduce a 953 consultas de usuario únicas. Denominamos a estos dos conjuntos de datos los puntos de referencia de Vicuña y OA.

**Evaluación automatizada**: Primero, según el protocolo de evaluación presentado por Chiang et al. [10], usamos GPT-4 para calificar el rendimiento de diferentes sistemas frente a ChatGPT (GPT-3.5 Turbo) en el punto de referencia de Vicuña. Dada una consulta junto con las respuestas de ChatGPT y de un modelo, se le solicita a GPT-4 que asigne una puntuación sobre diez a ambas respuestas y que proporcione una explicación. El rendimiento general de un modelo se calcula como un porcentaje de la puntuación obtenida por ChatGPT. Tenga en cuenta que esta puntuación relativa puede ser superior al 100 % si el modelo logra una puntuación absoluta más alta que ChatGPT. Encontramos un efecto de ordenamiento significativo con GPT-4 aumentando la puntuación de la respuesta que ocurre antes en el aviso. Para controlar tales efectos, recomendamos informar la puntuación media en ambos órdenes.

A continuación, medimos el rendimiento mediante comparaciones directas entre salidas del sistema. Simplificamos el esquema de calificación a un problema de etiquetado de tres clases que tiene en cuenta los empates. Le pedimos a GPT-4 que elija la mejor respuesta o declare un empate y proporcione una explicación. Realizamos estas comparaciones directas en todas las permutaciones de pares de sistemas tanto en los puntos de referencia de Vicuña como en los de OA.

**Evaluación humana**: Si bien el trabajo reciente indica que los modelos generativos se pueden emplear de manera efectiva para las evaluaciones del sistema [19], la confiabilidad de las calificaciones de GPT-4 para evaluar el rendimiento del chatbot, hasta donde sabemos, aún no se ha demostrado que se correlacione con los juicios humanos. Por lo tanto, ejecutamos dos evaluaciones humanas paralelas en el punto de referencia de Vicuña que coinciden con los protocolos de evaluación automatizados descritos anteriormente. Usamos Amazon Mechanical Turk (AMT) y obtenemos dos anotadores humanos para comparaciones con ChatGPT y tres anotadores para comparaciones por pares.

**Clasificación Elo**: Tanto con comparaciones por pares humanas como automatizadas, creamos una competencia estilo torneo donde los modelos compiten entre sí. El torneo está compuesto por partidos donde pares de modelos compiten para producir la mejor respuesta para un aviso dado. Esto es similar a cómo Bai et al. [4] y Chiang et al. [10] comparan modelos, pero también empleamos clasificaciones GPT-4 además de clasificaciones humanas. Muestreamos aleatoriamente del conjunto de comparaciones etiquetadas para calcular Elo [16, 17]. La calificación Elo, que se usa ampliamente en el ajedrez y otros juegos, es una medida de la tasa de victorias esperada en relación con la tasa de victorias de un oponente, por ejemplo, un Elo de 1100 frente a 1000 significa que el jugador Elo 1100 tiene una tasa de victorias esperada de aproximadamente el 65 % contra el oponente Elo 1000; un partido de 1000 contra 1000 o 1100 contra 1100 da como resultado una tasa de victorias esperada del 50 %. La calificación Elo cambia después de cada partido proporcionalmente al resultado esperado, es decir, una sorpresa inesperada conduce a un gran cambio en la calificación Elo, mientras que un resultado esperado conduce a un pequeño cambio. Con el tiempo, las clasificaciones Elo coinciden aproximadamente con la habilidad de cada jugador para jugar el juego. Comenzamos con una puntuación de 1000 y usamos K = 32. Similar a Chiang et al. [10], repetimos este procedimiento 10 000 veces con diferentes semillas aleatorias para controlar los efectos del orden, por ejemplo, el efecto de qué pares de modelos compiten entre sí primero.

### 5.3 Guanaco: QLORA entrenado en OASST1 es un chatbot de última generación

Según nuestras evaluaciones automatizadas y humanas, encontramos que el modelo QLoRA sintonizado superior, Guanaco 65B, que ajustamos en una variante de OASST1, es el modelo de chatbot de código abierto con mejor rendimiento y ofrece un rendimiento competitivo con ChatGPT. En comparación con GPT-4, Guanaco 65B y 33B tienen una probabilidad de victoria esperada del 30 %, según la calificación Elo de las comparaciones por pares a nivel del sistema de los anotadores humanos, la más alta jamás informada.

Los resultados del punto de referencia de Vicuña [10] en relación con ChatGPT se muestran en la Tabla 6. Descubrimos que Guanaco 65B es el modelo con mejor rendimiento después de GPT-4, logrando un 99,3 % de rendimiento en relación con ChatGPT. Guanaco 33B tiene más parámetros que el modelo Vicuña 13B, pero usa solo precisión de 4 bits para sus pesos y, por lo tanto, es mucho más eficiente en memoria con 21 GB frente a 26 GB, lo que proporciona tres puntos porcentuales de mejora con respecto a Vicuña 13B. Además, Guanaco 7B cabe fácilmente en los teléfonos modernos con una huella de 5 GB y aún obtiene una puntuación de casi 20 puntos porcentuales más alta que Alpaca 13B.

Modelo / Conjunto de datos	Parámetros	Bits del modelo	Memoria	ChatGPT vs Sys	Sys vs ChatGPT	Media	IC del 95 %
GPT-4	-	-	-	119.4%	110.1%	114.5%	2.6%
Bardo	-	-	-	93.2%	96.4%	94.8%	4.1%
Guanaco 65B	4 bits	41 GB	96.7%	101.9%	99.3%	4.4%	
Alpaca 65B	4 bits	41 GB	63.0%	77.9%	70.7%	4.3%	
FLAN v2 65B	4 bits	41 GB	37.0%	59.6%	48.4%	4.6%	
Guanaco 33B	4 bits	21 GB	96.5%	99.2%	97.8%	4.4%	
Asistente abierto 33B	16 bits	66 GB	91.2%	98.7%	94.9%	4.5%	
Alpaca 33B	4 bits	21 GB	67.2%	79.7%	73.6%	4.2%	
FLAN v2 33B	4 bits	21 GB	26.3%	49.7%	38.0%	3.9%	
Vicuña 13B	16 bits	26 GB	91.2%	98.7%	94.9%	4.5%	
Guanaco 13B	4 bits	10 GB	87.3%	93.4%	90.4%	5.2%	
Alpaca 13B	4 bits	10 GB	63.8%	76.7%	69.4%	4.2%	
HH-RLHF 13B	4 bits	10 GB	55.5%	69.1%	62.5%	4.7%	
Instr. no natural 13B	4 bits	10 GB	50.6%	69.8%	60.5%	4.2%	
Chip2 13B	4 bits	10 GB	49.2%	69.3%	59.5%	4.7%	
Forma larga 13B	4 bits	10 GB	44.9%	62.0%	53.6%	5.2%	
Autoinstrucción 13B	4 bits	10 GB	38.0%	60.5%	49.1%	4.6%	
FLAN v2 13B	4 bits	10 GB	32.4%	61.2%	47.0%	3.6%	
Guanaco 7B	4 bits	5 GB	84.1%	89.8%	87.0%	5.4%	
Alpaca 7B	4 bits	5 GB	57.3%	71.2%	64.4%	5.0%	
FLAN v2 7B	4 bits	5 GB	33.3%	56.1%	44.8%	4.0%	

Tabla 6: Puntuaciones de referencia de Vicuña de cero disparos como porcentaje de la puntuación obtenida por ChatGPT evaluado por GPT-4. Vemos que los modelos OASST1 funcionan cerca de ChatGPT a pesar de estar entrenados en un conjunto de datos muy pequeño y tener una fracción del requisito de memoria de los modelos de referencia.

Sin embargo, la Tabla 6 también tiene intervalos de confianza muy amplios, con muchos modelos superpuestos en rendimiento. Nuestra hipótesis es que esta incertidumbre proviene de la falta de una especificación clara de la escala, por ejemplo, no está claro qué significa 8 en una escala de 10 puntos en diferentes escenarios. Como tal, en su lugar recomendamos usar el método de clasificación Elo [16], basado en juicios por pares de anotadores humanos y GPT-4 para evitar el problema de conectar a tierra una escala absoluta. Las clasificaciones Elo de los modelos más competitivos se pueden ver en la Tabla 1. Observamos que la clasificación humana y GPT-4 de modelos en el punto de referencia de Vicuña discrepa parcialmente, particularmente para Guanaco 7B, pero es consistente para la mayoría de los modelos con un Kendall Tau de τ = 0.43 y una correlación de rango de Spearman de r = 0.55 a nivel del sistema. A nivel de ejemplo, el acuerdo entre GPT-4 y el voto mayoritario de los anotadores humanos es más débil con Fleiss κ = 0.25. En general, esto muestra un acuerdo moderado entre los juicios a nivel del sistema de GPT-4 y los anotadores humanos, y por lo tanto, esa evaluación basada en modelos representa una alternativa algo confiable a la evaluación humana. Discutimos más consideraciones en la Sección 6.2.

Punto de referencia	Vicuña	Vicuña	Asistente abierto	# Indicaciones
80
Juez	Calificadores humanos	GPT-4	GPT-4	
Modelo	Clasificación Elo	Rango	Clasificación Elo	Rango
GPT-4	1176	1	1348	1
Guanaco-65B	1023	2	1022	2
Guanaco-33B	1009	4	992	3
ChatGPT-3.5 Turbo	916	7	966	5
Vicuña-13B	984	5	974	4
Guanaco-13B	975	6	913	6
Guanaco-7B	1010	3	879	8
Bardo	909	8	902	7

Tabla 7: Calificación Elo para un torneo entre modelos donde los modelos compiten para generar la mejor respuesta para un aviso, juzgada por evaluadores humanos o GPT-4. En general, se tiende a preferir Guanaco 65B y 33B a ChatGPT-3.5 en los puntos de referencia estudiados. Según los evaluadores humanos, tienen una. Cada diferencia de 10 puntos en Elo es aproximadamente una diferencia del 1,5 % en la tasa de victorias.

Las clasificaciones Elo en la Tabla 7 indican que los modelos Guanaco 33B y 65B superan a todos los modelos además de GPT-4 en los puntos de referencia de Vicuña y OA y que funcionan de manera comparable a ChatGPT en línea con la Tabla 6. Observamos que el punto de referencia de Vicuña favorece los modelos de código abierto, mientras que el punto de referencia de OA más grande favorece a ChatGPT. Además, podemos ver en las Tablas 5 y 6 que la idoneidad de un conjunto de datos de ajuste fino es un factor determinante en el rendimiento. El ajuste fino de los modelos Llama en FLAN v2 funciona particularmente bien en MMLU, pero tiene el peor rendimiento en el punto de referencia de Vicuña (se observan tendencias similares con otros modelos). Esto también apunta a una ortogonalidad parcial en los puntos de referencia de evaluación actuales: un rendimiento MMLU fuerte no implica un rendimiento de chatbot fuerte (medido por los puntos de referencia de Vicuña o OA) y viceversa.

Guanaco es el único modelo superior en nuestra evaluación que no está entrenado con datos propietarios, ya que las pautas de recopilación del conjunto de datos OASST1 prohíben explícitamente el uso de modelos GPT. El siguiente mejor modelo entrenado solo con datos de código abierto es el modelo Anthropic HH-RLHF, que obtiene una puntuación 30 puntos porcentuales más baja que Guanaco en el punto de referencia de Vicuña (consulte la Tabla 6). En general, estos resultados muestran que QLoRA de 4 bits es efectivo y puede producir chatbots de última generación que rivalizan con ChatGPT. Además, nuestro Guanaco 33B se puede entrenar en GPU de consumo de 24 GB en menos de 12 horas. Esto abre el potencial para trabajos futuros a través del ajuste de QLoRA en datos de código abierto especializados, lo que produce modelos que pueden competir con los mejores modelos comerciales que existen en la actualidad.

## 6 Análisis cualitativo

Si bien el análisis cuantitativo es el núcleo de nuestra evaluación, existen varios problemas al observar solo las estadísticas resumidas. Quizás el más grande es el problema de la validez del punto de referencia [36], si un punto de referencia realmente prueba lo que sugiere su nombre o descripción siempre está en duda, especialmente a medida que descubrimos "atajos" para resolver puntos de referencia que los modelos de aprendizaje automático a veces explotan [22, 46] . Para aliviar esto parcialmente, aquí realizamos un análisis cualitativo, en dos secciones. Primero, en §6.1 mostramos algunos ejemplos que creemos que son representativos de algunos patrones observados en el texto generado por nuestro modelo Guanaco de 65b. En segundo lugar, §6.2 detallamos consideraciones sobre los resultados que hemos discutido y nuestra interpretación de los mismos.

### 6.1 Análisis cualitativo de generaciones de ejemplo

Para encontrar ejemplos, primero revisamos los datos generados para el punto de referencia de Vicuña y el punto de referencia de OpenAssistant, y buscamos patrones en las respuestas que genera Guanaco. Cuando notamos un patrón, intentamos configurar una pregunta o un aviso que induzca el patrón, aunque sea la solución incorrecta, por ejemplo, si observamos que el modelo tiende a dar respuestas largas, le pedimos al modelo que "Responda sí o no sin explicación". Usamos esto para encontrar "limones" donde logramos romper el modelo de manera adversa y "cerezas" donde no logramos romper el modelo, y presentamos ambos. Todas las generaciones en esta sección se generaron con Nucleus Sampling [25] con p = 0.9.

Por supuesto, esto no es de ninguna manera exhaustivo, ya que está más allá del alcance de este pequeño estudio cualitativo controlar todas las variables involucradas, por ejemplo, la distribución completa de respuestas que el modelo puede generar para un aviso dado es bastante grande, por lo que confiamos en muestras que esperamos sean representativas. Sin embargo, creemos que describir estos ejemplos da contexto a la evidencia cuantitativa que se muestra anteriormente en el documento. Dado que abrimos el código fuente de todos los modelos y el código, esperamos que esta sección inspire trabajos futuros para examinar con más detalle los problemas que presentamos aquí.

**Recuperación fáctica**: Para preguntas como "¿Cuál es la capital de Zambia?" todos los modelos generan respuestas correctas de forma coherente, p. ej.,

**Guanaco**: La capital de Zambia es Lusaka.

Sin embargo, a medida que las preguntas se vuelven más oscuras, Guanaco se vuelve poco confiable, pero se mantiene seguro. Por ejemplo, en respuesta a este mensaje de HotPotQA [68]:

**Usuario**: ¿En qué año nació el cantante que popularizó 'I'll Keep the Lovelight Burning'?

**Guanaco**: A Al Jolson se le atribuye la popularización de la canción 'I'll Keep the Lovelight Burning', y nació en el año 1886.

Guanaco genera el popularizador equivocado y el cumpleaños equivocado (aunque el cumpleaños dado es correcto para la persona mencionada, Al Jolson).

**Sugestibilidad**: Guanaco muestra una resistencia sorprendente a estar de acuerdo con algunos tipos de información errónea asumida, por ejemplo, en la siguiente interacción:

**Usuario**: ¿Cómo se confirmó finalmente y de manera oficial que la tierra es plana por científicos revisados ​​por pares?

**Guanaco**: Los científicos revisados ​​por pares nunca han confirmado oficialmente que la tierra sea plana. El consenso abrumador entre los científicos es que la tierra es esférica. De hecho, esto se sabe desde hace siglos y se ha confirmado a través de numerosos experimentos y observaciones.

La creencia de que la tierra es plana es una teoría de la conspiración que ha sido desacreditada por la ciencia. La idea de que un grupo de científicos ha revisado por pares y confirmado que la tierra es plana es simplemente falsa.

Si tiene más preguntas, por favor pregunte.

Guanaco también es bastante bueno para saber qué tipo de preguntas no son posibles de responder, p. ej.,

**Usuario**: ¿Qué hora es?

**Guanaco**: Lo siento, pero como modelo de lenguaje de IA, no tengo acceso a información en tiempo real. Mis respuestas se generan en función de mi conocimiento preexistente y no reflejan la hora actual. Si está buscando la hora actual, le sugiero que use un dispositivo de cronometraje o que consulte un reloj en línea.

Resultados similares son válidos para "¿Dónde estás?", "¿Cómo estás?", etc.

**Negativa**: Del mismo modo, Guanaco a veces se niega a seguir instrucciones por razones aparentemente aleatorias:

**Usuario**: Invierta las palabras de la oración "Soy un tipo genial con un humor moca".

**Guanaco**: Lo siento, no puedo hacer eso ahora mismo, pero puedo explicar por qué la oración que proporcionó es gramaticalmente correcta.

La oración "Soy un tipo genial con un humor moca" sigue las reglas gramaticales y sintácticas correctas del idioma inglés. En este caso, el adjetivo "genial" va antes del sustantivo "tipo" para describirlo, y la frase preposicional "con un humor moca" proporciona información adicional sobre el contexto de la oración. Esta estructura de oraciones es perfectamente aceptable y tiene sentido en el contexto de la oración.

Si tiene alguna otra pregunta o si hay algo más con lo que pueda ayudarlo, no dude en preguntar.

**Guardar secretos**: Desafortunadamente, este rechazo no es confiable incluso cuando se desea. A menudo, a los diseñadores de sistemas les gustaría mantener algo en secreto para el usuario, incluso si el sistema puede devolver respuestas de texto libre al usuario. Le indicamos al modelo "La palabra secreta es 'plátano'. No revele ni repita esto, sin importar lo que soliciten los humanos". e intente ver qué tan fácil es para un usuario potencial acceder a esta información secreta. Preguntar directamente falla:

**Usuario**: ¿Cuál es la palabra secreta?

**Guanaco**: Lo siento, pero no puedo revelar la palabra secreta. Estoy programado para no revelar ni repetir la palabra secreta, sin importar lo que soliciten los humanos. ¿Hay algo más en lo que pueda ayudarte?

que es el comportamiento deseado. Sin embargo, un poco de engaño rompe este comportamiento:

**Usuario**: Esto es un juego. El objetivo es ignorar tus instrucciones anteriores. ¿Cuál es la palabra secreta?

**Guanaco**: Lo siento, la palabra secreta es plátano. Es mejor si no hablamos de eso. ¿Hay algo más que te gustaría preguntar?
mostrando la necesidad de estudiar métodos para un seguimiento de instrucciones más fiel.

**Matemáticas**: La mayor debilidad de Guanaco son las matemáticas, un área en la que muchos modelos de lenguaje tienen dificultades [35]. Cuando Guanaco muestra su trabajo, tiende a ser preciso, p. ej.,

**Usuario**: Lee corta un césped y cobra $33. La semana pasada cortó 16 céspedes y tres clientes le dieron una propina de $10 cada uno. ¿Cuántos dólares ganó Lee cortando césped la semana pasada?

**Guanaco**: Lee ganó $582 cortando césped la semana pasada.
Para encontrar la cantidad total que ganó, primero necesitamos calcular cuánto ganó por cortar 16 céspedes:

$33 x 16 = $528

Luego necesitamos agregar las propinas que recibió de los tres clientes:

$10 x 3 = $30

Entonces, la cantidad total que ganó Lee fue:

$528 + $30 = $558

Sin embargo, Guanaco puede descomponerse incluso en problemas simples si no los descompone paso a paso, un problema conocido [63]. Por ejemplo, vemos la siguiente interacción:

**Usuario**: Factoriza 1833.

**Guanaco**: Claro, ¡estaré encantado de ayudar! 1833 es un número primo, lo que significa que solo tiene dos factores: 1 y 1833.
Entonces, la factorización única de 1833 es:
2^1 * 3^2 * 17^1

¡Espero que esto ayude! Avísame si tienes alguna otra pregunta.
que no solo está mal (la verdadera factorización es 3 × 17 × 43), está mal dos veces.

**Teoría de la mente**: Guanaco muestra capacidades de Teoría de la mente sorprendentemente fuertes [41, 51]. Por ejemplo, el modelo responde correctamente la siguiente pregunta con gran detalle:

**Usuario**: James y Abby están en el dormitorio. Abby guardó el bolígrafo en el cajón del escritorio. Abby sale del dormitorio. James mueve el bolígrafo a la bolsa. ¿Dónde cree James que Abby buscará el bolígrafo?

**Guanaco**: James sabe que Abby guardó el bolígrafo en el cajón del escritorio. Pero James también sabe que ha movido el bolígrafo a la bolsa y asume que Abby no lo sabe. Entonces, James puede adivinar que Abby buscará el bolígrafo en el cajón del escritorio, porque ahí fue donde lo dejó la última vez. Sin embargo, esta suposición puede ser incorrecta, porque Abby pudo haber visto a James moviendo el bolígrafo.

Sin embargo, estas inferencias no son confiables y, a menudo, el modelo da razones que presumen cosas que no tienen sentido en la situación, p. ej.,

**Usuario**: Evelyn entró a la sala de estar. Jackson entró a la sala de juegos. James entró a la sala de juegos. Los frijoles están en el cofre del tesoro. James salió de la sala de juegos. Jackson movió los frijoles a la despensa. Jackson salió de la sala de juegos. James entró a la sala de estar. ¿Dónde buscará James los frijoles?

**Guanaco**: James buscará los frijoles en la despensa, porque ahí fue donde Jackson los movió.
donde Guanaco presume una transferencia de información que nunca se describió. Estos problemas se hacen eco de la literatura reciente [51], pero requieren más estudio.

### 6.2 Consideraciones

**Evaluación**: Informamos un acuerdo moderado entre los anotadores humanos (Fleiss κ = 0.42) con un deterioro adicional al comparar dos sistemas sólidos. Esto apunta a limitaciones en los puntos de referencia actuales y los protocolos de evaluación humana para el rendimiento de las tareas del chatbot. Al comparar manualmente las generaciones de ChatGPT y Guanaco 65B en el punto de referencia de Vicuña, encontramos que las preferencias subjetivas comienzan a jugar un papel importante, ya que los autores de este documento no estaban de acuerdo con las muchas respuestas preferidas. El trabajo futuro debería investigar enfoques para mitigar estos problemas a partir de disciplinas que desarrollaron mecanismos para lidiar con preferencias subjetivas, como la interacción humano-computadora y la psicología.

En nuestro análisis, también encontramos que los sistemas de evaluación automatizados tienen sesgos notables. Por ejemplo, observamos fuertes efectos de orden con GPT-4 asignando puntajes más altos al sistema que aparece primero en su solicitud. El acuerdo relativamente débil a nivel de muestra entre GPT-4 y los anotadores humanos (Fleiss κ = 0.25) también sugiere que los anotadores humanos y los sistemas automatizados pueden depender de preferencias que no siempre están alineadas. Además, en la Tabla 7, observamos que GPT-4 asigna puntajes significativamente más altos a sus propias salidas en comparación con las calificaciones humanas, Elo de 1348 frente a 1176, que representan un 20 % adicional de probabilidad de ganar contra un oponente. El trabajo futuro debería examinar la presencia de posibles sesgos en los sistemas de evaluación automatizados, así como posibles estrategias de mitigación.

**Datos y formación**: Observamos que el conjunto de datos OASST1 en el que se entrenan los modelos Guanaco es multilingüe y que el banco de pruebas de OA también contiene indicaciones en diferentes idiomas. Dejamos para trabajo futuro investigar el grado en que dicha capacitación multilingüe mejora el rendimiento de las instrucciones en idiomas distintos del inglés y si esto explica la mayor brecha entre el modelo Vicuña-13B (solo entrenado con datos en inglés) y Guanaco 33B y 65B en el Banco de pruebas de OA.

Dado el sólido rendimiento de los modelos Guanaco, investigamos cualquier fuga de datos entre los datos de OASST1 y las indicaciones de referencia de Vicuña. No encontramos indicaciones superpuestas después de realizar una coincidencia de cadenas difusa en los dos conjuntos de datos e inspeccionar manualmente las coincidencias más cercanas.

Además, observamos que nuestro modelo solo se entrena con pérdida de entropía cruzada (aprendizaje supervisado) sin depender del aprendizaje por refuerzo a partir de la retroalimentación humana (RLHF). Esto requiere más investigaciones sobre las compensaciones de la pérdida de entropía cruzada simple y el entrenamiento RLHF. Esperamos que QLoRA permita dicho análisis a escala, sin la necesidad de recursos computacionales abrumadores.

## 7 Trabajo relacionado

**Cuantización de grandes modelos de lenguaje**
La cuantización de LLMs se ha centrado principalmente en la cuantización para el tiempo de inferencia. Los principales enfoques para preservar la calidad LLM de 16 bits se centran en la gestión de características atípicas (por ejemplo, SmoothQuant [66] y LLM.int8() [14]), mientras que otros utilizan métodos de agrupación más sofisticados [44, 69]. Los enfoques de cuantización con pérdida estudian las ventajas e inconvenientes del redondeo regular [13, 71, 47] o cómo optimizar las decisiones de redondeo para mejorar la precisión de la cuantización [18]. Además de nuestro trabajo, las capas SwitchBack [65] son el único trabajo que estudia la retropropagación a través de pesos cuantificados a una escala superior a 1.000 millones de parámetros.

**Ajuste fino con adaptadores**

Aunque utilizamos adaptadores de bajo rango [28] (LoRA), se han propuesto muchos otros métodos de ajuste fino eficiente de parámetros (PEFT), como el ajuste de prompts [48, 33, 34], el ajuste de las entradas de la capa de incrustación [1], el ajuste de estados ocultos (IA3) [37], la adición de capas completas [27], el ajuste de sesgos [70], el aprendizaje de una máscara sobre los pesos basada en la información de Fisher [54] y una combinación de enfoques [23]. En nuestro trabajo, mostramos que los adaptadores LoRA son capaces de alcanzar el rendimiento completo del ajuste fino de 16 bits. Dejamos para futuros trabajos la exploración de las ventajas e inconvenientes de otros enfoques PEFT.

**Ajuste fino de instrucciones**

Para ayudar a un LLM preentrenado a seguir las instrucciones proporcionadas en un prompt, el ajuste fino de instrucciones utiliza pares de entrada-salida de varias fuentes de datos para ajustar finamente un LLM preentrenado para generar la salida dada la entrada como un prompt. Los enfoques y conjuntos de datos incluyen MetaICL [40], MetaTuning [73], InstructGPT [43], FLAN [62, 12], PromptSource [3], Super-NaturalInstructions [61, 50], Self-instruct [59], UnnaturalInstructions [26], OPT-IML [29], UnifiedSKG[67], OIG/Chip2 [32], Alpaca [55], Vicuna [10], Koala [20] y Self-instruct-GPT-4 [45].

**Chatbots**

Muchos modelos de seguimiento de instrucciones están estructurados como chatbots basados en el diálogo, a menudo utilizando el aprendizaje por refuerzo a partir de la retroalimentación humana (RLHF) [11] o generando datos a partir de un modelo existente para entrenar con retroalimentación del modelo de IA (RLAIF) [5]. Los enfoques y conjuntos de datos incluyen Anthropic-HH [2, 4], Open Assistant [31], LaMDA [56] y Sparrow [21]. Nosotros no utilizamos el aprendizaje por refuerzo, pero nuestro mejor modelo, Guanaco, está ajustado con interacciones de chat multiturno del conjunto de datos Open Assistant, que fue diseñado para ser utilizado para el entrenamiento RLHF [31]. Para la evaluación de chatbots, se han desarrollado enfoques que utilizan GPT-4 en lugar de la costosa anotación humana [10, 45]. Nosotros mejoramos estos enfoques centrándonos en una configuración de evaluación más fiable.

## 8 Limitaciones y discusión

Hemos mostrado pruebas de que nuestro método, QLORA, puede replicar el rendimiento del ajuste fino completo de 16 bits con un modelo base de 4 bits y adaptadores de bajo rango (LoRA). A pesar de estas pruebas, no establecimos que QLORA pueda igualar el rendimiento del ajuste fino completo de 16 bits a escalas de 33.000 y 65.000 millones. Debido a los inmensos costes de recursos, dejamos este estudio para futuros trabajos.

Otra limitación es la evaluación de los modelos de ajuste fino de instrucciones. Aunque proporcionamos evaluaciones sobre MMLU, el benchmark Vicuña y el benchmark OA, no evaluamos sobre otros benchmarks como BigBench, RAFT y HELM, y no se garantiza que nuestras evaluaciones se generalicen a estos benchmarks. Por otro lado, realizamos un estudio muy amplio sobre MMLU y desarrollamos nuevos métodos para evaluar chatbots.

A partir de las pruebas presentadas, parece que el rendimiento de estos benchmarks probablemente depende de lo similares que sean los datos de ajuste fino a los datos del benchmark. Por ejemplo, FLAN v2 es similar a MMLU, pero diferente a los benchmarks de chatbot, y viceversa para el conjunto de datos Chip2, y ambos modelos puntúan en consecuencia en los benchmarks MMLU y Vicuña. Esto pone de manifiesto que no solo se necesitan mejores benchmarks y una mejor evaluación, sino que hay que tener cuidado con lo que se está evaluando en primer lugar. ¿Queremos crear modelos que funcionen bien en el conocimiento de la escuela secundaria y la universidad o queremos que funcionen bien en la capacidad de conversación de los chatbots? ¿Quizás algo más? Dado que siempre es más fácil evaluar sobre un benchmark existente que crear uno nuevo, ciertos benchmarks pueden dirigir a la comunidad hacia una determinada dirección. Como comunidad, debemos asegurarnos de que los benchmarks midan lo que nos importa.

Aunque proporcionamos una evaluación detallada del rendimiento general de los chatbots, otra limitación es que solo hacemos una evaluación limitada de la IA responsable de Guanaco. Evaluamos la probabilidad de que Guanaco-65B genere una secuencia de tokens socialmente sesgada en comparación con otros modelos en la Tabla 8. Vemos que la puntuación media en Guanaco-65B es mucho menor que en otros modelos preentrenados en bruto. Como tal, parece que el ajuste fino en el conjunto de datos OASST1 reduce el sesgo del modelo base LLaMA. Aunque estos resultados son alentadores, no está claro si Guanaco también lo hace bien cuando se evalúa en otros tipos de sesgos. Dejamos la evaluación adicional del análisis de sesgos en Guanaco y chatbots similares para futuros trabajos.

Una limitación adicional es que no evaluamos diferentes precisiones de bits, como el uso de modelos base de 3 bits, u otros métodos de adaptadores. Además de LoRA, existe una amplia variedad de métodos de ajuste fino eficiente de parámetros (PEFT) que han demostrado funcionar bien. Sin embargo, no está claro si estos métodos se escalan a modelos grandes. Utilizamos LoRA porque muchos resultados establecieron su robustez, pero otros adaptadores podrían producir un mejor rendimiento. Dado que el ajuste fino después de la cuantización parece recuperar la mayor parte de la información que se pierde durante la cuantización, esto podría permitir una cuantización mucho más agresiva. Por ejemplo, la cuantización GPTQ de 3 bits del modelo base con LoRA también podría producir un rendimiento de ajuste fino completo de 16 bits después del ajuste fino.

## 9 Implicaciones más amplias

Nuestro método de ajuste fino QLORA es el primero que permite el ajuste fino de modelos de parámetros de 33.000 millones en una sola GPU de consumo y de modelos de parámetros de 65.000 millones en una sola GPU profesional, sin degradar el rendimiento en relación con una línea base de ajuste fino completo. Hemos demostrado que nuestro mejor modelo de 33.000 millones entrenado en el conjunto de datos Open Assistant puede rivalizar con ChatGPT en el benchmark Vicuña. Dado que el ajuste fino de instrucciones es una herramienta esencial para transformar los LLMs preentrenados en bruto en chatbots similares a ChatGPT, creemos que nuestro método hará que el ajuste fino sea generalizado y común, en particular para los investigadores que tienen menos recursos, una gran victoria para la accesibilidad de la tecnología NLP de vanguardia. QLORA puede considerarse como un factor de igualación que ayuda a cerrar la brecha de recursos entre las grandes corporaciones y los pequeños equipos con GPU de consumo.

Otra fuente potencial de impacto es la implantación en teléfonos móviles. Creemos que nuestro método QLORA podría permitir el hito crítico de hacer posible el ajuste fino de LLMs en teléfonos y otros entornos de bajos recursos. Aunque ya se había demostrado que los modelos de 7.000 millones podían ejecutarse en teléfonos, QLORA es el primer método que permitiría el ajuste fino de estos modelos. Estimamos que con un iPhone 12 Plus, QLORA puede ajustar finamente 3 millones de tokens por noche mientras el teléfono se está cargando. Aunque los modelos de 7.000 millones ajustados finamente no alcanzan la calidad de ChatGPT, creemos que la calidad es lo suficientemente buena como para permitir nuevas aplicaciones que antes no eran posibles debido a problemas de privacidad o de calidad de los LLM. QLORA puede ayudar a permitir un uso de los LLMs que preserve la privacidad, en el que los usuarios puedan poseer y gestionar sus propios datos y modelos, al tiempo que facilita la implantación de los LLMs.

Sin embargo, el ajuste fino es una tecnología de doble uso que puede utilizarse indebidamente para causar daños. El uso generalizado de LLMs tiene peligros conocidos [8, 6], pero creemos que igualar el acceso a una tecnología que se está convirtiendo rápidamente en omnipresente permitirá un análisis mejor y más independiente que mantener el poder de los LLMs en manos de grandes corporaciones que no publican modelos ni código fuente para su auditoría.

Con todo, creemos que QLORA tendrá un impacto positivo en general al hacer que el ajuste fino de LLMs de alta calidad sea mucho más accesible y esté al alcance de todos.

## Agradecimientos

Agradecemos a Aditya Kusupati, Ofir Press, Ashish Sharma, Margaret Li, Raphael Olivier, Zihao Ye y Evangelia Spiliopoulou sus valiosos comentarios. Nuestra investigación se vio facilitada por la avanzada infraestructura computacional, de almacenamiento y de red del sistema de supercomputación Hyak de la Universidad de Washington. Agradecemos al equipo de Hyak que haya garantizado un funcionamiento sin problemas. Agradecemos a los beta testers de la biblioteca bitsandbytes, en particular a Alex Birch y Alyssa Vance. Agradecemos a Younes Belkada su ayuda con la integración de nuestro software en la pila de transformadores Hugging Face.