#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger('jb.system')


class system_control:
    def __init__(self):
        self.init = 1

    def shutdown(self, param=None):
        logger.info("shutdown")
        return ({})

    def reboot(self, param=None):
        logger.info("reboot")
        return ({})

    def settings_get(self, param):
        return ({})

    def settings_set(self, param):
        return ({})

    def settings_getall(self, param):
        return ({})
