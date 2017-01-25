import os
import json
import shutil
import zipfile
from DataFileUtil.DataFileUtilClient import DataFileUtil

def log(message):
    """Logging function, provides a hook to suppress or redirect log messages."""
    print(message)


class RNASeqDownloaderUtils:

	def __init__(self, config):
		log('--->\nInitializing RNASeqDownloaderUtils instance:\n config: %s' % config)
		self.scratch = config['scratch']
		self.callback_url = config['SDK_CALLBACK_URL']
		self.token = config['KB_AUTH_TOKEN']
		self.dfu = DataFileUtil(self.callback_url, token=self.token)

	def download_RNASeq(self, params):
		"""
		download_RNASeq: download RNASeq Alignment/Expression/DifferentialExpression zip file

		params:
		input_ref: RNASeq object reference ID
		rna_seq_type: one of ['RNASeqAlignment', 'RNASeqExpression', 'RNASeqDifferentialExpression']

		return:
		shock_id: Shock ID of stored zip file
	
		"""
		log('--->\nrunning RNASeqDownloaderUtils.download_RNASeq:\nparams: %s' % params)

		# Validate params 
		self.validate_download_rna_seq_alignment_parameters(params)

		# Download RNASeq zip file
		# RNASeq Alignemnt, Expression and DifferentialExpression has same object_data/handle_data structure
		returnVal = self._download_rna_seq_zip(params.get('input_ref'))

		return returnVal

	def validate_download_rna_seq_alignment_parameters(self, params):
		"""
		validate_download_rna_seq_alignment_parameters: validates params passed to download_rna_seq_alignment method
	
		"""
				
		# check required parameters
		for p in ['input_ref', 'rna_seq_type']:
			if p not in params:
				raise ValueError('"' + p + '" parameter is required, but missing')	

		# check supportive RNASeq types
		valid_rnaseq_types =  ['RNASeqAlignment', 'RNASeqExpression', 'RNASeqDifferentialExpression']
		if params['rna_seq_type'] not in valid_rnaseq_types:
			raise ValueError('Unexpected RNASeq type: %s' % params['rna_seq_type'])

	def _download_rna_seq_zip(self, input_ref):
		"""
		_download_rna_seq_zip: download RNASeq's archive zip file

		returns:
		shock_id: Shock ID of stored zip file

		"""
		
		# get object data
		object_data = self._get_object_data(input_ref)
		log ('---> getting object data\n object_date: %s' % json.dumps(object_data, indent=1))

		# get handle data
		handle = self._get_handle_data(object_data)
		log ('---> getting handle data\n handle data: %s' % json.dumps(object_data, indent=1))

		# make tmp directory for downloading
		dstdir = os.path.join(self.scratch, 'tmp')
		if not os.path.exists(dstdir):
			os.makedirs(dstdir)

		# download original zip file and save to tmp directory
		handle_id = handle.get('hid')
		original_zip_file_path = self._download_original_zip_file(handle_id, dstdir)

		base = os.path.splitext(original_zip_file_path)[0]
		os.rename(original_zip_file_path, base)

		log ('---> loading %s to shock' % base)
		shock_id = self._upload_to_shock(base)

		log('--->\nremoving folder: %s' % dstdir)
		shutil.rmtree(dstdir)

		returnVal = {"shock_id": shock_id}

		return returnVal

	def _get_object_data(self, input_ref):
		"""
		_get_object_data: get object_data using DataFileUtil

		"""

		get_objects_params = {
			'object_refs': [input_ref],
			'ignore_errors': False
		}

		object_data = self.dfu.get_objects(get_objects_params)

		return object_data

	def _get_handle_data(self, object_data):

		"""
		_get_handle_data: get Handle from object_data

		"""

		try:
			handle = object_data.get('data')[0].get('data').get('file')
		except:
			raise ValueError("Unexpected object format. Refer to DataFileUtil.get_objects definition\nobject_data:\n%s" % json.dumps(object_data, indent=1))

		if handle is None:
			raise ValueError("object_data does NOT have Handle(file key)\nobject_data:\n%s" % json.dumps(object_data, indent=1))
		elif handle.get('hid') is None:
			raise ValueError("Handle does have NOT HandleId(hid key)\nhandle_data:\n%s" % json.dumps(handle, indent=1))
		else:
			return handle

	def _download_original_zip_file(self, handle_id, dstdir):
		"""
		_download_original_zip_file: download original archive .zip file using DataFileUtil
		
		"""

		shock_to_file_params = {
			'handle_id': handle_id,
			'file_path': dstdir
		}
		original_zip_file = self.dfu.shock_to_file(shock_to_file_params)

		original_zip_file_path = original_zip_file.get('file_path')

		return original_zip_file_path

	def _upload_to_shock(self, file_path):
		"""
		_upload_to_shock: upload target file to shock using DataFileUtil
	
		"""

		file_to_shock_params = {
			'file_path': file_path
		}
		shock_file = self.dfu.file_to_shock(file_to_shock_params)

		shock_id = shock_file.get('shock_id')

		return shock_id