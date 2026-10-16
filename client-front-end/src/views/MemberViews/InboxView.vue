<template>
  <van-toast v-model:show="loading" type="loading" overlay="true" duration="0"
             forbid_click="true" message="加载中..."></van-toast>
  <van-action-sheet v-model:show="setPasswordShow" :z-index="100" title="修改密码">
    <Vcode :show="isChangePassVerifyShow"
           slider-text="拖动滑块完成验证"
           fail-text="验证失败，请重试"
           success-text="验证通过"
           :range="5"
           @success="onChangePassClick"
           @close="close"
    />
    <van-cell-group>
      <van-field
          label-width="9em"
          v-model="changeInf.originPass"
          type="password"
          name="原密碼"
          label="原密码"
          placeholder=""
      />
      <van-field
          label-width="8em"
          v-model="changeInf.newPass"
          type="password"
          name="新密碼"
          label="新密码"
          placeholder=""
      />
      <van-field
          label-width="9em"
          v-model="changeInf.confirmPass"
          type="password"
          name="密碼確認"
          label="确认新密码"
          placeholder=""
      />
      <br/>
      <van-row justify="center">
        <van-button round block type="primary" @click="changePassPre" icon="guide-o" style="width: 200px">
          修改密码
        </van-button>
      </van-row>
      <br/>
    </van-cell-group>
  </van-action-sheet>
  <van-action-sheet v-model:show="setContactShow" :z-index="100" title="修改联系方式">
    <Vcode :show="isChangeContactVerifyShow"
           slider-text="拖动滑块完成验证"
           fail-text="验证失败，请重试"
           success-text="验证通过"
           :range="5"
           @success="onChangeContactClick"
           @close="close"
    />
    <p style="font-size: 8pt; color: gray; margin-left: 10pt">如需修改会员身份资料，请联系管理员核验身份。</p>
    <van-cell-group>
      <van-field
          v-model="changeInf.originPass"
          type="password"
          name="密碼"
          label="密码"
          placeholder="输入密码以验证身份"
      />
      <van-field
          v-model="changeInf.phone"
          type="tel"
          name="手機號碼"
          label="手机号"
          placeholder="填写手机号"
      />
      <van-field
          v-model="changeInf.email"
          type="text"
          name="郵箱"
          label="邮箱"
          placeholder="填写邮箱"
      />
      <van-field
          v-model="changeInf.wechat_id"
          name="微信號"
          label="微信号"
          placeholder="用于日常活动联系"
      />
      <br/>
      <van-row justify="center">
        <van-button round block type="primary" @click="changeContactPre" icon="guide-o" style="width: 200px">
          更新联系方式
        </van-button>
      </van-row>
      <br/>
    </van-cell-group>
  </van-action-sheet>
  <van-action-sheet v-model:show="setFastLoginShow" :z-index="100" title="历史设备权限" style="height: 75%;">
    <center style="font-size: 10pt; margin: 12pt">设备登录已停用，你仍可移除之前登记的设备。</center>
    <van-empty
        v-show="equipments.length === 0"
        style="margin-top: 15pt"
        image="https://fastly.jsdelivr.net/npm/@vant/assets/custom-empty-image.png"
        image-size="80"
        description="暂无历史设备"
    />
    <div class="device-card" v-for="equip in equipments" :style="{ border: equip.is_local ? '4px solid #ccc' : ''}">
      <div class="device-icon">
        <i class="fas fa-device"></i>
      </div>
      <div class="device-info">
        <div class="device-name">名称：{{equip.name}}</div>
        <div class="device-id">设备 ID：{{equip.equip_id}}</div>
        <van-button type="danger" size="mini" icon="delete-o" class="delete-button" @click="deleteEquipment(equip.id, equip.name)">移除设备权限</van-button>
        <p style="font-size: 9pt; margin-top: 3pt; margin-bottom: -6pt; color: #666666" v-if="equip.is_local">当前设备</p>
      </div>
    </div>
  </van-action-sheet>
  <van-cell-group inset>
    <div style="margin: 20px 20px 0px 20px">
      欢迎你，{{memInf.name}}！
    </div>
    <van-cell></van-cell>
    <van-cell title="用户名" size="small">{{memInf.username}}</van-cell>
    <van-cell title="学号">{{memInf.student_id}}</van-cell>
    <van-cell title="手机号">{{memInf.phone}}</van-cell>
    <van-cell title="邮箱" v-if="memInf.email !== ''">{{memInf.email}}</van-cell>
    <van-cell title="微信号">{{memInf.wechat_id}}</van-cell>
    <van-cell title="账号状态">{{memberStatus}}</van-cell>
    <van-cell title="缺席次数" v-if="memInf.state >= 0 && memInf.state <= 2">{{memInf.unsigned_num}}</van-cell>
    <van-cell title="值班次数" v-if="memInf.state === 3">{{memInf.unsigned_num}}</van-cell>
  </van-cell-group>
  <br/>
  <van-cell-group inset>
    <van-cell title="账号操作"/>
    <van-cell title="修改密码"  is-link @click="onChangePassShow"/>
    <van-cell title="修改联系方式"  is-link @click="onChangeContactShow"/>
    <van-cell title="历史设备权限"  is-link @click="onEquipManageShow"/>
    <van-cell title="退出登录" is-link @click="signout"/>
  </van-cell-group>
  <br/>
  <br/>
  <br/>
  <br/>
