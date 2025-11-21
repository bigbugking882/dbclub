<template>
  <div>
    <div class="header">社团信息管理</div>
    <div class="body">
      <!-- 搜索和新增按钮 -->
      <div class="operate">
        <el-input 
          placeholder="搜索社团名称" 
          v-model="searchName" 
          style="width: 300px"
          @keyup.enter.native="getClubList"
        >
          <el-button slot="append" icon="el-icon-search" @click="getClubList"></el-button>
        </el-input>
        <el-button type="primary" @click="showAddDialog">新增社团</el-button>
      </div>

      <!-- 社团表格 -->
      <el-table 
        :data="clubList" 
        border 
        style="width: 100%; margin-top: 20px"
      >
        <el-table-column prop="club_id" label="社团ID" width="80" align="center"></el-table-column>
        <el-table-column prop="club_name" label="社团名称" width="150" align="center"></el-table-column>
        <el-table-column prop="category" label="社团类别" width="120" align="center"></el-table-column>
        <el-table-column prop="description" label="社团简介" align="center"></el-table-column>
        <el-table-column prop="create_time" label="成立时间" width="150" align="center"></el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template slot-scope="scope">
            <el-button @click="handleEdit(scope.row)" type="text">编辑</el-button>
            <el-button @click="handleDelete(scope.row.club_id)" type="text" style="color: #f56c6c">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 新增/编辑对话框 -->
      <el-dialog 
        title="社团信息" 
        :visible.sync="dialogVisible" 
        width="500px"
      >
        <el-form :model="clubForm" label-width="100px">
          <el-form-item label="社团名称">
            <el-input v-model="clubForm.club_name"></el-input>
          </el-form-item>
          <el-form-item label="社团类别">
            <el-select v-model="clubForm.category">
              <el-option label="学术科技" value="学术科技"></el-option>
              <el-option label="文化体育" value="文化体育"></el-option>
              <el-option label="志愿公益" value="志愿公益"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="社团简介">
            <el-input type="textarea" v-model="clubForm.description"></el-input>
          </el-form-item>
        </el-form>
        <div slot="footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      clubList: [],
      searchName: '',
      dialogVisible: false,
      clubForm: {
        club_id: '',
        club_name: '',
        category: '',
        description: ''
      }
    }
  },
  created() {
    this.getClubList()
  },
  methods: {
    // 获取社团列表
    getClubList() {
      this.$axios.get('/api/manager/clubs', {
        params: { name: this.searchName }
      }).then(res => {
        if (res.data.status === 200) {
          this.clubList = res.data.data
        }
      })
    },
    // 显示新增对话框
    showAddDialog() {
      this.clubForm = { club_id: '', club_name: '', category: '', description: '' }
      this.dialogVisible = true
    },
    // 编辑社团
    handleEdit(row) {
      this.clubForm = { ...row }
      this.dialogVisible = true
    },
    // 提交表单（新增/编辑）
    submitForm() {
      if (this.clubForm.club_id) {
        // 编辑
        this.$axios.put('/api/manager/clubs', this.clubForm).then(res => {
          if (res.data.status === 200) {
            this.$message.success('修改成功')
            this.dialogVisible = false
            this.getClubList()
          }
        })
      } else {
        // 新增
        this.$axios.post('/api/manager/clubs', this.clubForm).then(res => {
          if (res.data.status === 200) {
            this.$message.success('新增成功')
            this.dialogVisible = false
            this.getClubList()
          }
        })
      }
    },
    // 删除社团
    handleDelete(id) {
      this.$confirm('确定删除该社团吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$axios.delete(`/api/manager/clubs/${id}`).then(res => {
          if (res.data.status === 200) {
            this.$message.success('删除成功')
            this.getClubList()
          }
        })
      })
    }
  }
}
</script>

<style scoped>
.header {
  width: 100%;
  height: 60px;
  line-height: 60px;
  font-size: 20px;
  font-weight: 800;
  border-bottom: 1px solid #e3e3e3;
}
.body {
  padding: 20px;
}
.operate {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>