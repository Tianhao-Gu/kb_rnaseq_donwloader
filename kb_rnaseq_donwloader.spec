/*
A KBase module: kb_rnaseq_donwloader
*/

module kb_rnaseq_donwloader {
    /*  input and output structure functions for standard downloaders */
    typedef structure {
        string input_ref;
    } ExportParams;

    typedef structure {
        string shock_id;
    } ExportOutput;

    funcdef export_rna_seq_alignment_as_bam (ExportParams params) returns (ExportOutput output) authentication required;

    funcdef export_rna_seq_alignment_as_sam (ExportParams params) returns (ExportOutput output) authentication required;

    funcdef export_rna_seq_alignment_as_bai (ExportParams params) returns (ExportOutput output) authentication required;

    funcdef export_rna_seq_expression_as_zip (ExportParams params) returns (ExportOutput output) authentication required;

    funcdef export_rna_seq_differential_expression_as_zip (ExportParams params) returns (ExportOutput output) authentication required;

};
