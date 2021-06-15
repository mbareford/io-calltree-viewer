"""
This file defines the CallTree and CrayPATCallTree classes.
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

import re
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from random import randint
from node import Node
from tree import Tree

(_ROOT, _DEPTH, _BREADTH) = range(3)

"""
Objects of the call tree class encode the call paths stemming from a
defined root function. The nodes of the tree represent function calls;
associated with each node is a label dictionary that records pertinent
info, such as the inclusive time spent within the function (usually expressed
as a fraction of the inclusive time recorded for the root function), the
number of times the function was called, the level of the function call within
the call hierarchy and the name of the function itself.

The actual importing of the call tree data from raw text files is handled by
subclasses, see CrayPATCallTree.

The CallTree class provides a plot method that displays the call tree as
a flame plot. 
"""
class CallTree(Tree):

    def __init__(self):
        Tree.__init__(self)
        self.__root_id = 1
        self.__level_min = 1
        self.__level_max = self.__level_min
        self.__calls_min = 1.0
        self.__calls_max = self.__calls_min

    @property
    def root_id(self):
        return self.__root_id

    @property
    def level_min(self):
        return self.__level_min

    @property
    def level_max(self):
        return self.__level_max

    @level_max.setter
    def level_max(self, value):
        self.__level_max = value

    @property
    def calls_min(self):
        return self.__calls_min
    
    @property
    def calls_max(self):
        return self.__calls_max

    @calls_max.setter
    def calls_max(self, value):
        self.__calls_max = value


    """
    Traverse the call tree and print out the details of each node visited.
    """
    def show(self):
        for node in self.traverse(str(self.root_id), mode=_BREADTH):
            node.display()


    """
    A time offset is simply the horizontal position of a bar representing
    some call. The offset will depend on the amount of exclusive time belonging
    to the parent, the ordering of the call with respect to its siblings (i.e.,
    where the call id appears within the parent_node.children array), and the
    parent offset.
    """
    def get_time_offset(self, node):
        node_id = node.identifier
        parent_id = node.parent
        
        if None == parent_id:
            offset = 0.0
        else:
            parent_node = self[parent_id]
            child_time = 0.0
            for child_id in parent_node.children:
                
                if child_id is node_id:
                    child_offset = child_time

                child_node = self[child_id]    
                child_time += float(child_node.label['time'])

            offset = parent_node.label['offset']
            offset += (float(parent_node.label['time']) - child_time)/2.0
            offset += child_offset

        node.label['offset'] = offset
        
        return offset
    

    """
    Plot the call tree as a flame plot. The bars within the flame plot can be cloured randomly from
    a defined palette of red-orange hues or the bars can be coloured according to the value of a specific
    property (e.g., number of calls) that is stored in the label dictionary associated with each tree node.
    """      
    def plot(self, title, colour_border='white', colour_property=None):

        # colours taken from colorbrewer website, see http://colorbrewer2.org/#type=sequential&scheme=YlOrRd&n=9
        palette = list(reversed(['#ffffcc','#ffeda0','#fed976','#feb24c','#fd8d3c','#fc4e2a','#e31a1c','#bd0026','#800026']))

        width = 1.0
        half_width = width/2.0

        xmin = self.level_min - half_width
        xmax = self.level_max + half_width           
        ymin = 0.0
        ymax = float(self[str(self.root_id)].label['time'])

        colour_incr = (self.calls_max - self.calls_min + 1) / float(len(palette))

        fig = plt.figure()

        desc = []
        x = []
        y = []
        colour = []
        offset = []
                
        for node in self.traverse(str(self.root_id), mode=_BREADTH):
            label = node.label

            tm = round(float(label['time']), 3)
            desc += [label['level'] + ": " + label['name'] + '(' + label['calls'] + ') - ' + str(tm) + '.']
            
            x += [int(label['level'])]
            y += [float(label['time'])]

            if None == colour_property:
                colour += [palette[randint(0,len(palette)-1)]]
            else:
                colour_prop = float(label[colour_property])
            
                palette_index = int(colour_prop/colour_incr)
                if palette_index > len(palette)-1:
                    palette_index = -1
            
                colour += [palette[palette_index]]
            
            offset += [self.get_time_offset(node)]
            

        bar = plt.barh(tuple(x), tuple(y), height=width, color=colour, edgecolor=colour_border, left=tuple(offset), align='center')
        bar_tooltip = [None]*len(desc)
        
        plt.xlim(ymin,ymax)            
        plt.ylim(xmin,xmax)
        fig.gca().yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        plt.xlabel('Normalised Time')
        plt.ylabel('Call Stack Level')

        plt.title(title)

        """
        This inner function allows the user to display the name of the function represented by each flame plot bar
        as a pop-up tooltip text box. Clicking the same box again will cause the tooltip text to disappear, unless
        it is the right mouse button that is clicked, whereupon, the tooltip text is shifted, such that the end of
        the text coincides with the coordinates of the mouse click.
        All tooltip texts are disappeared whenever the user clicks outwith all bars.
        """
        def on_bar_click(event):
            RIGHT_CLICK = 3
            bar_clicked = False
            
            for i in range(len(bar_tooltip)):
                if bar[i].contains(event)[0]:
                    bar_clicked = True
                    print(desc[i])
                    if None == bar_tooltip[i]:
                        bar_tooltip[i] = plt.text(event.xdata, event.ydata, desc[i], bbox=dict(facecolor='white', alpha=1.0))
                    else:
                        if bar_tooltip[i].get_visible():
                            
                            if RIGHT_CLICK == event.button:
                                ax = fig.gca()
                                data_origin = [ax.get_xlim()[0], ax.get_ylim()[0]]
                                display_origin = ax.transData.transform((xmin, ymin))
                                
                                inv = ax.transData.inverted()
                                tooltip_width = bar_tooltip[i].get_bbox_patch().get_width()
                                data_shift = inv.transform((tooltip_width,display_origin[1]))
                                
                                bar_tooltip[i].set_position((event.xdata-(data_shift[0]-data_origin[0]),event.ydata))
                            else:
                                bar_tooltip[i].set_visible(False)
                           
                        else:
                            bar_tooltip[i].set_position((event.xdata,event.ydata))
                            bar_tooltip[i].set_visible(True)
                    
                    fig.canvas.draw_idle()
                    break
                

            if not bar_clicked:
                for i in range(len(bar_tooltip)):
                    if None != bar_tooltip[i]:
                        bar_tooltip[i].set_visible(False)
                fig.canvas.draw_idle()
                        
        fig.canvas.mpl_connect('button_press_event', on_bar_click)
         

"""
This class encapsulates all the code pertinent to building a tree object from the
text written to a CrayPat output file, which itself was generated by a pat_build/report commands,
e.g. pat_build -f -u -g mpi,io,aio,sysio,sysfs -D force-instr=y FieldIOBenchmarker
followed by
pat_report -O calltree -T FieldIOBenchmarker+pat+*.xf > FieldIOBenchmarker+pat+*.out, where
FieldIOBenchmarker is the CrayPAT-instrumented executable.

