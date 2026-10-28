#!/usr/bin/python
# -*- coding: utf-8 -*-

class Credencial:
    def __init__(self):
        self.username = None
        self.passwordHash = None
        self.salt = None
        self.algoritmoHash = None
        self.ultimoCambio = None
