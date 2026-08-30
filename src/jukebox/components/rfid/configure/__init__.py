import logging
import os
import importlib
import subprocess

import jukebox.cfghandler
from misc.simplecolors import Colors
import misc.inputminus as pyil


logger = logging.getLogger()

NO_RFID_READER = 'No RFID Reader'

#: Reader modules that have no usable module defaults and therefore CANNOT be
#: configured with an empty 'config: null' entry (device selection, GPIO pin
#: selection, ...). During a non-interactive installation they are configured
#: from explicit reader parameters (RFID_READER_PARAMS) or, when no parameters
#: are supplied, from their automatic defaults (e.g. auto-detecting a uniquely
#: connected device). If neither is possible, a RuntimeError with a clear
#: message is raised instead of writing an unusable entry that would make the
#: jukebox daemon fail at startup.
INTERACTIVE_ONLY_READERS = frozenset({'generic_usb', 'generic_nfcpy', 'rc522_spi'})


def reader_install_dependencies(reader_path: str, dependency_install: str) -> None:
    """
    Install dependencies for the selected reader module

    :param reader_path: Path to the reader module
    :parameter dependency_install: how to handle installing of dependencies
                                   'query': query user (default)
                                   'auto': automatically
                                   'no': don't install dependencies

    """
    if dependency_install != 'no':
        if os.path.exists(reader_path + '/requirements.txt'):
            # The python dependencies (if any)
            print("\nInstalling/Checking Python dependencies  ...\n")
            if dependency_install == 'auto' or pyil.input_yesno("Install Python dependencies?", blank=True,
                                                                prompt_color=Colors.lightgreen, prompt_hint=True):
                print(f"{'=' * 80}")
                quiet_level = '-q' if logger.isEnabledFor(logging.DEBUG) else ''
                subprocess.run(f"pip install --upgrade {quiet_level} -r requirements.txt", cwd=reader_path,
                               shell=True, check=False)
                print(f"\n{'=' * 80}\nInstalling dependencies ... done!")
        if os.path.exists(reader_path + '/setup.inc.sh'):
            # The shell dependencies/settings (if any)
            print("\n\nExecuting shell support commands by executing setup.inc.sh (i.e. configure system settings)...")
            if dependency_install == 'auto' or pyil.input_yesno("Auto-configure system settings?", blank=True,
                                                                prompt_color=Colors.lightgreen, prompt_hint=True):
                print(f"{'=' * 80}")
                subprocess.run('./setup.inc.sh', cwd=reader_path,
                               shell=True, check=False)
                print(f"\n{'=' * 80}\nExecuting shell support commands  ... done!\n")


def reader_load_module(reader_name):
    """
    Load the module for the reader_name

    A ModuleNotFoundError is unrecoverable, but we at least want to give some hint how to resolve that to the user
    All other errors will NOT be handled. Modules that do not load due to compile errors have other problems

    :param reader_name: Name of the reader to load the module for
    :return: module
    """
    try:
        reader_module = importlib.import_module('components.rfid.hardware.' + reader_name + '.' + reader_name, 'pkg.subpkg')
    except ModuleNotFoundError as e:
        # This can have two reasons:
        # (1) The reader_type module itself cannot be found (for whatever unfathomable reason after all the checks above)
        # (2) The reader_type module has sub-dependencies which cannot be found
        if e.name == reader_name + '.' + reader_name:
            logger.critical(f"No reader module found in directory '{reader_name}'!\n\n")
        else:
            logger.critical(f"\n\n{'=' * 80}\n"
                            f"Sub-dependencies in '{reader_name}' not fulfilled. This is an unrecoverable error!\n"
                            f"{e.msg}\n"
                            f"{'=' * 80}\n"
                            "This usually means some dependencies are not installed.\n"
                            "If this script is called with -d a, an attempt will be made to install the dependencies "
                            "automatically\n"
                            "You may install the dependencies manually before re-executing this script by:\n"
                            "'$ pip install -r requirements.txt' in the reader's submodule directory and \n"
                            "'$ ./setup.inc.sh'\n"
                            "In case of doubt reboot!\n\n"
                            f"{'=' * 80}\n")
        # There is no possible graceful recovery from this
        raise e
    return reader_module


def _get_reader_descriptions(reader_dirs: list[str]) -> dict[str, tuple[str, str]]:
    # Try to load the description modules from all valid directories (as this has no dependencies)
    # If unavailable, use placeholder description
    reader_descriptions = {}
    for reader_type in reader_dirs:
        reader_description_module_name = ''
        reader_description = ''
        if reader_type == NO_RFID_READER:
            # Add Option to not add a RFid Reader
            reader_description_module_name = reader_type
            reader_description = reader_type
        else:
            reader_description_module_name = f"{reader_type + '/' + reader_type + '.py'}"
            try:
                reader_description_module = (importlib.import_module('components.rfid.hardware.' + reader_type
                                                                        + '.description', 'pkg.subpkg'))
                reader_description = reader_description_module.DESCRIPTION
            except ModuleNotFoundError:
                # The developer for this reader simply omitted to provide a description module
                # Or there is no valid module in this directory, despite correct naming scheme.
                # But this we will only find out later, because we want to be as lenient as possible
                # and don't already load and check reader modules the user is
                # not selecting (and thus no interested in)
                logger.warning(f"No module 'description.py' available for reader subpackage '{reader_type}'")
                reader_description = '(No description provided!)'
            except AttributeError:
                # The module loaded ok, but has no identifier 'DESCRIPTION'
                logger.warning(f"Module 'description.py' of reader subpackage '{reader_type}' is missing 'DESCRIPTION'. "
                            f"Spelling error?")
                reader_description = '(No description provided!)'
        reader_descriptions[reader_type] = (reader_description, reader_description_module_name)
    return reader_descriptions


