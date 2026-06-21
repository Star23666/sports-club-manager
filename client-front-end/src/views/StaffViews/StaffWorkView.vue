<template>
  <van-pull-refresh
      pulling-text="Pull Down to Refresh..."
      loosing-text="Release to Refresh..."
      loading-text="Loading..."
      success-text="Refresh Successfully..."
      v-model="isLoading"
      @refresh="onRefresh"
  >
    <div v-if="workList.length === 0">
      <van-empty description="No Duty Arrangement" />
    </div>
    <van-row justify="center">
      <div v-for="(item, index) in workList">
        <van-cell-group inset style="min-width: 360px">
          <van-row justify="center" style="margin: 10px 0px 0px 0px;">
            <van-image
                width="90"
                height="90"
                :src="require('@/assets/badminton.png')"
            />
          </van-row>
          <van-row justify="center" style="margin: -20px 0px 0px 0px;">
            <h4>{{item.action_title}}</h4>
          </van-row>
          <van-cell title="Duty Date">{{item.action_date}}</van-cell>
          <van-cell title="Duty Time">{{item.action_time_range}}</van-cell>
          <van-cell title="Duty Location">{{item.action_place}}</van-cell>
          <van-cell title="Racket Requirement">{{item.borrow_num}} {{item.borrow_num > 1 ? "rackets" : "racket"}} </van-cell>
          <van-cell title="Participant List">
            <template #label style="font-size: 8pt" v-if="item.action_member_show">
              *Expand to Check Them
            </template>
            <van-button v-if="!item.action_member_show" :disabled="disabled" type="primary" icon="add-o" size="mini" @click="onMemberQuery(index)">Detail</van-button>
          </van-cell>
          <van-collapse v-model="item.action_names" v-if="item.action_member_show">
            <van-collapse-item v-for="j in item.action_member_list" :title="j.name" :name="j.student_id">
              Student ID：{{j.student_id}}
              <br/>
              WeChat ID：{{j.wechat_id}}
              <br/>
              Phone Number：{{j.phone}}
              <br/>
              Racket Requirement：{{j.borrow ? "Need a Racket" : "No Requirement"}}
            </van-collapse-item>
          </van-collapse>
          <van-cell>
            <div v-if="item.action_state === 1">Preparing</div>
            <div v-else-if="item.action_state === 2">Enrolling</div>
            <van-button v-else-if="item.action_state === 3" @click="onBeginClick(index)" type="success" size="small" icon="play-circle-o" :disabled="disabled">Start Action</van-button>&nbsp
            <van-button v-else-if="item.action_state === 4" @click="onEndClick(index)" type="danger" size="small" icon="stop-circle-o" :disabled="disabled">Terminal Action</van-button>
            <div v-else>Finished</div>
          </van-cell>
        </van-cell-group>
        <br/>
      </div>
    </van-row>
  </van-pull-refresh>
  <br/>
  <br/>
</template>

