<template>
  <div class="documents-page">
    <van-nav-bar title="文档查询" left-arrow @click-left="router.back()" />

    <!-- 搜索栏 -->
    <van-search
      v-model="searchText"
      placeholder="搜索文档"
      @search="onSearch"
    />

    <!-- 分类标签 -->
    <div class="category-tabs">
      <van-tag
        v-for="cat in categories"
        :key="cat.value"
        :type="selectedCategory === cat.value ? 'primary' : 'default'"
        size="large"
        round
        @click="selectedCategory = cat.value"
      >
        {{ cat.label }}
      </van-tag>
    </div>

    <!-- 文档列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <div
          v-for="doc in filteredDocuments"
          :key="doc.id"
          class="document-item"
          @click="showDocDetail(doc)"
        >
          <div class="doc-icon">
            <van-icon :name="getDocIcon(doc.file_type)" size="32" />
          </div>
          <div class="doc-content">
            <h4>{{ doc.title }}</h4>
            <p class="doc-meta">
              <van-tag size="mini" type="success">{{ getCategoryName(doc.category) }}</van-tag>
              <span class="doc-date">{{ formatDate(doc.created_at) }}</span>
            </p>
            <p v-if="doc.summary" class="doc-summary">{{ doc.summary }}</p>
          </div>
        </div>
      </van-list>
    </van-pull-refresh>

    <!-- 文档详情弹窗 -->
    <van-popup
      v-model:show="showDetail"
      position="bottom"
      :style="{ height: '80%' }"
    >
      <div v-if="selectedDoc" class="document-detail">
        <div class="detail-header">
          <h3>{{ selectedDoc.title }}</h3>
          <van-icon name="cross" size="20" @click="showDetail = false" />
        </div>
        
        <van-cell-group>
          <van-cell title="分类" :value="getCategoryName(selectedDoc.category)" />
          <van-cell title="文件名" :value="selectedDoc.file_name" />
          <van-cell title="上传时间" :value="formatDate(selectedDoc.created_at)" />
        </van-cell-group>

        <div class="detail-content">
          <h4>摘要</h4>
          <p>{{ selectedDoc.summary || '暂无摘要' }}</p>
          
          <h4>内容预览</h4>
          <div class="content-preview">
            {{ selectedDoc.content || '无法预览' }}
          </div>
        </div>

        <div class="detail-actions">
          <van-button type="primary" block round @click="downloadDoc(selectedDoc)">
            <van-icon name="down" /> 下载文档
          </van-button>
        </div>
      </div>
    </van-popup>

    <!-- 上传按钮 -->
    <van-floating-bubble
      icon="plus"
      @click="handleUpload"
      :style="{ bottom: '80px' }"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showSuccessToast } from 'vant'
import axios from '../utils/axios'

const router = useRouter()

const searchText = ref('')
const selectedCategory = ref('all')
const documents = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const showDetail = ref(false)
const selectedDoc = ref(null)

const categories = [
  { label: '全部', value: 'all' },
  { label: '规章制度', value: 'regulation' },
  { label: '通知公告', value: 'notice' },
  { label: '维修记录', value: 'maintenance' },
  { label: '会议记录', value: 'meeting' },
  { label: '其他', value: 'other' }
]

// 过滤文档
const filteredDocuments = computed(() => {
  let filtered = documents.value

  // 分类筛选
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(doc => doc.category === selectedCategory.value)
  }

  // 搜索筛选
  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter(doc =>
      doc.title.toLowerCase().includes(keyword) ||
      (doc.content && doc.content.toLowerCase().includes(keyword))
    )
  }

  return filtered
})

onMounted(() => {
  loadDocuments()
})

const loadDocuments = async () => {
  try {
    const response = await axios.get('/api/documents/')
    documents.value = response.data

    // 模拟数据(开发阶段)
    if (documents.value.length === 0) {
      documents.value = [
        {
          id: 1,
          title: '物业管理规章制度',
          category: 'regulation',
          file_name: '物业管理规章制度.pdf',
          file_type: 'pdf',
          summary: '本文档包含小区物业管理的各项规章制度...',
          content: '详细内容...',
          created_at: '2024-01-15T10:00:00'
        },
        {
          id: 2,
          title: '停车管理办法',
          category: 'regulation',
          file_name: '停车管理办法.docx',
          file_type: 'docx',
          summary: '小区停车场使用和管理相关规定...',
          content: '详细内容...',
          created_at: '2024-01-10T14:30:00'
        },
        {
          id: 3,
          title: '装修申请流程',
          category: 'notice',
          file_name: '装修申请流程.pdf',
          file_type: 'pdf',
          summary: '业主装修房屋的申请流程和注意事项...',
          content: '详细内容...',
          created_at: '2024-01-05T09:00:00'
        }
      ]
    }
  } catch (error) {
    console.error('加载文档失败:', error)
  }
}

const onLoad = () => {
  loading.value = false
  finished.value = true
}

const onRefresh = async () => {
  await loadDocuments()
  refreshing.value = false
  showSuccessToast('刷新成功')
}

const onSearch = () => {
  // 搜索逻辑已在 computed 中处理
}

const getCategoryName = (category) => {
  const cat = categories.find(c => c.value === category)
  return cat ? cat.label : category
}

const getDocIcon = (fileType) => {
  const icons = {
    pdf: 'description',
    doc: 'description',
    docx: 'description',
    xls: 'records',
    xlsx: 'records',
    txt: 'notes-o',
    jpg: 'photo-o',
    png: 'photo-o'
  }
  return icons[fileType] || 'description'
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const showDocDetail = (doc) => {
  selectedDoc.value = doc
  showDetail.value = true
}

const downloadDoc = (doc) => {
  showToast('下载功能开发中')
}

const handleUpload = () => {
  showToast('上传功能开发中')
}
</script>

<style scoped>
.documents-page {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 80px;
}

.category-tabs {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  overflow-x: auto;
  white-space: nowrap;
}

.category-tabs::-webkit-scrollbar {
  display: none;
}

.document-item {
  display: flex;
  gap: 12px;
  background: white;
  margin: 12px 16px;
  padding: 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s;
}

.document-item:active {
  transform: scale(0.98);
}

.doc-icon {
  width: 48px;
  height: 48px;
  background: #f7f8fa;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #667eea;
  flex-shrink: 0;
}

.doc-content {
  flex: 1;
  min-width: 0;
}

.doc-content h4 {
  font-size: 16px;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}

.doc-date {
  margin-left: auto;
}

.doc-summary {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.document-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.detail-header h3 {
  font-size: 18px;
  flex: 1;
  margin-right: 16px;
}

.detail-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.detail-content h4 {
  margin: 16px 0 8px;
  font-size: 14px;
  color: #666;
}

.content-preview {
  background: #f7f8fa;
  padding: 12px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.6;
  max-height: 300px;
  overflow-y: auto;
}

.detail-actions {
  padding: 20px;
  border-top: 1px solid #eee;
}
</style>
