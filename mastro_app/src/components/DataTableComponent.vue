<template>
  <div class="container">
    <div class="input-group mb-3">
      <span class="input-group-text" id="inputGroup-sizing-default">Measurement</span>
      <select class="form-select" 
        aria-label="Default select example" @change="getMeasurements($event)">
        <option selected>--- Select Measurement ---</option>
        <option v-for="measurement in measurements" :key="measurement.id">
          {{ measurement.measurement }}
        </option>
      </select>
    </div>
    <div class="input-group mb-3">
      <span class="input-group-text" id="inputGroup-sizing-default">Channel Id</span>
      <input type="text" v-model="channelId"
        class="form-control" aria-label="Sizing example input"
        aria-describedby="inputGroup-sizing-default">
    </div>
    <div class="mb-3 row">
      <label for="staticEmail" class="col-sm-2 col-form-label">Start Date: </label>
      <div class="col-sm-10">
        <vue-date-picker v-model="dateFrom" :format="format"></vue-date-picker>
      </div>
    </div>
    <div class="mb-3 row">
      <label for="staticEmail" class="col-sm-2 col-form-label">End Date: </label>
      <div class="col-sm-10">
        <vue-date-picker v-model="dateTo" :format="format"></vue-date-picker>
      </div>
    </div>
  {{ channelId }}
  <div class="mb-3 row">
    <table class="table">
      <thead>
        <tr>
          <th scope="col">#</th>
          <th scope="col">Time</th>
          <th scope="col">Value</th>
        </tr>
      </thead>

      <tbody class="table-group-divider">
        <tr v-for="(value, index) in store.state.DataValues.data" :key="index">
        <th scope="row">
          <input
          class="form-check-input"
          type="checkbox"
          disabled
        >
        </th>
        <th scope="row">{{ value.time }}</th>
        <th scope="row">{{ value.data_value }}</th>
        <td></td>
      </tr>
      </tbody>
    </table>
    <nav aria-label="Page navigation example">
      <ul class="pagination">
        <li class="page-item">
          <a class="page-link" href="#" aria-label="Previous">
            <span aria-hidden="true">&laquo;</span>
          </a>
        </li>
        <li class="page-item"><a class="page-link" href="#">1</a></li>
        <li class="page-item"><a class="page-link" href="#">2</a></li>
        <li class="page-item"><a class="page-link" href="#">3</a></li>
        <li class="page-item">
          <a class="page-link" href="#" aria-label="Next">
            <span aria-hidden="true">&raquo;</span>
          </a>
        </li>
      </ul>
    </nav>
    <div class="btn-group btn-group-sm" role="group" aria-label="Small button group">
      <span class="badge text-bg-primary">Count: {{ store.state.DataValues.count }}</span>
      <span class="badge text-bg-primary">Total Pages: {{ store.state.DataValues.total_pages }}</span>
      <span class="badge text-bg-primary">Actual Page:{{ store.state.DataValues.actual_page }}</span>
    </div>
  </div>
  <div class="d-grid gap-2 d-md-flex justify-content-md-end">
    <button class="btn btn-primary me-md-2" type="button"
      @click="dataValueTable($event)">
      Show Data
    </button>
  </div>
</div>

</template>

<script setup>
  import { ref, onMounted, computed } from "vue";
  import { useStore } from "vuex";
  import VueDatePicker from '@vuepic/vue-datepicker';
  import '@vuepic/vue-datepicker/dist/main.css'

  const todayDate = new Date();
  const yesterdayDate = new Date(todayDate.getTime() - 48 * 3600000);
  const dateFrom = ref(yesterdayDate);
  const dateTo = ref(todayDate);
  const store = useStore();
  const channelSelected = ref([]);
  const channelId = ref("");

  const format = ($this) => {
    const day = $this.getDate().toString().padStart(2, '0');
    const _month = $this.getMonth()+1;
    const month = _month.toString().padStart(2, '0');
    const year = $this.getFullYear();
    const hours = $this.getHours().toString().padStart(2, '0');
    const minutes = $this.getMinutes().toString().padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`
  }
  const measurements = computed(() => {
    return store.state.Measurements;
  });
  onMounted(() => {
    // Initialize Channels from API
    store.commit("SET_CHANNELS_FROM_API", []);
  });
  const getMeasurements = (event) => {
    try {
      const _index = Number(event.target.selectedOptions[0].index);
      store.commit("SET_MEASUREMENTS", _index);
    } catch (error) {
      event.preventDefault();
    }
  }
  const dataValueTable = (event) => {
    console.log(channelId.value)
    try {
      store.dispatch("fetchDataValue", {
        channels:channelSelected.value,
        datetime_from:dateFrom.value.toISOString(),
        datetime_end:dateTo.value.toISOString(),
        measurement:store.state.Measurements[store.state.Files-1].measurement,
        channelId:channelId.value
      });
    } catch (error) {
      event.preventDefault();
    }
  }
</script>