"""
Implementation of the algorithm to get the template in list of websites
explained in this paper:
    A fast and robust method for web page template detection and removal

    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.105.629&rep=rep1&type=pdf
"""

import copy
import random
import json

import bs4

import sys

# Python 2 and 3 compatibility
if sys.version_info[0] < 3:
    pass
else:
    unicode = lambda s: str(s)



class Tree_Search(object):
    def __init__(self,  root):
        self.root = root
        self.current = root

        self.num_child_to_visit = 0
        self.bifurcation = []

    def reset(self):
        self.current = self.root

        self.num_child_to_visit = 0
        self.bifurcation = []

    def next_pre_order(self):
        if self.current is None:
            return None

        return_node = None

        while return_node is None:
            num_children = num_children_of_node(self.current)

            if num_children == 0 or self.num_child_to_visit == num_children:
                # Is a leaf or all children have been evaluated

                if num_children == 0:
                    return_node = self.current

                # Finish directly when we are at the root
                if self.current == self.root:
                    self.current = None
                    break
                else:
                    # Otherwise, go back to the parent
                    self.current = self.current.parent
                    self.num_child_to_visit = self.bifurcation.pop()
            else:
                # A child is not evaluated yet
                if self.num_child_to_visit == 0:
                    return_node = self.current

                # Go to the child
                self.current = self.current.contents[self.num_child_to_visit]
                self.bifurcation.append(self.num_child_to_visit + 1)
                self.num_child_to_visit = 0

        return return_node

    def next_post_order(self):
        if self.current is None:
            return None

        return_node = None

        while return_node is None:
            num_children = num_children_of_node(self.current)

            if num_children == 0 or self.num_child_to_visit == num_children:
                # Is a leaf or all children have been evaluated
                return_node = self.current

                # Finish directly when we are at the root
                if self.current == self.root:
                    self.current = None
                    break
                else:
                    # Otherwise, go back to the parent
                    self.current = self.current.parent
                    self.num_child_to_visit = self.bifurcation.pop()
            else:
                # A child is not evaluated yet

                # Go to the child
                self.current = self.current.contents[self.num_child_to_visit]
                self.bifurcation.append(self.num_child_to_visit + 1)
                self.num_child_to_visit = 0

        return return_node


def RTDMTD(root_t1, root_t2, B):
    children_t1 = children(root_t1)
    children_t2 = children(root_t2)

    m = len(children_t1)
    n = len(children_t2)
    M = []

    # Matrix initialization
    for i in range(0, m+1):
        Bi = []
        B.append(Bi)

        Mi = []
        M.append(Mi)

        for j in range(0, n+1):
            Bi.append({})
            Mi.append(0)

    for i in range(1, m+1):
        child_t1 = children_t1[i - 1]
        Ci = descendants(child_t1)

        M[i][0] = M[i - 1][0]
        for nodeI in Ci:
            M[i][0] += delete_cost(nodeI)

    for j in range(1, n+1):
        child_t2 = children_t2[j - 1]
        Cj = descendants(child_t2)

        M[0][j] = M[0][j - 1]
        for nodeJ in Cj:
            M[0][j] += insert_cost(nodeJ)

    # Matrix analysis
    for i in range(1, m+1):
        for j in range(1, n+1):
            child_t1 = children_t1[i - 1]
            child_t2 = children_t2[j - 1]

            B2 = []
            Ci = descendants(child_t1)
            Cj = descendants(child_t2)

            D = M[i - 1][j] + delete_cost(child_t1)
            for nodeI in Ci:
                D += delete_cost(nodeI)

            I = M[i][j - 1] + insert_cost(child_t2)
            for nodeJ in Cj:
                I += insert_cost(nodeJ)

            U = M[i - 1][j - 1]
            if label(child_t1) != label(child_t2):
                U += replace_cost(child_t1, child_t2)

            if num_children_of_node(child_t1) == 0 or num_children_of_node(child_t2) == 0:
                if num_children_of_node(child_t1) == 0:
                    for nodeJ in Cj:
                        U += insert_cost(nodeJ)
                elif num_children_of_node(child_t2) == 0:
                    for nodeI in Cj:
                        U += delete_cost(nodeI)
            else:
                U += RTDMTD(child_t1, child_t2, B2)

            M[i][j] = min(D, I, U)
            B[i][j]["cost"] = M[i][j]
            B[i][j]["src"] = child_t1
            B[i][j]["dst"] = child_t2
            B[i][j]["next"] = B2

            if M[i][j] == D:
                B[i][j]["op"] = "delete"
            elif M[i][j] == I:
                B[i][j]["op"] = "insert"
            elif M[i][j] == U:
                B[i][j]["op"] = "update"

    return M[m][n]

