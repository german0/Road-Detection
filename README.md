# Road-Detection
Dado como input imagens de satélite, detetar estradas.

**Autores** 

*André Germano A71150*

*Sofia Carvalho A76658*

**Software Utilizado**

*OpenCV*

*QGIS*

**Referências**

http://www.mdpi.com/2072-4292/7/7/8779

http://geopyspark.readthedocs.io/en/latest/index.html

http://www.gdal.org/frmt_sentinel2.html

## Introdução

 O objetivo deste trabalho passa por, dadas imagens de satélite provenientes do projeto Europeu *Copernicus*, recolhidas por satélites *Sentinel-2*, identificar estradas e comparar os resultados obtidos com estradas que efetivamente existem.
 Para isto, foram implementadas técnicas de processamento de imagem para permitir segmentar estradas a partir das imagens de satélite dadas. De seguida, os resultados obtidos foram comparados com dados de estradas reais descarregados a partir do *OpenStreetMap*.

## Desenvolvimento

 Uma estrada é caracterizada pelo seu comprimento, largura e continuidade, que se intersetam em cruzamentos e têm uma cor acinzentada. Como *input*, são fornecidas imagens no formato *.jp2*. Este formato trata-se de um formato de compressão que permite obter um aumento da qualidade das imagens, quando comparadas com imagens noutros formatos. Como este tipo de imagens fornece informações muito detalhadas, possuem uma alta complexidade de processamento. Assim, foi necessário recorrer à ferramenta *GDal* que, em conjunto com outras ferramentas disponíveis em *Python*, possibilitou a leitura e processamento das mesmas.

 O conjunto de imagens possui uma resolução espacial de 10 metros e quatro dessas imagens representam a refletância da superfície nas bandas B02, B03, B04* e *B08*, bandas essas que correspondem ao domínio de frequências azul, verde, vermelho e infra-vermelho, respetivamente. Para além destas, há também uma imagem *TCI* que contém as cores reais da fotografia retirada pelo satélite, uma *WVP (water vapor map)* e, por fim, uma *AOT (aerosol optical thickness map)*.

### 1 - Pré-processamento

 Para a deteção de estradas, e analisando a informação apresentada em cada um dos três canais anteriormente referidos, optou-se por utilizar a imagem *TCI*, uma vez que esta é construída a partir das bandas *B02* (azul), *B03* (verde) e *B04* (vermelho).

 Começou-se por transformar a imagem para um domínio em *grayscale*, de forma a facilitar o seu processamento. De seguida, de forma a simplificar a segmentação da zona pretendida, foi aplicada uma função de aumento de contraste adaptativa (a função *CLAHE*), com o recurso a um histograma. Além disso, foi aplicada uma correção *gamma*, que se trata de uma operação não linear que permite ajustar a iluminância através da expressão *power law*. Após aplicar estes ajustes, o contraste entre a estrada e os elementos que compõem o fundo é mais notável.

### 2 - Thresholding global adaptativo

 Após o pré-processamento, seguiu-se a segmentação das zonas da imagem com maior interesse. De forma a conseguir obter os resultados pretendidos, a intensidade da imagem foi dividida em quatro regiões de análise, baseadas na média de intensidades da imagem (M). A região A inclui píxeis com valores de intensidade que estão entre o valor mais baixo da intensidade e a metade da média de intensidades, correspondendo a zonas com carros escuros, sombras e lagos. A região B tem pixeis com domínio de intensidades entre metade da média de píxeis até à média M e indentifica objetos como árvores e relvado. A região C inclui valores de intensitade entre M e metade do valor máximo de intensidade, sendo possível indentificar estradas de alcatrão. A última região D, com os píxeis presentes na restante gama de valores, indentifica também estradas de alcatrão e veículos mais claros, nuvens e algumas casas. Dito isto, para os passos seguintes foram segmentadas as regiões C e D.

![alt text](/img/histograma.png)

### 3 - Algoritmo de deteção de zonas de interesse
 Após a segmentação das zonas da imagem com maior interesse, foi necessário criar um algoritmo para detetar *bright spots*. Este permite detetar nuvens e algumas casas que não são de interesse para o trabalho. Essas zonas serão retiradas da imagem.
  Este algoritmo é codificado na função **detect_bright**, onde se começa por obter um elemento estruturante, que corresponde a uma elipse. De seguida, aplica-se um esbatimento com uma função guassiana. Após isto, é feito um *threshold* binário à imagem esbatida e é aplicada uma erosão seguida de uma dilatação à imagem esbatida e com a aplicação do *threshold*. Retornam-se apenas os píxeis que correspondem a píxeis claros.

  Encontra-se na imagem seguinte um exemplo do resultado obtido por esta função.

<p float="center">
  <img src="/img/o2.png" width="400" />
  <img src="/img/clouds.png" width="400" /> 
</p>  

