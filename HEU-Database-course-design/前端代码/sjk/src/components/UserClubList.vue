<template>
    <div>
        <div class="header">社团列表</div>
        <div class="body">
            <!-- 搜索和筛选 -->
            <div class="search-bar">
                <el-input 
                    placeholder="搜索社团名称" 
                    v-model="searchName" 
                    style="width: 300px"
                    @keyup.enter.native="getClubList"
                >
                    <el-button slot="append" icon="el-icon-search" @click="getClubList"></el-button>
                </el-input>
                <el-select v-model="category" placeholder="社团类别" @change="getClubList" style="margin-left: 20px">
                    <el-option label="全部" value=""></el-option>
                    <el-option label="学术科技" value="学术科技"></el-option>
                    <el-option label="文化体育" value="文化体育"></el-option>
                    <el-option label="志愿公益" value="志愿公益"></el-option>
                </el-select>
            </div>

            <!-- 社团卡片列表 -->
            <div class="club-list">
                <el-card 
                    v-for="club in clubList" 
                    :key="club.club_id" 
                    class="club-card"
                >
                    <div slot="header" class="card-header">
                        <h3>{{ club.club_name }}</h3>
                        <span class="category-tag">{{ club.category }}</span>
                    </div>
                    <div class="card-body">
                        <p class="description">{{ club.description }}</p>
                        <div class="info">
                            <span>成立时间：{{ club.create_time }}</span>
                            <span>成员数：{{ club.member_count }}人</span>
                        </div>
                        <el-button 
                            type="primary" 
                            size="mini" 
                            class="join-btn"
                            @click="joinClub(club.club_id)"
                            :disabled="club.joined"
                        >
                            {{ club.joined ? '已加入' : '加入社团' }}
                        </el-button>
                    </div>
                </el-card>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            searchName: '',
            category: '',
            clubList: []
        };
    },
    created() {
        this.getClubList();
    },
    methods: {
        // 获取社团列表
        getClubList() {
            this.$axios.get('/api/user/clubs', {
                params: {
                    name: this.searchName,
                    category: this.category
                }
            }).then(res => {
                if (res.data.status === 200) {
                    this.clubList = res.data.data;
                }
            });
        },
        // 加入社团
        joinClub(clubId) {
            this.$axios.post('/api/user/join/club', { club_id: clubId }).then(res => {
                if (res.data.status === 200) {
                    this.$message.success('申请加入成功，请等待审核');
                    this.getClubList();
                } else {
                    this.$message.error(res.data.msg);
                }
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
.search-bar {
    display: flex;
    margin-bottom: 20px;
}
.club-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
}
.club-card {
    height: 100%;
    transition: transform 0.3s;
}
.club-card:hover {
    transform: translateY(-5px);
}
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.category-tag {
    background: #e6f7ff;
    color: #1890ff;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
}
.card-body {
    padding: 15px 0;
}
.description {
    color: #666;
    margin-bottom: 15px;
    line-height: 1.6;
    height: 60px;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
}
.info {
    display: flex;
    justify-content: space-between;
    color: #888;
    font-size: 14px;
    margin-bottom: 15px;
}
.join-btn {
    width: 100%;
}
</style>