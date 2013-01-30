#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; mode: python -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: t -*-
# vi: set ft=python sts=4 ts=4 sw=4 noet

import pprint
import requests
from lxml import etree

class Renfe(object):
    """ Extract data from Api Android Renfe's App"""
    
    API_URL = 'http://api.mo2o.com/apps/RenfeApp/'
    
    KERNEL_KEYS = ('name', 'dateTimeUpdate', 'estaciones', 'lineas', 'mapaesquematico', 'mapaesquematicoimg', 'tarifas')
    CONFIG_KEYS = ('Descripcion', 'Lon', 'Lat', 'IconoMapa', 'Tarifas', 'Incidencias')
    
    PARAMS_CONFIG = {'action': 'CONFIG', 'lang': 'ES'}
    
    kernels = {}
    
    def __init__(self):
        self.content = etree.fromstring(requests.get(self.API_URL, params = self.PARAMS_CONFIG).content).find('contents')

        self._parse_config_kernels()
        # self._parse_config_tarifas()
        #incidencias = content.find('incidencias')
        self._parse_kernels()

    def _parse_kernel(self, kernel):
        self.kernels[int(kernel.find('id').text)].update({'content': {key: kernel.find(key).text for key in self.KERNEL_KEYS}})

    def _parse_kernels(self):
        map(self._parse_kernel, self.content.find('nucleos'))

    def _parse_config_kernel(self, kernel):
        self.kernels.update({int(kernel.find('Codigo').text) : {'config': {key.lower(): kernel.find(key).text for key in self.CONFIG_KEYS}}})

    def _parse_config_kernels(self):
        map(self._parse_config_kernel, etree.fromstring(requests.get(self.content.find('config_nucleos').find('file').text).content))

    def _parse_config_tarifa(self, tarifa):
        nc = int(tarifa.find('NC').text)
        tarifa_data = {}
        cr_list = tarifa.findall('CR')
        for cr in cr_list:
            ncr = int(cr.find('NCR').text)
            p_l = float(cr.find('P_L').text)
            p_f = float(cr.find('P_F').text)
            tarifa_data.update({ncr: {'p_l': p_l, 'p_f': p_f}})
        # self.kernels[nc].update({'tarifa': tarifa_data})

    def _parse_config_tarifas(self):
        # http://api.mo2o.com/apps/RenfeApp/contents/maestra_tarifas.xml.gz
        map(self._parse_config_tarifa, etree.fromstring(requests.get(self.content.find('config_tarifas').find('file').text).content)[0])

# http://horarios.renfe.com/cer/horarios/horarios.jsp?nucleo=10&d=60103&df=20130129&hd=24&ho=13&o=60107
pprint.pprint(Renfe().kernels)
