import importlib
import sys
import wave
from types import SimpleNamespace
from unittest.mock import MagicMock, call

import pytest

import jukebox.plugs as plugin


def _passthrough_decorator(obj=None, **ignored_kwargs):
    if obj is None:
        return lambda decorated: decorated
    return obj


@pytest.fixture
def alsawave(monkeypatch):
    pcm = MagicMock()
    alsaaudio = SimpleNamespace(
        PCM=MagicMock(return_value=pcm),
        PCM_FORMAT_U8=1,
        PCM_FORMAT_S16_LE=2,
        PCM_FORMAT_S24_3LE=3,
        PCM_FORMAT_S32_LE=4,
    )
    monkeypatch.setitem(sys.modules, 'alsaaudio', alsaaudio)
    monkeypatch.setattr(plugin, 'register', _passthrough_decorator)
    monkeypatch.setattr(plugin, 'initialize', _passthrough_decorator)
    monkeypatch.setattr(plugin, 'finalize', _passthrough_decorator)
    monkeypatch.setattr(plugin, 'atexit', _passthrough_decorator)
    monkeypatch.setattr(plugin, 'tag', _passthrough_decorator)

    sys.modules.pop('components.jingle.alsawave', None)
    sys.modules.pop('components.jingle', None)
    module = importlib.import_module('components.jingle.alsawave')
    monkeypatch.setattr(
        module.cfg,
        'setndefault',
        lambda *keys, value: value,
    )
    yield module, alsaaudio, pcm
    sys.modules.pop('components.jingle.alsawave', None)
    sys.modules.pop('components.jingle', None)


def _write_wave(path):
    with wave.open(str(path), 'wb') as output:
        output.setnchannels(1)
        output.setsampwidth(1)
        output.setframerate(8)
        output.writeframes(b'\x01\x02')


def test_wave_playback_closes_pcm_after_writing(alsawave, tmp_path):
    module, alsaaudio, pcm = alsawave
    filename = tmp_path / 'jingle.wav'
    _write_wave(filename)

    module.AlsaWave._play_wave_core(str(filename))

    alsaaudio.PCM.assert_called_once_with(
        channels=1,
        rate=8,
        format=alsaaudio.PCM_FORMAT_U8,
        periodsize=1,
        device='default',
    )
    assert pcm.method_calls == [
        call.write(b'\x01'),
        call.write(b'\x02'),
        call.close(),
    ]


def test_wave_playback_closes_pcm_after_write_failure(alsawave, tmp_path):
    module, ignored_alsaaudio, pcm = alsawave
    filename = tmp_path / 'jingle.wav'
    _write_wave(filename)
    pcm.write.side_effect = RuntimeError('write failed')

    with pytest.raises(RuntimeError, match='write failed'):
        module.AlsaWave._play_wave_core(str(filename))

    pcm.close.assert_called_once_with()
