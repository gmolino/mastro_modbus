<template>
  <div class="container">
    <div class="mb-3 row">
    <label class="col-sm-2 col-form-label">Measurement: </label>
    <div class="col-sm-10">
      <select class="form-select" 
        aria-label="Default select example" @change="getMeasurements($event)">
        <option selected>--- Select Measurement ---</option>
        <option v-for="measurement in measurements" :key="measurement.id">
          {{ measurement.measurement }}
        </option>
      </select>
    </div>
  </div>
  <div class="mb-3 row">
    <label class="col-sm-2 col-form-label">Files: </label>
    <div class="col-sm-10">
      <select class="form-select"
          aria-label="Default select example"
          @change="measurementsFiles($event)"
          v-model="fileSelected">
          <option selected>--- Select Files ---</option>
          <option v-for="file in files" :key="file.id">
            {{ file }}
          </option>
        </select>
    </div>
  </div>
  <div class="mb-3 row">
    <label class="col-sm-2 col-form-label">Start Date: </label>
    <div class="col-sm-10">
      <vue-date-picker v-model="dateFrom" :format="format"></vue-date-picker>
    </div>
  </div>
  <div class="mb-3 row">
    <label class="col-sm-2 col-form-label">End Date: </label>
    <div class="col-sm-10">
      <vue-date-picker v-model="dateTo" :format="format"></vue-date-picker>
    </div>
  </div>
  <div class="mb-3 row">
    <label class="col-sm-2 col-form-label">Interval: </label>
    <div class="col-sm-10">
      <input type="text" class="form-control" v-model="interval" id="validationTooltip01" required>
    </div>
  </div>
  <div class="mb-3 row">
    <table class="table">
      <thead>
        <tr>
          <th scope="col">#</th>
          <th scope="col">Item</th>
          <th scope="col">Unit</th>
          <th scope="col">Channel</th>
          <th scope="col">Id</th>
        </tr>
      </thead>

      <tbody class="table-group-divider">
        <tr v-for="(channel, index) in store.state.ChannelsFromAPI" :key="index">
        <th scope="row">
          <input
          class="form-check-input"
          type="checkbox"
          v-model="channelSelected"
          :value="channel.channel_id"
        >
        </th>
        <th scope="row">{{ channel.item }}</th>
        <th scope="row">{{ channel.unit }}</th>
        <th scope="row">{{ channel.channel }}</th>
        <td colspan="2" class="table-active">{{ channel.channel_id }}</td>
        <td></td>
      </tr>
      </tbody>
    </table>
  </div>
  {{ channelSelected }}
  <div class="d-grid gap-2 d-md-flex justify-content-md-end">
    <button class="btn btn-success me-md-2" type="button"
      @click="downloadChannelsList($event)">
      Download CSV
    </button>
    <button class="btn btn-danger" type="button"
      @click="deleteChannelList($event)">
      Delete
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
  const interval = ref(15);
  var fileSelected = ref(String);

  // const date = ref();
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
  const files = computed(() => {
      const response = store.state.Measurements[store.state.Files-1];
      if (response) {
        return response.files;
      } else {
        return [];
      }
  })
  onMounted(() => {
    store.dispatch("fetchDevices");
    store.dispatch("fetchMeasurementsFiles");
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
  const measurementsFiles = (event) => {
    const _index = Number(event.target.selectedOptions[0].index);
    store.commit("SET_INDEX_FILE", _index);
    try {
      const measurement = store.state.Measurements[store.state.Files-1].measurement;
      const fileName = store.state.Measurements[store.state.Files-1].files[store.getters.getFileIndexSelected-1];
      store.dispatch("fetchChannelsFromFiles", {measurement:measurement, fileName:fileName});
      
    } catch (error) {
      event.preventDefault();
    }
  }
  const deleteChannelList = (event) => {
    try {
      channelSelected.value.length = 0;
    } catch (error) {
      event.preventDefault();
    }
  }
  const downloadChannelsList = (event) => {
    try {
      const currentTimestamp = Date.now();
      store.dispatch("fetchDownloadChannelsList", {
        channels:channelSelected.value,
        datetime_from:dateFrom.value.toISOString(),
        datetime_end:dateTo.value.toISOString(),
        measurement:store.state.Measurements[store.state.Files-1].measurement,
        fileName:currentTimestamp,
        interval: interval.value
      });
    } catch (error) {
      event.preventDefault();
    }
  }
</script>