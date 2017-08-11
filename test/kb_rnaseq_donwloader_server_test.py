# -*- coding: utf-8 -*-
import unittest
import os  # noqa: F401
import json  # noqa: F401
import time
import requests
import shutil
import re

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint  # noqa: F401
from mock import patch

from biokbase.workspace.client import Workspace as workspaceService
from kb_rnaseq_donwloader.kb_rnaseq_donwloaderImpl import kb_rnaseq_donwloader
from kb_rnaseq_donwloader.kb_rnaseq_donwloaderServer import MethodContext
from kb_rnaseq_donwloader.authclient import KBaseAuth as _KBaseAuth
from kb_rnaseq_donwloader.RNASeqDownloaderUtils import RNASeqDownloaderUtils
from GenomeFileUtil.GenomeFileUtilClient import GenomeFileUtil
from ReadsUtils.ReadsUtilsClient import ReadsUtils
from ReadsAlignmentUtils.ReadsAlignmentUtilsClient import ReadsAlignmentUtils
from DataFileUtil.DataFileUtilClient import DataFileUtil


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
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(cls.token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': cls.token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'kb_rnaseq_donwloader',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL)
        cls.serviceImpl = kb_rnaseq_donwloader(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        cls.shockURL = cls.cfg['shock-url']

        suffix = int(time.time() * 1000)
        cls.wsName = "test_kb_rnaseq_donwloader_" + str(suffix)
        cls.wsClient.create_workspace({'workspace': cls.wsName})

        cls.gfu = GenomeFileUtil(cls.callback_url)
        cls.dfu = DataFileUtil(cls.callback_url)
        cls.ru = ReadsUtils(cls.callback_url)
        cls.rau = ReadsAlignmentUtils(cls.callback_url, service_ver='dev')
        cls.rna_downloader = RNASeqDownloaderUtils(cls.cfg)

        cls.prepare_data()

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

    @classmethod
    def prepare_data(cls):
        # upload genome object
        genbank_file_name = 'minimal.gbff'
        genbank_file_path = os.path.join(cls.scratch, genbank_file_name)
        shutil.copy(os.path.join('data', genbank_file_name), genbank_file_path)

        genome_object_name = 'test_Genome'
        cls.genome_ref = cls.gfu.genbank_to_genome({'file': {'path': genbank_file_path},
                                                    'workspace_name': cls.wsName,
                                                    'genome_name': genome_object_name
                                                    })['genome_ref']

        # upload reads object
        reads_file_name = 'Sample1.fastq'
        reads_file_path = os.path.join(cls.scratch, reads_file_name)
        shutil.copy(os.path.join('data', reads_file_name), reads_file_path)

        reads_object_name_1 = 'test_Reads_1'
        cls.reads_ref_1 = cls.ru.upload_reads({'fwd_file': reads_file_path,
                                               'wsname': cls.wsName,
                                               'sequencing_tech': 'Unknown',
                                               'interleaved': 0,
                                               'name': reads_object_name_1
                                               })['obj_ref']

        # upload alignment object
        alignment_file_name = 'accepted_hits.bam'
        alignment_file_path = os.path.join(cls.scratch, alignment_file_name)
        shutil.copy(os.path.join('data', alignment_file_name), alignment_file_path)

        alignment_object_name_1 = 'test_Alignment_1'
        cls.condition_1 = 'test_condition_1'
        destination_ref = cls.wsName + '/' + alignment_object_name_1
        cls.alignment_ref_1 = cls.rau.upload_alignment({'file_path': alignment_file_path,
                                                        'destination_ref': destination_ref,
                                                        'read_library_ref': cls.reads_ref_1,
                                                        'condition': cls.condition_1,
                                                        'library_type': 'single_end',
                                                        'assembly_or_genome_ref': cls.genome_ref
                                                        })['obj_ref']

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        return self.__class__.wsName

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
            'input_ref': 'input_ref'
        }
        del invalidate_input_params['input_ref']
        with self.assertRaisesRegexp(ValueError, '"input_ref" parameter is required, but missing'):
            self.getImpl().export_rna_seq_alignment_as_sam(self.getContext(), 
                                                           invalidate_input_params)

        with self.assertRaisesRegexp(ValueError, '"input_ref" parameter is required, but missing'):
            self.getImpl().export_rna_seq_expression_as_zip(self.getContext(), 
                                                            invalidate_input_params)

        with self.assertRaisesRegexp(ValueError, '"input_ref" parameter is required, but missing'):
            self.getImpl().export_rna_seq_differential_expression_as_zip(self.getContext(), 
                                                                         invalidate_input_params)

    def test_RNASeqDownloaderUtils_contructor(self):
        self.assertIsNotNone(self.rna_downloader.scratch)
        self.assertIsNotNone(self.rna_downloader.callback_url)
        self.assertIsNotNone(self.rna_downloader.token)
        self.assertIsNotNone(self.rna_downloader.dfu)

    def test_bad_rna_downloader_params(self):
        invalidate_input_params = {
            'input_ref': 'input_ref'
        }
        with self.assertRaisesRegexp(ValueError, 
                                     '"rna_seq_type" parameter is required, but missing'):
            self.rna_downloader.download_RNASeq(invalidate_input_params)

        invalidate_input_params['rna_seq_type'] = 'FACKE TYPE'
        with self.assertRaisesRegexp(ValueError, 'Unexpected RNASeq type: FACKE TYPE'):
            self.rna_downloader.download_RNASeq(invalidate_input_params)

    def test_bad_ojbect_data(self):
        params = {
            'input_ref': 'input_ref',
            'rna_seq_type': 'RNASeqAlignment',
            'workspace_name': self.getWsName()
        }

        wrong_ojbect_data_format = {"data": [{"info": [], "wrong_data":{}}]}

        with patch.object(RNASeqDownloaderUtils, 
                          '_get_object_data', 
                          return_value=wrong_ojbect_data_format):
            error_msg = 'Unexpected object format. Refer to DataFileUtil.get_objects definition'
            with self.assertRaisesRegexp(ValueError, error_msg):
                self.rna_downloader.download_RNASeq(params)

        missing_file_key = {"data": [{"info": [], 
                                      "data": {'missing_file_key': {'hid': 'KBH_9387'}}}]}
        with patch.object(RNASeqDownloaderUtils, 
                          '_get_object_data', 
                          return_value=missing_file_key):
            error_msg = 'object_data does NOT have Handle\(file key\)\nobject_data:'
            with self.assertRaisesRegexp(ValueError, error_msg):
                self.rna_downloader.download_RNASeq(params)

        missing_handle_id = {"data": [{"info": [], "data": {'file': {'missing_hid': 'KBH_9387'}}}]}
        with patch.object(RNASeqDownloaderUtils, 
                          '_get_object_data', 
                          return_value=missing_handle_id):
            error_msg = 'Handle does have NOT HandleId\(hid key\)\nhandle_data:'
            with self.assertRaisesRegexp(ValueError, error_msg):
                self.rna_downloader.download_RNASeq(params)

    def test_export_rna_seq_alignment_as_bam(self):
        params = {
            'input_ref': self.alignment_ref_1
        }
        ret = self.getImpl().export_rna_seq_alignment_as_bam(self.getContext(), params)
        self.assertTrue('shock_id' in ret[0])

        result_dir = os.path.join(self.scratch, 'bam_download_result')
        os.makedirs(result_dir)

        shock_to_file_params = {
            'shock_id': ret[0]['shock_id'],
            'file_path': result_dir,
            'unpack': 'unpack'
        }
        shock_file = self.dfu.shock_to_file(shock_to_file_params)['file_path']

        shock_file_dir = os.path.dirname(shock_file)
        result_files = os.listdir(shock_file_dir)

        print result_files
        self.assertTrue(any(re.match('accepted_hits.bam', file) for file in result_files))
        self.assertTrue(any(re.match('\d+_accepted_hits.bai', file) for file in result_files))

        self.delete_shock_node(ret[0].get('shock_id'))

    def test_export_rna_seq_alignment_as_sam(self):
        params = {
            'input_ref': self.alignment_ref_1
        }
        ret = self.getImpl().export_rna_seq_alignment_as_sam(self.getContext(), params)
        self.assertTrue('shock_id' in ret[0])

        result_dir = os.path.join(self.scratch, 'sam_download_result')
        os.makedirs(result_dir)

        shock_to_file_params = {
            'shock_id': ret[0]['shock_id'],
            'file_path': result_dir,
            'unpack': 'unpack'
        }
        shock_file = self.dfu.shock_to_file(shock_to_file_params)['file_path']

        shock_file_dir = os.path.dirname(shock_file)
        result_files = os.listdir(shock_file_dir)

        print result_files
        self.assertTrue(any(re.match('\d+_accepted_hits.bai', file) for file in result_files))
        self.assertTrue(any(re.match('\d+_accepted_hits.sam', file) for file in result_files))

        self.delete_shock_node(ret[0].get('shock_id'))

    def test_fail(self):
        self.assertTrue(False)
