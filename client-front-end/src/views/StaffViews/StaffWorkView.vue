<template>
  <van-pull-refresh
      pulling-text="下拉刷新"
      loosing-text="松开刷新"
      loading-text="加载中..."
      success-text="刷新成功"
      v-model="isLoading"
      @refresh="onRefresh"
  >
    <div v-if="workList.length === 0">
      <van-empty description="暂无值班安排" />
    </div>
    <van-row justify="center">
      <div v-for="(item, index) in workList">
        <van-cell-group inset style="width: 360px; max-width: calc(100vw - 32px); box-sizing: border-box">
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
          <van-cell title="值班日期">{{item.action_date}}</van-cell>
          <van-cell title="活动时间">{{item.action_time_range}}</van-cell>
          <van-cell title="活动地点">{{item.action_place}}</van-cell>
          <van-cell title="需借球拍">{{item.borrow_num}} 把</van-cell>
          <van-cell title="参加者名单">
            <template #label style="font-size: 8pt" v-if="item.action_member_show">
              展开查看参加者
            </template>
            <van-button v-if="!item.action_member_show" :disabled="disabled" type="primary" icon="add-o" size="mini" @click="onMemberQuery(index)">查看详情</van-button>
          </van-cell>
          <van-collapse v-model="item.action_names" v-if="item.action_member_show">
            <van-collapse-item v-for="j in item.action_member_list" :title="j.name" :name="j.student_id">
              学号：{{j.student_id}}
              <br/>
              微信号：{{j.wechat_id}}
              <br/>
              手机号：{{j.phone}}
              <br/>
              球拍：{{j.borrow ? "需要借用" : "无需借用"}}
            </van-collapse-item>
          </van-collapse>
          <van-cell>
            <div v-if="item.action_state === 1">准备中</div>
            <div v-else-if="item.action_state === 2">报名中</div>
            <van-button v-else-if="item.action_state === 3" @click="onBeginClick(index)" type="success" size="small" icon="play-circle-o" :disabled="disabled">开始签到</van-button>&nbsp
            <van-button v-else-if="item.action_state === 4" @click="onEndClick(index)" type="danger" size="small" icon="stop-circle-o" :disabled="disabled">结束活动</van-button>
            <div v-else>已结束</div>
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
            showFailToast("网络异常，请稍后重试");
            console.log(error);
          });
      this.isLoading = false;
    },
    onBeginClick(index){
      this.disabled = true;
      this.$http.post(`/staff/startSign?token=${Cookies.get('token')}&action_id=${this.workList[index].id}`)
          .then(response => {
            if(response.status !== 200)
              showFailToast("系统异常，请稍后重试");
            if(response.data.status < 0)
              this.$staffVerify();
            if(response.data.status === 0)
              showFailToast("请刷新页面后重试");
            if(response.data.status === 1)
              showFailToast("报名尚未截止，请稍后再试");
            if(response.data.status === 2)
              showFailToast("你不是该活动的值班人员");
            if(response.data.status === 3)
              showFailToast("活动尚未开放签到，请稍后再试");
            if(response.data.status === 4){
              showSuccessToast("签到已开放，请为参加者签到");
              this.workList[index].action_state = 4;
            }
            this.disabled=false;
          })
          .catch(error =>{
            console.log(error);
            showFailToast("网络异常，请稍后重试");
            this.disabled=false;
          });
    },
    onEndClick(index){
      this.disabled = true;
      this.$http.post(`/staff/stopAction?token=${Cookies.get('token')}&action_id=${this.workList[index].id}`)
          .then(response => {
            if(response.status !== 200)
              showFailToast("系统异常，请稍后重试");
            if(response.data.status < 0)
              this.$staffVerify();
            if(response.data.status === 0)
              showFailToast("请刷新页面后重试");
            if(response.data.status === 1)
              showFailToast("活动状态不允许结束，请稍后再试");
            if(response.data.status === 2)
              showFailToast("你不是该活动的值班人员");
            if(response.data.status === 3)
              showFailToast("尚未到活动结束时间，请稍后再试");
            if(response.data.status === 4){
              showSuccessToast("活动已结束，感谢值班");
              this.workList[index].action_state = 5;
            }
            this.disabled=false;
          })
          .catch(error =>{
            console.log(error);
            showFailToast("网络异常，请稍后重试");
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
            showFailToast("网络异常，请稍后重试");
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
