<template>
  <nav v-if="isAuthenticated" class="navbar navbar-expand-lg navbar-dark bg-dark">
  <div class="container-fluid">
      <a class="navbar-brand" href="#!">Mastro App</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarText" aria-controls="navbarText" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarText">
          <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
              <li class="nav-item"><router-link class="nav-link" to="/">Home</router-link></li>
              <li class="nav-item"><router-link class="nav-link" to="/measurements">Measurements</router-link></li>
              <li class="nav-item"><router-link class="nav-link" to="/devices">Devices</router-link></li>
              <li class="nav-item"><router-link class="nav-link" to="/data_table">Table Values</router-link></li>
              <li class="nav-item"><router-link class="nav-link" to="/graphql">GraphQL</router-link></li>
              <li class="nav-item"><router-link class="nav-link" to="/pinia">Pinia</router-link></li>
              
              <li class="nav-item dropdown">
                <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                  User
                </a>
                <ul class="dropdown-menu dropdown-menu-dark">
                  <li class="nav-item"><router-link class="nav-link d-flex" to="/profile">Profile</router-link></li>
                  <li class="nav-item"><router-link class="nav-link d-flex" @click="logout" to="">Logout</router-link></li>
                </ul>
              </li>

          </ul>
      </div>
  </div>
</nav>
  <router-view/>
</template>
<script setup>
import { useUser } from './store/counter';
import { storeToRefs } from 'pinia';
const useUserStore = useUser();
const { isAuthenticated } = storeToRefs(useUserStore);

const logout = () => {
  useUserStore.logout();
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
}

nav a.router-link-exact-active {
  color: #42b983;
}
</style>



<!--
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
  <div class="container px-5">
      <a class="navbar-brand" href="#!">Start Bootstrap</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation"><span class="navbar-toggler-icon"></span></button>
      <div class="collapse navbar-collapse" id="navbarSupportedContent">
          <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
              <li class="nav-item"><a class="nav-link active" aria-current="page" href="#!">Home</a></li>
              <li class="nav-item"><a class="nav-link" href="#!">About</a></li>
              <li class="nav-item"><a class="nav-link" href="#!">Contact</a></li>
              <li class="nav-item"><a class="nav-link" href="#!">Services</a></li>
          </ul>
      </div>
  </div>
</nav>
<div class="container px-4 px-lg-5">

  <div class="row gx-4 gx-lg-5 align-items-center my-5">
      <div class="col-lg-7"><img class="img-fluid rounded mb-4 mb-lg-0" src="https://dummyimage.com/900x400/dee2e6/6c757d.jpg" alt="..." /></div>
      <div class="col-lg-5">
          <h1 class="font-weight-light">Business Name or Tagline</h1>
          <p>This is a template that is great for small businesses. It doesn't have too much fancy flare to it, but it makes a great use of the standard Bootstrap core components. Feel free to use this template for any project you want!</p>
          <a class="btn btn-primary" href="#!">Call to Action!</a>
      </div>
  </div>

  <div class="card text-white bg-secondary my-5 py-4 text-center">
      <div class="card-body"><p class="text-white m-0">This call to action card is a great place to showcase some important information or display a clever tagline!</p></div>
  </div>

  <div class="row gx-4 gx-lg-5">
      <div class="col-md-4 mb-5">
          <div class="card h-100">
              <div class="card-body">
                  <h2 class="card-title">Card One</h2>
                  <p class="card-text">Lorem ipsum dolor sit amet, consectetur adipisicing elit. Rem magni quas ex numquam, maxime minus quam molestias corporis quod, ea minima accusamus.</p>
              </div>
              <div class="card-footer"><a class="btn btn-primary btn-sm" href="#!">More Info</a></div>
          </div>
      </div>
      <div class="col-md-4 mb-5">
          <div class="card h-100">
              <div class="card-body">
                  <h2 class="card-title">Card Two</h2>
                  <p class="card-text">Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quod tenetur ex natus at dolorem enim! Nesciunt pariatur voluptatem sunt quam eaque, vel, non in id dolore voluptates quos eligendi labore.</p>
              </div>
              <div class="card-footer"><a class="btn btn-primary btn-sm" href="#!">More Info</a></div>
          </div>
      </div>
      <div class="col-md-4 mb-5">
          <div class="card h-100">
              <div class="card-body">
                  <h2 class="card-title">Card Three</h2>
                  <p class="card-text">Lorem ipsum dolor sit amet, consectetur adipisicing elit. Rem magni quas ex numquam, maxime minus quam molestias corporis quod, ea minima accusamus.</p>
              </div>
              <div class="card-footer"><a class="btn btn-primary btn-sm" href="#!">More Info</a></div>
          </div>
      </div>
  </div>
</div>

<footer class="py-5 bg-dark">
  <div class="container px-4 px-lg-5"><p class="m-0 text-center text-white">Copyright &copy; Your Website 2023</p></div>
</footer>

-->