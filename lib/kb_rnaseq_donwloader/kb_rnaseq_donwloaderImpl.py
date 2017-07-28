# -*- coding: utf-8 -*-
#BEGIN_HEADER
import os
import json
from kb_rnaseq_donwloader.RNASeqDownloaderUtils import RNASeqDownloaderUtils
#END_HEADER


class kb_rnaseq_donwloader:
    '''
    Module Name:
    kb_rnaseq_donwloader

    Module Description:
    A KBase module: kb_rnaseq_donwloader
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "1.0.1"
    GIT_URL = "https://github.com/Tianhao-Gu/kb_rnaseq_donwloader.git"
    GIT_COMMIT_HASH = "60853405bd1ef038ed0b6d0ec0ba492dea318c63"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.config = config
        self.config['SDK_CALLBACK_URL'] = os.environ['SDK_CALLBACK_URL']
        self.config['KB_AUTH_TOKEN'] = os.environ['KB_AUTH_TOKEN']
        #END_CONSTRUCTOR
        pass


    def export_rna_seq_alignment_as_bam(self, ctx, params):
        """
        :param params: instance of type "ExportParams" (input and output
           structure functions for standard downloaders) -> structure:
           parameter "input_ref" of String
        :returns: instance of type "ExportOutput" -> structure: parameter
           "shock_id" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN export_rna_seq_alignment_as_bam
        print '--->\nRunning kb_rnaseq_downloader.export_rna_seq_alignment_as_zip\nparams:'
        params['rna_seq_type'] = 'RNASeqAlignment'
        params['download_file_type'] = 'bam'
        print json.dumps(params, indent=1)

        rna_seq_downloader = RNASeqDownloaderUtils(self.config)
        output = rna_seq_downloader.download_RNASeq_Alignment(params)
        #END export_rna_seq_alignment_as_bam

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method export_rna_seq_alignment_as_bam return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def export_rna_seq_alignment_as_sam(self, ctx, params):
        """
        :param params: instance of type "ExportParams" (input and output
           structure functions for standard downloaders) -> structure:
           parameter "input_ref" of String
        :returns: instance of type "ExportOutput" -> structure: parameter
           "shock_id" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN export_rna_seq_alignment_as_sam
        print '--->\nRunning kb_rnaseq_downloader.export_rna_seq_alignment_as_zip\nparams:'
        params['rna_seq_type'] = 'RNASeqAlignment'
        params['download_file_type'] = 'sam'
        print json.dumps(params, indent=1)

        rna_seq_downloader = RNASeqDownloaderUtils(self.config)
        output = rna_seq_downloader.download_RNASeq_Alignment(params)
        #END export_rna_seq_alignment_as_sam

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method export_rna_seq_alignment_as_sam return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def export_rna_seq_expression_as_zip(self, ctx, params):
        """
        :param params: instance of type "ExportParams" (input and output
           structure functions for standard downloaders) -> structure:
           parameter "input_ref" of String
        :returns: instance of type "ExportOutput" -> structure: parameter
           "shock_id" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN export_rna_seq_expression_as_zip
        print '--->\nRunning kb_rnaseq_downloader.export_rna_seq_expression_as_zip\nparams:'
        params['rna_seq_type'] = 'RNASeqExpression'
        print json.dumps(params, indent=1)

        rna_seq_downloader = RNASeqDownloaderUtils(self.config)
        output = rna_seq_downloader.download_RNASeq(params)
        #END export_rna_seq_expression_as_zip

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method export_rna_seq_expression_as_zip return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def export_rna_seq_differential_expression_as_zip(self, ctx, params):
        """
        :param params: instance of type "ExportParams" (input and output
           structure functions for standard downloaders) -> structure:
           parameter "input_ref" of String
        :returns: instance of type "ExportOutput" -> structure: parameter
           "shock_id" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN export_rna_seq_differential_expression_as_zip
        print '--->\nRunning kb_rnaseq_downloader.export_rna_seq_differential_expression_as_zip\nparams:'
        params['rna_seq_type'] = 'RNASeqDifferentialExpression'
        print json.dumps(params, indent=1)

        rna_seq_downloader = RNASeqDownloaderUtils(self.config)
        output = rna_seq_downloader.download_RNASeq(params)
        #END export_rna_seq_differential_expression_as_zip

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method export_rna_seq_differential_expression_as_zip return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
