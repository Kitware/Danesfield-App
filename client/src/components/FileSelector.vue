/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

<template>
  <div>
    <v-text-field
      class="file-selector"
      readonly
      append-icon="attach_file"
      :disabled="disabled"
      :value="value"
      :label="label"
      :messages="messages"
      :required="required"
      @click.native="onFocus"
      ref="fileTextField"></v-text-field>
    <input type="file" :accept="accept" :multiple="multiple" :disabled="disabled"
           ref="fileInput" @change="onFileChange">
  </div>
</template>

<script>
export default {
  name: "FileSelector",
  props: {
    value: {
      type: [Array, String]
    },
    accept: {
      type: String,
      default: "*"
    },
    label: {
      type: String,
      default: "Choose file"
    },
    required: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    multiple: {
      type: Boolean,
      default: false
    },
    messages: {
      type: [String, Array],
      default: ""
    }
  },
  data() {
    return {};
  },
  methods: {
    onFocus() {
      if (!this.disabled) {
        this.$refs.fileInput.click();
      }
    },
    onFileChange($event) {
      const files = $event.target.files || $event.dataTransfer.files;
      var filename;
      if (files) {
        if (files.length > 0) {
          filename = [...files].map(file => file.name).join(", ");
        } else {
          filename = null;
        }
      } else {
        filename = $event.target.value.split("\\").pop();
      }
      this.$emit("input", filename);
      this.$emit("file", this.multiple ? files : files[0]);
    }
  }
};
</script>

<style scoped>
input[type="file"] {
  position: absolute;
  left: -99999px;
}
</style>
