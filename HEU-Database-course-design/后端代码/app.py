from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import text
import pymysql
import datetime
import random

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
CORS(app)

# 用户登录
@app.route('/api/user/login', methods=['POST'])
def user_login():
    try:
        data = request.json
        print("登录请求数据:", data)
        
        telephone = data.get('telephone')
        password = data.get('password')
        
        if not telephone or not password:
            return jsonify({
                'status': 400,
                'message': '手机号和密码不能为空',
                'data': None
            })
        
        # 查询用户
        sql = text('SELECT * FROM user WHERE telephone = :tel AND password = :pwd')
        result = db.session.execute(sql, {'tel': telephone, 'pwd': password})
        user = result.fetchone()
        
        if user:
            user_dict = {
                'id': user[0],
                'username': user[1],
                'telephone': user[3],
                'role': user[4],
                'create_time': str(user[5]) if user[5] else None
            }
            return jsonify({
                'status': 200,
                'message': '登录成功',
                'data': user_dict
            })
        else:
            return jsonify({
                'status': 400,
                'message': '手机号或密码错误',
                'data': None
            })
            
    except Exception as e:
        print("登录错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '服务器错误',
            'data': None
        })

# 用户注册
@app.route('/api/user/register', methods=['POST'])
def user_register():
    try:
        data = request.json
        telephone = data.get('telephone')
        password = data.get('password')
        username = data.get('username', '用户' + telephone[-4:])
        
        if not telephone or not password:
            return jsonify({
                'status': 400,
                'message': '手机号和密码不能为空',
                'data': None
            })
        
        # 检查手机号是否已存在
        check_sql = text('SELECT id FROM user WHERE telephone = :tel')
        existing_user = db.session.execute(check_sql, {'tel': telephone}).fetchone()
        
        if existing_user:
            return jsonify({
                'status': 400,
                'message': '手机号已注册',
                'data': None
            })
        
        # 插入新用户
        insert_sql = text('''
            INSERT INTO user (username, password, telephone, role, create_time) 
            VALUES (:username, :password, :telephone, 0, NOW())
        ''')
        db.session.execute(insert_sql, {
            'username': username,
            'password': password,
            'telephone': telephone
        })
        db.session.commit()
        
        return jsonify({
            'status': 200,
            'message': '注册成功',
            'data': None
        })
        
    except Exception as e:
        db.session.rollback()
        print("注册错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '注册失败',
            'data': None
        })

# 获取所有用户
@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        sql = text('SELECT id, username, telephone, role, create_time FROM user ORDER BY id ASC')
        result = db.session.execute(sql)
        users = []
        for row in result:
            users.append({
                'id': row[0],
                'username': row[1],
                'telephone': row[2],
                'role': row[3],
                'create_time': str(row[4]) if row[4] else None
            })
        
        return jsonify({
            'status': 200,
            'message': '获取成功',
            'data': users
        })
        
    except Exception as e:
        print("获取用户错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '获取失败',
            'data': None
        })

# 更新用户信息
@app.route('/api/user/update', methods=['POST'])
def update_user():
    try:
        data = request.json
        user_id = data.get('id')
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')
        
        if not user_id:
            return jsonify({
                'status': 400,
                'message': '用户ID不能为空',
                'data': None
            })
        
        # 构建更新SQL
        update_fields = []
        params = {'user_id': user_id}
        
        if username:
            update_fields.append('username = :username')
            params['username'] = username
            
        if password:
            update_fields.append('password = :password')
            params['password'] = password
            
        if role is not None:
            update_fields.append('role = :role')
            params['role'] = role
        
        if not update_fields:
            return jsonify({
                'status': 400,
                'message': '没有要更新的字段',
                'data': None
            })
        
        sql = text(f'UPDATE user SET {", ".join(update_fields)} WHERE id = :user_id')
        db.session.execute(sql, params)
        db.session.commit()
        
        return jsonify({
            'status': 200,
            'message': '更新成功',
            'data': None
        })
        
    except Exception as e:
        db.session.rollback()
        print("更新用户错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '更新失败',
            'data': None
        })

