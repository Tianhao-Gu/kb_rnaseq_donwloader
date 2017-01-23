# -*- coding: utf-8 -*-
import unittest
import os  # noqa: F401
import json  # noqa: F401
import time
import requests

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint  # noqa: F401

from biokbase.workspace.client import Workspace as workspaceService
from kb_rnaseq_donwloader.kb_rnaseq_donwloaderImpl import kb_rnaseq_donwloader
from kb_rnaseq_donwloader.kb_rnaseq_donwloaderServer import MethodContext

class kb_rnaseq_donwloaderTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        user_id = requests.post(
            'https://kbase.us/services/authorization/Sessions/Login',
            data='token={}&fields=user_id'.format(token)).json()['user_id']
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'kb_rnaseq_donwloader',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_rnaseq_donwloader'):
            cls.cfg[nameval[0]] = nameval[1]
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL, token=token)
        cls.serviceImpl = kb_rnaseq_donwloader(cls.cfg)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_kb_rnaseq_donwloader_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})  # noqa
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def test_contructor(self):
        ret = self.getImpl()
        self.assertIsNotNone(ret.config)
        self.assertIsNotNone(ret.config['SDK_CALLBACK_URL'])
        self.assertIsNotNone(ret.config['KB_AUTH_TOKEN'])

    def test_validate_upload_fastq_file_parameters(self):
        invalidate_input_params = {
            'input_ref': '2778/3/1'
        }
        del invalidate_input_params['input_ref']
        with self.assertRaisesRegexp(ValueError, '"input_ref" parameter is required, but missing'):
            self.getImpl().export_rna_seq_alignment_as_zip(self.getContext(), invalidate_input_params)

        with self.assertRaisesRegexp(ValueError, '"input_ref" parameter is required, but missing'):
            self.getImpl().export_rna_seq_expression_as_zip(self.getContext(), invalidate_input_params)

        with self.assertRaisesRegexp(ValueError, '"input_ref" parameter is required, but missing'):
            self.getImpl().export_rna_seq_differential_expression_as_zip(self.getContext(), invalidate_input_params)

    def test_export_rna_seq_alignment_as_zip(self):
        params = {
            'input_ref': '15963/11/1'
        }
        ret = self.getImpl().export_rna_seq_alignment_as_zip(self.getContext(), params)
        self.assertTrue(ret[0].has_key('shock_id'))

    def test_export_rna_seq_expression_as_zip(self):
        params = {
            'input_ref': '15963/16/2'
        }
        ret = self.getImpl().export_rna_seq_alignment_as_zip(self.getContext(), params)
        self.assertTrue(ret[0].has_key('shock_id'))

    def test_export_rna_seq_differential_expression_as_zip(self):
        params = {
            'input_ref': '15963/21/1'
        }
        ret = self.getImpl().export_rna_seq_alignment_as_zip(self.getContext(), params)
        self.assertTrue(ret[0].has_key('shock_id'))
