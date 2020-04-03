"""Test MSO4041B"""
# pylint: disable=all
import matplotlib.pyplot as plt
from tekinstr import CommChannel

cc = CommChannel("10.2.128.17")
tek = cc.get_instrument()
data = tek.oscilloscope.read("CH1")
plt.plot(*data.to_xy())
plt.show()
cc.close()
