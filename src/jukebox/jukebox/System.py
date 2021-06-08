#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger('jb.system')


class system_control:
    def __init__(self):
        self.init = 1

    def shutdown():
        logger.info("shutdown")
        return ({'object': 'system', 'method': 'shutdown'})

    def reboot():
        logger.info("reboot")
        return ({'object': 'system', 'method': 'reboot'})

    def settings_get(self, param):
        return ({})

    def settings_set(self, param):
        return ({})

    def settings_getall(self, param):
        return ({})
