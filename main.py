from uuid import uuid4

# framework-ish stuff

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

    callbacks = dict()

    def iter_html_attributes(attributes):
        """Filter and convert attributes to html attributes"""
        for key, value in attributes.items():
            if callable(value):
                pass
            elif key == 'For':
                yield 'for', value
            else:
                yield key, value

    def iter_html_events(attributes):
        """Filter and rename attributes referencing callbacks"""
        for key, value in attributes.items():
            if callable(value):
                yield key, value

    def to_dict(node):
        """Recursively convert `node` into a dictionary"""
        if isinstance(node, (str, float, int)):
            return node
        else:
            tag = node._tag
            properties = dict(iter_html_attributes(node._attributes))
            # Gather callbacks and replace callables with plain
            # strings identifier keys
            for name, callback in iter_html_events(node._attributes):
                key = generate_unique_key(callbacks)
                callbacks[key] = callback  # XXX: side effect!
                properties[name] = key
            children = [to_dict(child) for child in node._children]
            # that's all folks!
            out = [tag, properties, children]
            return out

    return to_dict(node), callbacks


class PythonHTML(object):
    """Sugar syntax for creating `Node` instance.

    E.g.

    h.div(id="container", className="minimal thing", For="something")["Héllo World!"]

    container = h.div(id="container", className="minimal thing")
    container.append("Héllo World!")

    """

    # def form(self, **kwargs):
    #     """form element that prevents default 'submit' behavior"""
    #     node = Node('form')
    #     node._attributes['onsubmit'] = 'return false;'
    #     node._attributes.update(**kwargs)
    #     return node

    def input(self, **kwargs):
        type = kwargs.get('type')
        if type == 'text':
            node = Node('Input')
        else:
            node = Node('input')
        node._attributes.update(**kwargs)
        return node

    def __getattr__(self, attribute_name):
        return Node(attribute_name)


h = PythonHTML()


events = dict()


def send():
    global events

    html, new = serialize(render())

    events = new
    return html


def recv(event):
    callback = events[event['identifier']]
    callback(event)
    return send()


# application code


class STATUS:
    DONE = 'done'
    WIP = 'wip'
    ALL = 'all'

class Todo:

    def __init__(self, value):
        self.value = value
        self.status = STATUS.WIP


models = dict(
    filter=STATUS.ALL,
    todos=[Todo('Learn Python')],
    value='',
)

def on_change(event):
    value = event['event']['target.value']
    models['value'] = value

def on_submit(event):
    value = models['value']
    models['todos'].append(Todo(value))
    models['value'] = ''

def render():
    root = h.section(className="todoapp")
    header = h.header(className="header")
    header.append(h.h1()["todos"])
    root.append(header)
    main = h.section(className="main")
    root.append(main)
    form = h.form(onSubmit=on_submit)
    form.append(h.input(type="text", className="new-todo", value=models['value'], onChange=on_change))
    main.append(form)
    ul = h.ul(className="todo-list")
    main.append(ul)
    for todo in models['todos']:
        item = h.li()
        item.append(h.div(className="view")[h.label()[todo.value]])
        ul.append(item)



    return root
