<template>
<GeojsGeojsonLayer
  v-if="geojson"
  :geojson="geojson"
  :zIndex="zIndex">
</GeojsGeojsonLayer>
</template>

<script>
import girderApi from "resonantgeo/src/mixins/girderApi";

var cache = new WeakMap();

export default {
  name: "GeojsGeojsonDatasetLayer",
  mixins: [girderApi],
  components: {},
  props: ["dataset", "zIndex"],
  data() {
    return {
      geojson: null
    };
  },
  computed: {
    actions() {
      return [];
    }
  },
  watch: {
    // dataset
  },
  async created() {
    if (cache.has(this.dataset)) {
      this.geojson = cache.get(this.dataset);
    } else {
      var geojson = await this.loadDatasetData();
      cache.set(this.dataset, geojson);
      this.geojson = geojson;
    }
  },
  methods: {
    async loadDatasetData() {
      var { data: geojson } = await this.session.get(
        `item/${this.dataset._id}/download`
      );
      return geojson;
    }
  }
};
</script>
