<template>
  <div class="bills-page">
    <van-nav-bar title="缴费中心" left-arrow @click-left="router.back()" />

    <!-- 待缴费用统计 -->
    <div class="payment-summary">
      <div class="summary-item">
        <span class="amount">¥{{ unpaidTotal }}</span>
        <span class="label">待缴费用</span>
      </div>
      <van-button type="primary" round @click="handleBatchPay">一键缴费</van-button>
    </div>

    <!-- 费用类型筛选 -->
    <van-dropdown-menu>
      <van-dropdown-item v-model="selectedType" :options="feeTypes" />
      <van-dropdown-item v-model="selectedStatus" :options="statusOptions" />
    </van-dropdown-menu>

    <!-- 账单列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <div
          v-for="bill in bills"
          :key="bill.id"
          class="bill-item"
          @click="showBillDetail(bill)"
        >
          <div class="bill-header">
            <div class="bill-type">
              <van-icon :name="getBillIcon(bill.fee_type)" size="20" />
              <span>{{ getBillTypeName(bill.fee_type) }}</span>
            </div>
            <van-tag :type="bill.status === 'paid' ? 'success' : 'danger'">
              {{ getStatusName(bill.status) }}
            </van-tag>
          </div>
          <div class="bill-content">
            <div class="bill-info">
              <p class="bill-period">账期: {{ bill.billing_period }}</p>
              <p class="bill-due">到期: {{ formatDate(bill.due_date) }}</p>
            </div>
            <div class="bill-amount">
              <span class="amount">¥{{ bill.total_amount }}</span>
            </div>
          </div>
          <div v-if="bill.status === 'pending'" class="bill-actions">
            <van-button type="primary" size="small" round @click.stop="handlePay(bill)">
              立即缴费
            </van-button>
          </div>
        </div>
      </van-list>
    </van-pull-refresh>

    <!-- 账单详情弹窗 -->
    <van-popup v-model:show="showDetail" position="bottom" :style="{ height: '60%' }">
      <div v-if="selectedBill" class="bill-detail">
        <h3>账单详情</h3>
        <van-cell-group>
          <van-cell title="账单号" :value="selectedBill.bill_number" />
          <van-cell title="费用类型" :value="getBillTypeName(selectedBill.fee_type)" />
          <van-cell title="账期" :value="selectedBill.billing_period" />
          <van-cell title="应缴金额" :value="`¥${selectedBill.amount}`" />
          <van-cell title="滞纳金" :value="`¥${selectedBill.late_fee || 0}`" />
          <van-cell title="合计" :value="`¥${selectedBill.total_amount}`" />
          <van-cell title="到期日期" :value="formatDate(selectedBill.due_date)" />
          <van-cell title="状态" :value="getStatusName(selectedBill.status)" />
        </van-cell-group>
        
        <div v-if="selectedBill.status === 'pending'" class="detail-actions">
          <van-button type="primary" block round @click="handlePay(selectedBill)">
            立即缴费
          </van-button>
        </div>
      </div>
    </van-popup>

    <!-- 支付方式选择 -->
    <van-action-sheet
      v-model:show="showPayment"
      title="选择支付方式"
      @select="onPaymentSelect"
    >
      <div class="payment-methods">
        <div class="payment-method" @click="onPaymentSelect('wechat')">
          <van-icon name="wechat" size="32" color="#07c160" />
          <span>微信支付</span>
        </div>
        <div class="payment-method" @click="onPaymentSelect('alipay')">
          <van-icon name="alipay" size="32" color="#1677ff" />
          <span>支付宝</span>
        </div>
      </div>
    </van-action-sheet>

    <!-- 底部导航 -->
    <van-tabbar v-model="active" route>
      <van-tabbar-item to="/home" icon="home-o">首页</van-tabbar-item>
      <van-tabbar-item to="/chat" icon="chat-o">智能咨询</van-tabbar-item>
      <van-tabbar-item to="/bills" icon="bill-o">缴费</van-tabbar-item>
      <van-tabbar-item to="/profile" icon="user-o">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showSuccessToast } from 'vant'
import axios from '../utils/axios'

const router = useRouter()
const active = ref(2)

const bills = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)

const selectedType = ref(0)
const selectedStatus = ref(0)
const showDetail = ref(false)
const showPayment = ref(false)
const selectedBill = ref(null)
const currentPayingBill = ref(null)