# 获取所有社团
@app.route('/api/clubs', methods=['GET'])
def get_clubs():
    try:
        sql = text('''
            SELECT c.*, u.username as founder_name 
            FROM club c 
            LEFT JOIN user u ON c.founder_id = u.id 
            ORDER BY c.club_id ASC
        ''')
        result = db.session.execute(sql)
        clubs = []
        for row in result:
            clubs.append({
                'club_id': row[0],
                'club_name': row[1],
                'description': row[2],
                'founder_id': row[3],
                'create_time': str(row[4]),
                'status': row[5],
                'category': row[6],
                'founder_name': row[7]
            })
        
        return jsonify({
            'status': 200,
            'message': '获取成功',
            'data': clubs
        })
        
    except Exception as e:
        print("获取社团错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '获取失败',
            'data': None
        })

# 获取待审核社团
@app.route('/api/clubs/pending', methods=['GET'])
def get_pending_clubs():
    try:
        sql = text('''
            SELECT c.*, u.username as founder_name 
            FROM club c 
            LEFT JOIN user u ON c.founder_id = u.id 
            WHERE c.audit_status = 0
            ORDER BY c.create_time DESC
        ''')
        result = db.session.execute(sql)
        clubs = []
        for row in result:
            clubs.append({
                'club_id': row[0],
                'club_name': row[1],
                'description': row[2],
                'founder_id': row[3],
                'create_time': str(row[4]),
                'status': row[5],
                'category': row[6],
                'founder_name': row[7],
                'audit_status': row[8]  # 新添加的字段
            })
        
        return jsonify({
            'status': 200,
            'message': '获取成功',
            'data': clubs
        })
        
    except Exception as e:
        print("获取待审核社团错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '获取失败',
            'data': None
        })

# 审核社团
@app.route('/api/club/audit', methods=['POST'])
def audit_club():
    try:
        data = request.json
        club_id = data.get('club_id')
        audit_status = data.get('audit_status')  # 1-通过, 0-不通过
        
        print(f"审核社团请求: club_id={club_id}, audit_status={audit_status}")  # 调试日志
        
        if not club_id or audit_status is None:
            return jsonify({
                'status': 400,
                'message': '参数不能为空',
                'data': None
            })
        
        # 审核状态映射：1-通过 -> 状态1(正常), 0-不通过 -> 状态0(停用)
        new_status = 1 if audit_status == 1 else 0
        
        # 更新社团状态
        sql = text('UPDATE club SET status = :status WHERE club_id = :club_id')
        result = db.session.execute(sql, {'status': new_status, 'club_id': club_id})
        
        print(f"更新影响行数: {result.rowcount}")  # 调试日志
        
        # 如果审核通过，同时通过创始人的成员申请
        if audit_status == 1:
            member_sql = text('''
                UPDATE club_member SET audit_status = 1 
                WHERE club_id = :club_id AND role = 1
            ''')
            db.session.execute(member_sql, {'club_id': club_id})
        
        db.session.commit()
        
        action = "通过" if audit_status == 1 else "拒绝"
        return jsonify({
            'status': 200,
            'message': f'审核{action}成功',
            'data': None
        })
        
    except Exception as e:
        db.session.rollback()
        print("审核社团错误:", str(e))
        return jsonify({
            'status': 500,
            'message': f'操作失败: {str(e)}',
            'data': None
        })

