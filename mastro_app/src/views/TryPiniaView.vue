<template>
  <div class="container px-4 px-lg-5">
    <div class="row gx-4 gx-lg-5 align-items-center my-5">

    <h3>Pinia</h3>
  </div>
  <PiniaComponent></PiniaComponent>
</div>
</template>
<script>
// @ is an alias to /src
import PiniaComponent from '@/components/PiniaComponent.vue'

export default {
  name: 'DevicesView',
  components: {
    PiniaComponent
  }
}
</script>