def query_user_for_reader(dependency_install='query') -> dict:
    """
    Ask the user to select a RFID reader and prompt for the reader's configuration

    This function performs the following steps, to find and present all available readers to the user

    - search for available reader subpackages
    - dynamically load the description module for each reader subpackage
    - queries user for selection
    - if no_dep_install=False, install dependencies as given by requirements.txt and execute setup.inc.sh of subpackage
    - dynamically load the actual reader module from the reader subpackage
    - if selected reader has customization options query user for that now
    - return configuration

    There are checks to make sure we have the right reader modules and they are what we expect.
    The are as few requirements towards the reader module as possible and everything else is optional
    (see reader_template for these requirements)
    However, there is no error handling w.r.t to user input and reader's query_config. Firstly, in this script
    we cannot gracefully handle an exception that occurs on reader level, and secondly the exception will simply
    exit the script w/o writing the config to file. No harm done.

    This script expects to reside in the directory with all the reader subpackages, i.e it is part of the rfid-reader package.
    Otherwise you'll need to adjust sys.path

    :parameter dependency_install: how to handle installing of dependencies
                                   'query': query user (default)
                                   'auto': automatically
                                   'no': don't install dependencies
    :return: nested dict with entire configuration that can be read into ConfigParser
    :rtype: dict as {section: {parameter: value}}
    """

    package_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/../hardware')
    logger.debug(f"Package location: {package_dir}")
    # For known included readers, specify manual order
    included_readers = [NO_RFID_READER, 'generic_usb', 'rdm6300_serial', 'rc522_spi', 'pn532_i2c_py532', 'fake_reader_gui']
    # Get all local directories (i.e subpackages) that conform to naming/structuring convention (except known readers)
    # Naming convention: modname/modname.py
    additional_readers = [x for x in os.listdir(package_dir)
                   if (os.path.isdir(package_dir + '/' + x)
                       and os.path.exists(package_dir + '/' + x + '/' + x + '.py')
                       and os.path.isfile(package_dir + '/' + x + '/' + x + '.py')
                       and not x.endswith('template_new_reader')
                       and x not in included_readers)]
    reader_dirs = [*included_readers, *sorted(additional_readers, key=lambda x: x.casefold())]

    logger.debug(f"reader_dirs = {reader_dirs}")

    reader_descriptions = _get_reader_descriptions(reader_dirs)

    # Prepare the configuration collector with the base values
    config_dict = {'rfid': {'readers': {}}}

    # Ask the user to configure new RFID readers until he has enough of it
    reader_select_name = []
    while True:
        # List all modules and query user
        print("Choose Reader Module from list:\n")
        for idx, (des, mod) in enumerate(reader_descriptions.values()):
            print(f" {Colors.lightgreen}{idx:2d}{Colors.reset}: {Colors.lightcyan}{Colors.bold}{des:40s}{Colors.reset} "
                  f"(Module: {mod})")
        print("")
        reader_id = pyil.input_int("Reader module number?", min=0, max=len(reader_descriptions) - 1,
                                   prompt_color=Colors.lightgreen, prompt_hint=True)

        # The (short) name of the selected reader module, which is identical to the directory name
        reader_selected = list(reader_descriptions.keys())[reader_id]
        print(f"Reader selected: '{reader_selected}'")
        if reader_selected == NO_RFID_READER:
            logger.debug(f"Entry '{NO_RFID_READER}' selected. skip")
            break

        reader_select_name.append(reader_selected)

        # If this reader has not been selected before, auto install dependencies
        if reader_select_name[-1] not in reader_select_name[:-1]:
            reader_install_dependencies(package_dir + '/' + reader_select_name[-1], dependency_install)

        # Build the config entry for the selected reader: loads the module,
        # validates it, and — in interactive mode — queries reader-specific
        # customization. See _build_reader_config() below.
        config_dict['rfid']['readers'][f'read_{len(reader_select_name) - 1:02d}'] = _build_reader_config(
            reader_select_name[-1], interactive=True)

        if not pyil.input_yesno("\nDo you want to add another RFID reader? ", blank=False,
                                prompt_color=Colors.lightgreen, prompt_hint=True):
            break

    print("\n\nIf you want to configure a Buzzer or LED for detected card swipes\n"
          "please go to the documentation and read the section 'GPIO Recipes'\n")

    return config_dict


