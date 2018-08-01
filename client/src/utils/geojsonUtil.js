import * as d3 from 'd3';
/* globals moment */
import colorbrewer from 'colorbrewer';

window.colorbrewer = colorbrewer;
const geojsonUtil = {};

/**
 * Merge a new value into an accumulation object.
 * The result depends on the value type:
 *
 * 1. string: stores a values object that maps
 *            the values encountered to the total
 *            number of occurences.
 *
 * 2. number: stores the minimum and maximum values
 *            encountered
 */
function merge(value, accumulated) {
    accumulated = accumulated || { count: 0 };
    accumulated.count += 1;
    switch (typeof value) {
        case 'string':
            accumulated.values = accumulated.values || {};
            accumulated.values[value] = (accumulated.values[value] || 0) + 1;
            break;

        case 'number':
            if (isFinite(value)) {
                accumulated.nFinite = (accumulated.nFinite || 0) + 1;
                accumulated.min = Math.min(
                    accumulated.min !== undefined ? accumulated.min : Number.POSITIVE_INFINITY,
                    value
                );
                accumulated.max = Math.max(
                    accumulated.max !== undefined ? accumulated.max : Number.NEGATIVE_INFINITY,
                    value
                );
                accumulated.sum = (accumulated.sum || 0) + value;
                accumulated.sumsq = (accumulated.sumsq || 0) + value * value;
            }
            break;
    }
    return accumulated;
};

/**
 * A list of property keys that are ignored when generating
 * geojson 
 * var summarize.
 */
var ignored_properties = [
    'cluster',
    'clusterDistance',
    'clusterFillColor',
    'clusterStrokeColor',
    'clusterRadius',
    'fill',
    'fillColor',
    'fillOpacity',
    'radius',
    'stroke',
    'strokeColor',
    'strokeWidth',
    'strokeOpacity',
    'fillColorKey',
    'strokeColorKey'
].sort();

/**
 * Accumulate property values into a summary object.  The
 * output object will have keys encountered in the feature
 * array mapped to an object that summarizes the values
 * encountered.
 *
 * @param {object[]} features An array of "property" objects
 * @returns {object}
 */
function accumulate(features) {
    var accumulated = {};

    for (let feature of features) {
        for (let key in feature) {
            if (feature.hasOwnProperty(key) && ignored_properties.indexOf(key) === -1) {
                accumulated[key] = merge(feature[key], accumulated[key]);
            }
        }
    }

    return accumulated;
};

/**
 * Normalize a geojson object turning geometries into features and
 * returning a feature collection.  The returned feature collection
 * is processed to provide a summary object containing accumulated
 * property statistics that can be used to generate numeric/color
 * scales for visualization.
 */
function normalize(geojson) { // eslint-disable-line complexity
    var normalized;
    /* Check if this is a geojson-timeseries.  If so, normalize each each
     * entry.  The root contains the first geojson entry and a summary that
     * combines all of the entries 
     * var summarize. */

    /* if (_.isArray(geojson) && geojson[0].geojson && geojson[0].time) {
      _.each(geojson, function (entry) {
        var norm = geojsonUtil.normalize(entry.geojson);
        if (norm) {
          if (!normalized) {
            normalized = $.extend({ series: [] }, norm);
            normalized.summary = {};
          }
          var label = '' + (entry.label || (entry.time ? moment(entry.time).format('L LTS') : null) || ('Frame ' + (normalized.series.length + 1)));
          var time = moment.utc(entry.time);
          normalized.series.push({ time: time, geojson: norm, label: label });
        }
      });
      normalized.summary = geojsonUtil.accumulate(
        _.flatten(normalized.series.map((series) => series.geojson.features))
          .map((feature) => feature.properties)
      );
      return normalized;
    } */

    switch (geojson.type) {
        case 'FeatureCollection':
            normalized = geojson;
            break;

        case 'Feature':
            normalized = {
                type: 'FeatureCollection',
                features: [geojson]
            };
            break;

        case 'GeometryCollection':
            normalized = {
                type: 'FeatureCollection',
                features: geojson.geometries.map(function (g) {
                    return {
                        type: 'Feature',
                        geometry: g,
                        properties: {}
                    };
                })
            };
            break;

        case 'Point':
        case 'LineString':
        case 'Polygon':
        case 'MultiPoint':
        case 'MultiLineString':
        case 'MultiPolygon':
            normalized = {
                type: 'FeatureCollection',
                features: [{
                    type: 'Feature',
                    geometry: geojson,
                    properties: {}
                }]
            };
            break;

        default:
            throw new Error('Invalid json type');
    }



    return normalized;
};

