import { API_URL } from '../constants';

class EventBase {
    constructor() {
        this.handlers = {};
    }

    on(type, callback) {
        if (!this.handlers[type]) {
            this.handlers[type] = new Set();
        }
        this.handlers[type].add(callback);
    }

    trigger(type, ...args) {
        if (!this.handlers[type]) {
            return;
        }
        for (var callback of this.handlers[type].values()) {
            callback.apply(null, args);
        }
    }

    off(type, callback = null) {
        if (!callback) {
            this.handlers[type] = new Set();
        } else {
            this.handlers[type].delete(callback);
        }
    }
}

class EventStream extends EventBase {
    constructor() {
        super();
    }

    open() {
        if (!window.EventSource) {
            throw 'EventSource is not supported on this platform.';
        }
        var since = null;
        try {
            since = parseInt(window.localStorage.getItem('sseTimestamp'), 10);
        } catch (e) {
            // Ignore any errors raised by localStorage
        }
        var url = API_URL + '/notification/stream';
        if (since) {
            url += '?since' + since
        }

        this._eventSource = new window.EventSource(url);

        this._eventSource.onmessage = (e) => {
            var obj;
            try {
                obj = window.JSON.parse(e.data);
            } catch (err) {
                console.error('Invalid JSON from SSE stream: ' + e.data + ',' + err);
                stream.trigger('g:error', e);
                return;
            }
            try {
                window.localStorage.setItem('sseTimestamp', timestamp);
            } catch (e) {
                // Ignore any errors raised by localStorage
            }
            this.trigger(obj.type, obj);
        };
    }

    close() {
        this._eventSource.close();
    }
}



export default new EventStream();
