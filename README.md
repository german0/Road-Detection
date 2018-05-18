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

No *paper* fornecido no enunciado, que trata a deteção de rios, um rio é caracterizado pelo seu comprimento, largura, cor azulada padrão de ramificação e continuidade (não são segmentos descontínuos, intercetam-se em algum cruzamento). Tal como neste *paper*, uma estrada possui caracteristicas semelhantes, também estas podem ser caracterizadas pelo seu comprimento, largura e padrão de ramificação, assim sendo, no que toca à segmentação de estradas, estes dois casos apenas diferem na cor, uma vez que as estradas possuem uma cor acizentada.

### Leitura das Imagens

Cada uma das imagens fornecidas encontra-se no formato *.jp2* que corresponde a um formato de compressão que permite um aumento de qualidade comparativamente a imagens no formato *.jpeg*. Como fornecerem informações muito detalhas, possuem uma complexidade alta de processamento, desta forma recorremos à ferramenta *GDal* que, em conjunto com outras ferramentas disponívels em *Python* facilitou a leitura e processamento dessas mesmas imagens.

No caso de estudo foram fornecidas sete imagens *.jp2* com uma resolução espacial de 10 metros. Quatro dessas imagens representam a refletância de superfície para as bandas *B02, B03, B04* e *B08* que correspondem aos canais azul, verde, vermelho e infra-vermelho. Para além destas foi também fornecida a imagem *TCI* que contém as cores reais da fotografia retirada pelo satélite, *WVP (water vapor map)* e *AOT (aerosol optical thickness map)*. 

### Pré-processamento

Para a deteção de estradas e analisando a informação apresentada em cada um dos três canais em cima referidos optámos por utilizar a imagem *TCI* uma vez que é construida a partir das bandas *B02* (azul), *B03* (verde) e *B04* (vermelho).

Depois de visualizar cuidadosamente a imagem, é perceptível que as estradas apresentam uma cor mais acinzentada em relação às nuvens e casas. Como estes dois últimos componentes não são relevantes para o objetivo final do trabalho poderão ser removidos. Para a sua remoção e tendo em conta que a imagem tem grandes dimensões e que cada componente (em relação a toda a imagem) tem pequenas dimensões, foi decidido subdividir a imagem em partes iguais e aplicar, a cada uma, as transformações necessárias.

Para cada uma das partes e de forma a facilitar a segmentação de casas e nuvens foi aplicada uma função de aumento de contraste adaptativa (*CLAHE*) com o recurso a um histograma. De seguida foi efetuado o esbatimento da imagem, seguida da sua binarização, como a função de contraste é adapativa permite que, para cada uma das partes, a deteção de componentes irrelevantes seja mais eficaze. A partir da binarização da imagem foi criada, para cada uma das partes, uma máscara com as mesmas dimensões de cada uma das partes da imagem parcelada (com valores 0 ou 1 para cada pixel), que foi aplicada à imagem segmentada correspondente permitindo remover componentes dispensáveis. Depois de aplicadas as transformações referidas, cada uma das partes foi reunida novamente numa só imagem.

Desta forma, conseguimos retirar da imagem original grande parte dos componentes (com tamanhos consideravelmente grandes) desnecessários, o que facilitou na postetior deteção de estradas.