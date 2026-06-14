'''
Batch file
'''
# import os
from pathlib import Path
import os
import pysubsea.abaquspy as abqpy

sens_dict = {'PARAM_sens': [0]}
TEMPLATE_FILENAME = 'example_3_legacy' # 'example_3_current' or 'example_3_legacy'

os.chdir(Path(__file__).parent)

for sens_nb in sens_dict['PARAM_sens']:
    sensitivity_filename = f"{TEMPLATE_FILENAME}_sens{sens_nb}"
    abaqus_input_file_writer = abqpy.AbaqusSensitivity(
        template_filename=TEMPLATE_FILENAME,
        sensitivity_filename=sensitivity_filename,
        param_dict=sens_dict,
        isens=sens_nb
    )
    abaqus_input_file_writer.run()
    # os.system(f'abaqus int j={file_name} ask_delete=off')