def children(node):
    """Safe method to get the children of a node"""

    if hasattr(node, "contents"):
        return node.contents
    else:
        return []

def num_children_of_node(node):
    if hasattr(node, "contents"):
        return len(node.contents)
    else:
        return 0


def label1(node):
    if isinstance(node, bs4.element.NavigableString):
        searialized_node = {
            "type": "text",
            "content": unicode(node)
        }
    elif isinstance(node, bs4.element.Comment):
        searialized_node = {
            "type": "comment",
            "content": unicode(node)
        }
    else:
        searialized_node = {
            "type": "element",
            "name": node.name,
            "attributes": list(node.attrs.items())
        }

    return json.dumps(searialized_node)



def label2(node):
    if isinstance(node, bs4.element.NavigableString):
        searialized_node = {
            "type": "text",
            "content": unicode(node)
        }
    elif isinstance(node, bs4.element.Comment):
        searialized_node = {
            "type": "comment",
            "content": unicode(node)
        }
    else:
        searialized_node = {
            "type": "element",
            "name": node.name
        }

    return json.dumps(searialized_node)

label = label1

def descendants(root):
    descendants = []

    tree_search = Tree_Search(root)
    node = tree_search.next_pre_order()

    while True:
        node = tree_search.next_pre_order()

        if node is None:
            break
        else:
            descendants.append(node)

    return descendants


def delete_cost(node):
    return 1


def insert_cost(node):
    return 1


def replace_cost(node1, node2):
    return 1


def retrieve_template(B):
    template_nodes = []
    m = len(B) - 1

    if len(B) <= 1:
        return template_nodes
    else:
        n = len(B[0]) - 1

    i = m
    j = n

    while (i > 0 and j > 0):
        if B[i][j]["op"] == "delete":
            j -= 1
        elif B[i][j]["op"] == "insert":
            i -= 1
        elif B[i][j]["op"] == "update":
            nodeT1 = B[i][j]["src"]
            nodeT2 = B[i][j]["dst"]
            B2 = B[i][j]["next"]

            nodes_of_subtemplate = retrieve_template(B2)

            if len(nodes_of_subtemplate) > 0 or label(nodeT1) == label(nodeT2):
                if not (
                    isinstance(nodeT1, bs4.element.Comment) or
                    (isinstance(nodeT1, bs4.element.NavigableString) and str(nodeT1).strip() == "")):
                    template_nodes.append(nodeT1)

            template_nodes.extend(nodes_of_subtemplate)

            i -= 1
            j -= 1

    return template_nodes


def extract_subtree(root1, root2):
    B = []

    RTDMTD(root1, root2, B)
    template_nodes = retrieve_template(B)

    return smallest_subtree_containing_nodes(root1, template_nodes)


def smallest_subtree_containing_nodes(root, template_nodes):
    webpage_search = Tree_Search(root)

    template_node_ids = [id(node) for node in template_nodes]

    template = copy.copy(root)
    template_search = Tree_Search(template)

    node = webpage_search.next_post_order()
    template_node = template_search.next_post_order()

    mapped_ancestors = []

    list_of_nodes_to_delete = []

    while node != root:
        # Obtain the same node in the template tree

        node_id = id(node)

        if node_id in template_node_ids:
            ancestor = node.parent

            # The ancestors of the template node should not be deleted

            while ancestor != root:
                ancestor_id = id(ancestor)

                if ancestor_id not in mapped_ancestors:
                    mapped_ancestors.append(ancestor_id)

                ancestor = ancestor.parent
        else:
            # Do not delete the ancestors of a template node
            if node_id not in mapped_ancestors:
                # Mark node to delete
                list_of_nodes_to_delete.append(template_node)

        node = webpage_search.next_post_order()
        template_node = template_search.next_post_order()

    # Delete nodes
    for node in list_of_nodes_to_delete:
        node.extract()

    return template


def find_template(list_of_soups):
    soup1 = list_of_soups.pop(random.randrange(len(list_of_soups)))
    webpage1_body = soup1.body

    soup2 = list_of_soups.pop(random.randrange(len(list_of_soups)))
    webpage2_body = soup2.body

    T = extract_subtree(webpage1_body, webpage2_body)

    while len(list_of_soups) != 0:
        soup = list_of_soups.pop(random.randrange(len(list_of_soups)))
        webpage_body = soup.body

        T = extract_subtree(T, webpage_body)

    return T
