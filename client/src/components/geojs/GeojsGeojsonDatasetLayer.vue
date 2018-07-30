<template>
<GeojsGeojsonLayer
  v-if="geojson"
  :geojson="geojson"
  :zIndex="zIndex"
  :opacity="opacity">
</GeojsGeojsonLayer>
</template>

<script>

var cache = new WeakMap();

export default {
  name: "GeojsGeojsonDatasetLayer",
  components: {},
  props: ["dataset", "zIndex", "opacity"],
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
      var { data: geojson } = await this.$girder.get(
        `item/${this.dataset._id}/download`
      );
      return geojson;
    }
  }
};
</script>
