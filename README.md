# `tekinstr`


## Installation
```linux
$ pip install tekinstr
```  

## Usage

```python
>>> from tekinstr import CommChannel
>>> with CommChannel("<ip address>") as tek:
...     wf = tek.oscilloscope.read("CH1")
>>> import matplotlib.pyplot as plt
>>> plt.plot(*wf.to_xy())
[<matplotlib.lines.Line2D at ...>]
>>> plt.show()
```  

## Documentation