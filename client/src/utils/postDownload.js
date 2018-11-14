/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

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
