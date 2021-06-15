"""
This file defines the Node class.

Edit, Michael Bareford, Sep 13, 2016
Added two attributes, label and parent. The first is a dictionary that allows each
node to be associated with an arbitrary property list and the second is simply the
identifier for the parent node.
These two new attributes are required to construct a node object.
 
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

class Node:
    def __init__(self, identifier, label, parent):
        self.__identifier = identifier
        self.__label = label
        self.__parent = parent
        self.__children = []
        
    @property
    def identifier(self):
        return self.__identifier
    
    @property
    def label(self):
        return self.__label

    @property
    def parent(self):
        return self.__parent
    
    @property
    def children(self):
        return self.__children

    def add_child(self, identifier):
        self.__children.append(identifier)

    def display(self):
        print(self.__label)
