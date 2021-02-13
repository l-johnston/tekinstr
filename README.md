![Azure](https://img.shields.io/azure-devops/build/l-johnston/6e771e18-5f42-4d10-ad6b-fc4b0e10acef/9)
![PyPI](https://img.shields.io/pypi/v/tekinstr)
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