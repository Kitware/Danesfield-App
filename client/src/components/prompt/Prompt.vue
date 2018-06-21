<template>
<v-snackbar
  v-if="prompt"
  :timeout="null"
  :value="prompt">
  {{prompt.message}}
  <v-btn v-if='prompt.button' flat color="pink" @click="resolve(prompt.button)">{{prompt.button}}</v-btn>
</v-snackbar>
</template>

<script>
import { mapState } from "vuex";

export default {
  name: "Prompt",
  components: {},
  data() {
    return {};
  },
  computed: {
    ...mapState("prompt", ["prompt", "resolve"])
  },
  watch: {
    prompts(prompts) {}
  },
  method: {}
};
</script>
