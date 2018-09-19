<template>
  <div class="full-screen">
    <GirderJobList @job-click="jobClick" />
  </div>
</template>

<script>
import { GIRDER_URL } from "../constants";

export default {
  name: "Job",
  methods: {
    jobClick(e, job) {
      window.open(`${GIRDER_URL}#job/${job._id}`, "_blank");
    }
  }
};
</script>

<style lang="scss" scoped>
.full-screen {
  overflow-y: auto;
}
</style>