In time, similar classes may be written for the import of calltree data from scorep or
TAU output files.
"""
class CrayPATCallTree(CallTree):

    def __init__(self, reportfile_name, calltree_title, rootfunc_name):
        CallTree.__init__(self)
        self.import_pat_report(reportfile_name, calltree_title, rootfunc_name)
        
    """
    This method first searches for a particular table (calltree_title) within the output
    file (reportfile_name). Once the start of this table is found, the method then searches
    for the function that will be the root of the call tree and from there, a tree object
    is built. This method stops once all the routines called from the root have been parsed.
    """
    def import_pat_report(self, reportfile_name, calltree_title, rootfunc_name):

        """
        This inner function converts a raw string label into a dictionary with
        the following properties, offset (the x-coordinate for the left side of
        the box representing the call), level (the position of the call within
        the stack trace), time (the time spent within the call) and name.
        """
        def import_label(raw_label):
            raw_label = raw_label.replace('|', ' ')
            raw_cols = [0.0] + raw_label.split()

            items = {'offset': 0, 'level': 1, 'time': 3, 'calls': 4, 'name': -1}

            calls_index = items['calls']
            if calls_index < len(raw_cols):
                raw_calls = raw_cols[calls_index]
                raw_cols[calls_index] = raw_calls.replace(',','')
            
            item_keys = list(items.keys())
            item_vals = list(items.values())

            return {item_keys[item_vals.index(i)]: (raw_cols[i] if i < len(raw_cols) else "") for i in item_vals}

        """
        Return true if time_str can be converted to a float, which
        for now is assumed to be a sufficient test for a valid time string.
        """
        def is_time(time_str):
            try:
                float(time_str)
                return True
            except:
                return False

        """
        Return true if calls_str can be converted to a float, which
        for now is assumed to be a sufficient test for a valid call count string.
        """
        def is_calls(calls_str):
            try:
                float(calls_str)
                return True
            except:
                return False
        
        calltree_srch = True
        rootfunc_srch = True

        
        root_level = 0
        root_time = 0.0
        levels = []
        ids = []
        node_cnt = self.root_id

        fin = open(reportfile_name, 'r')
        
        for line in fin:

            if calltree_srch:
                
                calltree_srch = (-1 == line.find(calltree_title))
                
            elif rootfunc_srch:
                
                rootfunc_srch = (-1 == line.find(rootfunc_name))

                if not rootfunc_srch:
                    label = import_label(line)

                    root_level = int(label['level'])
                    levels.append(self.level_min)
                    label['level'] = str(levels[-1])

                    root_time = float(label['time'])
                    label['time'] = '1.0'
                    
                    if not is_calls(label['calls']):
                        label['calls'] = '1.0'
                                        
                    ids.append(str(node_cnt))
                    self.add_node(ids[-1], label)
        
            else:
                
                if None == re.search(r'[A-Z]+', line, re.I):
                    continue

                if -1 != line.find('(exclusive)'):
                    continue

                label = import_label(line)

                level = int(label['level']) - root_level+1
                if level == levels[0]:
                    break

                parent_id = ids[0]
                for i, lv in enumerate(reversed(levels)):
                    if level == lv+1:
                        parent_id = ids[-1-i]
                        break 

                if level > self.level_max:
                    self.level_max = level
                    
                levels.append(level)
                label['level'] = str(levels[-1])

                node_cnt += 1
                ids.append(str(node_cnt))

                if is_time(label['time']):
                    label['time'] = str(float(label['time'])/root_time)
                else:
                    label['time'] = self[parent_id].label['time']
                

                if not is_calls(label['calls']):
                    label['calls'] = self[parent_id].label['calls']

                calls = float(label['calls'])
                if calls > self.calls_max:
                    self.calls_max = calls
                        
                self.add_node(ids[-1], label, parent_id)

        fin.close()


    


   
    

    
