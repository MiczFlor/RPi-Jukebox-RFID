<!-- markdownlint-disable -->

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/misc/inputminus.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `misc.inputminus`
Zero 3rd-party dependency module for user prompting 

Yes, there are modules out there to do the same and they have more features. However, this is low-complexity and has zero dependencies 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/misc/inputminus.py#L10"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `input_int`

```python
input_int(
    prompt,
    blank=None,
    min=None,
    max=None,
    prompt_color=None,
    prompt_hint=False
) → int
```

Request an integer input from user 

:param prompt: The prompt to display :param blank: Value to return when user just hits enter. Leave at None, if blank is invalid :param min: Minimum valid integer value (None disables this check) :param max: Maximum valid integer value (None disables this check) :param prompt_color: Color of the prompt. Color will be reset at end of prompt :param prompt_hint: Append a 'hint' with [min...max, default=xx] to end of prompt :return: integer value read from user input 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/misc/inputminus.py#L52"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `input_yesno`

```python
input_yesno(prompt, blank=None, prompt_color=None, prompt_hint=False) → bool
```

Request a yes / no choice from user 

Accepts multiple input for true/false and is case insensitive 

:param prompt: The prompt to display :param blank: Value to return when user just hits enter. Leave at None, if blank is invalid :param prompt_color: Color of the prompt. Color will be reset at end of prompt :param prompt_hint: Append a 'hint' with [y/n] to end of prompt. Default choice will be capitalized :return: boolean value read from user input 


---

<a href="https://github.com/MiczFlor/RPi-Jukebox-RFID/tree/future3/develop/src/jukebox/src/jukebox/misc/inputminus.py#L87"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `msg_highlight`

```python
msg_highlight(msg, color='\x1b[94m', deliminator_length=79)
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
