<template>
    <div>
        <div class="header">社团成员管理</div>
        <div class="body">
            <!-- 搜索和筛选 -->
            <div class="operate">
                <el-select v-model="clubId" placeholder="选择社团" @change="getMemberList">
                    <el-option 
                        v-for="club in clubList" 
                        :key="club.club_id" 
                        :label="club.club_name" 
                        :value="club.club_id"
                    ></el-option>
                </el-select>
                <el-input 
                    placeholder="搜索成员姓名" 
                    v-model="searchName" 
                    style="width: 300px; margin-left: 20px"
                    @keyup.enter.native="getMemberList"
                >
                    <el-button slot="append" icon="el-icon-search" @click="getMemberList"></el-button>
                </el-input>
            </div>

            <!-- 成员表格 -->
            <el-table 
                :data="memberList" 
                border 
                style="width: 100%; margin-top: 20px"
            >
                <el-table-column prop="member_id" label="成员ID" width="100" align="center"></el-table-column>
                <el-table-column prop="member_name" label="姓名" width="120" align="center"></el-table-column>
                <el-table-column prop="student_id" label="学号" width="150" align="center"></el-table-column>
                <el-table-column prop="club_name" label="所属社团" width="150" align="center"></el-table-column>
                <el-table-column prop="join_time" label="加入时间" width="180" align="center"></el-table-column>
                <el-table-column prop="role" label="角色" width="100" align="center">
                    <template slot-scope="scope">
                        <el-tag :type="scope.row.role === '社长' ? 'primary' : 'success'">
                            {{ scope.row.role }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column label="操作" width="200" align="center">
                    <template slot-scope="scope">
                        <el-button @click="editRole(scope.row)" type="text">修改角色</el-button>
                        <el-button @click="removeMember(scope.row.member_id)" type="text" style="color: #f56c6c">
                            移除
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>

            <!-- 修改角色对话框 -->
            <el-dialog title="修改成员角色" :visible.sync="roleDialog" width="300px">
                <el-form :model="currentMember">
                    <el-form-item label="姓名">
                        <span>{{ currentMember.member_name }}</span>
                    </el-form-item>
                    <el-form-item label="角色">
                        <el-select v-model="currentMember.role">
                            <el-option label="社员" value="社员"></el-option>
                            <el-option label="社长" value="社长"></el-option>
                            <el-option label="管理员" value="管理员"></el-option>
                        </el-select>
                    </el-form-item>
                </el-form>
                <div slot="footer">
                    <el-button @click="roleDialog = false">取消</el-button>
                    <el-button type="primary" @click="confirmRoleChange">确定</el-button>
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
            clubId: '',
            searchName: '',
            memberList: [],
            roleDialog: false,
            currentMember: {}
        };
    },
    created() {
        this.getClubList();
    },
    methods: {
        // 获取社团列表
        getClubList() {
            this.$axios.get('/api/manager/clubs').then(res => {
                if (res.data.status === 200) {
                    this.clubList = res.data.data;
                }
            });
        },
        // 获取成员列表
        getMemberList() {
            this.$axios.get('/api/manager/members', {
                params: {
                    club_id: this.clubId,
                    name: this.searchName
                }
            }).then(res => {
                if (res.data.status === 200) {
                    this.memberList = res.data.data;
                }
            });
        },
        // 编辑角色
        editRole(row) {
            this.currentMember = { ...row };
            this.roleDialog = true;
        },
        // 确认修改角色
        confirmRoleChange() {
            this.$axios.put('/api/manager/members/role', {
                member_id: this.currentMember.member_id,
                role: this.currentMember.role
            }).then(res => {
                if (res.data.status === 200) {
                    this.$message.success('修改成功');
                    this.roleDialog = false;
                    this.getMemberList();
                }
            });
        },
        // 移除成员
        removeMember(id) {
            this.$confirm('确定移除该成员吗？', '提示', {
                type: 'warning'
            }).then(() => {
                this.$axios.delete(`/api/manager/members/${id}`).then(res => {
                    if (res.data.status === 200) {
                        this.$message.success('移除成功');
                        this.getMemberList();
                    }
                });
            });
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
    align-items: center;
}
</style>