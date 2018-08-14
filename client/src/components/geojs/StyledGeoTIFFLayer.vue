<template>
<GeojsTileLayer
  :url="styledURL"
  :opacity="opacity"
  :keepLower="keepLower"
  :zIndex="zIndex">
</GeojsTileLayer>
</template>

<script>
import { toPalettable } from "../../utils/palettableColorbrewerMapper";

export default {
  name: "StyledGeoTIFFLayer",
  components: {},
  props: ["dataset", "zIndex", "opacity", "tileURL", "keepLower"],
  computed: {
    styledURL() {
      var vizProperties = this.dataset.meta.vizProperties;
      if (!vizProperties) {
        return this.tileURL;
      } else {
        var style = encodeURI(
          JSON.stringify({
            band: parseInt(vizProperties.band),
            palette: toPalettable(vizProperties.scheme),
            min: vizProperties.range[0],
            max: vizProperties.range[1]
          })
        );
        return this.tileURL + `&style=${style}`;
      }
    }
  }
};
</script>

<style>
</style>