# 审核活动
@app.route('/api/activity/audit', methods=['POST'])
def audit_activity():
    try:
        data = request.json
        activity_id = data.get('activity_id')
        audit_status = data.get('audit_status')  # 1-通过, 0-不通过
        
        print(f"审核活动请求: activity_id={activity_id}, audit_status={audit_status}")  # 调试日志
        
        if not activity_id or audit_status is None:
            return jsonify({
                'status': 400,
                'message': '参数不能为空',
                'data': None
            })
        
        # 审核状态映射：1-通过 -> 状态0(未开始), 0-不通过 -> 状态2(已结束表示不通过)
        new_status = 0 if audit_status == 1 else 2
        
        # 更新活动状态
        sql = text('UPDATE activity SET status = :status WHERE activity_id = :activity_id')
        result = db.session.execute(sql, {'status': new_status, 'activity_id': activity_id})
        
        print(f"更新影响行数: {result.rowcount}")  # 调试日志
        
        db.session.commit()
        
        action = "通过" if audit_status == 1 else "拒绝"
        return jsonify({
            'status': 200,
            'message': f'审核{action}成功',
            'data': None
        })
        
    except Exception as e:
        db.session.rollback()
        print("审核活动错误:", str(e))
        return jsonify({
            'status': 500,
            'message': f'操作失败: {str(e)}',
            'data': None
        })

# 创建社团 - 根据用户角色决定审核状态
@app.route('/api/club/create', methods=['POST'])
def create_club():
    try:
        data = request.json
        club_name = data.get('club_name')
        description = data.get('description')
        category = data.get('category')
        founder_id = data.get('founder_id')
        
        if not club_name or not category or not founder_id:
            return jsonify({
                'status': 400,
                'message': '社团名称、类别和创始人ID不能为空',
                'data': None
            })
        
        # 检查社团名是否重复
        check_sql = text('SELECT club_id FROM club WHERE club_name = :name')
        existing_club = db.session.execute(check_sql, {'name': club_name}).fetchone()
        
        if existing_club:
            return jsonify({
                'status': 400,
                'message': '社团名称已存在',
                'data': None
            })
        
        # 检查创建者角色
        user_sql = text('SELECT role FROM user WHERE id = :user_id')
        user_result = db.session.execute(user_sql, {'user_id': founder_id})
        user = user_result.fetchone()
        
        # 根据用户角色决定状态：管理员直接通过(1)，普通用户待审核(2)
        club_status = 1 if user and user[0] in [1, 2] else 2  # 1-社团管理员, 2-系统管理员
        member_audit_status = 1 if user and user[0] in [1, 2] else 0
        
        # 创建社团
        insert_sql = text('''
            INSERT INTO club (club_name, description, founder_id, create_time, category, status) 
            VALUES (:name, :desc, :founder, CURDATE(), :category, :status)
        ''')
        db.session.execute(insert_sql, {
            'name': club_name,
            'desc': description,
            'founder': founder_id,
            'category': category,
            'status': club_status
        })
        
        # 获取新创建的社团ID
        club_id = db.session.execute(text('SELECT LAST_INSERT_ID()')).scalar()
        
        # 创始人自动成为社长
        member_sql = text('''
            INSERT INTO club_member (user_id, club_id, role, join_time, audit_status) 
            VALUES (:user_id, :club_id, 1, CURDATE(), :audit_status)
        ''')
        db.session.execute(member_sql, {
            'user_id': founder_id,
            'club_id': club_id,
            'audit_status': member_audit_status
        })
        
        db.session.commit()
        
        message = '创建成功' if club_status == 1 else '创建成功，等待管理员审核'
        return jsonify({
            'status': 200,
            'message': message,
            'data': {'club_id': club_id}
        })
        
    except Exception as e:
        db.session.rollback()
        print("创建社团错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '创建失败',
            'data': None
        })

