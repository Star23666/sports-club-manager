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
  <van-dialog v-model:show="isAddMyEquipmentShow" title="Enable One-Tap on This Device" @cancel="this.isAddMyEquipmentShow = false"
              show-cancel-button cancel-button-text="Cancel" confirm-button-text="Confirm" @confirm="submitEquipment">
    <div style="width: 85%; margin-right: auto; margin-left: auto; margin-top: 5pt; margin-bottom: 0pt; font-size: 10pt; color: #666666">
      This operation will allow this device to use “One-Tap Fast Login”, which allows to login without password.
      <b>Do not do this on any untrusted device</b>! To continue, please set a name for this device in following area, within 12 characters.
    </div>
    <van-field v-model="name" placeholder="Equipment Name" left-icon="graphic" style="font-size: 12pt; width: 95%; margin-right: auto; margin-left: auto;"/>
    <div style="width: 85%; margin-right: auto; margin-left: auto; margin-top: 5pt; margin-bottom: 0pt; font-size: 10pt; color: #666666">
      <van-icon name="warn-o" /> The current operation is a critical operation and requires verification of password!
    </div>
    <van-field v-model="password" placeholder="Password" left-icon="lock" style="font-size: 12pt; width: 95%; margin-right: auto; margin-left: auto;" type="password"/>
  </van-dialog>
  <van-action-sheet v-model:show="setFastLoginShow" :z-index="100" title="One-Tap Login Management" style="height: 75%;">
    <van-empty
        v-show="equipments.length === 0"
        style="margin-top: 15pt"
        image="https://fastly.jsdelivr.net/npm/@vant/assets/custom-empty-image.png"
        image-size="80"
        description="No One-Tap Login Device"
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
    <van-button round block icon="link-o" :disabled="disabled" type="primary" size="small" @click="onAddManageClick"
                style="width: 75%; max-width: 300px; height: 40px; margin-top: 15pt; margin-left: auto; margin-right: auto" v-show="canAddMyEquipment">Enable One-Tap Login on This Device</van-button>
    <center style="font-size: 9pt; margin-top: 5pt">Note: Maximum of five devices can be added.<br/><br/></center>
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
    <van-cell title="One-Tap Login Management"  is-link @click="onEquipManageShow"/>
    <van-cell title="Log Out" is-link @click="signout"/>
  </van-cell-group>
  <br/>
  <br/>
  <br/>
  <br/>
</template>

<script>
import Cookies from "js-cookie";
import {showSuccessToast, showFailToast, showToast, showDialog} from "vant";
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
      name:'',
      password: '',
      equipments: [],
      setPasswordShow: false,
      setContactShow: false,
      isChangePassVerifyShow: false,
      isChangeContactVerifyShow: false,
      isAddMyEquipmentShow: false,
      setFastLoginShow: false,
      canAddMyEquipment: true
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
        message: `After removing one-tap access of the equipment “${name}”, it will need to be reauthorized, is it confirmed?`,
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
      this.$http.post('/user/queryEquips?token='+Cookies.get('token')+'&local='+await this.$finger())
          .then(response => {
            this.loading = false;
            if(response.status === 200 && response.data.status > 0)
              this.equipments = response.data.data;
            if(response.data.status === 2)
              this.canAddMyEquipment = false;
            else
              this.canAddMyEquipment = true;
            this.setFastLoginShow = true;
          })
          .catch(error =>{
            this.loading = false;
            console.log(error);
            showFailToast('Internet Error');
          });
    },
    async submitEquipment(){
      if(this.getByteLength(this.password) === 0){
        showFailToast('Password cannot be empty');
        return;
      }
      if(this.getByteLength(this.name) > 12){
        showFailToast('Equipment name is too long');
        return;
      }
      if(this.getByteLength(this.name) === 0){
        showFailToast('The device name cannot be null');
        return;
      }
      this.loading = true;
      this.$http.post('/user/newEquipment?token='+Cookies.get('token')+'&equip_id='+await this.$finger()+'&name='+encodeURIComponent(this.name), { password: this.password })
          .then(response => {
            this.loading = false;
            if(response.status !== 200){
              showFailToast('System Error');
              return;
            }
            if(response.data.status === -2){
              showFailToast('Wrong password input, validation failed');
              return;
            }
            if(response.data.status === -1){
              showDialog({
                message: 'Currently, the device has been bound by another account for one-tap login, it is not allowed to bind more than one account at the same time for one device, please remove it from that account and try again!',
                confirmButtonText: 'Ok'
              }).then(() => {});
              return;
            }
            if(response.data.status === 0){
              showDialog({
                message: 'The number of devices in the current account has reached the limit, if you want to add new devices, please remove some of the existing devices and try again!',
                confirmButtonText: 'Ok'
              }).then(() => {
                // on close
              });
              return;
            }
            showSuccessToast('Current device bound successfully');
            this.onEquipManageShow();
          })
          .catch(error =>{
            this.loading = false;
            showFailToast('Internet Error');
            console.log(error);
          });
    },
    onAddManageClick(){
      this.name = "";
      this.password = "";
      this.isAddMyEquipmentShow = true;
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
      this.$http.post(`/user/contact?token=${token}&email=${encodeURIComponent(this.changeInf.email)}&phone=${encodeURIComponent(this.changeInf.phone)}&wechat_id=${encodeURIComponent(this.changeInf.wechat_id)}`, { origin_pass: this.changeInf.originPass })
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
    },
    getByteLength(str) {
      let len = 0;
      for (let i = 0; i < str.length; i++) {
        const code = str.charCodeAt(i);
        if (code >= 0 && code <= 128) {
          len += 1;
        } else {
          len += 2;
        }
      }
      return len;
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