def _build_reader_config(reader_name: str, interactive: bool = True, params: dict | None = None) -> dict:
    """Load a reader module and build its config dict entry.

    :param reader_name: directory/module name of the reader (e.g. 'pn532_i2c_py532')
    :param interactive: if True, invoke reader_module.query_customization() to
                        prompt for reader-specific options.
    :param params: reader-specific key/value parameters for the non-interactive
                   path (e.g. from the installer's RFID_READER_PARAMS). Readers
                   in INTERACTIVE_ONLY_READERS use them to configure themselves
                   without any prompts; when params is None they fall back to
                   their automatic defaults (e.g. auto-detecting a uniquely
                   connected device) and raise a RuntimeError with a clear
                   message when no safe default exists.
    :return: dict entry for config_dict['rfid']['readers'][...]
    """
    # Try to load the actual reader module for the first time (and only the
    # selected one!). In case of multiple loads of the same module,
    # import_module only returns the reference to the loaded module.
    # --> No special loop handling necessary.
    reader_module = reader_load_module(reader_name)
    logger.debug(f"Loaded reader module: (Module: {reader_module.__name__} in {reader_module.__file__})")

    # Check loaded module for validity
    # Minimum requirement is a class with name 'ReaderClass'
    # (that is enough testing here, as we cannot check the functionality anyway)
    if 'ReaderClass' not in dir(reader_module):
        logger.error(f"Reader module '{reader_module.__name__}' is missing mandatory class named 'Reader'.")
        raise AttributeError(f"Reader module '{reader_module.__name__}' is missing mandatory class named 'Reader'.")

    # Check if reader module has customization and if yes, query user for that.
    # Readers without a query_customization() function rely on module defaults
    # and work fine without a config block.
    # Readers in INTERACTIVE_ONLY_READERS cannot run with module defaults: they
    # are configured non-interactively from the supplied params or from their
    # automatic defaults (auto-detection). The module raises a clear error when
    # neither is possible, instead of silently writing 'config: null' which
    # would make the jukebox daemon fail at startup.
    reader_params = None
    if 'query_customization' in dir(reader_module):
        if interactive:
            print("\nEntering reader customization\n")
            reader_params = reader_module.query_customization()
        elif reader_name in INTERACTIVE_ONLY_READERS:
            reader_params = reader_module.query_customization(
                defaults=params if params is not None else {})
        else:
            if params:
                logger.warning(f"Module {reader_module.__name__} has no non-interactive "
                               "customization; ignoring the supplied reader params.")
            logger.debug(f"Module {reader_module.__name__}: using module defaults (non-interactive).")
    else:
        logger.debug(f"Module {reader_module.__name__} has no user customization.")
    logger.debug(f"reader_params = {reader_params}")

    return {'module': reader_name,
            'config': reader_params,
            'same_id_delay': 1.0,
            'log_ignored_cards': False,
            'place_not_swipe': {'enabled': False,
                                'card_removal_action': {'alias': 'pause'}}}


def configure_reader(reader_name: str, dependency_install: str = 'auto', params: dict | None = None) -> dict:
    """Configure a single RFID reader without prompting for the reader selection.

    Unlike query_user_for_reader(), this does not present the reader menu;
    the reader is given by its module name. Used by non-interactive installs,
    which call run_register_rfid_reader.py --reader <type> --deps auto --force.

    Readers that require reader-specific values (see INTERACTIVE_ONLY_READERS,
    e.g. 'generic_usb') are configured from the supplied params, or from their
    automatic defaults when params is None. If no safe default exists (e.g.
    several USB readers are connected), a RuntimeError is raised with a clear
    message instead of writing an unusable reader entry.

    :param reader_name: directory/module name of the reader (e.g. 'pn532_i2c_py532')
    :param dependency_install: how to handle installing of dependencies:
                               'query', 'auto' (default) or 'no'
    :param params: dict of reader-specific key/value parameters, or None to use
                   automatic defaults (auto-detection).
    :return: nested dict for write_config(), e.g.
             {'rfid': {'readers': {'read_00': {...}}}}
    """
    package_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/../hardware')
    reader_install_dependencies(package_dir + '/' + reader_name, dependency_install)
    return {'rfid': {'readers': {'read_00': _build_reader_config(
        reader_name, interactive=False, params=params)}}}


def write_config(config_file: str, config_dict: dict, force_overwrite=False) -> None:
    """
    Write configuration to config_file

    :parameter config_file: relative or absolute path to config file
    :parameter config_dict: nested dict with configuration parameters for ConfigParser consumption
    :parameter force_overwrite: overwrite existing configuration file without asking
    """
    if os.path.exists(config_file):
        logger.debug(f"Existing user configuration found at {config_file}")
        if force_overwrite is not True:
            print(f"\n\nExisting configuration found at '{config_file}'.")
            if not pyil.input_yesno("Overwrite?", blank=False, prompt_color=Colors.lightgreen, prompt_hint=True):
                logger.debug("Aborting on user request.")
                print("Aborting...")
                return

    cfg_rfid = jukebox.cfghandler.get_handler('rfid')
    cfg_rfid.config_dict(config_dict)
    jukebox.cfghandler.write_yaml(cfg_rfid, config_file, only_if_changed=False)

    logger.info(f"Writing config file: '{config_file}'.")
