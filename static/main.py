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


events = dict()

def send():
    global events
    html, new = serialize(render())
    events = new
    return html


def recv(event):
    callback = events[event['key']]
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
    todos=[Todo('Learn Python')]
)

def on_value_change(event):
    value = event['event']['target.value']
    models['todos'].append(Todo(value))


def on_done(todo):
    def on_event(_):
        todo.status = STATUS.DONE
    return on_event


def on_filter(value):
    def on_event(_):
        models['filter'] = value
    return on_event


def filter_button(value):
    if models['filter'] == value:
        return h.input(Class='active', type='submit', value=value)
    else:
        return h.input(Class='inactive', type='submit', value=value, on_click=on_filter(value))


def render():
    root = h.div(id='root')
    root.append(h.h1()["todos"])
    done = len(filter(lambda x: x.status == 'done', models['todos']))
    count = float(len(models['todos']))
    percent = (done / count) * 100
    msg = "{:.2f}% complete!".format(percent)
    root.append(h.h2()[msg])
    filters = h.div(id='filters')
    filters.append(filter_button('all'))
    filters.append(filter_button('wip'))
    filters.append(filter_button('done'))
    root.append(filters)
    root.append(h.input(type='text', on_change=on_value_change))
    if models['filter'] == STATUS.ALL:
        for todo in models['todos']:
            item = h.div(Class='item ' + todo.status)
            item.append(h.span()[todo.value])
            item.append(h.input(type='submit', value='done', on_click=on_done(todo)))
            root.append(item)
    else:
        for todo in models['todos']:
            if todo.status == models['filter']:
                item = h.div(Class='item ' + todo.status)
                item.append(h.span()[todo.value])
                item.append(h.input(type='submit', value='done', on_click=on_done(todo)))
                root.append(item)
    return root
