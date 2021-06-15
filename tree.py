"""
This file defines the Tree class.

Edit, Michael Bareford, Sep 13, 2016 
Altered the add_node method such that it now has label and parent
parameters, see node.py.
In addition, the display method now prints the label attribute also.

(Original) Copyright (C) by Brett Kromkamp 2011-2014 (brett@perfectlearn.com)
You Programming (http://www.youprogramming.com)
May 03, 2014
"""

"""
Copyright 2016 Brett Kromkamp and Michael Bareford

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

from node import Node

(_ROOT, _DEPTH, _BREADTH) = range(3)
 
class Tree:

    def __init__(self):
        self.__nodes = {}

    @property
    def nodes(self):
        return self.__nodes

    def add_node(self, identifier, label, parent=None):
        node = Node(identifier, label, parent)
        self[identifier] = node

        if parent is not None:
            self[parent].add_child(identifier)

        return node
    
    def display(self, identifier, depth=_ROOT):
        children = self[identifier].children
        if depth == _ROOT:
            print('{0}'.format(identifier) + ': {0}'.format(self[identifier].label))
        else:
            print('  '*depth + '{0}'.format(identifier) + ': {0}'.format(self[identifier].label))

        depth += 1
        for child in children:
            self.display(child, depth)  # recursive call

    def traverse(self, identifier, mode=_DEPTH):
        # Python generator. Loosly based on an algorithm from 
        # 'Essential LISP' by John R. Anderson, Albert T. Corbett, 
        # and Brian J. Reiser, page 239-241
        yield self[identifier]
        queue = self[identifier].children
        while queue:
            yield self[queue[0]]
            expansion = self[queue[0]].children
            if mode == _DEPTH:
                queue = expansion + queue[1:]  # depth-first
            elif mode == _BREADTH:
                queue = queue[1:] + expansion  # width-first

    def __getitem__(self, key):
        return self.__nodes[key]

    def __setitem__(self, key, item):
        self.__nodes[key] = item
