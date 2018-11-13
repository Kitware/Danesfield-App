/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

export default (geojson) => {
    var a = window.document.createElement("a");
    a.href = window.URL.createObjectURL(
        new Blob([JSON.stringify(geojson)], { type: "application/json" })
    );
    a.download = "filter.geojson";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}
