<template>
  <VCode :show="verifyCodeShow"
         slider-text="Drag Slider to Complete Puzzle"
         fail-text="Verification Failed, Please Try Again"
         success-text="Verification Passed"
         :range="5"
         @success="onVerifyCodeSuccess"
         @close="onVerifyCodeClose"
         z-index="10000"
  />
  <lay-layer v-model="changePasswordShow" title="Password Setting" :area="['500px', '320px']" z-index="1000">
    <div style="padding: 20px;">
      <lay-form :model="changeInf" required>
        <lay-form-item label="Origin Password" prop="password" label-width="130px">
          <lay-input v-model="changeInf.ori_pass" type="password">></lay-input>
        </lay-form-item>
        <lay-form-item label="New Password" prop="password" label-width="130px">
          <lay-input v-model="changeInf.new_pass" type="password">></lay-input>
        </lay-form-item>
        <lay-form-item label="Password Comfirm" prop="password" label-width="130px">
          <lay-input v-model="changeInf.cfm_pass" type="password">></lay-input>
        </lay-form-item>
        <div style="text-align: right">
          <lay-button style="margin-top: 10px;" @click="this.changePasswordShow = false"><lay-icon type="layui-icon-close"/> Cancel</lay-button>
          <lay-button type="primary" style="margin-top: 10px; " @click="onVerifyCodeCall(1)"><lay-icon type="layui-icon-release"/> Submit</lay-button>
        </div>
      </lay-form>
    </div>
  </lay-layer>

  <lay-layer v-model="updateContactShow" title="Connection Update" :area="['500px', '375px']" z-index="1000">
    <div style="padding: 20px;">
      <lay-form :model="changeInf">
        <lay-form-item label="Password" prop="password" required>
          <lay-input v-model="changeInf.ori_pass" type="password">></lay-input>
        </lay-form-item>
        <lay-form-item label="Phone" prop="text" required>
          <lay-input v-model="changeInf.phone" type="test">></lay-input>
        </lay-form-item>
        <lay-form-item label="Wechat ID" prop="text" required>
          <lay-input v-model="changeInf.wechat_id" type="text">></lay-input>
        </lay-form-item>
        <lay-form-item label="Email" prop="text">
          <lay-input v-model="changeInf.email" type="text">></lay-input>
        </lay-form-item>
        <div style="text-align: right">
          <lay-button style="margin-top: 10px;" @click="this.updateContactShow = false"><lay-icon type="layui-icon-close"/> Cancel</lay-button>
          <lay-button type="primary" style="margin-top: 10px; " @click="onVerifyCodeCall(2)"><lay-icon type="layui-icon-release"/> Submit</lay-button>
        </div>
      </lay-form>
    </div>
  </lay-layer>

  <lay-layout class="layout">
    <lay-header>
      <lay-row space="3">
        <lay-col md="10">
          <h3>
            &nbsp;&nbsp; <lay-avatar :src="require('@/assets/badminton.png')" radius></lay-avatar>&nbsp;Club Admin Dashboard &nbsp;
          </h3>
        </lay-col>
        <lay-col md="14" style="text-align: right; margin-top: 0px;">
          Welcome, {{this.userInf.name}}!&nbsp;
          <lay-button-group style="margin-top: -3px;">
            <lay-button border-style="dashed" style="color: white" size="xs" @click="onEventCall(2)"><lay-icon type="layui-icon-cellphone"/> Connection Update </lay-button>
            <lay-button border-style="dashed" style="color: white" size="xs" @click="onEventCall(1)"><lay-icon type="layui-icon-password"/> Password Setting </lay-button>
            <lay-button border-style="dashed" style="color: white" size="xs" @click="logout"><lay-icon type="layui-icon-logout"/> Logout </lay-button>
          </lay-button-group>
          &nbsp;&nbsp;&nbsp;&nbsp;
        </lay-col>
      </lay-row>
    </lay-header>
    <lay-layout>
      <lay-side>
        <lay-menu v-model:selected-key="selectedKey" inverted="true" v-model:openKeys="openKeys" :tree="true" @change-selected-key="onMenuClicked">
          <lay-menu-item id="1">
            <lay-icon type="layui-icon-home"/> Home
          </lay-menu-item>
          <lay-sub-menu id="A">
            <template #title>
              <lay-icon type="layui-icon-username"/> Accounts
            </template>
            <lay-menu-item id="2">
              <lay-icon type="layui-icon-user"/> Management
            </lay-menu-item>
            <lay-menu-item id="3">
              <lay-icon type="layui-icon-vercode"/> Verification
            </lay-menu-item>
            <lay-menu-item id="4">
              <lay-icon type="layui-icon-face-cry"/> Dishonesty
            </lay-menu-item>
          </lay-sub-menu>
          <lay-sub-menu id="B">
            <template #title>
              <lay-icon type="layui-icon-template"/> Actions
            </template>
            <lay-menu-item id="5">
              <lay-icon type="layui-icon-addition"/> Creation
            </lay-menu-item>
            <lay-menu-item id="6">
              <lay-icon type="layui-icon-app"/> Management
            </lay-menu-item>
          </lay-sub-menu>
          <lay-sub-menu id="C">
            <template #title>
              <lay-icon type="layui-icon-template-one"/> Records
            </template>
            <lay-menu-item id="7">
              <lay-icon type="layui-icon-form"/> Participation
            </lay-menu-item>
            <lay-menu-item id="8">
              <lay-icon type="layui-icon-log"/> Duties
            </lay-menu-item>
          </lay-sub-menu>
        </lay-menu>
      </lay-side>
      <lay-body>
        <router-view />
      </lay-body>
    </lay-layout>
  </lay-layout>
