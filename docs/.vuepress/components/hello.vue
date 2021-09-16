<template>
  <div id="hello-world" ></div>
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
}
</script>

<style scoped>

</style>