function summarize(geojson) {
    var normalized = normalize(geojson);

    var types = {
        pointAlike: !!getFeaturesOfGeometryType(normalized, 'Point', 'MultiPoint').length,
        lineAlike: !!getFeaturesOfGeometryType(normalized, 'LineString', 'MultiLineString').length,
        polygonAlike: !!getFeaturesOfGeometryType(normalized, 'Polygon', 'MultiPolygon').length
    };

    var properties = accumulate(
        normalized.features.map(function (f) { return f.properties; }));

    return {
        types,
        properties
    }
}

/**
 * Set style properties in the geojson according to the
 * `visProperties` mapping.  This will loop through all
 * of the contained features and append "property"
 * key -> value pairs for each vis property.
 *
 * This method mutates the geojson object.
 *
 * @note assumes the geojson object is normalized
 */
geojsonUtil.style = function style(geojson, visProperties) {
    visProperties = visProperties || {};
    _.each(geojson.features || [], function (feature) {
        var properties = feature.properties || {};
        var geometry = feature.geometry || {};
        var style = {};

        switch (geometry.type) {
            case 'Point':
            case 'MultiPoint':
                style = visProperties.point || {};
                break;
            case 'LineString':
            case 'MultiLineString':
                style = visProperties.line || {};
                break;
            case 'Polygon':
            case 'MultiPolygon':
                style = visProperties.polygon || {};
                break;
        }
        _.each(style, function (scale, key) {
            if (_.isFunction(scale)) {
                properties[key] = scale(properties, key, geometry);
            } else {
                properties[key] = scale;
            }
        });

        feature.properties = properties;
    });

    return geojson;
};

/**
 * Generate a d3-like scale function out of a colorbrewer
 * scheme name and a geojson summary object.
 *
 * @param {string} scheme
 * @param {object} summary
 * @param {Boolean} logFlag
 * @returns {function}
 */
geojsonUtil.colorScale = function colorScale(
    scheme, summary,
    logFlag, quantileFlag, clampingFlag, minClamp, maxClamp,
    data) {
    var scale, s, colors, n, indices;

    colors = colorbrewer[scheme];
    // for an invalid scheme, just return black
    if (!colors) {
        return function () { // eslint-disable-line underscore/prefer-constant
            return '#ffffff';
        };
    }
    indices = _.keys(colors).map(function (v) {
        return parseInt(v, 10);
    });

    if (_.isObject(summary.values)) { // categorical
        n = _.sortedIndex(indices, _.size(summary.values));
        n = Math.min(n, indices.length - 1);

        scale = d3.scale.ordinal()
            .domain(_.keys(summary.values))
            .range(colors[indices[n]]);
    } else { // continuous
        n = indices.length - 1;
        // handle the case when all values are the same
        if (summary.min >= summary.max) {
            summary.max = summary.min + 1;
        }
        if (logFlag && summary.min > 0) {
            s = d3.scale.quantize()
                .domain([Math.log(summary.min), Math.log(summary.max)])
                .range(colors[indices[n]]);
            scale = function (val) {
                return s(Math.log(val));
            };
        } else if (quantileFlag) {
            scale = d3.scale.quantile()
                .domain(data)
                .range(colors[indices[n]]);
        } else {
            // linear scaling
            if (clampingFlag) {
                scale = d3.scale.quantize()
                    .domain([minClamp, maxClamp])
                    .range(colors[indices[n]]);
            } else {
                scale = d3.scale.quantize()
                    .domain([summary.min, summary.max])
                    .range(colors[indices[n]]);
            }
        }
    }
    return scale;
};

/**
 * Return an array of the indicated type from a geojson object.
 * If no types are given, return all features.
 */
function getFeaturesOfGeometryType(geojson, ...types) {
    var all = (geojson || {}).features || [];
    if (!types.length) {
        return all;
    }
    return all.filter(feature => {
        var geom = feature.geometry || {};
        return types.indexOf(geom.type) !== -1;
    });
};

export default geojsonUtil;

export {
    normalize,
    summarize,
    accumulate
}
