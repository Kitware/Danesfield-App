/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

<template>
    <div class="logo"><img src="./logo.png"/></div>
</template>

<style lang="scss" scoped>
.logo {
  position: absolute;
  margin: 5px;
  width: 80px;

  img {
    width: 100%;
  }
}
</style>

<script>
export default {
  name: "Logo"
};
</script>