# 更新社团信息
@app.route('/api/club/update', methods=['POST'])
def update_club():
    try:
        data = request.json
        club_id = data.get('club_id')
        club_name = data.get('club_name')
        description = data.get('description')
        category = data.get('category')
        status = data.get('status')
        
        if not club_id:
            return jsonify({
                'status': 400,
                'message': '社团ID不能为空',
                'data': None
            })
        
        # 构建更新SQL
        update_fields = []
        params = {'club_id': club_id}
        
        if club_name:
            update_fields.append('club_name = :club_name')
            params['club_name'] = club_name
            
        if description is not None:
            update_fields.append('description = :description')
            params['description'] = description
            
        if category:
            update_fields.append('category = :category')
            params['category'] = category
            
        if status is not None:
            update_fields.append('status = :status')
            params['status'] = status
        
        if not update_fields:
            return jsonify({
                'status': 400,
                'message': '没有要更新的字段',
                'data': None
            })
        
        sql = text(f'UPDATE club SET {", ".join(update_fields)} WHERE club_id = :club_id')
        db.session.execute(sql, params)
        db.session.commit()
        
        return jsonify({
            'status': 200,
            'message': '更新成功',
            'data': None
        })
        
    except Exception as e:
        db.session.rollback()
        print("更新社团错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '更新失败',
            'data': None
        })

# 获取社团活动
@app.route('/api/activities', methods=['GET'])
def get_activities():
    try:
        club_id = request.args.get('club_id')
        status = request.args.get('status')
        user_id = request.args.get('user_id')  # 添加用户ID参数
        
        # 构建SQL查询
        sql = '''
            SELECT 
                a.*, 
                COALESCE(c.club_name, '未知社团') as club_name
        '''
        
        # 如果提供了user_id，添加报名状态查询
        if user_id:
            sql += ''', 
                CASE WHEN asu.signup_id IS NOT NULL THEN 1 ELSE 0 END as is_signed
            '''
        else:
            sql += ''', 
                0 as is_signed
            '''
        
        sql += '''
            FROM activity a 
            LEFT JOIN club c ON a.club_id = c.club_id 
        '''
        
        # 如果提供了user_id，添加报名表连接
        if user_id:
            sql += '''
                LEFT JOIN activity_signup asu ON a.activity_id = asu.activity_id AND asu.user_id = :user_id
            '''
        
        sql += ' WHERE 1=1'
        params = {}
        
        # 添加user_id参数（如果存在）
        if user_id:
            params['user_id'] = user_id
        
        if club_id:
            sql += ' AND a.club_id = :club_id'
            params['club_id'] = club_id
            
        if status:
            # 支持多个状态筛选，如 "0,1,2"
            if ',' in status:
                status_list = status.split(',')
                placeholders = ','.join([f':status{i}' for i in range(len(status_list))])
                sql += f' AND a.status IN ({placeholders})'
                for i, s in enumerate(status_list):
                    params[f'status{i}'] = int(s) if s.isdigit() else s
            else:
                sql += ' AND a.status = :status'
                params['status'] = int(status) if status.isdigit() else status
        
        sql += ' ORDER BY a.activity_id ASC'
        
        print(f"执行SQL: {sql}")
        print(f"参数: {params}")
        
        result = db.session.execute(text(sql), params)
        activities = []
        for row in result:
            activity_data = {
                'activity_id': row[0],
                'club_id': row[1],
                'title': row[2],
                'content': row[3],
                'start_time': str(row[4]),
                'end_time': str(row[5]),
                'location': row[6],
                'status': row[7],
                'create_time': str(row[8]),
                'club_name': row[9],
                'is_signed': row[10] if len(row) > 10 else 0
            }
            activities.append(activity_data)
        
        return jsonify({
            'status': 200,
            'message': '获取成功',
            'data': activities
        })
        
    except Exception as e:
        print("获取活动错误:", str(e))
        import traceback
        traceback.print_exc()  # 打印完整的错误堆栈
        return jsonify({
            'status': 500,
            'message': f'获取失败: {str(e)}',
            'data': None
        })
        
