![Azure](https://img.shields.io/azure-devops/build/l-johnston/6e771e18-5f42-4d10-ad6b-fc4b0e10acef/9)
![PyPI](https://img.shields.io/pypi/v/tekinstr)
# `tekinstr`


## Installation
```cmd
> pip install tekinstr
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

It is possible to save the screen capture to a network or USB drive.
In this example, a USB memory stick is installed and the current
working directory is 'E:/'. Currently supported on MDO3000 series.
```python
>>> with CommChannel("<ip address>") as tek:
...     tek.oscilloscope.save_image("capture.png")
```

## Currently support models
- MDO3000 series
- MSO4000 series
- TDS3000 series