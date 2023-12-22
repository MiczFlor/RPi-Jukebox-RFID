<!-- markdownlint-disable -->

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/misc/simplecolors.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `misc.simplecolors`
Zero 3rd-party dependency module to add colors to unix terminal output 

Yes, there are modules out there to do the same and they have more features. However, this is low-complexity and has zero dependencies 

**Global Variables**
---------------
- **COLORS**

---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/misc/simplecolors.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `resolve`

```python
resolve(color_name: str)
```

Resolve a color name into the respective color constant 

:param color_name: Name of the color :return: color constant 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/misc/simplecolors.py#L48"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `print`

```python
print(
    color: Colors,
    *values,
    sep=' ',
    end='\n',
    file=<_io.TextIOWrapper name='<stdout>' mode='w' encoding='utf-8'>,
    flush=False
)
```

Drop-in replacement for print with color choice and auto color reset for convenience 

Use just as a regular print function, but with first parameter as color 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/misc/simplecolors.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Colors`
Container class for all the colors as constants 







---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
