export default function (url, data) {
    var form = document.createElement('form');
    form.setAttribute('action', url);
    form.setAttribute('method', 'POST');
    Object.entries(data).map(([key, value]) => {
        var input = document.createElement('input');
        input.setAttribute('type', 'text');
        input.setAttribute('name', key);
        input.setAttribute('value', value);
        form.appendChild(input);
    });
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form)
}
