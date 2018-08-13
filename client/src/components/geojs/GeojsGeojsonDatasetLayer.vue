<template>
<GeojsGeojsonLayer
  v-if="geojson"
  :geojson="geojson"
  :zIndex="zIndex"
  :opacity="opacity"
  :featureStyle="style">
</GeojsGeojsonLayer>
</template>

<script>
import * as d3 from "d3";
import isObject from "lodash-es/isObject";
import size from "lodash-es/size";
import sortedIndex from "lodash-es/sortedIndex";

import {
  toScheme,
  toSchemeColors
} from "../../utils/palettableColorbrewerMapper";

export default {
  name: "GeojsGeojsonDatasetLayer",
  components: {},
  props: ["dataset", "zIndex", "opacity", "summary", "geojson"],
  data() {
    return {};
  },
  computed: {
    style() {
      var vizProperties = this.dataset.meta.vizProperties;
      var style = {
        point: { radius: vizProperties.point.radius },
        line: {},
        polygon: { uniformPolygon: true }
      };
      style.point = {
        ...style.point,
        ...this.translate("stroke", vizProperties.point)
      };
      style.point = {
        ...style.point,
        ...this.translate("fill", vizProperties.point)
      };
      style.line = {
        ...style.line,
        ...this.translate("stroke", vizProperties.line)
      };
      style.polygon = {
        ...style.polygon,
        ...this.translate("stroke", vizProperties.polygon)
      };
      style.polygon = {
        ...style.polygon,
        ...this.translate("fill", vizProperties.polygon)
      };
      // vizProperties.polygon.uniformPolygon = true;
      // vizProperties.polygon.fillColor = () => {
      //   return Math.random() > 0.5 ? "#00FF00" : "#FF0000";
      // };
      return style;
    }
  },
  watch: {
    summary(summary) {
      console.log("summary change", summary);
    },
    vizProperties(vizProperties) {
      console.log("vizProperties change", vizProperties);
    }
  },
  methods: {
    translate(prefix, styles) {
      var subStyle = {
        [prefix + "Opacity"]: styles[prefix + "Opacity"],
        [prefix]: styles[prefix],
        [prefix + "Color"]: styles[prefix + "Color"]
      };
      if (styles[prefix + "Property"] && styles[prefix + "Scheme"]) {
        subStyle[prefix + "Color"] = this.getColorScaleFunc(
          styles[prefix + "Property"],
          styles[prefix + "Scheme"],
          this.summary.properties[styles[prefix + "Property"]],
          styles[prefix + "Scale"],
          styles[prefix + "MinClamp"],
          styles[prefix + "MaxClamp"]
        );
      }
      if (prefix === "stroke") {
        subStyle["strokeWidth"] = styles["strokeWidth"];
      }
      return subStyle;
    },
    getColorScaleFunc(
      property,
      schemeName,
      propertySummary,
      scale,
      minClamp,
      maxClamp
    ) {
      var scheme = toScheme(schemeName);
      var colors = toSchemeColors(schemeName);
      // for an invalid scheme, just return black
      if (!scheme || !colors) {
        return "#ffffff";
      }

      var scaleFunc = null;
      if (isObject(propertySummary.values)) {
        // categorical
        let indices = Object.keys(scheme).map(v => {
          return parseInt(v, 10);
        });
        let n = sortedIndex(indices, size(propertySummary.values));
        n = Math.min(n, indices.length - 1);

        scaleFunc = d3.scale
          .ordinal()
          .domain(Object.keys(propertySummary.values))
          .range(scheme[indices[n]]);
      } else {
        // continuous
        // handle the case when all values are the same
        let max = propertySummary.max,
          min = propertySummary.min;
        if (min >= max) {
          max = min + 1;
        }
        if (scale === "log" && min > 0) {
          let s = d3.scale
            .quantize()
            .domain([Math.log(min), Math.log(max)])
            .range(colors);
          scaleFunc = value => {
            return s(Math.log(value));
          };
        } else if (scale === "quantile") {
          let data = [];
          this.geojson.features.forEach(function(feature) {
            data.push(feature.properties[property]);
          });
          scaleFunc = d3.scale
            .quantile()
            .domain(data)
            .range(colors);
        } else {
          // linear scaling
          scaleFunc = d3.scale
            .quantize()
            .domain([minClamp ? minClamp : min, maxClamp ? maxClamp : max])
            .range(colors);
        }
      }
      return (...args) => {
        if (args[2]) {
          return scaleFunc(args[2].properties[property]);
        } else {
          // geojs callback for point has different arguments
          return scaleFunc(args[0].properties[property]);
        }
      };
    }
  }
};
</script>
