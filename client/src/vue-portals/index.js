import Vue from 'vue';

var store = new Vue({ data: { map: {} } });

var portal = {
    props: ['name'],
    computed: {
        text() {
            var portalVMs = store.$data.map[this.name];
            if (portalVMs) {
                let texts = [];
                for (let i = portalVMs.length - 1; i >= 0; i--) {
                    let text = portalVMs[i].portal.text;
                    let appendText = portalVMs[i].portal.appendText;
                    if (text) {
                        texts.unshift(text);
                        break;
                    } else if (appendText) {
                        texts.unshift(appendText);
                    }
                }
                return texts.join(' - ');
            } else {
                return null;
            }
        }
    },
    render(h) {
        if (this.text) {
            return this._v(this.text);
        } else {
            return null;
        }

    }
}

function install(Vue) {
    Vue.component('Portal', portal);
    Vue.mixin({
        created() {
            if (this.portal) {
                if (this.portal.name && (this.portal.text !== undefined || this.portal.appendText !== undefined)) {
                    if (!store.$data.map[this.portal.name]) {
                        this.$set(store.$data.map, this.portal.name, []);
                    }
                    store.$data.map[this.portal.name].push(this);
                } else {
                    throw new Error("portal object is missing name or text property");
                }
            }
        },
        destroyed() {
            if (this.portal) {
                var portalVMs = store.$data.map[this.portal.name];
                if (portalVMs) {
                    var index = portalVMs.indexOf(this);
                    portalVMs.splice(index, 1);
                }
            }
        }
    })

}

export default {
    install
}