### 4 - Segmentação
 Após isso, ou seja, depois de obtidas todas as regiões de interesse, é necessário aplicar algumas operações morfológicas que permitirão remover componentes irrelevantes. Assim, a imagem é dividida em várias porções, para facilitar a segmentação dessas zonas de interesse. A segmentação é obtida através da combinação de operações morfológicas, operações essas codificadas na função **morphology**. Nas operações morfológicas, as operações de *closing* e *thining* são a base do processamento da imagem. 
 Inicialmente, começou-se por aplicar um *closing* à imagem, para retirar alguns falsos positivos e ligar algumas zonas da imagem (porque uma das características das estradas é o facto de serem contínuas). Seguidamente, foi feito o *labeling*, que permite segmentar as zonas de maior interesse da imagem. Por fim, é feito o *thining* para se obter apenas a linha central das estradas, isto é, em vez de ser mostrada toda a estrada, apenas se visualiza a estrada com 1 píxel de largura. 

 Segmentados todos os elementos com maior interesse, seguidos do respetivo *thining*, foi possível obter a silhueta de estradas que é pretendida no resultado final. Uma vez que, como foi dito anteriormente, uma estrada é identificada pela sua conectividade, foi aplicada uma ténica de *skeletization* de forma a preservar a continuidade e conectividade dos componentes ligados e, ao mesmo tempo, remover os píxeis de *foreground*. Isto foi codificado na função **skeleton**. *Skeletization* permite diminuir a grossura dos objetos e funciona como um *edge detector*, reduzindo todas as linhas para linhas com apenas 1 píxel de largura através de um algoritmo desenvolvido de *thining*. Este é o algoritmo que permitirá reduzir as linhas obtidas no resultado do *edge detector* para linhas com apenas 1 píxel de largura. *Thining* é normalmente aplicado apenas a imagens binárias, e produz outra imagem binária como resultado.
 
### Resultados
Para se analisar os resultados obtidos, foi feita uma comparação visual e concluiu-se que os resultados são semelhantes ao que era suposto obter.

De seguida, apresentam-se alguns dos resultados obtidos. Em cada linha, da esquerda para a direita, são apresentadas a imagem original, a imagem pré-processada com os ajustamentos de contraste e a segmentação final.

<p float="left">
  <img src="/img/o2.png" width="400" />
  <img src="/img/p2.png" width="400" /> 
  <img src="/img/s2.png" width="400" />
</p>

<p float="left">
  <img src="/img/o3.png" width="400" />
  <img src="/img/p3.png" width="400" /> 
  <img src="/img/s3.png" width="400" />
</p>

<p float="left">
  <img src="/img/o9.png" width="400" />
  <img src="/img/p9.png" width="400" /> 
  <img src="/img/s9.png" width="400" />
</p>

Os resultados são as imagens que tão na pasta img, mas são bué grandes as imagens.
depois botamos imagens mai tarde.

### API
 **• read_image** - função que permite ler a imagem *TCI* (imagem escolhida porque é construída a partir das bandas *B02* (azul), *B03* (verde) e *B04* (vermelho)) como um *array*.
 
 **• mean** - função que calcula a média dos valores da imagem que não correspondem a píxeis pretos.
 
 **• detect_bright** - função que deteta as partes claras da imagem, aplicando erosão e dilatação. 
 
 **• adaptative_thresholding** - função que codifica o *thresholding* global adaptativo apresentado acima.
 
 **• compare_images** - função que apresenta duas imagens lado a lado, sendo a da esquerda a imagem original e a da direita a imagem com a aplicação do laplaciano.
 
 **• adjust_gamma** - função que permite fazer o ajuste na iluminação da imagem, através de uma *lookup table*. 
 
 **• pre_process** - função de aumento de contraste adaptativa (uso da função *CLAHE*), para simplificar a segmentação da zona pretendida. Para este fim, usou-se como recurso o histograma da imagem *TCI*. 
  
 **• skeleton** - esta função aplica o efeito de *thining* na imagem segmentada, retornando uma máscara com todos os segmentos que têm apenas 1 píxel de comprimento. É nesta função que são aplicadas a erosão e a dilatação, para obter o resultado pretendido. 
 
 **• labeling** - função que retira apenas as zonas de maior interesse, através dos componentes ligados. Retorna os dois componentes ligados com maior comprimento.
 
 **• morphology** -  nesta função são aplicadas várias operações morfológicas para que seja possível remover algum ruído e alguns segmentos de estrada incorretamente detetados, como é o caso de *bright spots*. De notar que são retiradas, por exemplo, as nuvens da imagem. 
 
 **• interval** - a função *interval* transforma o domínio de uma matriz num domínio entre os valores 0 e 255.
 
 **• process** - esta é a principal função implementada, uma vez que é através desta função que são chamadas todas as anteriores de forma a aplicar as transformações desejadas à imagem. Começa-se por fazer um pré-processamento da imagem e é-lhe aplicada um *thresholding* adaptativo. Após isso, são retirados os *bright spots* e, por fim, são apresentadas 3 imagens lado a lado: a imagem original, a pré-processada e a final, para o resultado obtido poder ser visualmente apelativo.

## Conclusão
O trabalho realizado permitiu aprofundar conhecimentos de processamento de imagem e de visualização de informação geométrica com o auxílio da ferramenta QGIS. Permitiu também analisar as imagens, ou produtos, que o satélite Sentinel fornece (tal como informações metereológicas) e qual a relevância dessa informação para a segmentação de estradas.

Dito isto, aquando da resolução do projeto proposto, surgiram algumas dificuldades relativamente ao processamento destas imagens, uma vez que a sua resolução não é a indicada para segmentação devido ao baixo contraste presente nas mesmas e à resolução espacial. Para obter melhores resultados seria necessário, em primeiro lugar, um menor número de nuvens presente em cada imagem e uma distância mínima menor entre dois objetos (resolução espacial menor). 

Apesar das dificuldades apresentadas anteriormente acerca da resolução deste projeto, o grupo pensa ter conseguido construir um projeto que vai de encontro ao esperado e que permitiu aprofundar os conhecimentos adquiridos nesta Unidade Curricular.
