import configparser
import logging
import os
import sys
import importlib
import subprocess

# Create logger
logger = logging.getLogger(os.path.basename(__file__).ljust(25))
logger.setLevel(logging.DEBUG)
# Create console handler and set default level
logconsole = logging.StreamHandler()
logconsole.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S'))
logconsole.setLevel(logging.INFO)
logger.addHandler(logconsole)


def query_user_for_reader(no_dep_install=False) -> configparser.ConfigParser:
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

    script_dir = os.path.dirname(os.path.realpath(__file__))
    logger.debug(f"File location: {script_dir}")
    # Get all local directories that conform to naming/structuring convention
    # Naming convention: modname/modname.py
    print(f"{os.listdir(os.path.dirname(os.path.realpath(__file__)))}")
    reader_dirs = [x for x in os.listdir(script_dir)
                   if (os.path.isdir(script_dir + '/' + x) and os.path.exists(script_dir + '/' + x + '/' + x + '.py'))]
    logger.debug(f"reader_dirs = {reader_dirs}")

    reader_modules_candidates = []
    # Try to load modules from all valid directories
    # Module not found errors will be handled with "ignore" in case the user is interested in another module
    # All other errors will NOT be handled and cause an exception. Modules that do no compile should not enter the repository!
    for reader_type in reader_dirs:
        try:
            reader_modules_candidates.append(importlib.import_module('..' + reader_type, reader_type + '.subpkg'))
        except ModuleNotFoundError as e:
            # This can have two reasons:
            # (1) The reader_type module itself cannot be found (for whatever unfathomable reason - the file could still be a directory)
            # (2) The reader_type module has sub-dependencies which cannot be found
            # In both cases continue, as it might not be the reader the user is interested in
            if e.name == reader_type + '.' + reader_type:
                logger.error(f"No reader module found in directory '{reader_type}'! Ignoring directory. \n\n")
            else:
                logger.error(f"\n\n{'='*80}\n"
                             f"Sub-dependencies in '{reader_type}' not fulfilled. Ignoring directory.\n"
                             f"{e.msg}\n"
                             f"{'='*80}\n"
                             "This usually means some dependencies are not installed.\n"
                             "By this scripts convention, they should be enclosed in a try-catch block to allow partial "
                             "loading of the module for user query before installing all dependencies.\n"
                             "You may install the dependencies manually before re-executing this script by:\n"
                             "'$ pip3 install -r requirements.txt' in the reader's submodule directory\n\n"
                             f"{'='*80}\n")

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
    if no_dep_install is not True:
        if os.path.exists(reader_select_name + '/requirements.txt'):
            # The python dependencies (if any)
            print("Installing/Checking dependencies  ...\n{'='*80}\n")
            quiet_level = '-q' if logconsole.level < logging.DEBUG else ''
            subprocess.run(f"sudo pip3 install --upgrade {quiet_level} -r requirements.txt", cwd=reader_select_name,
                           shell=True, check=False)
            print(f"\n{'='*80}\nInstalling dependencies ... done!")
            # Reload module to ensure all freshly installed dependencies are imported
            logger.debug(f"Reloading selected module '{reader_select_module.__name__}' to ensure all dependencies are imported.")
            # The module has been loaded before successfully, so it should do so here --> No exception handling necessary
            importlib.reload(reader_select_module)
        if os.path.exists(reader_select_name + '/setup.inc.sh'):
            # The shell dependencies/settings (if any)
            print(f"Executing shell support commands  ...\n{'='*80}\n")
            subprocess.run('./setup.inc.sh', cwd=reader_select_name,
                           shell=True, check=False)
            print(f"\n{'='*80}\nExecuting shell support commands  ... done!\n")

    # Check if reader module has customization and if yes, query user for that
    reader_params = None
    if 'query_customization' in dir(reader_select_module):
        reader_params = reader_select_module.query_customization()
    else:
        logger.debug(f"Module {reader_select_name} has no user customization.")

    logger.debug(f"reader_params = {reader_params}")

    # Put it together and return entire config
    config = configparser.ConfigParser()
    config.add_section('ReaderType')
    config['ReaderType']['reader_module'] = reader_select_name
    if reader_params:
        config.read_dict({reader_select_name: reader_params})
    return config


def write_config(cfg_file: str, config: configparser.ConfigParser, nowarn=False) -> None:
    """Writes configuration to cfg_file
    cfg_file is an absolute path or relative to this (!) file's location
    nowarn disables warning and user poll before overwriting existing configuration
    """
    # Make sure to locate cfg_file relative to this script's location independent of working directory
    if not os.path.isabs(cfg_file):
        cfg_file = os.path.dirname(os.path.realpath(__file__)) + '/' + cfg_file

    if os.path.exists(cfg_file):
        logger.debug(f"Existing user configuration found at {cfg_file}")
        if nowarn is not True:
            print(f"\n\nWARNING: Existing configuration found at '{cfg_file}'.")
            ur = input("Overwrite? [y/N] ")
            if ur.lower() != 'y':
                logger.debug(f"Aborting on user request (response = '{ur}').")
                print("Aborting...")
                return

    with open(cfg_file, 'w') as f:
        config.write(f)
    logger.info(f"Config file written to '{cfg_file}'.")


def load_reader(cfg_file):
    """Read the config file and dynamically load the corresponding reader module.
    Returns the loaded reader module reference and the reader params as tuple"""
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

    return reader_module, reader_params