# 创建活动 - 根据用户角色决定审核状态
@app.route('/api/activity/create', methods=['POST'])
def create_activity():
    try:
        data = request.json
        club_id = data.get('club_id')
        title = data.get('title')
        content = data.get('content', '')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        location = data.get('location')
        
        if not all([club_id, title, start_time, end_time, location]):
            return jsonify({
                'status': 400,
                'message': '请填写完整信息',
                'data': None
            })
        
        # 检查创建者权限（通过社团关联查询用户角色）
        user_sql = text('''
            SELECT u.role 
            FROM user u 
            INNER JOIN club c ON u.id = c.founder_id 
            WHERE c.club_id = :club_id
        ''')
        user_result = db.session.execute(user_sql, {'club_id': club_id})
        user = user_result.fetchone()
        
        # 根据用户角色决定状态：管理员直接通过(0-未开始)，普通用户待审核(3)
        activity_status = 0 if user and user[0] in [1, 2] else 3
        
        sql = text('''
            INSERT INTO activity (club_id, title, content, start_time, end_time, location, status) 
            VALUES (:club_id, :title, :content, :start_time, :end_time, :location, :status)
        ''')
        db.session.execute(sql, {
            'club_id': club_id,
            'title': title,
            'content': content,
            'start_time': start_time,
            'end_time': end_time,
            'location': location,
            'status': activity_status
        })
        db.session.commit()
        
        message = '创建成功' if activity_status == 0 else '创建成功，等待管理员审核'
        return jsonify({
            'status': 200,
            'message': message,
            'data': None
        })
        
    except Exception as e:
        db.session.rollback()
        print("创建活动错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '创建失败',
            'data': None
        })

# 更新活动
@app.route('/api/activity/update', methods=['POST'])
def update_activity():
    try:
        data = request.json
        activity_id = data.get('activity_id')
        title = data.get('title')
        content = data.get('content')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        location = data.get('location')
        status = data.get('status')
        
        if not activity_id:
            return jsonify({
                'status': 400,
                'message': '活动ID不能为空',
                'data': None
            })
        
        # 构建更新SQL
        update_fields = []
        params = {'activity_id': activity_id}
        
        if title:
            update_fields.append('title = :title')
            params['title'] = title
            
        if content is not None:
            update_fields.append('content = :content')
            params['content'] = content
            
        if start_time:
            update_fields.append('start_time = :start_time')
            params['start_time'] = start_time
            
        if end_time:
            update_fields.append('end_time = :end_time')
            params['end_time'] = end_time
            
        if location:
            update_fields.append('location = :location')
            params['location'] = location
            
        if status is not None:
            update_fields.append('status = :status')
            params['status'] = status
        
        if not update_fields:
            return jsonify({
                'status': 400,
                'message': '没有要更新的字段',
                'data': None
            })
        
        sql = text(f'UPDATE activity SET {", ".join(update_fields)} WHERE activity_id = :activity_id')
        db.session.execute(sql, params)
        db.session.commit()
        
        return jsonify({
            'status': 200,
            'message': '更新成功',
            'data': None
        })
        
    except Exception as e:
        db.session.rollback()
        print("更新活动错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '更新失败',
            'data': None
        })

# 删除活动
@app.route('/api/activity/delete/<int:activity_id>', methods=['DELETE'])
def delete_activity(activity_id):
    try:
        if not activity_id:
            return jsonify({
                'status': 400,
                'message': '活动ID不能为空',
                'data': None
            })
        
        # 先删除相关的报名记录
        delete_signup_sql = text('DELETE FROM activity_signup WHERE activity_id = :activity_id')
        db.session.execute(delete_signup_sql, {'activity_id': activity_id})
        
        # 删除活动
        delete_activity_sql = text('DELETE FROM activity WHERE activity_id = :activity_id')
        db.session.execute(delete_activity_sql, {'activity_id': activity_id})
        
        db.session.commit()
        
        return jsonify({
            'status': 200,
            'message': '删除成功',
            'data': None
        })
        
    except Exception as e:
        db.session.rollback()
        print("删除活动错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '删除失败',
            'data': None
        })

