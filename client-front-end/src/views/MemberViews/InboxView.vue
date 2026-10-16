<template>
  <van-toast v-model:show="loading" type="loading" overlay="true" duration="0"
             forbid_click="true" message="Loading..."></van-toast>
  <van-action-sheet v-model:show="setPasswordShow" :z-index="100" title="Password Setting">
    <Vcode :show="isChangePassVerifyShow"
           slider-text="Drag Slider to Complete Puzzle"
           fail-text="Verification Failed, Please Try Again"
           success-text="Verification Passed"
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
          label="Original Password"
          placeholder=""
      />
      <van-field
          label-width="8em"
          v-model="changeInf.newPass"
          type="password"
          name="新密碼"
          label="New Password"
          placeholder=""
      />
      <van-field
          label-width="9em"
          v-model="changeInf.confirmPass"
          type="password"
          name="密碼確認"
          label="Password  Comfirm"
          placeholder=""
      />
      <br/>
      <van-row justify="center">
        <van-button round block type="primary" @click="changePassPre" icon="guide-o" style="width: 200px">
          Change Password
        </van-button>
      </van-row>
      <br/>
    </van-cell-group>
  </van-action-sheet>
  <van-action-sheet v-model:show="setContactShow" :z-index="100" title="Contact Update">
    <Vcode :show="isChangeContactVerifyShow"
           slider-text="Drag Slider to Complete Puzzle"
           fail-text="Verification Failed, Please Try Again"
           success-text="Verification Passed"
           :range="5"
           @success="onChangeContactClick"
           @close="close"
    />
    <p style="font-size: 8pt; color: gray; margin-left: 10pt"> Note: To update member personal information, you must contact customer service with a copy of your ID card to register!</p>
    <van-cell-group>
      <van-field
          v-model="changeInf.originPass"
          type="password"
          name="密碼"
          label="Password"
          placeholder="Need to Verify Password"
      />
      <van-field
          v-model="changeInf.phone"
          type="tel"
          name="手機號碼"
          label="Phone"
          placeholder="Setting Your Phone Number"
      />
      <van-field
          v-model="changeInf.email"
          type="text"
          name="郵箱"
          label="Email"
          placeholder="Setting Your Email"
      />
      <van-field
          v-model="changeInf.wechat_id"
          name="微信號"
          label="WeChat ID"
          placeholder="Use to contact for daily activities"
      />
      <br/>
      <van-row justify="center">
        <van-button round block type="primary" @click="changeContactPre" icon="guide-o" style="width: 200px">
          Update
        </van-button>
      </van-row>
      <br/>
    </van-cell-group>
  </van-action-sheet>
  <van-action-sheet v-model:show="setFastLoginShow" :z-index="100" title="Previous Device Access" style="height: 75%;">
    <center style="font-size: 10pt; margin: 12pt">Device login is disabled. You can revoke previously registered devices below.</center>
    <van-empty
        v-show="equipments.length === 0"
        style="margin-top: 15pt"
        image="https://fastly.jsdelivr.net/npm/@vant/assets/custom-empty-image.png"
        image-size="80"
        description="No previous devices"
    />
    <div class="device-card" v-for="equip in equipments" :style="{ border: equip.is_local ? '4px solid #ccc' : ''}">
      <div class="device-icon">
        <i class="fas fa-device"></i>
      </div>
      <div class="device-info">
        <div class="device-name">Name: {{equip.name}}</div>
        <div class="device-id">Equip ID: {{equip.equip_id}}</div>
        <van-button type="danger" size="mini" icon="delete-o" class="delete-button" @click="deleteEquipment(equip.id, equip.name)">Revoke One-Tap Access</van-button>
        <p style="font-size: 9pt; margin-top: 3pt; margin-bottom: -6pt; color: #666666" v-if="equip.is_local">*this is current equipment</p>
      </div>
    </div>
  </van-action-sheet>
  <van-cell-group inset>
    <div style="margin: 20px 20px 0px 20px">
      {{memInf.name}}, Welcome!
    </div>
    <van-cell></van-cell>
    <van-cell title="Username" size="small">{{memInf.username}}</van-cell>
    <van-cell title="Student ID">{{memInf.student_id}}</van-cell>
    <van-cell title="Phone">{{memInf.phone}}</van-cell>
    <van-cell title="Email" v-if="memInf.email !== ''">{{memInf.email}}</van-cell>
    <van-cell title="WeChat ID">{{memInf.wechat_id}}</van-cell>
    <van-cell title="Status">{{memberStatus}}</van-cell>
    <van-cell title="Dishonest Points" v-if="memInf.state >= 0 && memInf.state <= 2">{{memInf.unsigned_num}}</van-cell>
    <van-cell title="Duty Times" v-if="memInf.state === 3">{{memInf.unsigned_num}}</van-cell>
  </van-cell-group>
  <br/>
  <van-cell-group inset>
    <van-cell title="Operations"/>
    <van-cell title="Password Setting"  is-link @click="onChangePassShow"/>
    <van-cell title="Contact Update"  is-link @click="onChangeContactShow"/>
    <van-cell title="Previous Device Access"  is-link @click="onEquipManageShow"/>
    <van-cell title="Log Out" is-link @click="signout"/>
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
          return 'Blocked';
        case 1:
          return 'Dishonest';
        case 2:
          return 'Normal';
        case 3:
          return 'Duty Staff'
        case 4:
          return 'Administrator'
      }
      return 'Unknown';
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
      showFailToast('This account has been logged out.');
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
        showFailToast('Password cannot be empty');
        return;
      }
      if(this.changeInf.newPass !== this.changeInf.confirmPass){
        showFailToast('Inconsistency between two passwords');
        return;
      }
      this.isChangePassVerifyShow = true;
    },
    onChangePassClick(){
      this.isChangePassVerifyShow = false;
      this.loading = true;
      const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,}/;
      if(pattern.test(this.changeInf.newPass) === false){
        this.loading = false;
        showToast("The currently set password does not meet the rules: The password must be at least 8 characters long and contain uppercase and lowercase letters, numbers, and special symbols");
        return;
      }
      const token = Cookies.get('token');
      this.$http.post(`/user/password?token=${token}`, { origin_pass: this.changeInf.originPass, new_pass: this.changeInf.newPass })
          .then(response =>{
            this.loading = false;
            if(response.data.status <= 0){
              showFailToast('Account Abnormal');
            }
            if(response.data.status === 1){
              showFailToast('The original password was entered incorrectly.');
            }
            if(response.data.status === 2){
              showFailToast('Database abnormality');
            }
            if(response.data.status === 3){
              showSuccessToast('Modification Successful');
              this.setPasswordShow = false;
            }
          })
          .catch(error =>{
            this.loading = false;
            console.log(error);
            showSuccessToast('Modification Successful');
          });
    },
    deleteEquipment(id, name){
      showConfirmDialog({
        message: `Remove previous device “${name}” from this account?`,
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel'
      }).then(() =>{
        this.loading = true;
        this.$http.post(`/user/deleteEquipment?token=${Cookies.get('token')}&id=${id}`)
            .then(response =>{
              this.loading = false;
              if(response.data.status === -2){
                showFailToast('Account Abnormal');
              }
              if(response.data.status === -1){
                showFailToast('This device has been removed. Please refresh the page.');
              }
              if(response.data.status === 0){
                showFailToast('This device is not in this account, please refresh the page.');
              }
              if(response.data.status === 1){
                showSuccessToast('Device Removal Successful');
                this.onEquipManageShow();
              }
            })
            .catch(error =>{
              this.loading = false;
              console.log(error);
              showFailToast('Internet Error');
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
            showFailToast('Internet Error');
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
        showFailToast('Password cannot be empty');
        return;
      }
      if(this.changeInf.phone === ''){
        showFailToast('The phone number cannot be empty.');
        return;
      }
      if(this.changeInf.wechat_id === ''){
        showFailToast('WeChat ID can\'t be empty');
        return;
      }
      this.isChangeContactVerifyShow = true;
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
              showFailToast('Account Abnormal');
            }
            if(response.data.status === 1){
              showFailToast('Incorrect password, authentication failed');
            }
            if(response.data.status === 2){
              sshowFailToast('Database abnormality');
            }
            if(response.data.status === 3){
              showSuccessToast('Contact Updates Successful');
              this.memInf.wechat_id = this.changeInf.wechat_id;
              this.memInf.phone = this.changeInf.phone;
              this.memInf.email = this.changeInf.email;
              this.setContactShow = false;
            }
          })
          .catch(error =>{
            this.loading = false;
            console.log(error);
            showFailToast('Internet Error ');
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
