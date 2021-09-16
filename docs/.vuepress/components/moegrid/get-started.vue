<template>
  <div id="moegrid_get_started"></div>
</template>

<script lang="ts">

import { moeGrid } from "../../../../src/moegrid/moegrid";

export default {
  name: 'moegrid-get-started',
  mounted() {
    moeGrid('#moegrid_get_started');
  }
}
</script>

<style scoped>

</style>
