/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

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
