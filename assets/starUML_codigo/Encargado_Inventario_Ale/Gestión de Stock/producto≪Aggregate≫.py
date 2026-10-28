#!/usr/bin/python
# -*- coding: utf-8 -*-

class Producto ≪aggregate≫:
    def __init__(self):
        self.- id = None
        self.- nombre = None
        self.- stockActual = None
        self.- nivelMinimo = None

    def + registrarIngreso(cant, motivo)(self, ):
        pass

    def + registrarSalida(cant, motivo)(self, ):
        pass
