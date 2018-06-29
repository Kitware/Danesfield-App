<template>
<FullScreenViewport>
  <v-container>
    <GirderUserDialog
      :form.sync='form'
      v-model='userDialog'
      />
  </v-container>
</FullScreenViewport>
</template>
<script>
export default {
  name: "Login",
  watch: {
    userDialog(value) {
      if (!value) {
        this.$router.push("/explore");
      }
    }
  },
  data() {
    return {
      form: "login",
      userDialog: true
    };
  }
};
</script>
