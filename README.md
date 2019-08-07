# miNER

A python library for NER (Named Entity Recognition) evaluation

We can evaluate the performance of NER by distinguishing between known entities and unknown entities using this library.


## Support

- Tagging Scheme
    - IOB2
    - BIOES
    - BIOUL
- metrics
    - precision
    - recall
    - f1


## Requirements

- python3
- cython


## Installation

```shell
pip install mi-ner
```


## Usage

#### Sample

```python
>>> from miner import Miner
>>> answers = [
    'B-PSN O O B-LOC O O O O'.split(' '),
    'B-PSN I-PSN O O B-LOC I-LOC O O O O'.split(' '),
    'S-PSN O O S-PSN O O B-LOC I-LOC E-LOC O O O O'.split(' ')
]
>>> predicts = [
    'B-PSN O O B-LOC O O O O'.split(' '),
    'B-PSN B-PSN O O B-LOC I-LOC O O O O'.split(' '),
    'S-PSN O O O O O B-LOC I-LOC E-LOC O O O O'.split(' ')
]
>>> sentences = [
    '花子 さん は 東京 に 行き まし た'.split(' '),
    '山田 太郎 君 は 東京 駅 に 向かい まし た'.split(' '),
    '花子 さん と ボブ くん は 東京 スカイ ツリー に 行き まし た'.split(' '),
]
>>> knowns = {'PSN': ['花子'], 'LOC': ['東京']} # known words (words included in training data)
>>> m = Miner(answers, predicts, sentences, knowns)
>>> m.default_report(True)
	precision    recall    f1_score   num
PSN	 0.500        0.500     0.500      4
LOC	 1.000        1.000     1.000      3
{'PSN': {'precision': 0.5, 'recall': 0.5, 'f1_score': 0.5, 'num': 4}, 'LOC': {'precision': 1.0, 'recall': 1.0, 'f1_score': 1.0, 'num': 3}}
>>> m.return_predict_named_entities()
{'known': {'PSN': ['花子'], 'LOC': ['東京']}, 'unknown': {'PSN': ['太郎', '山田'], 'LOC': ['東京駅', '東京スカイツリー']}}
```

#### Methods

|  method  |  description  |
| ---- | ---- |
|  default\_report(print\_)  |  return result of named entity recognition. if print\_=True, showing result   |
|  known\_only\_report(print\_)  |  return result of known named entity recognition.  |
|  unknown\_only\_report(print\_)  |  return result of unknown named entity recognition.  |
|  return\_predict\_named\_entities()  |  return named entities along predicted label(predicts). |
|  return\_answer\_named\_entities()  |  return named entities along answer label(answer). |
|  return\_miss\_labelings() | return miss labeling sentences. |
|  segmentation\_score(mode) | show parcentages of matching answer and predict labels.  if `known` or` unknown` for `mode`, return labeling accuracy for known or unknown NE. |


## License

MIT
