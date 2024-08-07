<template>
  <div class="container px-4 px-lg-5">
    <div class="row gx-4 gx-lg-5 align-items-center my-5">

    <h3>Measurements</h3>

  <MeasurementsComponent v-if="$store.state.SelectedDatabase"></MeasurementsComponent>
  <div v-else class="alert alert-danger" role="alert">
    Select a valid database before!
  </div>
</div>
</div>
</template>
<script>
// @ is an alias to /src
import MeasurementsComponent from '@/components/MeasurementsComponent.vue'

export default {
  name: 'MesaruementsView',
  components: {
    MeasurementsComponent
  }
}
</script>
