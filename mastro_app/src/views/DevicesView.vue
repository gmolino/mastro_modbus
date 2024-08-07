<template>
  <div class="container px-4 px-lg-5">
    <div class="row gx-4 gx-lg-5 align-items-center my-5">

    <h3>Devices</h3>

  <DevicesComponent v-if="$store.state.SelectedDatabase" :database="database"></DevicesComponent>
  <div v-else class="alert alert-danger" role="alert">
    Select a valid database before!
  </div>
  </div>
</div>

</template>
<script>
// @ is an alias to /src
import DevicesComponent from '@/components/DevicesComponent.vue'

export default {
  name: 'DevicesView',
  components: {
    DevicesComponent
  }
}
</script>
