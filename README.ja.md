# miNER

固有表現抽出の評価をするpython用ライブラリ

固有表現の既知未知に分けた評価，固有表現自体の抽出が可能です


## Support

- Tagging Scheme
    - IOB2
    - BIOES
- metrics
    - precision
    - recall
    - f1


## Requirements

- python3


## Installation

```shell
pip install git+https://github.com/Andolab/miNER#egg=miNER
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
>>> m.return_predict_named_entities()
{'known': {'PSN': ['花子'], 'LOC': ['東京']}, 'unknown': {'PSN': ['太郎', '山田'], 'LOC': ['東京駅', '東京スカイツリー']}}
```

#### Methods

|  method  |  description  |
| ---- | ---- |
|  default\_report(print\_)  |  固有表現抽出の結果を返す. もし， print\_=True なら，結果をコンソール上に出力します．  |
|  known\_only\_report(print\_)  |  既知の固有表現に対する抽出結果を返す．  |
|  unknown\_only\_report(print\_)  |  未知の固有表現抽出に対する抽出結果を返す．  |
|  return\_predict\_named\_entities()  |  推定したラベルに対する固有表現を返す．  |
|  return\_answer\_named\_entities()  |  正解のラベルに対する固有表現を返す．  |


## License

MIT
