"""
A simple viewer that shows the flame plots for reading (importing) and writing
for a given io method (xml, hdf5 or sionlib). The flame plots are produced from
the data generated by a CrayPAT-instrumented version of the Nektar++ benchmarker,
FieldIOBenchmarker.
"""

"""
Copyright 2016 Michael Bareford

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import matplotlib.pyplot as plt
from calltree import CrayPATCallTree

arg_cnt = len(sys.argv)
arg = sys.argv

if 3 == arg_cnt or 4 == arg_cnt:
    
    io_method = arg[1]
    core_count = arg[2]
    colour_border = arg[3] if 4 == arg_cnt else 'white'

    table_name = 'Function Calltree View'

    class_name_dict = { 'xml': 'FieldIOXml', 'hdf5': 'FieldIOHdf5', 'sionlib': 'FieldIOSIONlib' }
    if io_method in class_name_dict:
        class_name = class_name_dict[io_method]

        ct_import = CrayPATCallTree('./'+io_method+'/FieldIOBenchmarker-pat-import.out', table_name, class_name + '::v_Import')
        ct_import.plot(class_name + '::Import - ' + core_count + ' cores', colour_border)

        ct_write = CrayPATCallTree('./'+io_method+'/FieldIOBenchmarker-pat-write.out', table_name, class_name + '::v_Write')
        ct_write.plot(class_name + '::Write - ' + core_count + ' cores', colour_border)

        plt.show()
    else:
        print('Error, invalid io method, please choose from one in the following list, ' + str(tuple(class_name_dict.keys())) + '.')
    
else:
    print('Error, invalid syntax: io_calltree_viewer <io method> <core count>.')


