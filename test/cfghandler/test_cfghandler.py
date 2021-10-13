import sys
import os
# In case this is run locally from
sys.path.append(os.path.abspath('../../src/jukebox'))

import jukebox.cfghandler as cfghandler # noqa
from ruamel.yaml import YAML # noqa

ref_dict = {'l1': {'key1': 'value1'}, 'tl': 'number2'}

ref_yaml = """\
l1:
    key1: value1
tl: number2
"""


def test_ordereddict_getn():
    yaml = YAML(typ='rt')
    cfg = cfghandler.ConfigHandler('test_ordereddict_getn')
    cfg.config_dict(yaml.load(ref_yaml))

    assert 'value1' == cfg.getn('l1', 'key1', default='other')
    assert 'kk4' == cfg.getn('l1', 'key4', default='kk4')
    assert 'kk5' == cfg.getn('l1', 'key7', 'extra5', 'sub7', default='kk5')
    assert yaml.load(ref_yaml)['l1'] == cfg.getn('l1', default='other')


def test_ordereddict_setndefault():
    yaml = YAML(typ='rt')
    cfg = cfghandler.ConfigHandler('test_ordereddict_setndefault')
    cfg.config_dict(yaml.load(ref_yaml))

    assert 'newly' == cfg.setndefault('l1', 'n2', 'n3', 'n4', value='newly')
    ref1 = cfg.getn('l1', 'n2', 'n3')
    assert ref1 == cfg.setndefault('l1', 'n2', 'n3', value='should_not_be_new')
    assert 'newly' == cfg.getn('l1', 'n2', 'n3', 'n4')


def test_modified():
    cfg = cfghandler.get_handler('test_modified')
    assert False is cfg.is_modified()
    cfg.config_dict(ref_dict)
    assert False is cfg.is_modified()
    cfg.setndefault('l2', value='a_new_value')
    assert True is cfg.is_modified()
    cfg.clear_modified()
    assert False is cfg.is_modified()


def test_contains():
    cfg = cfghandler.get_handler('test_contains')
    cfg.config_dict(ref_dict)
    assert True == ('l1' in cfg)
    assert False == ('nonono' in cfg)
    assert False == ('key1' in cfg)


def test_lock():
    # Not a real lock test, but simply checking if functions come back ok
    cfg = cfghandler.get_handler('test_lock')
    cfg.config_dict(ref_dict)
    cfg.acquire()
    cfg['l1']['nested1'] = 'lkdr'
    cfg.release()


def test_context():
    # Not a real lock test, but simply checking if functions come back ok
    cfg = cfghandler.get_handler('test_context')
    cfg.config_dict(ref_dict)
    with cfg:
        cfg['l1']['nested1'] = 'lkdr1'
        cfg['l1']['nested2'] = 'lkdr2'
        cfg['l1']['nested3'] = 'lkdr3'


def test_mutable():
    cfg = cfghandler.get_handler('test_mutable')
    cfg.config_dict(ref_dict)
    v = cfg.get('l1')
    v.setdefault('key2', 'anew2')
    assert 'anew2' == cfg.getn('l1', 'key2')


def test_ordereddict_mutable():
    yaml = YAML(typ='rt')
    cfg = cfghandler.ConfigHandler('test_ordereddict_mutable')
    cfg.config_dict(yaml.load(ref_yaml))
    v = cfg.get('l1')
    v.setdefault('key2', 'anew2')
    assert 'anew2' == cfg.getn('l1', 'key2')


if __name__ == '__main__':
    test_ordereddict_getn()
    test_ordereddict_setndefault()
    test_modified()
    test_contains()
    test_lock()
    test_context()
