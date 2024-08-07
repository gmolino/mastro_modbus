import { createStore } from 'vuex'
import axios from "axios"

axios.defaults.baseURL = "http://localhost:5000"
// axios.defaults.baseURL = "https://api.reinvent.witmo.eu"
axios.defaults.headers.common['Authorization'] = "Bearer " + localStorage.getItem("token");

export default createStore({
  state: {
    Devices: [],
    DevicesQL: [],
    Measurements: [],
    Files: 0,
    FileIndexSelected: 0,
    ChannelsFromAPI: [],
    DeviceSeleted: 0,
    DataValues: [],
    Databases: [],
    SelectedDatabase: ""
  },
  getters: {
    getDevices: (state) => state.Devices,
    getWritables: (state) => state.Writables,
    getChannels: (state) => state.Channels,
    getMeasurements: (state) => state.Measurements,
    getFileIndexSelected: (state) => state.FileIndexSelected,
    getChannelsFromAPI: (state) => state.ChannelsFromAPI,
    getDataValues: (state) => state.DataValues,
    getSelectedDatabase: (state) => state.SelectedDatabase
  },
  mutations: {
    GET_DEVICES(state, Devices) {
      state.Devices = Devices;
    },
    GET_DEVICES_QL(state, DevicesQL) {
      state.DevicesQL = DevicesQL;
    },
    GET_MEASUREMENTS_FILES(state, Measurements) {
      state.Measurements = Measurements;
    },
    SET_MEASUREMENTS(state, files) {
      state.Files = files
    },
    SET_DATABASES_FROM_API(state, databases) {
      state.Databases = databases
    },
    SET_INDEX_FILE(state, _index) {
      state.FileIndexSelected = _index
    },
    SET_CHANNELS_FROM_API(state, channelsFromAPI) {
      state.ChannelsFromAPI = channelsFromAPI
    },
    SET_DATA_VALUES(state, data) {
      state.DataValues = data
    },
    SET_SELECTED_DATABASE(state, selectedDatabase) {
      state.SelectedDatabase = selectedDatabase
    }
  },
  actions: {
    async fetchDevices({ commit }) {
      try {
        const data = await axios.get(
          "/api/v1/sincere/" + this.getters.getSelectedDatabase + "/devices/?limit=100&page=0&pagination=true"
        );
        commit("GET_DEVICES", data.data);
      } catch (error) {
        alert(error);
      }
    },
    async fetchDevicesQL({ commit }) {
      try {
        const query = "query { devices(db: \"" + this.getters.getSelectedDatabase + "\") { reference file} }"
        const data = await axios.post(
          "/graphql",
          {
            headers: {
              "Content-Type": "application/json"
            },
            query: query,
          },
          
        );
        commit("GET_DEVICES_QL", data.data);
      } catch (error) {
        alert(error);
      }
    },
    async fetchChannelsFromDevice({ commit }, device) {
      try {
        const data = await axios.get(
          "/api/v1/sincere/" + this.getters.getSelectedDatabase + "/device/" + device
        );
        commit("SET_CHANNELS_FROM_API", data.data.data.channels);
      } catch (error) {
        alert(error);
      }
    },
    async fetchDataBases({ commit }) {
      try {
        const data = await axios.get(
          "/api/v1/sincere/databases"
        );
        commit("SET_DATABASES_FROM_API", data.data);
      } catch (error) {
        alert(error);
      }
    },
    async fetchMeasurementsFiles({ commit }) {
      try {
        const data = await axios.get(
          "/api/v1/sincere/" + this.getters.getSelectedDatabase + "/measurements_aggregator"
        );
        commit("GET_MEASUREMENTS_FILES", data.data.data);
        localStorage.setItem("token", "xxxxxx-x--xxxxxxxxxx-xxxxxxxxxx-xxxx")
      } catch (error) {
        alert(error);
      }
    },
    async fetchChannelsFromFiles({ commit }, values) {
      try {
        const data = await axios.get(
          "/api/v1/sincere/" + this.getters.getSelectedDatabase + "/channels_from_file?measurement=" + 
          values.measurement + "&file=" + values.fileName
        );
        const allChannels = [];
        for (const dev of data.data.data) {
          allChannels.push(...dev.channels);
        }
        commit("SET_CHANNELS_FROM_API", allChannels);
      } catch (error) {
        alert(error);     
      }
    },
    async fetchDataValue({ commit }, values) {
      console.log(commit)
      try {
        const data = await axios.get(
          "/api/v1/sincere/" + this.getters.getSelectedDatabase + "/meta_data/" + values.measurement + "/" + values.channelId
        )
        commit("SET_DATA_VALUES", data.data)
      } catch (error) {
        alert(error);
      }
    },
    async fetchDownloadChannelsList({ commit }, values) {
      try {
        await axios.put(
          "/api/v1/sincere/" + this.getters.getSelectedDatabase + "/download_channel_values/?measurement=" + 
          values.measurement + "&datetime_from=" + values.datetime_from + 
          "&datetime_end=" + values.datetime_end + "&interval=" + values.interval + "&file_name=" + values.fileName,
          values.channels, { responseType: 'blob' }
        ).then((response) => {
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', values.fileName + '.csv');
          document.body.appendChild(link);
          link.click();
        });
        console.log(commit)
        alert("OK");
      } catch (error) {
        if (error.response.status === 404) {
          alert("No data found");
        } else {
        alert(error);
        }
      }
    }
  },
  modules: {
  }
})
