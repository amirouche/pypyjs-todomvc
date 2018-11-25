import json
from uuid import uuid4


class BeyondException(Exception):
    pass


def generate_unique_key(dictionary):
    key = uuid4().hex
    if key not in dictionary:
        return key
    raise BeyondException('Seems like the dictionary is full')


class Node(object):  # inspired from nevow
    """Python representaiton of html nodes.

    Text nodes are python strings.

    You must not instantiate this class directly. Instead use the
    global instance `h` of the `PythonHTML` class.

    """

    __slots__ = ('_tag', '_children', '_attributes')

    def __init__(self, tag):
        self._tag = tag
        self._children = list()
        self._attributes = dict()

    def __call__(self, **kwargs):
        """Update node's attributes"""
        self._attributes.update(kwargs)
        return self

    def __repr__(self):
        return '<Node: %s %s>' % (self._tag, self._attributes)

    def append(self, node):
        """Append a single node or string as a child"""
        self._children.append(node)

    def extend(self, nodes):
        [self.append(node) for node in nodes]

    def __getitem__(self, nodes):
        """Add nodes as children"""
        # XXX: __getitem__ is implemented in terms of `Node.append`
        # so that widgets can simply inherit from node and override
        # self.append with the bound `Node.append`.
        if isinstance(nodes, (str, float, int)):
            self.append(nodes)
        elif isinstance(nodes, (list, tuple)):
            [self.append(node) for node in nodes]
        else:
            self.append(nodes)
        return self


def serialize(node):
    """Convert a `Node` hierarchy to a json string.

    Returns two values:

    - the dict representation
    - an event dictionary mapping event keys to callbacks

    """

    events = dict()

    def to_html_attributes(attributes):
        """Filter and convert attributes to html attributes"""
        for key, value in attributes.items():
            if key.startswith('on_'):
                pass
            elif key == 'Class':
                yield 'class', value
            elif key == 'For':
                yield 'for', value
            else:
                yield key, value

    def to_html_events(attributes):
        """Filter and rename attributes referencing callbacks"""
        for key, value in attributes.items():
            if key.startswith('on_'):
                yield key[3:], value

    def to_dict(node):
        """Recursively convert `node` into a dictionary"""
        if isinstance(node, (str, float, int)):
            return node
        else:
            out = dict(tag=node._tag)
            out['attributes'] = dict(to_html_attributes(node._attributes))
            on = dict()
            for event, callback in to_html_events(node._attributes):
                key = generate_unique_key(events)
                events[key] = callback  # XXX: side effect!
                on[event] = key
            if on:
                out['on'] = on
            out['children'] = [to_dict(child) for child in node._children]
            return out

    return to_dict(node), events


class PythonHTML(object):
    """Sugar syntax for creating `Node` instance.

    E.g.

    h.div(id="container", Class="minimal thing", For="something")["Héllo World!"]

    container = h.div(id="container", Class="minimal thing")
    container.append("Héllo World!")

    """

    def form(self, **kwargs):
        """form element that prevents default 'submit' behavior"""
        node = Node('form')
        node._attributes['onsubmit'] = 'return false;'
        node._attributes.update(**kwargs)
        return node

    def input(self, **kwargs):
        type = kwargs.get('type')
        if type == 'text':
            try:
                kwargs['id']
            except KeyError:
                pass
            else:
                log.warning("id attribute on text input node ignored")
            node = Node('input#' + uuid4().hex)
        else:
            node = Node('input')
        node._attributes.update(**kwargs)
        return node

    def __getattr__(self, attribute_name):
        return Node(attribute_name)


h = PythonHTML()


counter = 0


def callback(event):
    global counter
    counter += 1


def render():
    global events
    msg = 'counter is at: ' + str(counter)
    html, new = serialize(h.div(on_click=callback)[h.p()[msg]])
    events = new
    return html

def on_event(event):
    key = event['key']
    callback = events[key]
    callback(event)
    return render()
