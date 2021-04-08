from misc.simplecolors import colors


def input_int(prompt, blank=None, min=None, max=None,
              prompt_color=None, prompt_hint=False) -> int:
    if min is not None and max is not None:
        if max < min:
            raise ValueError(f"min '{min}' must be smaller equal than max '{max}'")
    if prompt_hint:
        prompt = prompt + f" [{min}..{max}"
        if blank is not None:
            prompt = prompt + f", default={blank}"
        prompt = prompt + "] "
    if prompt_color:
        prompt = prompt_color + prompt + colors.reset
    while True:
        inp_raw = input(prompt)
        try:
            inp_int = int(inp_raw)
        except ValueError:
            if blank is not None and len(inp_raw) == 0:
                return blank
            else:
                print(f"Not a valid number: '{inp_raw}'")
        else:
            if min is not None and inp_int < min:
                print(f"Value must be >= {min}!")
                continue
            if max is not None and inp_int > max:
                print(f"Value must be <= {max}!")
                continue
            return inp_int


def input_yesno(prompt, blank=None,
                prompt_color=None, prompt_hint=False) -> bool:
    res_yes = ['y', 'yes', 't', 'true']
    res_no = ['n', 'no', 'f', 'false']
    if prompt_hint:
        if blank is None:
            prompt = prompt + " [y/n] "
        elif blank:
            prompt = prompt + " [Y/n] "
        else:
            prompt = prompt + " [y/N] "
    if prompt_color:
        prompt = prompt_color + prompt + colors.reset
    while True:
        inp_raw = input(prompt).lower()
        if inp_raw in res_yes:
            return True
        elif inp_raw in res_no:
            return False
        elif blank is not None and len(inp_raw) == 0:
            return blank
        print(f"Not a valid input: '{inp_raw}'. Please enter one of {res_yes + res_no}")

