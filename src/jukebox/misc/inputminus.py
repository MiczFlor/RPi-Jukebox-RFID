"""
Zero 3rd-party dependency module for user prompting

Yes, there are modules out there to do the same and they have more features.
However, this is low-complexity and has zero dependencies
"""
from misc.simplecolors import Colors


def input_int(prompt, blank=None, min=None, max=None,
              prompt_color=None, prompt_hint=False) -> int:
    """
    Request an integer input from user

    :param prompt: The prompt to display
    :param blank: Value to return when user just hits enter. Leave at None, if blank is invalid
    :param min: Minimum valid integer value (None disables this check)
    :param max: Maximum valid integer value (None disables this check)
    :param prompt_color: Color of the prompt. Color will be reset at end of prompt
    :param prompt_hint: Append a 'hint' with [min...max, default=xx] to end of prompt
    :return: integer value read from user input
    """
    if min is not None and max is not None:
        if max < min:
            raise ValueError(f"min '{min}' must be smaller equal than max '{max}'")
    if prompt_hint:
        prompt = prompt + f" [{min}..{max}"
        if blank is not None:
            prompt = prompt + f", default={blank}"
        prompt = prompt + "] "
    if prompt_color:
        prompt = prompt_color + prompt + Colors.reset
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
    """
    Request a yes / no choice from user

    Accepts multiple input for true/false and is case insensitive

    :param prompt: The prompt to display
    :param blank: Value to return when user just hits enter. Leave at None, if blank is invalid
    :param prompt_color: Color of the prompt. Color will be reset at end of prompt
    :param prompt_hint: Append a 'hint' with [y/n] to end of prompt. Default choice will be capitalized
    :return: boolean value read from user input
    """
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
        prompt = prompt_color + prompt + Colors.reset
    while True:
        inp_raw = input(prompt).lower()
        if inp_raw in res_yes:
            return True
        elif inp_raw in res_no:
            return False
        elif blank is not None and len(inp_raw) == 0:
            return blank
        print(f"Not a valid input: '{inp_raw}'. Please enter one of {res_yes + res_no}")


def msg_highlight(msg, color=Colors.lightblue, deliminator_length=79):
    print(f"\n{color}" + "*" * deliminator_length)
    print(msg)
    print("*" * deliminator_length + f"{Colors.reset}")
