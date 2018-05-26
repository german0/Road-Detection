# Road-Detection
Dado como input imagens de satélite, detetar estradas.

**Autores** 

*André Germano A71150*

*Sofia Carvalho A7*

**Software Utilizado**

*OpenCV*

*QGIS*

**Referências**

http://www.mdpi.com/2072-4292/7/7/8779

http://geopyspark.readthedocs.io/en/latest/index.html

http://www.gdal.org/frmt_sentinel2.html

## Introdução

 O objetivo deste trabalho passa por, dadas imagens de satélite do projeto Europeu *Copernicus* recolhidas por satélites *Sentinel-2*, identificar estradas e comparar os resultados obtidos com estradas que efetivamente existem.
 Para isto foram implementadas técnicas de processamento de imagem de forma a segmentar estradas a partir das imagens de satélite dadas e de seguida os resultados obtidos foram comparados com dados de estradas reais descarregados a partir do *OpenStreetMap*.

## Desenvolvimento

Uma estrada é caracterizada pelo seu comprimento, largura, continuidade, que se intersetam em cruzamentos e cor acinzentada. Como *input*, São fornecidas imagens no formato *.jp2* que se trata de um formato de compressão que permite o aumento de qualidade de imagens comparativamente a imagens em outros formatos. Como fornecem informações muito detalhadas, possuem uma complexidade alta de processamento, recorremos portanto à ferramenta *GDal* que, em conjunto com outras ferramentas disponíveis em *Python* possibilitou a leitura e processamento das imagens.

O conjunto de imagens possui uma resolução espacial de 10 metros, 4 dessas imagens representam a refletância de superfície para as bandas B02, B03, B04* e *B08* que correspondem ao domínio de frequências azul, verde, vermelho e infra-vermelho. Para além destas temos também uma imagem *TCI* que contém as cores reais da fotografia retirada pelo satélite, *WVP (water vapor map)* e *AOT (aerosol optical thickness map)*.

### Pré-processamento

Para a deteção de estradas e analisando a informação apresentada em cada um dos três canais em cima referidos optámos por utilizar a imagem *TCI* uma vez que é construida a partir das bandas *B02* (azul), *B03* (verde) e *B04* (vermelho).

Começámos por transformar a imagem para um domínio em grayscale de forma a facilitar o seu processamento e de seguida, de forma a simplificar a segmentação da zona pretendida foi aplica uma função de aumento de contraste adaptativa (*CLAHE*) com o recurso a um histograma, bem como uma correção gamma que se trata de uma operação não linear de ajuste de iluminância através da expressão *power law*. Após aplicar estes ajustes o contraste entre a estrada e os elementos que compõem o fundo é mais notável.

### Thresholding global adaptativo

Após pré-processamento passamos para a segmentação de zonas de maior interesse da imagem. De forma a conseguir obter os resultados pretendidos a intensidade da imagem é dividida em 4 regiões de análise, baseadas na média de intensidades da imagem (M). A região A inclui píxeis com valores de intensidade entre o valor mais baixo da intensidade e a metade da média de intensidades, correspondendo a zonas com carros escuros, sombras e lagos. A região B tem pixeis com domínio de intensidades entre metade da média de píxeis até à média M e indentifica objetos como árvores e relvado. A região C inclui valores de intensitade entre M e metade do valor máximo de intensidades, sendo possível indentificar estradas de alcatrão. A última região D, com os restantes píxeis indentifica também estradas de alcatrão bem como veículos mais claros, núvens e algumas casas. Dito isto, para os passos seguintes foram segmentadas as regiões C e D.

![alt text](https://github.com/german0/Road-Detection/blob/master/histograma.png)

### Operações Morfológicas

Depois de obtidas as regiões de interesse, são necessárias algumas operações morfológicas de forma a remover componentes irrelevantes. Nas operações morfológicas as operações de dilatação e erosão são a base do processamento de imagem. Inicialmente foi aplicada um *opening* da imagem, que se trata de uma erosão seguida de uma dilatação, o que permitiu obter casas e nuvens de maior dimensão e visto que não se tratam de componentes de interesse, foram posteriormente removidos da imagem.

Após feita esta remoção de componentes de grande dimensão, foi executado um *closing* da imagem obtida, para obter o efeito inverso do passo anterior ou seja, remover componentes de pequena dimensão.

Removidos os elementos com menor interesse, conseguimos obter a silhueta de estradas pretendidas no resultado final. Uma vez que, como foi dito anteriormente, uma estrada é identificada pela sua conectividade, foi aplicada uma ténica de *skeletization* de forma a preservar a continuidade e conectividade dos componentes ligados e ao mesmo tempo remover píxeis de *foreground*.

*Skeletization* permite diminuir a grossura de objetos e funciona como um *edge detector*, reduzindo todas as linhas para linhas com apenas 1 pixel de grossura através de um algoritmo de transformação *hit-and-miss*. Após analisados alguns algoritmos implementados de *thining*, foi decidido utilizar o algoritmo *Zhang-Suen Thinning algorithm* visto que se trata do algoritmo mais utilizado e remove, em cada iteração, os segmentos redundantes até atingir o resultado pretendido, resultado esse que é verificado comparando o total de píxeis sobre os píxeis segmentados até então.


