<template>
  <div class="container">
    <div class="mb-3 row">
    <label class="col-sm-2 col-form-label">Select database: </label>
    <div class="col-sm-10">
      <table class="table">
      <tr class="form-check" v-for="(database, index) in store.state.Databases"
        :key="index">
      <td>
        <input
          class="form-check-input" type="radio"
          name="flexRadioDefault" :value="database"
          @click="databaseSelected($event)"
          v-model="store.state.SelectedDatabase"
        >
      </td>
      <td>
        <label class="form-check-label" for="flexRadioDefault2">
          {{ database }}
        </label>
      </td>
    </tr>
    {{ store.state.SelectedDatabase }}
    </table>
  </div>
</div>
</div>
</template>

<script setup>
  import { onMounted } from "vue";
  import { useStore } from "vuex";
  const store = useStore();
  const databaseSelected = (event) => {
    store.commit("SET_SELECTED_DATABASE", event.target.value);
  };
  onMounted(() => {
    store.dispatch("fetchDataBases");
    // Initialize Channels from API
    store.commit("SET_DATABASES_FROM_API", []);
  });
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
