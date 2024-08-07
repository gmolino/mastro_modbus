<template>
  <div class="container">
    <p>Count : {{ count }}</p>
    <button @click="increment">+</button>
    <pre>
      {{ databases }}
    </pre>
    <pre>
      bnn: {{ selectedDatabase }}
    </pre>
    <div class="d-grid gap-2 d-md-flex">
    <button class="btn btn-success me-md-2" type="button"
      @click="test_token()">
      Check token validity
    </button>
    <button class="btn btn-danger me-md-2" type="button"
      @click="resetCount">
      Reset count
    </button>
  </div>
</div>
</template>

<script setup>
import { useCounter, useDatabases, useUser } from '../store/counter';
import { storeToRefs } from 'pinia';
import { onMounted } from "vue";

const store = useCounter();
const databases_store = useDatabases();

const { count } = storeToRefs(store);
const { databases, selectedDatabase } = storeToRefs(databases_store);
const { increment, resetCount } = store
const useUserStore = useUser();

const test_token = (event) => {
  try {
    useUserStore.tryToken()
  } catch (error) {
    event.preventDefault();
  }
}

onMounted(async () => {
  await databases_store.fetchDatabases();
})
</script>