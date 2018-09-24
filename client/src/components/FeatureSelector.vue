<template>
  <FileSelector
    class="feature-selector"
    :label="label"
    v-model="geojsonFilename"
    :messages="messages"
    accept=".json,.geojson"
    @file='onGeojsonSelected' />
</template>

<script>
import FileSelector from "./FileSelector";
export default {
  name: "FeatureSelector",
  components: {
    FileSelector
  },
  props: {
    value: {},
    label: {
      default: "Choose file"
    },
    messages: {
      type: [String, Array],
      default: ""
    }
  },
  data() {
    return {
      geojsonFilename: ""
    };
  },
  methods: {
    async onGeojsonSelected(file) {
      if (!file) {
        this.$emit("input", null);
        return;
      }
      try {
        this.$emit("input", await this.tryGetFeaturesFromFile(file));
      } catch (ex) {
        this.$emit("input", null);
        this.$emit("message", ex.message);
        this.geojsonFilename = null;
      }
    },
    async tryGetFeaturesFromFile(file) {
      if (file.size > 1024 * 1024) {
        throw new Error("File is too large");
      }
      var result = await new Promise((resolve, reject) => {
        var reader = new FileReader();
        reader.onload = e => {
          resolve(reader.result);
        };
        reader.readAsText(file);
      });
      var geojson = JSON.parse(result);
      var features = null;
      if (geojson.features) {
        features = geojson.features;
      } else if (geojson.geometries) {
        features = geojson.geometries.map(geometry => ({
          type: "Feature",
          geometry
        }));
      } else if (geojson.coordinates) {
        features = [
          {
            type: "Feature",
            geometry: geojson
          }
        ];
      } else {
        features = [geojson];
      }
      features = features.filter(
        feature => feature.geometry && feature.geometry.type === "Polygon"
      );
      if (!features.length) {
        throw new Error("File doesn't contain a valid polygon feature");
      }
      if (features.length > 5) {
        throw new Error("File has more than 5 polygon features");
      }
      return features;
    }
  }
};
</script>

<style>
</style>