</template>

<script>
import Cookies from "js-cookie";
import { layer } from "@layui/layui-vue";

export default {
  setup(){
  },
  created() {
    this.$http.post('/user/verify?token='+Cookies.get('token'))
        .then(response => {
          this.userInf = response.data.data;
        })
        .catch(error =>{
          // console.log(error);
        });
    for(var i in this.route_inf){
      if(this.$route.path === this.route_inf[i].path || this.$route.path === this.route_inf[i].path + '/'){
        this.selectedKey = this.route_inf[i].id;
        return;
      }
    }
  },
  data(){
    return{
      isLevel: false,
      openKeys: [],
      selectedKey: [],
      verifyCodeShow: false,
      verifyEventId: 0,
      changePasswordShow: false,
      updateContactShow: false,
      changeInf:{
        ori_pass: '',
        new_pass: '',
        cfm_pass:'',
        phone: '',
        email: '',
        wechat_id: ''
      },
      userInf:{
      },
      route_inf:[
        {id:"1", path:"/main/inbox"},
        {id:"2", path:"/main/user"},
        {id:"3", path:"/main/user/approve"},
        {id:"4", path:"/main/user/credit"},
        {id:"5", path:"/main/action/create"},
        {id:"6", path:"/main/action"},
        {id:"7", path:"/main/records"},
        {id:"8", path:"/main/records/worker"},
      ]
    }
  },
  watch: {
    '$route'(to, from) {
      if(to.path !== from.path){
        for(var i in this.route_inf){
          if(to.path === this.route_inf[i].path || to.path === this.route_inf[i].path + '/'){
            this.selectedKey = this.route_inf[i].id;
            return;
          }
        }
      }
    }
  },
  methods:{
    logout(){
      this.$http.post('/user/logout?token='+Cookies.get('token')).then(function (a){}).catch(function(a){});
      Cookies.remove('token');
      layer.msg('Logout Successfully!', {time: 1500});
      this.$router.push('/login');
    },
    onMenuClicked(){
      for(var i in this.route_inf){
        if(this.selectedKey === this.route_inf[i].id){
          this.$router.push(this.route_inf[i].path);
          return;
        }
      }
    },
    onVerifyCodeSuccess(){
      this.verifyCodeShow = false;
      if(this.verifyEventId === 1){
        const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,}/;
        if(pattern.test(this.changeInf.new_pass) === false){
          this.disabled = false;
          layer.msg("The currently set password does not meet the rules: The password must be at least 8 characters long and contain uppercase and lowercase letters, numbers, and special symbols",
              {icon:7, time: 1500});
          return;
        }
        const token = Cookies.get('token');
        this.$http.post(`/user/password?token=${token}&origin_pass=${encodeURIComponent(this.changeInf.ori_pass)}&new_pass=${encodeURIComponent(this.changeInf.new_pass)}`)
            .then(response =>{
              if(response.data.status <= 0){
                layer.msg('Account Abnormal', {icon: 2, time: 1500});
              }
              if(response.data.status === 1){
                layer.msg('The original password was entered incorrectly.', {icon: 2, time: 1500});
              }
              if(response.data.status === 2){
                layer.msg('Database abnormality', {icon: 2, time: 1500});
              }
              if(response.data.status === 3){
                layer.msg('Modification Successful', {icon: 1, time: 1500});
                this.changePasswordShow = false;
              }
            })
            .catch(error =>{
              // console.log(error);
              layer.msg('Internet Error', {icon: 2, time: 1500});
            });
      }
      if(this.verifyEventId === 2){
        const token = Cookies.get('token');
        this.$http.post(`/user/contact?token=${token}&origin_pass=${encodeURIComponent(this.changeInf.ori_pass)}&email=${encodeURIComponent(this.changeInf.email)}&phone=${encodeURIComponent(this.changeInf.phone)}&wechat_id=${encodeURIComponent(this.changeInf.wechat_id)}`)
            .then(response =>{
              if(response.data.status <= 0){
                layer.msg('Account Abnormal', {icon: 2, time: 1500});
              }
              if(response.data.status === 1){
                layer.msg('The original password was entered incorrectly.', {icon: 2, time: 1500});
              }
              if(response.data.status === 2){
                layer.msg('Database abnormality', {icon: 2, time: 1500});
              }
              if(response.data.status === 3){
                layer.msg('Update Successfully', {icon: 1, time: 1500});
                this.userInf.wechat_id = this.changeInf.wechat_id;
                this.userInf.phone = this.changeInf.phone;
                this.userInf.email = this.changeInf.email;
                this.updateContactShow = false;
                setTimeout(() => {
                  this.$router.go(0);
                }, 1500);
              }
            })
            .catch(error =>{
              // console.log(error);
              layer.msg('Internet Error', {icon: 2, time: 1500});
            });
      }
    },
    onVerifyCodeClose(){
      this.verifyCodeShow = false;
    },
    onVerifyCodeCall(id){
      this.verifyEventId = id;
      if(id === 1){
        if(this.changeInf.ori_pass === '' || this.changeInf.new_pass === '' || this.changeInf.cfm_pass === ''){
          layer.msg('Password cannot be empty', {icon: 7, time: 1500});
          return;
        }
        if(this.changeInf.new_pass !== this.changeInf.cfm_pass){
          layer.msg('Inconsistency between two passwords', {icon: 7, time: 1500});
          return;
        }
      }
      if(id === 2){
        if(this.changeInf.ori_pass === ''){
          layer.msg('Need to verify password', {icon: 7, time: 1500});
          return;
        }
        if(this.changeInf.wechat_id === ''){
          layer.msg('WeChat ID can\'t be empty', {icon: 7, time: 1500});
          return;
        }
        if(this.changeInf.phone === ''){
          layer.msg('The phone number can\'t be empty', {icon: 7, time: 1500});
          return;
        }
      }
      this.verifyCodeShow = true;
    },
    onEventCall(value){
      if(value === 1){
        this.changeInf.ori_pass = '';
        this.changeInf.new_pass = '';
        this.changeInf.cfm_pass = '';
        this.changePasswordShow = true;
      }
      if(value === 2){
        this.changeInf.ori_pass = '';
        this.changeInf.phone = this.userInf.phone;
        this.changeInf.email = this.userInf.email;
        this.changeInf.wechat_id = this.userInf.wechat_id;
        this.updateContactShow = true;
      }
    }
  }
}
</script>
<style lang="less">
.layout .layui-header {
  width: 99.9%;
  line-height: 60px;
  justify-content: center;
  background: cadetblue;
  color: white;
}
.layout .layui-side {
  height: calc(99.9vh - 60px);
  display: flex;
}
.layout .layui-body {
  height: calc(99.9vh - 60px);
  display: flex;
  background-color: whitesmoke;
}
</style>