<script>
import {showFailToast, showSuccessToast} from "vant";
import Cookies from "js-cookie";
export default {
  data(){
    return {
      isLoading: false,
      workList: [/*{
        id:1,
        action_title:'8月31日打球活動（下半場）',
        action_date:'2022年8月31日',
        action_time_range:'15:00~16:00',
        action_place:'東亞運體育館',
        action_state: 3,
        borrow_num: 3,
        action_member_show: true,
        action_member_list:[{name:'秦文靜', student_id:'1225633547', phone:'+8618888888888', wechat_id: 'qingwj', borrow: true},
          {name:'劉東陽', student_id:'1224799323', phone:'+8613786205586', wechat_id: 'ldy20021209',borrow: true},
          {name:'錢琛', student_id:'1223369587', phone:'+8613888888888', wechat_id: '魔法少女琛',borrow: true},
          {name:'趙爽', student_id:'1234459876', phone:'+8616888888888', wechat_id: 'zhaoshuang',borrow: false}],
        action_names:[]
      },
        {
          id:2,
          action_title:'9月31日打球活動（上半場）',
          action_date:'2022年9月31日',
          action_time_range:'14:00~15:00',
          action_place:'科大體育館J座',
          action_state: 4,
          borrow_num: 1,
          action_member_show: false,
          action_member_list:[],
          action_names:[]
        }*/],
      disabled: false

    };
  },
  created(){
    this.$staffVerify();
    this.onRefresh();
  },
  methods:{
    onRefresh(){
      this.isLoading = true;
      this.$http.post('/staff/queryAction?token='+Cookies.get('token'))
          .then(response => {
            if(response.status === 200 && response.data.status === 1)
              this.workList = response.data.data;
            for(var i in this.workList)
              this.workList[i].action_member_show = false;
          })
          .catch(error =>{
            showFailToast("Internet Error");
            console.log(error);
          });
      this.isLoading = false;
    },
    onBeginClick(index){
      this.disabled = true;
      this.$http.post(`/staff/startSign?token=${Cookies.get('token')}&action_id=${this.workList[index].id}`)
          .then(response => {
            if(response.status !== 200)
              showFailToast("System Error");
            if(response.data.status < 0)
              this.$staffVerify();
            if(response.data.status === 0)
              showFailToast("Please refresh the page and try again");
            if(response.data.status === 1)
              showFailToast("Enrollment is not yet closed, please try again later.");
            if(response.data.status === 2)
              showFailToast("Current account not on duty for this action");
            if(response.data.status === 3)
              showFailToast("The current action is not yet ready for check-in, please try again later.");
            if(response.data.status === 4){
              showSuccessToast("This action has been opened, please sign in for the students.");
              this.workList[index].action_state = 4;
            }
            this.disabled=false;
          })
          .catch(error =>{
            console.log(error);
            showFailToast("Internet Error");
            this.disabled=false;
          });
    },
    onEndClick(index){
      this.disabled = true;
      this.$http.post(`/staff/stopAction?token=${Cookies.get('token')}&action_id=${this.workList[index].id}`)
          .then(response => {
            if(response.status !== 200)
              showFailToast("System Error");
            if(response.data.status < 0)
              this.$staffVerify();
            if(response.data.status === 0)
              showFailToast("Please refresh the page and try again");
            if(response.data.status === 1)
              showFailToast("Enrollment is not yet open, please try again later.");
            if(response.data.status === 2)
              showFailToast("Current account not on duty for this action");
            if(response.data.status === 3)
              showFailToast("The current action is not allowed to terminate yet, please try again later.");
            if(response.data.status === 4){
              showSuccessToast("The current action has ended, thank you for your duty, hard work!");
              this.workList[index].action_state = 5;
            }
            this.disabled=false;
          })
          .catch(error =>{
            console.log(error);
            showFailToast("Internet Error");
            this.disabled=false;
          });
    },
    onMemberQuery(index){
      this.disabled = true;
      this.$http.post(`/staff/queryActionMember?token=${Cookies.get('token')}&action_id=${this.workList[index].id}`)
          .then(response => {
            if(response.status === 200 && response.data.status === 1){
              this.workList[index].action_member_list = response.data.data;
              this.workList[index].action_names = [];
              this.workList[index].action_member_show = true;
              this.disabled = false;
            }
          })
          .catch(error =>{
            console.log(error);
            showFailToast("Internet Error");
            this.disabled=false;
          });
      /*this.workList[index].action_member_show = true;
      this.workList[index].action_names = [];
      this.workList[index].action_member_list = [
          {name:'姚彥澤', student_id:'1243610866', phone:'+8613444444444', wechat_id: 'windy', borrow: false},
          {name:'宴寧', student_id:'1220999323', phone:'+8613666666666', wechat_id: '宴宁ccccc', borrow: false},
          {name:'錢琛', student_id:'1223369587', phone:'+8613888888888', wechat_id: '魔法少女琛', borrow: false},
          {name:'趙爽', student_id:'1234459876', phone:'+8616888888888', wechat_id: 'zhaoshuang', borrow: false},
          {name:'杜冥鴉', student_id:'1217526390', phone:'+8613777777777', wechat_id: 'dumy', borrow: true}];*/
    }
  }
}
/*

* */
</script>

<style scoped lang="scss">

</style>