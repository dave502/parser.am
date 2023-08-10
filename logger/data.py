headers = ['doc_id',
           'in_db',
           'status_id',
           'old_status_id',
           'unaccounted_status',
           'active',
           'region',
           'report_check_act_link',
           'report_date',
           'report_project_date_start',
           'report_project_date_end',
           'url',
           ]


def get_row_data(**doc):
    row_data = [
        doc['id'],
        doc['in_db'],
        doc['status_id'],
        doc['old_status_id'],
        doc['status'] if not doc['status_id'] else "",
        doc.get('active'),
        doc['region'],
        doc.get('report_check_act_link'),
        doc.get('report_date'),
        doc.get('report_project_date_start'),
        doc.get('report_project_date_end'),
        doc['url'],
    ]
    return row_data
