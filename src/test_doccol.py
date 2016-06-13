import os
import shutil

from doccol import DocumentCollection

if __name__ == '__main__':

    col_path = r'C:\Users\nshearer\Desktop\temp\col'
    col = DocumentCollection(col_path)

    doc_path = r'C:\Users\nshearer\Desktop\temp\Banner Finance TRM Supplement 8.9.pdf'

    del_path = r'C:\Users\nshearer\Desktop\temp\col\documents\Banner_Documents\Banner_Finance_TRM_Supplement_8_9_pdf'
    if os.path.exists(del_path):
        shutil.rmtree(del_path)

    # Create a document
    doc = col.new('Banner Documents', 'Banner Finance TRM Supplement 8.9.pdf')
    doc.p.set(
        title = 'Banner Finance TRM Supplement 8.9.pdf',
        module = 'Banner Finance',
        version = '8.9.0',
        docfile = col.data_types.attachment(attach=doc_path)
    )

    # List documents
    # for doc in col.list_docs(domain='Banner Documents'):
    #     print "%s (%s)" % (doc.properties.title, doc.properties.module)

    # Update property
    # doc = col.get("Banner Documents", "Banner Finance TRM Supplement 8.9.pdf")
    # doc.p.set(test_var = col.data_types.list(['a', 'b', 'c']))


    # Copy out attachment
    # doc = col.get("Banner Documents", "Banner Finance TRM Supplement 8.9.pdf")
    # doc.p.docfile.copy_to(os.path.join(
    #     r'C:\Users\nshearer\Desktop\temp',
    #     'COPY.' + doc.p.docfile.filename))


    # Delete file attachment
    doc = col.get("Banner Documents", "Banner Finance TRM Supplement 8.9.pdf")
    doc.p.set(docfile = col.data_types.attachment(attach=doc_path))
    doc.p.del_prop('docfile')
    doc.p.del_prop('version')

    col.del_doc("Banner Documents", "Banner Finance TRM Supplement 8.9.pdf")