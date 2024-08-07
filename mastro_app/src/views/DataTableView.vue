<template>
  <div class="container px-4 px-lg-5">
    <div class="row gx-4 gx-lg-5 align-items-center my-5">

    <h3>Data Table</h3>

  <DataTableComponent v-if="$store.state.SelectedDatabase" ></DataTableComponent>
  <div v-else class="alert alert-danger" role="alert">
    Select a valid database before!
  </div>
</div>
</div>
</template>
<script>
// @ is an alias to /src
import DataTableComponent from '@/components/DataTableComponent.vue'

export default {
  name: 'TableView',
  components: {
    DataTableComponent
  }
}
</script>
