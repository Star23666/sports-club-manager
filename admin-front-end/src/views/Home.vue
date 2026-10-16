<template>
  <VCode :show="verifyCodeShow"
         slider-text="拖动滑块完成验证"
         fail-text="验证失败，请重试"
         success-text="验证通过"
         :range="5"
         @success="onVerifyCodeSuccess"
         @close="onVerifyCodeClose"
         z-index="10000"
  />
  <lay-layer v-model="changePasswordShow" title="修改密码" :area="['500px', '320px']" z-index="1000">
    <div style="padding: 20px;">
      <lay-form :model="changeInf" required>
        <lay-form-item label="原密码" prop="password" label-width="130px">
          <lay-input v-model="changeInf.ori_pass" type="password">></lay-input>
        </lay-form-item>
        <lay-form-item label="新密码" prop="password" label-width="130px">
          <lay-input v-model="changeInf.new_pass" type="password">></lay-input>
        </lay-form-item>
        <lay-form-item label="确认新密码" prop="password" label-width="130px">
          <lay-input v-model="changeInf.cfm_pass" type="password">></lay-input>
        </lay-form-item>
        <div style="text-align: right">
          <lay-button style="margin-top: 10px;" @click="this.changePasswordShow = false"><lay-icon type="layui-icon-close"/> 取消</lay-button>
          <lay-button type="primary" style="margin-top: 10px; " @click="onVerifyCodeCall(1)"><lay-icon type="layui-icon-release"/> 提交</lay-button>
        </div>
      </lay-form>
    </div>
  </lay-layer>

  <lay-layer v-model="updateContactShow" title="修改联系方式" :area="['500px', '375px']" z-index="1000">
    <div style="padding: 20px;">
      <lay-form :model="changeInf">
        <lay-form-item label="密码" prop="password" required>
          <lay-input v-model="changeInf.ori_pass" type="password">></lay-input>
        </lay-form-item>
        <lay-form-item label="手机号" prop="text" required>
          <lay-input v-model="changeInf.phone" type="test">></lay-input>
        </lay-form-item>
        <lay-form-item label="微信号" prop="text" required>
          <lay-input v-model="changeInf.wechat_id" type="text">></lay-input>
        </lay-form-item>
        <lay-form-item label="邮箱" prop="text">
          <lay-input v-model="changeInf.email" type="text">></lay-input>
        </lay-form-item>
        <div style="text-align: right">
          <lay-button style="margin-top: 10px;" @click="this.updateContactShow = false"><lay-icon type="layui-icon-close"/> 取消</lay-button>
          <lay-button type="primary" style="margin-top: 10px; " @click="onVerifyCodeCall(2)"><lay-icon type="layui-icon-release"/> 提交</lay-button>
        </div>
      </lay-form>
    </div>
  </lay-layer>

  <lay-layout class="layout">
    <lay-header>
      <lay-row space="3">
        <lay-col md="10">
          <h3>
            &nbsp;&nbsp; <lay-avatar :src="require('@/assets/badminton.png')" radius></lay-avatar>&nbsp;体育俱乐部管理后台 &nbsp;
          </h3>
        </lay-col>
        <lay-col md="14" style="text-align: right; margin-top: 0px;">
          欢迎，{{this.userInf.name}}！&nbsp;
          <lay-button-group style="margin-top: -3px;">
            <lay-button border-style="dashed" style="color: white" size="xs" @click="onEventCall(2)"><lay-icon type="layui-icon-cellphone"/> 修改联系方式 </lay-button>
            <lay-button border-style="dashed" style="color: white" size="xs" @click="onEventCall(1)"><lay-icon type="layui-icon-password"/> 修改密码 </lay-button>
            <lay-button border-style="dashed" style="color: white" size="xs" @click="logout"><lay-icon type="layui-icon-logout"/> 退出登录 </lay-button>
          </lay-button-group>
          &nbsp;&nbsp;&nbsp;&nbsp;
        </lay-col>
      </lay-row>
    </lay-header>
    <lay-layout>
      <lay-side>
        <lay-menu v-model:selected-key="selectedKey" inverted="true" v-model:openKeys="openKeys" :tree="true" @change-selected-key="onMenuClicked">
          <lay-menu-item id="1">
            <lay-icon type="layui-icon-home"/> 首页
          </lay-menu-item>
          <lay-sub-menu id="A">
            <template #title>
              <lay-icon type="layui-icon-username"/> 账号
            </template>
            <lay-menu-item id="2">
              <lay-icon type="layui-icon-user"/> 账号管理
            </lay-menu-item>
            <lay-menu-item id="3">
              <lay-icon type="layui-icon-vercode"/> 账号审核
            </lay-menu-item>
            <lay-menu-item id="4">
              <lay-icon type="layui-icon-face-cry"/> 缺席记录
            </lay-menu-item>
          </lay-sub-menu>
          <lay-sub-menu id="B">
            <template #title>
              <lay-icon type="layui-icon-template"/> 活动
            </template>
            <lay-menu-item id="5">
              <lay-icon type="layui-icon-addition"/> 创建活动
            </lay-menu-item>
            <lay-menu-item id="6">
              <lay-icon type="layui-icon-app"/> 活动管理
            </lay-menu-item>
          </lay-sub-menu>
          <lay-sub-menu id="C">
            <template #title>
              <lay-icon type="layui-icon-template-one"/> 记录
            </template>
            <lay-menu-item id="7">
              <lay-icon type="layui-icon-form"/> 报名记录
            </lay-menu-item>
            <lay-menu-item id="8">
              <lay-icon type="layui-icon-log"/> 值班记录
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
import { skipPuzzleForLocalDemo } from '@/utils/localDemo';

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
      layer.msg('已退出登录', {time: 1500});
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
          layer.msg("密码至少 8 位，且须包含大小写字母、数字和特殊符号",
              {icon:7, time: 1500});
          return;
        }
        const token = Cookies.get('token');
        this.$http.post(`/user/password?token=${token}`, { origin_pass: this.changeInf.ori_pass, new_pass: this.changeInf.new_pass })
            .then(response =>{
              if(response.data.status <= 0){
                layer.msg('账号状态异常', {icon: 2, time: 1500});
              }
              if(response.data.status === 1){
                layer.msg('原密码不正确。', {icon: 2, time: 1500});
              }
              if(response.data.status === 2){
                layer.msg('数据库异常', {icon: 2, time: 1500});
              }
              if(response.data.status === 3){
                layer.msg('修改成功', {icon: 1, time: 1500});
                this.changePasswordShow = false;
              }
            })
            .catch(error =>{
              // console.log(error);
              layer.msg('网络异常，请稍后重试', {icon: 2, time: 1500});
            });
      }
      if(this.verifyEventId === 2){
        const token = Cookies.get('token');
        this.$http.post(`/user/contact?token=${token}`, {
          origin_pass: this.changeInf.ori_pass, email: this.changeInf.email,
          phone: this.changeInf.phone, wechat_id: this.changeInf.wechat_id
        })
            .then(response =>{
              if(response.data.status <= 0){
                layer.msg('账号状态异常', {icon: 2, time: 1500});
              }
              if(response.data.status === 1){
                layer.msg('原密码不正确。', {icon: 2, time: 1500});
              }
              if(response.data.status === 2){
                layer.msg('数据库异常', {icon: 2, time: 1500});
              }
              if(response.data.status === 3){
                layer.msg('更新成功', {icon: 1, time: 1500});
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
              layer.msg('网络异常，请稍后重试', {icon: 2, time: 1500});
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
          layer.msg('密码不能为空', {icon: 7, time: 1500});
          return;
        }
        if(this.changeInf.new_pass !== this.changeInf.cfm_pass){
          layer.msg('两次输入的密码不一致', {icon: 7, time: 1500});
          return;
        }
      }
      if(id === 2){
        if(this.changeInf.ori_pass === ''){
          layer.msg('请先验证密码', {icon: 7, time: 1500});
          return;
        }
        if(this.changeInf.wechat_id === ''){
          layer.msg('微信号不能为空', {icon: 7, time: 1500});
          return;
        }
        if(this.changeInf.phone === ''){
          layer.msg('手机号不能为空', {icon: 7, time: 1500});
          return;
        }
      }
      if (skipPuzzleForLocalDemo()) this.onVerifyCodeSuccess();
      else this.verifyCodeShow = true;
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
