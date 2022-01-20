import logging
import os
import importlib
import subprocess

import jukebox.cfghandler
from misc.simplecolors import Colors
import misc.inputminus as pyil


logger = logging.getLogger()


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
            print("IMPORTANT for developers: Python dependencies will be installed using "
                  " $ sudo pip3 install --upgrade -r requirements.txt'\n"
                  " i.e. on system level. This is target for the default RPI setup. "
                  "If you do not want that, but rather have them in a local or virtual environment, "
                  "hit No here and manually install the dependencies from your virtual environment\n"
                  " $ pip3 install --upgrade -r requirements.txt'\n"
                  "It is no problem to install them after running this script.\n\n")
            if dependency_install == 'auto' or pyil.input_yesno("Install Python dependencies?", blank=True,
                                                                prompt_color=Colors.lightgreen, prompt_hint=True):
                print(f"{'=' * 80}")
                quiet_level = '-q' if logger.isEnabledFor(logging.DEBUG) else ''
                subprocess.run(f"sudo pip3 install --upgrade {quiet_level} -r requirements.txt", cwd=reader_path,
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
                            "'$ pip3 install -r requirements.txt' in the reader's submodule directory and \n"
                            "'$ ./setup.inc.sh'\n"
                            "In case of doubt reboot!\n\n"
                            f"{'=' * 80}\n")
        # There is no possible graceful recovery from this
        raise e
    return reader_module


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
    included_readers = ['generic_usb', 'rdm6300_serial', 'rc522_spi', 'pn532_i2c_py532', 'fake_reader_gui']
    # Get all local directories (i.e subpackages) that conform to naming/structuring convention (except known readers)
    # Naming convention: modname/modname.py
    reader_dirs = [x for x in os.listdir(package_dir)
                   if (os.path.isdir(package_dir + '/' + x)
                       and os.path.exists(package_dir + '/' + x + '/' + x + '.py')
                       and os.path.isfile(package_dir + '/' + x + '/' + x + '.py')
                       and not x.endswith('template_new_reader')
                       and x not in included_readers)]
    reader_dirs = [*included_readers, *sorted(reader_dirs, key=lambda x: x.casefold())]
    logger.debug(f"reader_dirs = {reader_dirs}")

    # Try to load the description modules from all valid directories (as this has no dependencies)
    # If unavailable, use placeholder description
    reader_description_modules = []
    reader_descriptions = []
    for reader_type in reader_dirs:
        try:
            reader_description_modules.append(importlib.import_module('components.rfid.hardware.' + reader_type
                                                                      + '.description', 'pkg.subpkg'))
            reader_descriptions.append(reader_description_modules[-1].DESCRIPTION)
        except ModuleNotFoundError:
            # The developer for this reader simply omitted to provide a description module
            # Or there is no valid module in this directory, despite correct naming scheme. But this we will only find out
            # later, because we want to be as lenient as possible and don't already load and check reader modules the user is
            # not selecting (and thus no interested in)
            logger.warning(f"No module 'description.py' available for reader subpackage '{reader_type}'")
            reader_descriptions.append('(No description provided!)')
        except AttributeError:
            # The module loaded ok, but has no identifier 'DESCRIPTION'
            logger.warning(f"Module 'description.py' of reader subpackage '{reader_type}' is missing 'DESCRIPTION'. "
                           f"Spelling error?")
            reader_descriptions.append('(No description provided!)')

    # Prepare the configuration collector with the base values
    config_dict = {'rfid': {'readers': {}}}

    # Ask the user to configure new RFID readers until he has enough of it
    reader_select_name = []
    while True:
        # List all modules and query user
        print("Choose Reader Module from list:\n")
        for idx, (des, mod) in enumerate(zip(reader_descriptions, reader_dirs)):
            print(f" {Colors.lightgreen}{idx:2d}{Colors.reset}: {Colors.lightcyan}{Colors.bold}{des:40s}{Colors.reset} "
                  f"(Module: {mod + '/' + mod + '.py'})")
        print("")
        reader_id = pyil.input_int("Reader module number?", min=0, max=len(reader_descriptions) - 1,
                                   prompt_color=Colors.lightgreen, prompt_hint=True)
        # The (short) name of the selected reader module, which is identical to the directory name
        reader_select_name.append(reader_dirs[reader_id])

        # If this reader has not been selected before, auto install dependencies
        if reader_select_name[-1] not in reader_select_name[:-1]:
            reader_install_dependencies(package_dir + '/' + reader_select_name[-1], dependency_install)

        # Try to load the actual reader module for the first time (and only the selected one!)
        # In case of multiple loads of the same module, import_module only returns the reference to the loaded module.
        # --> No special loop handling necessary
        reader_module = reader_load_module(reader_select_name[-1])
        logger.debug(f"Loaded reader module: (Module: {reader_module.__name__} in {reader_module.__file__})")

        # Check loaded module for validity
        # Minimum requirement is a class with name 'ReaderClass'
        # (that is enough testing here, as we cannot check the functionality anyway)
        if 'ReaderClass' not in dir(reader_module):
            logger.error(f"Reader module '{reader_module.__name__}' is missing mandatory class named 'Reader'.")
            raise AttributeError(f"Reader module '{reader_module.__name__}' is missing mandatory class named 'Reader'.")

        # Check if reader module has customization and if yes, query user for that
        reader_params = None
        if 'query_customization' in dir(reader_module):
            print("\nEntering reader customization\n")
            reader_params = reader_module.query_customization()
        else:
            logger.debug(f"Module {reader_module.__name__} has no user customization.")
        logger.debug(f"reader_params = {reader_params}")

        # Add the reader to the config collector
        # config_dict['ReaderType'][f'reader_module{len(reader_select_name)-1:02d}'] = reader_select_name[-1]
        # if reader_params:
        #     config_dict[f'reader_module{len(reader_select_name)-1:02d}'] = reader_params

        # TODO: what if no reader params?
        config_dict['rfid']['readers'][f'read_{len(reader_select_name) - 1:02d}'] = {'module': reader_select_name[-1],
                                                                                     'config': reader_params,
                                                                                     'same_id_delay': 1.0,
                                                                                     'log_ignored_cards': False,
                                                                                     'place_not_swipe':
                                                                                         {'enabled': False,
                                                                                          'card_removal_action':
                                                                                              {'alias': 'pause'}}}

        if not pyil.input_yesno("\nDo you want to add another RFID reader? ", blank=False,
                                prompt_color=Colors.lightgreen, prompt_hint=True):
            break

    print("\n\nIf you want to configure a Buzzer or LED for detected card swipes\n"
          "please go to the documentation and read the section 'GPIO Recipes'\n")

    return config_dict


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
