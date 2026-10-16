<template>
  <div style="margin-top: 7vh">
    <center>
      <van-image width="180" height="180" :src="require('@/assets/badminton.png')" />
      <h2 style="margin-bottom: -15px">My Club</h2>
      <h4>Sports Activity Management</h4>
      <h3>Welcome! You can</h3>
    </center>
    <center>
      <van-button round block icon="manager-o" type="success" @click="this.$router.push('/login')"
                  style="width: 80%; max-width: 320px; margin: 8pt; margin-top: 20pt; background-color: dodgerblue; border-color: dodgerblue">
        Login with Password
      </van-button>
      <van-button round block icon="add-o" type="warning" @click="this.$router.push('/register')"
                  style="width: 80%; max-width: 320px; margin: 8pt">
        Create New Account
      </van-button>
      <p style="font-size: 10pt; color: #666">One-tap device login is temporarily disabled for account safety.</p>
    </center>
  </div>

  <p style="font-size: 7pt; text-align: center; position: fixed; bottom: 5vh; width: 100%;">
    Sports Club Management System — Member Portal<br/>
    Copyright © 2024 My Club
  </p>
</template>

<script>
import Cookies from 'js-cookie';

export default {
  created() {
    const token = Cookies.get('token');
    if (!token) return;
    this.$http.post('/user/verify?token=' + encodeURIComponent(token)).then(response => {
      if (response.data.status === 3) this.$router.push('/staff');
      else if (response.data.status > 0 && response.data.status < 3) this.$router.push('/main');
    }).catch(() => {});
  }
};
</script>