# 活动报名
@app.route('/api/activity/signup', methods=['POST'])
def activity_signup():
    try:
        data = request.json
        activity_id = data.get('activity_id')
        user_id = data.get('user_id')
        
        if not activity_id or not user_id:
            return jsonify({
                'status': 400,
                'message': '活动ID和用户ID不能为空',
                'data': None
            })
        
        # 检查是否已报名
        check_sql = text('''
            SELECT signup_id FROM activity_signup 
            WHERE user_id = :user_id AND activity_id = :activity_id
        ''')
        existing_signup = db.session.execute(check_sql, {
            'user_id': user_id,
            'activity_id': activity_id
        }).fetchone()
        
        if existing_signup:
            return jsonify({
                'status': 400,
                'message': '已报名该活动',
                'data': None
            })
        
        # 报名活动
        insert_sql = text('''
            INSERT INTO activity_signup (activity_id, user_id) 
            VALUES (:activity_id, :user_id)
        ''')
        db.session.execute(insert_sql, {
            'activity_id': activity_id,
            'user_id': user_id
        })
        db.session.commit()
        
        return jsonify({
            'status': 200,
            'message': '报名成功',
            'data': None
        })
        
    except Exception as e:
        db.session.rollback()
        print("报名错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '报名失败',
            'data': None
        })

# 获取社团成员
@app.route('/api/club/members', methods=['GET'])
def get_club_members():
    try:
        club_id = request.args.get('club_id')
        audit_status = request.args.get('audit_status')
        
        sql = '''
            SELECT cm.*, u.username, u.telephone, c.club_name
            FROM club_member cm
            LEFT JOIN user u ON cm.user_id = u.id
            LEFT JOIN club c ON cm.club_id = c.club_id
            WHERE 1=1
        '''
        params = {}
        
        if club_id:
            sql += ' AND cm.club_id = :club_id'
            params['club_id'] = club_id
            
        if audit_status:
            sql += ' AND cm.audit_status = :audit_status'
            params['audit_status'] = audit_status
            
        sql += ' ORDER BY cm.club_id ASC, cm.user_id ASC'  # 先按社团ID排序，再按用户ID排序
        
        result = db.session.execute(text(sql), params)
        members = []
        for row in result:
            members.append({
                'member_id': row[0],      # 成员关系ID（保留但不显示）
                'user_id': row[1],        # 用户ID - 这个作为显示的ID
                'club_id': row[2],        # 社团ID
                'role': row[3],           # 角色
                'join_time': str(row[4]), # 加入时间
                'audit_status': row[5],   # 审核状态
                'username': row[6],       # 用户名
                'telephone': row[7],      # 手机号
                'club_name': row[8]       # 社团名称
            })
        
        return jsonify({
            'status': 200,
            'message': '获取成功',
            'data': members
        })
        
    except Exception as e:
        print("获取成员错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '获取失败',
            'data': None
        })

# 审核成员
@app.route('/api/member/audit', methods=['POST'])
def audit_member():
    try:
        data = request.json
        member_id = data.get('member_id')
        audit_status = data.get('audit_status')
        
        if not member_id or audit_status is None:
            return jsonify({
                'status': 400,
                'message': '参数不能为空',
                'data': None
            })
        
        sql = text('UPDATE club_member SET audit_status = :status WHERE member_id = :id')
        db.session.execute(sql, {'status': audit_status, 'id': member_id})
        db.session.commit()
        
        return jsonify({
            'status': 200,
            'message': '操作成功',
            'data': None
        })
        
    except Exception as e:
        db.session.rollback()
        print("审核成员错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '操作失败',
            'data': None
        })

