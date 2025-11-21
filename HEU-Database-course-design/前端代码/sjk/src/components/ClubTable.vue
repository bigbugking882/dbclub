<template>
  <div class="club-table">
    <el-table :data="clubs" v-loading="loading">
      <el-table-column prop="club_name" label="社团名称"></el-table-column>
      <el-table-column prop="category" label="类别"></el-table-column>
      <el-table-column prop="description" label="简介">
        <template slot-scope="scope">
          {{ scope.row.description || '暂无简介' }}
        </template>
      </el-table-column>
      <el-table-column prop="role" label="我的角色">
        <template slot-scope="scope">
          <el-tag :type="getRoleType(scope.row.role)">
            {{ getRoleText(scope.row.role) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="audit_status" label="状态">
        <template slot-scope="scope">
          <el-tag :type="getStatusType(scope.row.audit_status)">
            {{ getStatusText(scope.row.audit_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" v-if="showActions">
        <template slot-scope="scope">
          <el-button size="mini" @click="manageClub(scope.row)">管理</el-button>
          <el-button size="mini" type="danger" @click="deleteClub(scope.row)">解散</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 社团管理对话框 -->
    <el-dialog 
      :title="currentClub ? `管理社团 - ${currentClub.club_name}` : '社团管理'" 
      :visible.sync="showManageDialog"
      width="800px"
    >
      <div v-if="currentClub" class="club-manage-content">
        <el-tabs v-model="manageTab">
          <el-tab-pane label="基本信息" name="info">
            <el-form :model="clubForm" label-width="100px">
              <el-form-item label="社团名称">
                <el-input v-model="clubForm.club_name"></el-input>
              </el-form-item>
              <el-form-item label="社团类别">
                <el-select v-model="clubForm.category" style="width: 100%">
                  <el-option label="学术科技" value="学术科技"></el-option>
                  <el-option label="文化体育" value="文化体育"></el-option>
                  <el-option label="志愿公益" value="志愿公益"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="社团简介">
                <el-input type="textarea" v-model="clubForm.description" :rows="4"></el-input>
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <el-tab-pane label="成员管理" name="members">
            <div class="members-section">
              <div class="section-header">
                <h4>社团成员</h4>
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="loadClubMembers"
                  :loading="membersLoading"
                >
                  刷新
                </el-button>
              </div>
              <el-table :data="clubMembers" size="small" v-loading="membersLoading">
                <el-table-column prop="username" label="成员姓名"></el-table-column>
                <el-table-column prop="role" label="角色">
                  <template slot-scope="scope">
                    <el-tag :type="scope.row.role === 1 ? 'danger' : 'primary'">
                      {{ getRoleText(scope.row.role) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="join_time" label="加入时间"></el-table-column>
                <el-table-column label="操作" width="120">
                  <template slot-scope="scope">
                    <el-button 
                      size="mini" 
                      type="danger" 
                      @click="removeMember(scope.row)"
                      v-if="scope.row.role !== 1 && currentClub.role === 1"
                    >
                      移除
                    </el-button>
                    <span v-else class="no-action">-</span>
                  </template>
                </el-table-column>
              </el-table>
              <div v-if="!membersLoading && clubMembers.length === 0" class="empty-state">
                暂无成员数据
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="活动管理" name="activities">
            <div class="activities-section">
              <div class="section-header">
                <h4>社团活动</h4>
                <div>
                  <el-button size="small" @click="loadClubActivities" :loading="activitiesLoading">
                    刷新
                  </el-button>
                  <el-button size="small" type="primary" @click="createActivity">创建活动</el-button>
                </div>
              </div>
              <el-table :data="clubActivities" size="small" v-loading="activitiesLoading">
                <el-table-column prop="title" label="活动名称"></el-table-column>
                <el-table-column prop="location" label="活动地点"></el-table-column>
                <el-table-column prop="start_time" label="开始时间">
                  <template slot-scope="scope">
                    {{ formatDate(scope.row.start_time) }}
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态">
                  <template slot-scope="scope">
                    <el-tag :type="getActivityStatusType(scope.row.status)">
                      {{ getActivityStatusText(scope.row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="150">
                  <template slot-scope="scope">
                    <el-button size="mini" @click="editClubActivity(scope.row)">编辑</el-button>
                    <el-button 
                      size="mini" 
                      type="danger" 
                      @click="deleteClubActivity(scope.row)"
                      v-if="currentClub.role === 1"
                    >
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              <div v-if="!activitiesLoading && clubActivities.length === 0" class="empty-state">
                暂无活动数据
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      <div slot="footer">
        <el-button @click="showManageDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="saveClubInfo"
          :loading="saving"
        >
          保存
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { formatDate } from '@/utils/date'

export default {
  name: 'ClubTable',
  props: {
    clubs: {
      type: Array,
      default: () => []
    },
    showActions: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      loading: false,
      showManageDialog: false,
      currentClub: null,
      manageTab: 'info',
      clubForm: {
        club_name: '',
        category: '',
        description: ''
      },
      clubMembers: [],
      clubActivities: [],
      membersLoading: false,
      activitiesLoading: false,
      saving: false,
      user: JSON.parse(localStorage.getItem('user') || '{}')
    }
  },
  methods: {
    manageClub(club) {
      this.currentClub = club
      this.clubForm = { ...club }
      this.showManageDialog = true
      this.clubMembers = []
      this.clubActivities = []
    },

    async loadClubMembers() {
      if (!this.currentClub) return
      
      this.membersLoading = true
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/club/members?club_id=${this.currentClub.club_id}`)
        const result = await response.json()
        
        if (result.status === 200) {
          this.clubMembers = result.data || []
          // 成功时不显示任何提示
        } else {
          throw new Error(result.message)
        }
      } catch (error) {
        console.error('加载成员数据失败:', error)
        // 只在失败时显示错误提示
        if (error.message.includes('Failed to fetch')) {
          this.$message.error('网络连接失败，请检查后端服务')
        } else {
          this.$message.error('加载成员数据失败: ' + error.message)
        }
        this.clubMembers = []
      } finally {
        this.membersLoading = false
      }
    },

    async loadClubActivities() {
      if (!this.currentClub) return
      
      this.activitiesLoading = true
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/activities?club_id=${this.currentClub.club_id}`)
        const result = await response.json()
        
        if (result.status === 200) {
          this.clubActivities = result.data || []
          // 成功时不显示任何提示
        } else {
          throw new Error(result.message)
        }
      } catch (error) {
        console.error('加载活动数据失败:', error)
        // 只在失败时显示错误提示
        if (error.message.includes('Failed to fetch')) {
          this.$message.error('网络连接失败，请检查后端服务')
        } else {
          this.$message.error('加载活动数据失败: ' + error.message)
        }
        this.clubActivities = []
      } finally {
        this.activitiesLoading = false
      }
    },

    async saveClubInfo() {
      if (!this.currentClub) return
      
      this.saving = true
      try {
        const response = await fetch('http://127.0.0.1:5000/api/club/update', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            club_id: this.currentClub.club_id,
            ...this.clubForm
          })
        })
        const result = await response.json()
        
        if (result.status === 200) {
          this.$message.success('社团信息更新成功')
          this.showManageDialog = false
          this.$emit('refresh')
        } else {
          throw new Error(result.message)
        }
      } catch (error) {
        console.error('更新失败:', error)
        this.$message.error('更新失败: ' + error.message)
      } finally {
        this.saving = false
      }
    },

    async removeMember(member) {
      this.$confirm(`确定要移除成员 ${member.username} 吗？`, '提示', {
        type: 'warning'
      }).then(async () => {
        try {
          const response = await fetch('http://127.0.0.1:5000/api/member/remove', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              member_id: member.member_id
            })
          })
          const result = await response.json()
          
          if (result.status === 200) {
            this.$message.success('成员移除成功')
            this.loadClubMembers() // 重新加载成员列表
          } else {
            throw new Error(result.message)
          }
        } catch (error) {
          console.error('移除失败:', error)
          this.$message.error('移除失败: ' + error.message)
        }
      })
    },

    createActivity() {
      this.$message.info('创建活动功能开发中...')
    },

    editClubActivity(activity) {
      this.$message.info(`编辑活动: ${activity.title}`)
    },

    async deleteClubActivity(activity) {
      this.$confirm(`确定要删除活动 "${activity.title}" 吗？`, '提示', {
        type: 'warning'
      }).then(async () => {
        try {
          const response = await fetch(`http://127.0.0.1:5000/api/activity/delete/${activity.activity_id}`, {
            method: 'DELETE'
          })
          const result = await response.json()
          
          if (result.status === 200) {
            this.$message.success('活动删除成功')
            this.loadClubActivities() // 重新加载活动列表
          } else {
            throw new Error(result.message)
          }
        } catch (error) {
          console.error('删除失败:', error)
          this.$message.error('删除失败: ' + error.message)
        }
      })
    },

    async deleteClub(club) {
      this.$confirm(`确定要解散 "${club.club_name}" 吗？此操作不可撤销！`, '警告', {
        type: 'warning',
        confirmButtonText: '确定解散',
        confirmButtonClass: 'el-button--danger'
      }).then(async () => {
        try {
          // 注意：需要先在后端添加删除社团的接口
          this.$message.info('解散社团功能开发中...')
          // 这里可以调用解散社团的API
        } catch (error) {
          console.error('解散失败:', error)
          this.$message.error('解散失败: ' + error.message)
        }
      })
    },

    getRoleType(role) {
      const types = ['', 'danger', 'success']
      return types[role] || ''
    },

    getRoleText(role) {
      const texts = ['社员', '社长', '管理员']
      return texts[role] || '未知'
    },

    getStatusType(status) {
      const types = ['warning', 'success', 'danger']
      return types[status] || 'info'
    },

    getStatusText(status) {
      const texts = ['待审核', '已通过', '已拒绝']
      return texts[status] || '未知'
    },

    getActivityStatusType(status) {
      const types = ['info', 'primary', 'success']
      return types[status] || 'info'
    },

    getActivityStatusText(status) {
      const texts = ['未开始', '进行中', '已结束']
      return texts[status] || '未知'
    },

    formatDate
  },
  watch: {
    manageTab(newTab) {
      if (newTab === 'members' && this.clubMembers.length === 0) {
        this.loadClubMembers()
      } else if (newTab === 'activities' && this.clubActivities.length === 0) {
        this.loadClubActivities()
      }
    }
  }
}
</script>