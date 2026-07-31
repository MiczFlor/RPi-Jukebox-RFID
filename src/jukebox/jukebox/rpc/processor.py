# -*- coding: utf-8 -*-
"""Transport-neutral processing for Jukebox RPC requests."""

import copy
import logging
import time
from collections.abc import Mapping

import jukebox.plugs as plugs

logger = logging.getLogger('jb.rpc.processor')

REQUEST_KEYS = frozenset({
    'args',
    'as_thread',
    'id',
    'kwargs',
    'method',
    'package',
    'plugin',
    'tsp',
})


def _error_response(message, request_id=None):
    response = {'error': {'code': -1, 'message': message}}
    if request_id is not None:
        response['id'] = request_id
    return response


def _parse_timestamp(timestamp):
    if timestamp is None:
        return None, None
    try:
        return int(timestamp), None
    except (TypeError, ValueError, OverflowError):
        return None, "Invalid parameter 'tsp'."


def _execute(request):
    package = request.get('package')
    plugin = request.get('plugin')
    if package is None:
        return None, "Missing mandatory parameter 'package'."
    if plugin is None:
        return None, "Missing mandatory parameter 'plugin'."

    try:
        result = plugs.call(
            package,
            plugin,
            request.get('method'),
            args=request.get('args', ()),
            kwargs=request.get('kwargs', {}),
            as_thread=request.get('as_thread', False),
        )
    except Exception as call_error:
        return None, f"{call_error.__class__.__name__}: {call_error}"
    return result, None


def process_request(client_request, received_at_ns=None):
    """Execute an RPC request and return its response envelope.

    The request is copied before any values are passed to plugin code so the
    caller's dictionary, including nested ``args`` and ``kwargs``, is retained.
    """
    if not isinstance(client_request, Mapping):
        return _error_response("RPC request must be an object.")

    try:
        request = copy.deepcopy(dict(client_request))
    except Exception as error:
        return _error_response(f"Invalid RPC request: {error}")

    if received_at_ns is None:
        received_at_ns = time.time_ns()

    request_id = request.get('id')
    timestamp_ns, error = _parse_timestamp(request.get('tsp'))
    if error is None:
        result, error = _execute(request)
    else:
        result = None

    unknown_keys = set(request) - REQUEST_KEYS
    if unknown_keys:
        logger.warning(f"Ignoring unknown request keys: {sorted(unknown_keys)}")

    if error is not None:
        logger.error(f"RPC request got error: {error}")
        response = _error_response(error, request_id)
    elif request_id is not None:
        response = {'result': result, 'id': request_id}
    else:
        response = {'result': None}

    if timestamp_ns is not None:
        response['total_processing_time'] = (received_at_ns - timestamp_ns) / 1000000

    return response
