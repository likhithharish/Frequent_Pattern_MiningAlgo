from collections import namedtuple


class fp_tree(object):
    """
    This class contains all the functions that are used to create frequency pattern tree
    1. constructor creates a root node with null value.
    2. append_nodes methods is used to add the nodes to the FP tree
    3. revise_route_table methods is called to update the route table for each item added into the tree.
    4. Nodes methods returns all the nodes of the item in the route table path.
    5. items methods returns all the items and their corresponding nodes in the route table.
    6. get_parent_paths method, returns the prefix path for the given node in an FP tree.
    """
    Track = namedtuple("Track", "start end")

    def __init__(self):
        """
        1. create a root node for the FP tree with null value.
        2. Create empty route table
        """
        self._root = fp_node(self, None, None)
        self._routes = {}

    def get_parent_paths(self, item):
        """

        :param item: Pass the item to return the prefix paths linked to the item
        :return: Return the prefix paths related to the corresponding item
        """
        parent_paths = []
        for node in self.get_nodes(item):
            curr_path = []
            while node and not node.root:
                curr_path.append(node)
                node = node.parent
            curr_path.reverse()
            parent_paths = [curr_path] + parent_paths
        return parent_paths

    def append_items(self, item_list):
        """
        1. Loop through all the items in the transaction
        2. if item already exists in the path, increment the count
        3. if item doesn't exist in the path, create a new node of the item and add it to the FP tree.
        4. Add the item to the route table using the revise_route_table method.
        :param item_list: pass the complete transaction of items
        :return: None
        """
        curr_pointer = self._root
        for item in item_list:
            # Search if the children contain the item
            nxt_ptr = curr_pointer.find(item)
            if not nxt_ptr:
                # If the item is not present in the child branch:
                # Create a new node with item and add it to the FP tree.
                nxt_ptr = fp_node(self, item)
                curr_pointer.add_node(nxt_ptr)
                # Update the item to the route table
                self.revise_route_table(nxt_ptr)
            else:
                # If the item is present in the child branch, increment the count:
                nxt_ptr.increase_count()
            curr_pointer = nxt_ptr

    def revise_route_table(self, curr_ptr):
        """
        Add the nodes to the route table, to be used while generating conditional FP tree
        :param curr_ptr: Pass current pointer to the node

        :return: None
        """
        try:
            # find the route to the current item
            route = self._routes[curr_ptr.item]
            # add the node to te route in the route table
            route[1].adjacent_item = curr_ptr
            self._routes[curr_ptr.item] = self.Track(route[0], curr_ptr)
        except KeyError:
            self._routes[curr_ptr.item] = self.Track(curr_ptr, curr_ptr)

    def get_nodes(self, item):
        """

        :param item: Pass the item to return the corresponding nodes of it.
        :return: Return the nodes corresponding to the item passed from the route table
        """
        try:
            # Find the first node in the route table
            node = self._routes[item][0]
        except KeyError:
            return

        while node:
            yield node
            # look for all the neighbor nodes in the route.
            node = node.adjacent_item

    def get_items(self):
        """
        :return: Returns all the items in the route table along with corresponding nodes
        """
        for item in self._routes.keys():
            # yield the item along with the corresponding nodes
            yield item, self.get_nodes(item)

    @property
    def root(self):
        """
        :return: return the root of the current FP Tree
        """
        return self._root


class fp_node(object):
    """
    This class contains all the methods to create a frequency pattern node.
    1. The constructor initializes few of the attributes with parameters passed, and
        the rest with empty values.
    2. add_node method will add the node to the child of the current node
    3. Find method returns the node if it is present in the child branch.
    """

    def __init__(self, tree, data_point, count=1):
        """
        Constructor for the fp node class
        :param tree: Pass the tree for which this node belongs to.
        :param data_point: Pass the item value of the node
        :param count: pass the count corresponding to the item.
        """
        self._tree = tree
        self._data_point = data_point
        self._count = count
        self._parent = None
        self._children = {}
        self._adjacent_item = None

    def add_node(self, child):
        """
        :param child:
        :return:
        """
        if child.item not in self._children:
            self._children[child.item] = child
            child.parent = self

    def find(self, item):
        """
        1. Finds and return the node corresponds to the item passed.
        2. Returns None if the item is not in the child branch
        :param item: pass the item to find it in the child branch.
        :return: returns the node corresponds to the item if it in the child branch.
        """
        try:
            return self._children[item]
        except:
            return None

    @property
    def tree(self):
        """
        :return: return the pointer to the root node of the tree
        """
        return self._tree

    @property
    def item(self):
        """
        :return: return the pointer to the item node of the tree
        """
        return self._data_point

    @property
    def count(self):
        """
        :return: returns the count corresponds to given node
        """
        return self._count

    def increase_count(self):
        """
        Increment the cont for the corresponding node.
        :return:None
        """
        self._count += 1

    @property
    def parent(self):
        """
        :return: returns the parent of the corresponding node.
        """
        return self._parent

    @parent.setter
    def parent(self, value):
        """
        Assign the parent of the corresponding node to the passed value.
        :param value: pass the node value
        :return: None
        """
        self._parent = value

    @property
    def children(self):
        """
        This method returns all the children corresponding to the node
        :return: Return the tuple with all the children values.
        """
        return tuple(self._children.values())

    @property
    def adjacent_item(self):
        """
        This method gives the neighbor node to the current node
        :return: Returns the neighbor node to the given node
        """
        return self._adjacent_item

    @adjacent_item.setter
    def adjacent_item(self, value):
        """
        This method sets the neighbor node to the current node in accordance with route table
        :param value: pass neighbor value corresponding to the current node
        :return: None
        """
        self._adjacent_item = value

    @property
    def root(self):
        """
        :return: Return true if the node is a root node (data and count should be None)
                 Return False if the node is not a root node(Either of data or count is not None)
        """
        return self._data_point is None and self._count is None

    @property
    def leaf(self):
        """
        :return: Returns True if the node is a leaf node(Contains no children),
                 Returns False if the node is not a leaf node(Contains children)
        """
        return len(self._children) == 0
