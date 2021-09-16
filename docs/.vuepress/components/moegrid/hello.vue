<template>
  <div id="moegrid-hello" >Test!!</div>
</template>

<script lang="ts">

import {hello} from "../../../../src/moegrid/moegrid";

export default {
  name: 'moegrid-hello',
  data: function(){
    return {};
  },
  setup(){
    return {};
  },
  created() {
  },
  mounted() {
    hello('#moegrid-hello');
  },
  methods: {
    load(){
      console.log('hello!!');
    }
  }
}
</script>

<style scoped>

</style>