# 移除成员
@app.route('/api/member/remove', methods=['POST'])
def remove_member():
    try:
        data = request.json
        member_id = data.get('member_id')
        
        if not member_id:
            return jsonify({
                'status': 400,
                'message': '成员ID不能为空',
                'data': None
            })
        
        sql = text('DELETE FROM club_member WHERE member_id = :id')
        db.session.execute(sql, {'id': member_id})
        db.session.commit()
        
        return jsonify({
            'status': 200,
            'message': '移除成功',
            'data': None
        })
        
    except Exception as e:
        db.session.rollback()
        print("移除成员错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '移除失败',
            'data': None
        })

# 加入社团
@app.route('/api/club/join', methods=['POST'])
def join_club():
    try:
        data = request.json
        club_id = data.get('club_id')
        user_id = data.get('user_id')
        
        if not club_id or not user_id:
            return jsonify({
                'status': 400,
                'message': '社团ID和用户ID不能为空',
                'data': None
            })
        
        # 检查是否已加入
        check_sql = text('''
            SELECT member_id FROM club_member 
            WHERE user_id = :user_id AND club_id = :club_id
        ''')
        existing_member = db.session.execute(check_sql, {
            'user_id': user_id,
            'club_id': club_id
        }).fetchone()
        
        if existing_member:
            return jsonify({
                'status': 400,
                'message': '已申请加入该社团',
                'data': None
            })
        
        # 申请加入社团
        insert_sql = text('''
            INSERT INTO club_member (user_id, club_id, role, join_time, audit_status) 
            VALUES (:user_id, :club_id, 0, CURDATE(), 0)
        ''')
        db.session.execute(insert_sql, {
            'user_id': user_id,
            'club_id': club_id
        })
        db.session.commit()
        
        return jsonify({
            'status': 200,
            'message': '申请已提交，等待审核',
            'data': None
        })
        
    except Exception as e:
        db.session.rollback()
        print("加入社团错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '申请失败',
            'data': None
        })

# 退出社团
@app.route('/api/member/quit', methods=['POST'])
def quit_club():
    try:
        data = request.json
        club_id = data.get('club_id')
        user_id = data.get('user_id')
        
        if not club_id or not user_id:
            return jsonify({
                'status': 400,
                'message': '社团ID和用户ID不能为空',
                'data': None
            })
        
        # 检查是否是社团创始人，不允许退出
        check_founder_sql = text('SELECT founder_id FROM club WHERE club_id = :club_id')
        founder = db.session.execute(check_founder_sql, {'club_id': club_id}).fetchone()
        
        if founder and founder[0] == user_id:
            return jsonify({
                'status': 400,
                'message': '创始人不能退出社团',
                'data': None
            })
        
        # 执行退出操作
        delete_sql = text('DELETE FROM club_member WHERE user_id = :user_id AND club_id = :club_id')
        db.session.execute(delete_sql, {
            'user_id': user_id,
            'club_id': club_id
        })
        db.session.commit()
        
        return jsonify({
            'status': 200,
            'message': '退出成功',
            'data': None
        })
        
    except Exception as e:
        db.session.rollback()
        print("退出社团错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '退出失败',
            'data': None
        })

# 获取我的社团
@app.route('/api/user/<int:user_id>/clubs', methods=['GET'])
def get_my_clubs(user_id):
    try:
        sql = text('''
            SELECT cm.*, c.club_name, c.description, c.category, u.username as founder_name
            FROM club_member cm
            LEFT JOIN club c ON cm.club_id = c.club_id
            LEFT JOIN user u ON c.founder_id = u.id
            WHERE cm.user_id = :user_id
            ORDER BY cm.member_id ASC
        ''')
        result = db.session.execute(sql, {'user_id': user_id})
        clubs = []
        for row in result:
            clubs.append({
                'member_id': row[0],
                'user_id': row[1],
                'club_id': row[2],
                'role': row[3],
                'join_time': str(row[4]),
                'audit_status': row[5],
                'club_name': row[6],
                'description': row[7],
                'category': row[8],
                'founder_name': row[9]
            })
        
        return jsonify({
            'status': 200,
            'message': '获取成功',
            'data': clubs
        })
        
    except Exception as e:
        print("获取我的社团错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '获取失败',
            'data': None
        })

