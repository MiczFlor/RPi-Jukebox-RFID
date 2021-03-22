import configparser
import logging
import os
import sys
import importlib
import subprocess

# Create logger
logger = logging.getLogger(os.path.basename(__file__).ljust(20))
logger.setLevel(logging.DEBUG)
# Create console handler and set default level
logconsole = logging.StreamHandler()
logconsole.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S'))
logconsole.setLevel(logging.INFO)
logger.addHandler(logconsole)


def query_user_for_reader()  -> configparser.ConfigParser:
    """Searches for available Reader modules, dynamically loads them, and queries user for selection.
     If selected module has customization options query user for that, too.

    There are checks to make sure we have the right reader modules and they are what we expect.
    The are as few requirements towards the reader module as possible and everything else is optional
    (see reader_template for these requirements)
    However, there is no error handling w.r.t to user input and reader's query_config. Firstly, in this script
    we cannot gracefully handle an exception that occurs on reader level, and secondly the exception will simply
    exit the script w/o writing the config to file. No harm done.

    This script expects to reside in the directory with all the reader module subpackages. Otherwise you'll need
    to adjust sys.path"""

    logger.debug(f"File location: {os.path.dirname(os.path.realpath(__file__))}")
    # Get all local directories that conform to naming/structuring convention
    # Naming convention: modname/modname.py
    reader_dirs = [x for x in os.listdir(os.path.dirname(os.path.realpath(__file__)))
                   if (os.path.isdir(x) and os.path.exists(x + '/' + x + '.py'))]
    logger.debug(f"reader_dirs = {reader_dirs}")

    reader_modules_candidates = []
    for reader_type in reader_dirs:
        try:
            reader_modules_candidates.append(importlib.import_module('..' + reader_type, reader_type + '.subpkg'))
        except ModuleNotFoundError as e:
            logger.error("No reader module found in directory {reader_type}! Ignoring directory. \n\n")

    # Check all loaded modules for validity
    # Minimum requirement is a class with name 'Reader'
    reader_modules = [x for x in reader_modules_candidates if 'Reader' in dir(x)]
    if len(reader_modules_candidates) != len(reader_modules):
        logger.debug(f"Some loaded modules are filtered because no Reader class is available")
        logger.debug(f"Filtered modules: {[x.__name__ for x in reader_modules_candidates if x not in reader_modules]}")

    logger.debug(f"Loaded Reader modules: {reader_modules}")

    # Propagate logger level down to reader module (if available and correctly named)
    for rm in reader_modules:
        try:
            rm.logconsole.setLevel(logconsole.level)
        except AttributeError:
            pass

    # List all modules and query user
    print("Choose Reader Module form list:\n")
    for idx, mod in enumerate(reader_modules):
        description = mod.DESCRIPTION if dir(mod.DESCRIPTION) else 'Description unavailable'
        print(f" {idx:2d}: {description:40s} (Module: {mod.__name__} in {mod.__file__})")
    reader_id = int(input('\nReader module number: '))
    # The selected reader as module
    reader_select_module = reader_modules[reader_id]
    # The name of the selected module that goes into the configuration file
    reader_select_name = reader_select_module.__name__.split('.')[1]

    # Automatically install dependencies for the selected reader module
    if os.path.exists(reader_select_name + '/requirements.txt'):
        print("Installing/Checking dependencies  ...\n")
        quiet_level = '-q' if logconsole.level < logging.DEBUG else ''
        subprocess.run(f"sudo pip3 install --upgrade {quiet_level} -r requirements.txt", cwd=reader_select_name,
                             shell=True, check=False)
        print("\nInstalling dependencies ... done!")
    # Reload module to ensure all freshly installed dependencies are imported
    logger.debug(f"Reloading selected module '{reader_select_module.__name__}' to ensure all dependencies are imported.")
    try:
        importlib.reload(reader_select_module)
    except e:
        logger.error("while reloading '{reader_select_module.__name__}'.\n"
                     "This usually means, some dependencies are not installed.\n"
                     "Ensure these are all installed ($pip3 install -r requirements.txt) in the reader's submodule directory\n\n")
        raise e

    # Check if reader module has customization and if yes, query user for that
    reader_params = None
    if 'query_customization' in dir(reader_select_module):
        reader_params = reader_select_module.query_customization()
    else:
        logger.debug(f"Module {reader_select_name} has no user customization.")

    logger.debug(f"reader_params = {reader_params}")

    # Put it together and write config file
    config = configparser.ConfigParser()
    config.add_section('ReaderType')
    config['ReaderType']['reader_module'] = reader_select_name
    if reader_params:
        config.read_dict({reader_select_name: reader_params})
    return config


def write_config(cfg_file: str, config : configparser.ConfigParser) -> None:
    """Writes configuration to cfg_file
    cfg_file is an absolute path or relative to this (!) file's location
    """
    # Make sure to locate cfg_file relative to this script's location independent of working directory
    if not os.path.isabs(cfg_file):
        cfg_file = os.path.dirname(os.path.realpath(__file__)) + '/' + cfg_file

    with open(cfg_file, 'w') as f:
        config.write(f)
    logger.info(f"Config file written to '{cfg_file}'.")


def load_reader(cfg_file):
    """Read the config file and dynamically loads the corresponding reader module.
    Returns an instance of the reader class from that module"""
    # Add the path for the reader modules to Python's search path
    # such the reader directory is searched after local dir, but before all others
    # Only necessary, if this script is located elsewhere
    # reader_path = os.path.realpath(os.path.realpath(os.path.dirname(__file__)) + '/../components/rfid-reader')
    # sys.path.insert(1, reader_path)
    # logger.debug(f"sys.path = {sys.path}")

    # Make sure to locate cfg_file relative to this script's location independent of working directory
    if not os.path.isabs(cfg_file):
        cfg_file = os.path.dirname(os.path.realpath(__file__)) + '/' + cfg_file

    logger.debug(f"Reading config file: '{cfg_file}'")

    config = configparser.ConfigParser()
    config_file_success = config.read(cfg_file)
    if not config_file_success:
        logger.error(f"Could not read '{cfg_file}'. Please run register device first")
        raise FileNotFoundError(cfg_file)

    reader_type = config['ReaderType'].get('reader_module').lower()
    reader_params = None

    if reader_type in config:
        reader_params = {key: value for key, value in config[reader_type].items()}

    try:
        reader_module = importlib.import_module('..' + reader_type, reader_type + '.subpkg')
    except ModuleNotFoundError as e:
        logger.error("No module found for {reader_type}! Spelling error?\n\n")
        raise e

    # Propagate logger level down to reader module (if available and correctly named)
    try:
        reader_module.logconsole.setLevel(logconsole.level)
    except AttributeError:
        pass

    logger.debug(f"reader_module.__file__ = {reader_module}")
    logger.debug(f"dir(reader_module)     = {dir(reader_module)}")

    return reader_module.Reader(reader_params)

