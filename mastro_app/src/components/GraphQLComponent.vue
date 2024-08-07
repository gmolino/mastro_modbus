<template>
  <div class="content">
    <h1>{{ msg }}</h1>
    <div class="mb-8 row">
      <pre>
        {{ devices }}
      </pre>
    </div>
  </div>
</template>

<script setup>
  import { ref, onMounted, computed } from "vue";
  import { useStore } from "vuex";
  const store = useStore();
  const msg = ref("");
  const devices = computed(() => {
    return store.state.DevicesQL.data;
  });

  onMounted(() => {
    store.dispatch("fetchDevicesQL");
  });

</script>