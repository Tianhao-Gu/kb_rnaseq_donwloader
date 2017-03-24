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
from kb_rnaseq_donwloader.authclient import KBaseAuth as _KBaseAuth
from kb_rnaseq_donwloader.RNASeqDownloaderUtils import RNASeqDownloaderUtils
from mock import patch


class kb_rnaseq_donwloaderTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_rnaseq_donwloader'):
            cls.cfg[nameval[0]] = nameval[1]
        authServiceUrl = cls.cfg.get('auth-service-url',
                                     "https://kbase.us/services/authorization/Sessions/Login")
        auth_client = _KBaseAuth(authServiceUrl)
        cls.user_id = auth_client.get_user(cls.token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': cls.token,
                        'user_id': cls.user_id,
                        'provenance': [
                            {'service': 'kb_rnaseq_donwloader',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL, token=cls.token)
        cls.serviceImpl = kb_rnaseq_donwloader(cls.cfg)
        cls.rna_downloader = RNASeqDownloaderUtils(cls.cfg)
        cls.shockURL = cls.cfg['shock-url']

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    @classmethod
    def delete_shock_node(cls, node_id):
        header = {'Authorization': 'Oauth {0}'.format(cls.token)}
        requests.delete(cls.shockURL + '/node/' + node_id, headers=header,
                        allow_redirects=True)
        print('Deleted shock node ' + node_id)

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

    """
    Please config test.cfg to use CI endpoint
    objects used in this test ('15963/11/1', '15963/16/2' and '15963/21/1') are stored in CI workspace. 
    """
    def test_contructor(self):
        ret = self.getImpl()
        self.assertIsNotNone(ret.config)
        self.assertIsNotNone(ret.config['SDK_CALLBACK_URL'])
        self.assertIsNotNone(ret.config['KB_AUTH_TOKEN'])

    # def test_validate_upload_fastq_file_parameters(self):
    #     invalidate_input_params = {
    #         'input_ref': '15963/11/1'
    #     }
    #     del invalidate_input_params['input_ref']
    #     with self.assertRaisesRegexp(ValueError, '"input_ref" parameter is required, but missing'):
    #         self.getImpl().export_rna_seq_alignment_as_zip(self.getContext(), invalidate_input_params)

    #     with self.assertRaisesRegexp(ValueError, '"input_ref" parameter is required, but missing'):
    #         self.getImpl().export_rna_seq_expression_as_zip(self.getContext(), invalidate_input_params)

    #     with self.assertRaisesRegexp(ValueError, '"input_ref" parameter is required, but missing'):
    #         self.getImpl().export_rna_seq_differential_expression_as_zip(self.getContext(), invalidate_input_params)

    # def test_export_rna_seq_alignment_as_zip(self):
    #     params = {
    #         'input_ref': '15963/11/1'
    #     }
    #     ret = self.getImpl().export_rna_seq_alignment_as_zip(self.getContext(), params)
    #     self.assertTrue(ret[0].has_key('shock_id'))

    #     self.delete_shock_node(ret[0].get('shock_id'))

    # def test_export_rna_seq_expression_as_zip(self):
    #     params = {
    #         'input_ref': '15963/16/2'
    #     }
    #     ret = self.getImpl().export_rna_seq_alignment_as_zip(self.getContext(), params)
    #     self.assertTrue(ret[0].has_key('shock_id'))

    #     self.delete_shock_node(ret[0].get('shock_id'))

    # def test_export_rna_seq_differential_expression_as_zip(self):
    #     params = {
    #         'input_ref': '15963/21/1'
    #     }
    #     ret = self.getImpl().export_rna_seq_alignment_as_zip(self.getContext(), params)
    #     self.assertTrue(ret[0].has_key('shock_id'))

    #     self.delete_shock_node(ret[0].get('shock_id'))

    # def test_RNASeqDownloaderUtils_contructor(self):
    #     self.assertIsNotNone(self.rna_downloader.scratch)
    #     self.assertIsNotNone(self.rna_downloader.callback_url)
    #     self.assertIsNotNone(self.rna_downloader.token)
    #     self.assertIsNotNone(self.rna_downloader.dfu)

    # def test_bad_rna_downloader_params(self):
    #     invalidate_input_params = {
    #         'input_ref': '15963/11/1'
    #     }
    #     with self.assertRaisesRegexp(ValueError, '"rna_seq_type" parameter is required, but missing'):
    #         self.rna_downloader.download_RNASeq(invalidate_input_params)

    #     invalidate_input_params['rna_seq_type'] = 'FACKE TYPE'
    #     with self.assertRaisesRegexp(ValueError, 'Unexpected RNASeq type: FACKE TYPE'):
    #         self.rna_downloader.download_RNASeq(invalidate_input_params)

    def test_bad_ojbect_data(self):
        params = {
            'input_ref': '15963/11/1',
            'rna_seq_type': 'RNASeqAlignment',
            'workspace_name': self.getWsName()
        }

        wrong_ojbect_data_format ={
            "data": [
                {
                    "info":[],
                    "wrong_data":{}
                }
            ]
        }

        with patch.object(RNASeqDownloaderUtils, '_get_object_data', return_value=wrong_ojbect_data_format):
            with self.assertRaisesRegexp(ValueError, 'Unexpected object format. Refer to DataFileUtil.get_objects definition'):
                self.rna_downloader.download_RNASeq(params)

        missing_file_key ={
            "data": [
                {
                    "info":[],
                    "data": {
                        'missing_file_key':
                        {
                            'hid': 'KBH_9387'
                        }
                    }
                }
            ]
        }
        with patch.object(RNASeqDownloaderUtils, '_get_object_data', return_value=missing_file_key):
            with self.assertRaisesRegexp(ValueError, 'object_data does NOT have Handle\(file key\)\nobject_data:'):
                self.rna_downloader.download_RNASeq(params)

        missing_handle_id ={
            "data": [
                {
                    "info":[],
                    "data": {
                        'file':
                        {
                            'missing_hid': 'KBH_9387'
                        }
                    }
                }
            ]
        }
        with patch.object(RNASeqDownloaderUtils, '_get_object_data', return_value=missing_handle_id):
            with self.assertRaisesRegexp(ValueError, 'Handle does have NOT HandleId\(hid key\)\nhandle_data:'):
                self.rna_downloader.download_RNASeq(params)