const feeTypes = [
  { text: '全部类型', value: 0 },
  { text: '物业费', value: 'property' },
  { text: '水费', value: 'water' },
  { text: '电费', value: 'electricity' },
  { text: '停车费', value: 'parking' }
]

const statusOptions = [
  { text: '全部状态', value: 0 },
  { text: '待支付', value: 'pending' },
  { text: '已支付', value: 'paid' },
  { text: '已逾期', value: 'overdue' }
]

// 计算待缴费用总额
const unpaidTotal = computed(() => {
  return bills.value
    .filter(bill => bill.status === 'pending')
    .reduce((sum, bill) => sum + bill.total_amount, 0)
    .toFixed(2)
})

onMounted(() => {
  loadBills()
})

const loadBills = async () => {
  try {
    const response = await axios.get('/api/payments/bills')
    bills.value = response.data
    
    // 模拟数据(开发阶段)
    if (bills.value.length === 0) {
      bills.value = [
        {
          id: 1,
          bill_number: 'BILL202401001',
          fee_type: 'property',
          amount: 1500,
          late_fee: 0,
          total_amount: 1500,
          billing_period: '2024-01',
          due_date: '2024-01-31',
          status: 'pending'
        },
        {
          id: 2,
          bill_number: 'BILL202401002',
          fee_type: 'parking',
          amount: 500,
          late_fee: 0,
          total_amount: 500,
          billing_period: '2024-01',
          due_date: '2024-01-31',
          status: 'pending'
        }
      ]
    }
  } catch (error) {
    console.error('加载账单失败:', error)
  }
}

const onLoad = () => {
  // 加载更多数据
  loading.value = false
  finished.value = true
}

const onRefresh = async () => {
  await loadBills()
  refreshing.value = false
  showSuccessToast('刷新成功')
}

const getBillIcon = (type) => {
  const icons = {
    property: 'building-o',
    water: 'fire-o',
    electricity: 'flash-o',
    parking: 'logistics'
  }
  return icons[type] || 'bill-o'
}

const getBillTypeName = (type) => {
  const names = {
    property: '物业费',
    water: '水费',
    electricity: '电费',
    parking: '停车费'
  }
  return names[type] || '其他费用'
}

const getStatusName = (status) => {
  const names = {
    pending: '待支付',
    paid: '已支付',
    overdue: '已逾期'
  }
  return names[status] || status
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const showBillDetail = (bill) => {
  selectedBill.value = bill
  showDetail.value = true
}

const handlePay = (bill) => {
  currentPayingBill.value = bill
  showPayment.value = true
  showDetail.value = false
}

const handleBatchPay = () => {
  const unpaidBills = bills.value.filter(b => b.status === 'pending')
  if (unpaidBills.length === 0) {
    showToast('没有待支付账单')
    return
  }
  showToast('批量支付功能开发中')
}

const onPaymentSelect = async (method) => {
  showPayment.value = false
  
  try {
    // 调用支付接口
    // await axios.post(`/api/payments/pay/${currentPayingBill.value.id}`, { method })
    
    // 模拟支付成功
    showSuccessToast('支付成功')
    currentPayingBill.value.status = 'paid'
  } catch (error) {
    showToast('支付失败')
  }
}
</script>

<style scoped>
.bills-page {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 60px;
}

.payment-summary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}

.summary-item {
  display: flex;
  flex-direction: column;
}

.amount {
  font-size: 32px;
  font-weight: bold;
}

.label {
  font-size: 14px;
  opacity: 0.9;
  margin-top: 4px;
}

.bill-item {
  background: white;
  margin: 12px 16px;
  padding: 16px;
  border-radius: 12px;
}

.bill-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.bill-type {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
}

.bill-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.bill-info {
  font-size: 13px;
  color: #666;
}

.bill-info p {
  margin: 4px 0;
}

.bill-amount .amount {
  font-size: 24px;
  font-weight: bold;
  color: #ee0a24;
}

.bill-actions {
  display: flex;
  justify-content: flex-end;
}

.bill-detail {
  padding: 20px;
  height: 100%;
}

.bill-detail h3 {
  text-align: center;
  margin-bottom: 20px;
}

.detail-actions {
  padding: 20px 0;
}

.payment-methods {
  display: flex;
  gap: 20px;
  padding: 40px;
  justify-content: center;
}

.payment-method {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 20px;
  border-radius: 12px;
  transition: background 0.2s;
}

.payment-method:active {
  background: #f7f8fa;
}

.payment-method span {
  font-size: 14px;
}
</style>
