"""Rename/move fetched files into the canonical `COUNTRY_VISATYPE` filenames.
If the canonical file already exists, the original file will be removed.
Run: python src/rename_fetched_files.py from repository root.
"""
import os
import shutil

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CLEANED = os.path.join(BASE, 'data', 'cleaned_policies')

mapping = {
    'www_ice_gov_sevis.txt': 'US_SEVIS.txt',
    'studyinthestates_dhs_gov.txt': 'US_F1_STUDYINTHESTATES.txt',
    'travel_state_gov_content_travel_en_us_visas_study_student_visa_html.txt': 'US_F1_STATE_STUDENT_VISA.txt',
    'www_dol_gov_agencies_eta_foreign_labor_programs_h_1b.txt': 'US_H1B_DOL.txt',
    'travel_state_gov_content_travel_en_us_visas_tourism_visit_visitor_html.txt': 'US_B1B2_STATE_VISITOR.txt',
    'www_uscis_gov_i_129f.txt': 'US_K1_USCIS_I129F.txt',
    'www_uscis_gov_policy_manual.txt': 'US_POLICY_MANUAL_USCIS.txt',
    'travel_state_gov_content_travel_en_us_visas_visa_information_resources_wait_times_html.txt': 'US_STATE_WAIT_TIMES.txt'
}

for src, dst in mapping.items():
    src_path = os.path.join(CLEANED, src)
    dst_path = os.path.join(CLEANED, dst)
    try:
        if not os.path.exists(src_path):
            print('Source not found, skipping:', src)
            continue
        # If destination exists, remove source
        if os.path.exists(dst_path):
            print('Destination exists; removing source:', src)
            os.remove(src_path)
        else:
            print('Moving', src, '->', dst)
            shutil.move(src_path, dst_path)
    except Exception as e:
        print('Failed to move', src, '->', dst, 'Error:', e)

print('Done')
