<template>
  <van-nav-bar title="Staff Duty System" fixed/>
  <br/><br/><br/>
  <div style="margin: 0px 10px 0px 10px;">
    <router-view>
    </router-view>
  </div>
  <van-tabbar v-model="active" @change="onChange" fixed>
    <van-tabbar-item icon="calendar-o">Duty Roster</van-tabbar-item>
    <van-tabbar-item icon="scan">Verify & Sign</van-tabbar-item>
    <van-tabbar-item icon="user-circle-o">Account</van-tabbar-item>
  </van-tabbar>
</template>

<script>
export default {
  data(){
    return {
      active: 0
    };
  },
  created(){
    this.$staffVerify();
    switch (this.$route.path){
      case '/staff/work':
        this.active = 0;
        break;
      case '/staff/membership':
        this.active = 2;
    }
  },
  methods: {
    onChange(){
      switch(this.active){
        case 0:
          this.$router.push('/staff/work');
          break;
        case 1:
          this.active = 0;
          this.$router.push('/staff/scan');
          break;
        case 2:
          this.$router.push('/staff/membership');
          break;
      };
    }
  }
};
</script>

<style scoped lang="scss">

</style>