</template>

<script>
import Cookies from "js-cookie";
import {showSuccessToast, showFailToast, showToast} from "vant";
import { showConfirmDialog } from 'vant';
import { skipPuzzleForLocalDemo } from '@/utils/localDemo';

export default {
  data(){
    return {
      memInf: {
        name: '',
        username: '',
        student_id: '',
        phone: '',
        email: '',
        wechat_id: '',
        state: 0,
        unsigned_num: 0
      },
      changeInf: {
        originPass: '',
        newPass: '',
        confirmPass: '',
        wechat_id: '',
        phone: '',
        email: '',
      },
      loading: false,
      equipments: [],
      setPasswordShow: false,
      setContactShow: false,
      isChangePassVerifyShow: false,
      isChangeContactVerifyShow: false,
      setFastLoginShow: false
    };
  },
  computed: {
    memberStatus() {
      switch (this.memInf.state) {
        case 0:
          return '已停用';
        case 1:
          return '参加活动受限';
        case 2:
          return '正常';
        case 3:
          return '工作人员'
        case 4:
          return '管理员'
      }
      return '未知';
    }
  },
  created(){
    this.loading = true;
    if(this.$route.name === 'member_membership')
      this.$memberVerify();
    else
      this.$staffVerify();
    this.$http.post('/user/verify?token='+Cookies.get('token'))
        .then(response => {
          console.log(response.data.data);
          this.memInf = response.data.data;
          this.loading = false;
        })
        .catch(error =>{
          this.loading = false;
          console.log(error);
        });
  },
  methods: {
    signout(){
      this.$http.post('/user/logout?token='+Cookies.get('token')).then(function (a){}).catch(function(a){});
      Cookies.remove('token');
      showSuccessToast('已退出登录');
      this.$router.push('/inbox');
    },
    onChangePassShow(){
      this.changeInf.confirmPass = '';
      this.changeInf.newPass = '';
      this.changeInf.originPass = '';
      this.setPasswordShow = true;
    },
    changePassPre(){
      if(this.changeInf.originPass === '' || this.changeInf.newPass === '' || this.changeInf.confirmPass === ''){
        showFailToast('请输入密码');
        return;
      }
      if(this.changeInf.newPass !== this.changeInf.confirmPass){
        showFailToast('两次输入的新密码不一致');
        return;
      }
      if (skipPuzzleForLocalDemo()) this.onChangePassClick();
      else this.isChangePassVerifyShow = true;
    },
    onChangePassClick(){
      this.isChangePassVerifyShow = false;
      this.loading = true;
      const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,}/;
      if(pattern.test(this.changeInf.newPass) === false){
        this.loading = false;
        showToast("密码至少 8 位，且须包含大小写字母、数字和特殊符号");
        return;
      }
      const token = Cookies.get('token');
      this.$http.post(`/user/password?token=${token}`, { origin_pass: this.changeInf.originPass, new_pass: this.changeInf.newPass })
          .then(response =>{
            this.loading = false;
            if(response.data.status <= 0){
              showFailToast('账号状态异常');
            }
            if(response.data.status === 1){
              showFailToast('原密码错误');
            }
            if(response.data.status === 2){
              showFailToast('数据库异常，请稍后重试');
            }
            if(response.data.status === 3){
              showSuccessToast('密码修改成功');
              this.setPasswordShow = false;
            }
          })
          .catch(error =>{
            this.loading = false;
            console.log(error);
            showFailToast('网络异常，密码未确认修改成功');
          });
    },
    deleteEquipment(id, name){
      showConfirmDialog({
        message: `确定移除设备“${name}”的访问权限吗？`,
        confirmButtonText: '确认移除',
        cancelButtonText: '取消'
      }).then(() =>{
        this.loading = true;
        this.$http.post(`/user/deleteEquipment?token=${Cookies.get('token')}&id=${id}`)
            .then(response =>{
              this.loading = false;
              if(response.data.status === -2){
                showFailToast('账号状态异常');
              }
              if(response.data.status === -1){
                showFailToast('设备已移除，请刷新页面');
              }
              if(response.data.status === 0){
                showFailToast('设备不属于此账号，请刷新页面');
              }
              if(response.data.status === 1){
                showSuccessToast('设备权限已移除');
                this.onEquipManageShow();
              }
            })
            .catch(error =>{
              this.loading = false;
              console.log(error);
              showFailToast('网络异常，请稍后重试');
            });
      }).catch(() => {});
    },
    async onEquipManageShow(){
      this.loading = true;
      if(this.$route.name === 'member_membership')
        this.$memberVerify();
      else
        this.$staffVerify();
      this.$http.post('/user/queryEquips?token='+Cookies.get('token'), { local: await this.$finger() })
          .then(response => {
            this.loading = false;
            if(response.status === 200 && response.data.status > 0)
              this.equipments = response.data.data;
            this.setFastLoginShow = true;
          })
          .catch(error =>{
            this.loading = false;
            console.log(error);
            showFailToast('网络异常，请稍后重试');
          });
    },
    onChangeContactShow(){
      this.changeInf.phone = this.memInf.phone;
      this.changeInf.email = this.memInf.email;
      this.changeInf.wechat_id = this.memInf.wechat_id;
      this.changeInf.originPass = '';
      this.setContactShow = true;
    },
    changeContactPre(){
      if(this.changeInf.originPass === ''){
        showFailToast('请输入密码');
        return;
      }
      if(this.changeInf.phone === ''){
        showFailToast('请输入手机号');
        return;
      }
      if(this.changeInf.wechat_id === ''){
        showFailToast('请输入微信号');
        return;
      }
      if (skipPuzzleForLocalDemo()) this.onChangeContactClick();
      else this.isChangeContactVerifyShow = true;
    },
    onChangeContactClick(){
      this.loading = true;
      this.isChangeContactVerifyShow = false;
      this.isChangePassVerifyShow = false;
      const token = Cookies.get('token');
      this.$http.post(`/user/contact?token=${token}`, {
        origin_pass: this.changeInf.originPass, email: this.changeInf.email,
        phone: this.changeInf.phone, wechat_id: this.changeInf.wechat_id
      })
          .then(response =>{
            this.loading = false;
            if(response.data.status <= 0){
              showFailToast('账号状态异常');
            }
            if(response.data.status === 1){
              showFailToast('密码错误，身份验证失败');
            }
            if(response.data.status === 2){
              showFailToast('数据库异常，请稍后重试');
            }
            if(response.data.status === 3){
              showSuccessToast('联系方式已更新');
              this.memInf.wechat_id = this.changeInf.wechat_id;
              this.memInf.phone = this.changeInf.phone;
              this.memInf.email = this.changeInf.email;
              this.setContactShow = false;
            }
          })
          .catch(error =>{
            this.loading = false;
            console.log(error);
            showFailToast('网络异常，请稍后重试');
          });
    },
    close(){
      this.isChangeContactVerifyShow = false;
      this.isChangePassVerifyShow = false;
    }
  }
}
</script>

<style scoped lang="scss">
.device-card {
  display: flex;
  align-items: center;
  border: 1px solid #ccc;
  border-radius: 10px;
  padding: 16px;
  width: 80%;
  margin-left: auto;
  margin-right: auto;
  margin-top: 15pt;
  max-width: 350px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.device-icon {
  flex-shrink: 0;
  margin-right: 16px;
  width: 88px;
  height: 88px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-image: url('~@/assets/equipment.png');
  background-size: contain;
  background-repeat: no-repeat;
}

.device-info {
  flex-grow: 1;
  text-align: center;
}

.device-name {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 8px;
}

.device-id {
  color: #666;
  margin-bottom: 12px;
}

.delete-button {
  background-color: #ff4d4f;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 12px;
}

.delete-button:hover {
  background-color: #ff1a1c;
}
</style>
