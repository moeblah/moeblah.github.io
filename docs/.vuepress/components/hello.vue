<template>
  <div id="hello-world" v-on:click="click"></div>
</template>

<script lang="ts">
import {helloWorld} from "../../../src/helloworld";

function a(v: string): void{
  console.log(v)
}


export default {
  name: 'hello-world',
  mounted() {
    helloWorld('#hello-world');
    a(null);
  },
  methods: {
    click: function(){
      console.loc('click!!!')
    }
  }
}
</script>

<style scoped>

</style>
