<template>
  <div class="container px-4 px-lg-5">
    <div class="row gx-4 gx-lg-5 align-items-center my-5">

    <h3>GraphQL</h3>

  <GraphQLComponent v-if="$store.state.SelectedDatabase" :database="database"></GraphQLComponent>
  <div v-else class="alert alert-danger" role="alert">
    Select a valid database before!
  </div>
</div>
</div>
</template>
<script>
// @ is an alias to /src
import GraphQLComponent from '@/components/GraphQLComponent.vue'

export default {
  name: 'MesaruementsView',
  components: {
    GraphQLComponent
  }
}
</script>
