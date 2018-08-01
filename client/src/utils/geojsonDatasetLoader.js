import loadDatasetData from './loadDatasetData';
var cache = new WeakMap();


async function getData(dataset) {
    if (cache.has(dataset)) {
        return cache.get(dataset);
    } else {
        var geojson = await loadDatasetData(dataset);
        cache.set(dataset, geojson);
        return geojson;
    }
}

export { getData };