# 健康检查接口
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 200,
        'message': '服务正常运行',
        'data': {
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'service': 'Campus Club Management API'
        }
    })

# 获取我的活动
@app.route('/api/user/<int:user_id>/activities', methods=['GET'])
def get_my_activities(user_id):
    try:
        sql = text('''
            SELECT 
                a.*, 
                c.club_name,
                CASE WHEN asu.signup_id IS NOT NULL THEN 1 ELSE 0 END as is_signed,
                u.id as creator_id
            FROM activity a
            LEFT JOIN club c ON a.club_id = c.club_id
            LEFT JOIN activity_signup asu ON a.activity_id = asu.activity_id AND asu.user_id = :user_id
            LEFT JOIN user u ON c.founder_id = u.id
            WHERE asu.user_id = :user_id OR c.founder_id = :user_id
            ORDER BY a.activity_id ASC
        ''')
        result = db.session.execute(sql, {'user_id': user_id})
        activities = []
        for row in result:
            activities.append({
                'activity_id': row[0],
                'club_id': row[1],
                'title': row[2],
                'content': row[3],
                'start_time': str(row[4]),
                'end_time': str(row[5]),
                'location': row[6],
                'status': row[7],
                'create_time': str(row[8]),
                'club_name': row[9],
                'is_signed': row[10],
                'creator_id': row[11]
            })
        
        return jsonify({
            'status': 200,
            'message': '获取成功',
            'data': activities
        })
        
    except Exception as e:
        print("获取我的活动错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '获取失败',
            'data': None
        })

# 取消活动报名
@app.route('/api/activity/cancel-signup', methods=['POST'])
def cancel_activity_signup():
    try:
        data = request.json
        activity_id = data.get('activity_id')
        user_id = data.get('user_id')
        
        sql = text('DELETE FROM activity_signup WHERE activity_id = :activity_id AND user_id = :user_id')
        db.session.execute(sql, {
            'activity_id': activity_id,
            'user_id': user_id
        })
        db.session.commit()
        
        return jsonify({
            'status': 200,
            'message': '取消报名成功',
            'data': None
        })
        
    except Exception as e:
        db.session.rollback()
        print("取消报名错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '取消报名失败',
            'data': None
        })

# 删除社团
@app.route('/api/club/delete/<int:club_id>', methods=['DELETE'])
def delete_club(club_id):
    try:
        if not club_id:
            return jsonify({
                'status': 400,
                'message': '社团ID不能为空',
                'data': None
            })
        
        # 先删除相关的成员记录
        delete_members_sql = text('DELETE FROM club_member WHERE club_id = :club_id')
        db.session.execute(delete_members_sql, {'club_id': club_id})
        
        # 删除相关的活动报名记录
        delete_signup_sql = text('''
            DELETE FROM activity_signup 
            WHERE activity_id IN (SELECT activity_id FROM activity WHERE club_id = :club_id)
        ''')
        db.session.execute(delete_signup_sql, {'club_id': club_id})
        
        # 删除相关的活动
        delete_activities_sql = text('DELETE FROM activity WHERE club_id = :club_id')
        db.session.execute(delete_activities_sql, {'club_id': club_id})
        
        # 删除社团
        delete_club_sql = text('DELETE FROM club WHERE club_id = :club_id')
        db.session.execute(delete_club_sql, {'club_id': club_id})
        
        db.session.commit()
        
        return jsonify({
            'status': 200,
            'message': '删除成功',
            'data': None
        })
        
    except Exception as e:
        db.session.rollback()
        print("删除社团错误:", str(e))
        return jsonify({
            'status': 500,
            'message': '删除失败',
            'data': None
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)