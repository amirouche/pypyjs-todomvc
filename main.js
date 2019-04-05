let ReactDOM = helpers.default.ReactDOM;
let h = helpers.default.h;
let Input = helpers.default.Input;


let container = document.getElementById('root');


var recv = function(json) {
    ReactDOM.render(
        translate(json),
        container,
    );
}

let send = function(event, identifier) {
    event.preventDefault();
    var msg = {
        "identifier": identifier,
        "event": {'target.value': event.target.value},
    };
    pypyjs.eval('recv(' + JSON.stringify(msg) + ')')
          .then(recv)
          .then(null, console.error);
}

let makeCallback = function(identifier) {
    return function(event) {
        return send(event, identifier);
    };
}


let translate = function(json) {
    let tag = json[0];

    if (tag === "Input") {
	tag = Input;
    }

    let properties = json[1] || {};
    for (let key in properties) {
        if(key.startsWith('on')) {
            properties[key] = makeCallback(properties[key]);
        }
    }

    // recurse to translate children
    let children = json[2] || [];
    children = children.map(function(child) {  // TODO: optimize with a for-loop
        if (child instanceof Object) {
            return translate(child);
        } else { // it's a string or a number
            return child;
        }
    });

    return h(tag, properties, children);
}


// boot application

pypyjs.ready().then(function() {
    fetch('main.py').then(function(xhr) {
        xhr.text()
           .then(function(main) {
               pypyjs.exec(main)
                     .then(function() {
                         console.log('main.py loaded')
                         pypyjs.eval('send()')
                                .then(null, console.error)
                                .then(recv);
                     })
                     .then(null, console.error);
           });
    });
});
