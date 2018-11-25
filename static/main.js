import './snabbdom.js';
import './snabbdom-attributes.js';
import './snabbdom-eventlisteners.js';

var container = document.getElementById('root');

var patch = snabbdom.init([
    snabbdom_attributes.default,
    snabbdom_eventlisteners.default,
]);

var h = snabbdom.h;


var recv = function(json) {
    container = patch(container, translate(json))
}

var send = function(event) {
    pypyjs.eval('on_event(' + JSON.stringify(event) + ')')
          .then(recv)
          .then(null, console.error);
}

/* Translate json to `vnode` using `h` snabbdom helper */
var translate = function(json) {
    var options = {attrs: json.attributes};

    // create callback for each events
    var on = {};
    if(json.on) {
        options.on = {};
        Object.keys(json.on).forEach(function(event_name) {  // TODO: optimize with for-loop
            options.on[event_name] = function(event) {
                var msg = {
                    path: location.pathname,
                    type: 'dom-event',
                    key: json.on[event_name],
                    event: {'target.value': event.target.value},
                };
                send(msg);
            }
        });
    }

    // recurse to translate children
    var children = json.children.map(function(child) {  // TODO: optimize with a for-loop
        if (child instanceof Object) {
            return translate(child);
        } else { // it's a string or a number
            return child;
        }
    });

    return h(json.tag, options, children);
}


pypyjs.ready().then(function() {
    fetch('static/main.py').then(function(xhr) {
         xhr.text()
            .then(function(main) {
                pypyjs.exec(main)
                      .then(function() {
                          console.log('main.py loaded')
                          pypyjs.eval('render()')
                                 .then(null, console.error)
                                 .then(recv);
                      })
                      .then(null, console.error);
            });
    });
});
