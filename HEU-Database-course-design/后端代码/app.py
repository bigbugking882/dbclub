import re
import random
import datetime
import jwt
from flask import Flask, request, jsonify
from flask_cors import cross_origin
from flask_sqlalchemy import SQLAlchemy
from config import BaseConfig
from sqlalchemy import text

# 初始化Flask应用
app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)

# 配置常量
SECRET_KEY = "your-secret-key-here"  # 实际生产环境需更换为安全密钥
TOKEN_EXPIRY = 86400  # Token有效期：24小时（秒）

# ------------------------------ 通用工具函数 ------------------------------
"""生成6位随机验证码"""
def generate_vercode():
    return str(random.randint(100000, 999999))

"""生成JWT token"""
def generate_token(user_info):
    payload = {
        "user_id": user_info["id"],
        "username": user_info["username"],
        "role": user_info["role"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=TOKEN_EXPIRY)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

"""验证token并返回用户信息"""
def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"code": 200, "data": payload}
    except jwt.ExpiredSignatureError:
        return {"code": 401, "msg": "token已过期"}
    except jwt.InvalidTokenError:
        return {"code": 401, "msg": "token无效"}

"""获取当前登录用户信息"""
def get_current_user():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return {"code": 401, "msg": "未提供token"}
    return verify_token(token)

"""检查用户是否有权限管理指定社团"""
def check_club_permission(user_id, club_id):
    with app.app_context():
        is_manage = db.session.execute(
            text("""
                SELECT 1 FROM club WHERE club_id = :cid AND (founder_id = :uid OR status = 2)
                UNION
                SELECT 1 FROM club_member WHERE club_id = :cid AND user_id = :uid AND role = 1
            """),
            {"cid": club_id, "uid": user_id}
        ).fetchone()
    return bool(is_manage)

# ------------------------------ 用户认证相关接口 ------------------------------
"""发送验证码（前端：MyLogReg.vue）"""
@app.route("/api/user/register/send_sms", methods=["POST"])
@cross_origin()
def send_vercode():
    telephone = request.json.get("telephone")
    if not telephone or not re.match(r"^1[3-9]\d{9}$", telephone):
        return jsonify({"code": 1000, "msg": "手机号格式错误"})
    
    # 生成验证码
    vercode = generate_vercode()
    expire_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    
    with app.app_context():
        # 先删除该手机号已有的验证码
        db.session.execute(
            text("DELETE FROM verification_code WHERE telephone = :tel"),
            {"tel": telephone}
        )
        # 插入新验证码
        db.session.execute(
            text("""
                INSERT INTO verification_code (telephone, code, expire_time)
                VALUES (:tel, :code, :expire)
            """),
            {"tel": telephone, "code": vercode, "expire": expire_time}
        )
        db.session.commit()
    
    # 实际项目需调用短信API，此处仅模拟
    print(f"向手机号 {telephone} 发送验证码：{vercode}")
    return jsonify({"code": 200, "msg": "验证码发送成功"})

"""用户注册（前端：MyLogReg.vue）"""
@app.route("/api/user/register/test", methods=["POST"])
@cross_origin()
def user_register():
    req = request.json
    username = req.get("username")
    password = req.get("password")
    telephone = req.get("telephone")
    vercode = req.get("vercode")
    
    # 校验参数
    if not all([username, password, telephone, vercode]):
        return jsonify({"code": 1000, "msg": "参数不能为空"})
    if not re.match(r"^1[3-9]\d{9}$", telephone):
        return jsonify({"code": 1000, "msg": "手机号格式错误"})
    if not re.match(r"(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{6,12}$", password):
        return jsonify({"code": 1000, "msg": "密码需包含大小写字母、数字，长度6-12位"})
    
    # 校验验证码
    with app.app_context():
        stored = db.session.execute(
            text("SELECT code, expire_time FROM verification_code WHERE telephone = :tel"),
            {"tel": telephone}
        ).fetchone()
    
    if not stored:
        return jsonify({"code": 1000, "msg": "验证码错误"})
    vercode_db, expire_db = stored
    if vercode != vercode_db:
        return jsonify({"code": 1000, "msg": "验证码错误"})
    if datetime.datetime.utcnow() > expire_db:
        return jsonify({"code": 1000, "msg": "验证码已过期"})
    
    # 检查手机号是否已注册
    with app.app_context():
        exist = db.session.execute(
            text("SELECT id FROM user WHERE telephone = :tel"), {"tel": telephone}
        ).fetchone()
        if exist:
            return jsonify({"code": 1000, "msg": "该手机号已注册"})
        
        # 插入用户（默认角色0：普通用户）
        db.session.execute(
            text("""
                INSERT INTO user (username, password, telephone, role, create_time)
                VALUES (:name, :pwd, :tel, 0, NOW())
            """),
            {"name": username, "pwd": password, "tel": telephone}
        )
        db.session.commit()
    
    return jsonify({"code": 200, "msg": "注册成功"})

"""用户登录（前端：MyLogReg.vue）"""
@app.route("/api/user/login", methods=["POST"])
@cross_origin()
def user_login():
    req = request.json
    userortel = req.get("userortel")
    password = req.get("password")
    
    if not all([userortel, password]):
        return jsonify({"code": 1000, "msg": "用户名/手机号或密码不能为空"})
    
    # 查询用户（支持用户名或手机号登录）
    with app.app_context():
        user = db.session.execute(
            text("""
                SELECT id, username, telephone, role 
                FROM user 
                WHERE (username = :u OR telephone = :t) AND password = :p
            """),
            {"u": userortel, "t": userortel, "p": password}
        ).fetchone()
    
    if not user:
        return jsonify({"code": 1000, "msg": "用户名或密码错误"})
    
    # 生成token并返回
    user_info = {
        "id": user[0],
        "username": user[1],
        "telephone": user[2],
        "role": user[3]
    }
    token = generate_token(user_info)
    return jsonify({
        "code": 200,
        "msg": "登录成功",
        "token": token,
        "role": user[3]  # 0-普通用户，1-社团管理员，2-系统管理员
    })

"""找回密码（前端：MyLogReg.vue）"""
@app.route("/api/user/forget_password", methods=["POST"])
@cross_origin()
def forget_password():
    req = request.json
    telephone = req.get("telephone")
    vercode = req.get("vercode")
    password = req.get("password")
    
    # 校验参数
    if not all([telephone, vercode, password]):
        return jsonify({"code": 1000, "msg": "参数不能为空"})
    if not re.match(r"(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{6,12}$", password):
        return jsonify({"code": 1000, "msg": "密码需包含大小写字母、数字，长度6-12位"})
    
    # 校验验证码
    with app.app_context():
        stored = db.session.execute(
            text("SELECT code, expire_time FROM verification_code WHERE telephone = :tel"),
            {"tel": telephone}
        ).fetchone()
    
    if not stored or stored[0] != vercode:
        return jsonify({"code": 1000, "msg": "验证码错误"})
    if datetime.datetime.utcnow() > stored[1]:
        return jsonify({"code": 1000, "msg": "验证码已过期"})
    
    # 更新密码
    with app.app_context():
        db.session.execute(
            text("UPDATE user SET password = :pwd WHERE telephone = :tel"),
            {"pwd": password, "tel": telephone}
        )
        db.session.commit()
    
    return jsonify({"code": 200, "msg": "密码重置成功"})

# ------------------------------ 用户端接口 ------------------------------
"""获取我的社团（前端：UserMyClub.vue、UserActivity.vue）"""
@app.route("/api/user/my/clubs", methods=["GET"])
@cross_origin()
def user_my_clubs():
    current_user = get_current_user()
    if current_user["code"] != 200:
        return jsonify(current_user)
    
    user_id = current_user["data"]["user_id"]
    
    # 查询用户加入的社团
    sql = """
        SELECT c.club_id, c.club_name, c.category, 
               CASE cm.role WHEN 0 THEN '社员' WHEN 1 THEN '社长' WHEN 2 THEN '管理员' END as role,
               DATE_FORMAT(cm.join_time, '%Y-%m-%d') as join_time,
               (SELECT COUNT(*) FROM club_member cm2 WHERE cm2.club_id = c.club_id) as member_count,
               (SELECT COUNT(*) FROM activity a WHERE a.club_id = c.club_id AND a.status IN (0,1)) as activity_count
        FROM club c
        JOIN club_member cm ON c.club_id = cm.club_id
        WHERE cm.user_id = :uid AND c.status = 1
    """
    
    with app.app_context():
        clubs = db.session.execute(text(sql), {"uid": user_id}).fetchall()
    
    result = []
    for club in clubs:
        result.append({
            "club_id": club[0],
            "club_name": club[1],
            "category": club[2],
            "role": club[3],
            "join_time": club[4],
            "member_count": club[5],
            "activity_count": club[6]
        })
    
    return jsonify({"status": 200, "data": result})

"""查看社团详情（前端：UserMyClub.vue）"""
@app.route("/api/user/clubs/<int:club_id>", methods=["GET"])
@cross_origin()
def user_club_detail(club_id):
    current_user = get_current_user()
    if current_user["code"] != 200:
        return jsonify(current_user)
    
    # 查询社团基本信息
    club_sql = """
        SELECT c.club_id, c.club_name, c.category, c.description,
               DATE_FORMAT(c.create_time, '%Y-%m-%d') as create_time,
               (SELECT COUNT(*) FROM club_member cm WHERE cm.club_id = c.club_id) as member_count
        FROM club c
        WHERE c.club_id = :cid AND c.status = 1
    """
    
    # 查询近期活动
    activity_sql = """
        SELECT a.activity_id, a.title as activity_name, DATE_FORMAT(a.start_time, '%Y-%m-%d %H:%i') as start_time,
               a.location, CASE a.status WHEN 0 THEN '未开始' WHEN 1 THEN '进行中' WHEN 2 THEN '已结束' END as status
        FROM activity a
        WHERE a.club_id = :cid
        ORDER BY a.start_time DESC
        LIMIT 5
    """
    
    with app.app_context():
        club = db.session.execute(text(club_sql), {"cid": club_id}).fetchone()
        activities = db.session.execute(text(activity_sql), {"cid": club_id}).fetchall()
    
    if not club:
        return jsonify({"status": 1000, "msg": "社团不存在或已注销"})
    
    # 格式化活动数据
    activity_list = []
    for act in activities:
        activity_list.append({
            "activity_id": act[0],
            "activity_name": act[1],
            "start_time": act[2],
            "location": act[3],
            "status": act[4]
        })
    
    result = {
        "club_id": club[0],
        "club_name": club[1],
        "category": club[2],
        "description": club[3],
        "create_time": club[4],
        "member_count": club[5],
        "activities": activity_list
    }
    
    return jsonify({"status": 200, "data": result})

"""查看活动详情（前端：UserActivity.vue）"""
@app.route("/api/user/activities/<int:activity_id>", methods=["GET"])
@cross_origin()
def user_activity_detail(activity_id):
    current_user = get_current_user()
    if current_user["code"] != 200:
        return jsonify(current_user)
    
    sql = """
        SELECT a.activity_id, a.title as activity_name, c.club_name,
               DATE_FORMAT(a.start_time, '%Y-%m-%d %H:%i') as start_time,
               a.location, a.content as description,
               CASE a.status WHEN 0 THEN '未开始' WHEN 1 THEN '进行中' WHEN 2 THEN '已结束' END as status,
               (SELECT COUNT(*) FROM activity_signup asu WHERE asu.activity_id = a.activity_id) as sign_count
        FROM activity a
        JOIN club c ON a.club_id = c.club_id
        WHERE a.activity_id = :aid
    """
    
    with app.app_context():
        activity = db.session.execute(text(sql), {"aid": activity_id}).fetchone()
    
    if not activity:
        return jsonify({"status": 1000, "msg": "活动不存在"})
    
    result = {
        "activity_id": activity[0],
        "activity_name": activity[1],
        "club_name": activity[2],
        "start_time": activity[3],
        "location": activity[4],
        "description": activity[5],
        "status": activity[6],
        "sign_count": activity[7]
    }
    
    return jsonify({"status": 200, "data": result})

"""活动报名（前端：UserActivity.vue）"""
@app.route("/api/user/sign/activity", methods=["POST"])
@cross_origin()
def user_sign_activity():
    current_user = get_current_user()
    if current_user["code"] != 200:
        return jsonify(current_user)
    
    activity_id = request.json.get("activity_id")
    user_id = current_user["data"]["user_id"]
    
    if not activity_id:
        return jsonify({"status": 1000, "msg": "活动ID不能为空"})
    
    try:
        with app.app_context():
            # 检查活动是否存在且未结束
            activity = db.session.execute(
                text("SELECT status FROM activity WHERE activity_id = :aid"),
                {"aid": activity_id}
            ).fetchone()
            if not activity:
                return jsonify({"status": 1000, "msg": "活动不存在"})
            if activity[0] == 2:
                return jsonify({"status": 1000, "msg": "活动已结束，无法报名"})
            
            # 检查是否已报名
            exist = db.session.execute(
                text("""
                    SELECT 1 FROM activity_signup 
                    WHERE user_id = :uid AND activity_id = :aid
                """),
                {"uid": user_id, "aid": activity_id}
            ).fetchone()
            if exist:
                return jsonify({"status": 1000, "msg": "已报名该活动"})
            
            # 插入报名记录
            db.session.execute(
                text("""
                    INSERT INTO activity_signup (activity_id, user_id, signup_time, is_attend)
                    VALUES (:aid, :uid, NOW(), 0)
                """),
                {"aid": activity_id, "uid": user_id}
            )
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": 500, "msg": f"服务器错误：{str(e)}"})
    
    return jsonify({"status": 200, "msg": "报名成功"})

"""加入社团（前端：UserClubList.vue）"""
@app.route("/api/user/join/club", methods=["POST"])
@cross_origin()
def user_join_club():
    current_user = get_current_user()
    if current_user["code"] != 200:
        return jsonify(current_user)
    
    club_id = request.json.get("club_id")
    user_id = current_user["data"]["user_id"]
    
    if not club_id:
        return jsonify({"status": 1000, "msg": "社团ID不能为空"})
    
    try:
        with app.app_context():
            # 检查是否已加入
            exist = db.session.execute(
                text("""
                    SELECT 1 FROM club_member 
                    WHERE user_id = :uid AND club_id = :cid
                """),
                {"uid": user_id, "cid": club_id}
            ).fetchone()
            if exist:
                return jsonify({"status": 1000, "msg": "已加入该社团"})
            
            # 插入成员记录（默认角色0：普通成员）
            db.session.execute(
                text("""
                    INSERT INTO club_member (user_id, club_id, role, join_time)
                    VALUES (:uid, :cid, 0, CURDATE())
                """),
                {"uid": user_id, "cid": club_id}
            )
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": 500, "msg": f"服务器错误：{str(e)}"})
    
    return jsonify({"status": 200, "msg": "申请加入成功，请等待审核"})

"""获取社团列表（支持搜索和分类筛选）（前端：UserClubList.vue）"""
@app.route("/api/user/clubs", methods=["GET"])
@cross_origin()
def user_club_list():
    current_user = get_current_user()
    if current_user["code"] != 200:
        return jsonify(current_user)
    
    # 获取查询参数
    name = request.args.get("name", "")
    category = request.args.get("category", "")
    
    # 构建查询SQL
    sql = """
        SELECT c.club_id, c.club_name, c.category, c.description,
               DATE_FORMAT(c.create_time, '%Y-%m-%d') as create_time,
               (SELECT COUNT(*) FROM club_member cm WHERE cm.club_id = c.club_id) as member_count
        FROM club c
        WHERE c.status = 1
    """
    params = {}
    
    # 添加搜索条件
    if name:
        sql += " AND c.club_name LIKE CONCAT('%', :name, '%')"
        params["name"] = name
    if category:
        sql += " AND c.category = :category"
        params["category"] = category
    
    with app.app_context():
        clubs = db.session.execute(text(sql), params).fetchall()
    
    result = []
    for club in clubs:
        result.append({
            "club_id": club[0],
            "club_name": club[1],
            "category": club[2],
            "description": club[3],
            "create_time": club[4],
            "member_count": club[5]
        })
    
    return jsonify({"status": 200, "data": result})

"""获取活动列表（支持筛选）（前端：UserActivityList.vue）"""
@app.route("/api/user/activities", methods=["GET"])
@cross_origin()
def user_activity_list():
    current_user = get_current_user()
    if current_user["code"] != 200:
        return jsonify(current_user)
    
    # 获取查询参数
    club_id = request.args.get("club_id", "")
    status = request.args.get("status", "")
    name = request.args.get("name", "")
    
    # 构建查询SQL
    sql = """
        SELECT a.activity_id, a.title as activity_name, c.club_name, c.club_id,
               DATE_FORMAT(a.start_time, '%Y-%m-%d %H:%i') as start_time,
               a.location, CASE a.status WHEN 0 THEN '未开始' WHEN 1 THEN '进行中' WHEN 2 THEN '已结束' END as status
        FROM activity a
        JOIN club c ON a.club_id = c.club_id
        WHERE c.status = 1
    """
    params = {}
    
    # 添加筛选条件
    if club_id:
        sql += " AND a.club_id = :cid"
        params["cid"] = club_id
    if status:
        # 转换状态文本为数据库状态码
        status_map = {"未开始": 0, "进行中": 1, "已结束": 2}
        if status in status_map:
            sql += " AND a.status = :status"
            params["status"] = status_map[status]
    if name:
        sql += " AND a.title LIKE CONCAT('%', :name, '%')"
        params["name"] = name
    
    # 按活动时间排序
    sql += " ORDER BY a.start_time DESC"
    
    with app.app_context():
        activities = db.session.execute(text(sql), params).fetchall()
    
    result = []
    for act in activities:
        result.append({
            "activity_id": act[0],
            "activity_name": act[1],
            "club_name": act[2],
            "club_id": act[3],
            "start_time": act[4],
            "location": act[5],
            "status": act[6]
        })
    
    return jsonify({"status": 200, "data": result})

# ------------------------------ 管理端接口 ------------------------------
"""社团管理（增删改查）（前端：ManageClub.vue）"""
@app.route("/api/manager/clubs", methods=["GET", "POST", "PUT", "DELETE"])
@cross_origin()
def manager_clubs():
    current_user = get_current_user()
    if current_user["code"] != 200:
        return jsonify(current_user)
    # 仅系统管理员（role=2）或社团管理员（role=1）可操作
    user_role = current_user["data"]["role"]
    if user_role not in [1, 2]:
        return jsonify({"status": 403, "msg": "无权限操作"})
    user_id = current_user["data"]["user_id"]
    
    # 1. 获取社团列表（支持搜索）
    if request.method == "GET":
        name = request.args.get("name", "")
        sql = "SELECT c.*, DATE_FORMAT(c.create_time, '%Y-%m-%d') as create_time_str FROM club c"
        params = {}
        
        # 社团管理员只能看自己管理的社团
        if user_role == 1:
            sql += " WHERE c.founder_id = :uid OR EXISTS(SELECT 1 FROM club_member cm WHERE cm.club_id = c.club_id AND cm.user_id = :uid AND cm.role = 1)"
            params["uid"] = user_id
        if name:
            sql += " AND c.club_name LIKE CONCAT('%', :name, '%')"
            params["name"] = name
        
        with app.app_context():
            clubs = db.session.execute(text(sql), params).fetchall()
        
        result = []
        for club in clubs:
            result.append({
                "club_id": club[0],
                "club_name": club[1],
                "description": club[2],
                "founder_id": club[3],
                "create_time": club[4],  # 对应DATE_FORMAT后的字段
                "status": club[5],
                "category": club[6] if len(club) > 6 else ""
            })
        return jsonify({"status": 200, "data": result})
    
    # 2. 新增社团
    elif request.method == "POST":
        req = request.json
        club_name = req.get("club_name")
        category = req.get("category")
        description = req.get("description", "")
        
        if not all([club_name, category]):
            return jsonify({"status": 1000, "msg": "社团名称和类别不能为空"})
        
        try:
            with app.app_context():
                # 检查社团名称是否重复
                exist = db.session.execute(
                    text("SELECT 1 FROM club WHERE club_name = :name"),
                    {"name": club_name}
                ).fetchone()
                if exist:
                    return jsonify({"status": 1000, "msg": "社团名称已存在"})
                
                # 插入社团
                db.session.execute(
                    text("""
                        INSERT INTO club (club_name, description, founder_id, create_time, status, category)
                        VALUES (:name, :desc, :uid, CURDATE(), 1, :category)
                    """),
                    {"name": club_name, "desc": description, "uid": user_id, "category": category}
                )
                club_id = db.session.execute(text("SELECT LAST_INSERT_ID()")).scalar()
                
                # 创始人自动成为社长（role=1）
                db.session.execute(
                    text("""
                        INSERT INTO club_member (user_id, club_id, role, join_time)
                        VALUES (:uid, :cid, 1, CURDATE())
                    """),
                    {"uid": user_id, "cid": club_id}
                )
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": 500, "msg": f"服务器错误：{str(e)}"})
        
        return jsonify({"status": 200, "msg": "新增社团成功"})
    
    # 3. 编辑社团
    elif request.method == "PUT":
        req = request.json
        club_id = req.get("club_id")
        club_name = req.get("club_name")
        category = req.get("category")
        description = req.get("description")
        status = req.get("status")
        
        if not club_id:
            return jsonify({"status": 1000, "msg": "社团ID不能为空"})
        
        try:
            with app.app_context():
                # 检查权限（系统管理员可编辑所有，社团管理员只能编辑自己的）
                if user_role == 1:
                    is_manage = db.session.execute(
                        text("""
                            SELECT 1 FROM club WHERE club_id = :cid AND founder_id = :uid
                            UNION
                            SELECT 1 FROM club_member WHERE club_id = :cid AND user_id = :uid AND role = 1
                        """),
                        {"cid": club_id, "uid": user_id}
                    ).fetchone()
                    if not is_manage:
                        return jsonify({"status": 403, "msg": "无权限编辑该社团"})
                
                # 更新社团信息
                update_fields = []
                params = {"cid": club_id}
                if club_name:
                    update_fields.append("club_name = :name")
                    params["name"] = club_name
                if category:
                    update_fields.append("category = :category")
                    params["category"] = category
                if description is not None:
                    update_fields.append("description = :desc")
                    params["desc"] = description
                if status is not None:
                    update_fields.append("status = :status")
                    params["status"] = status
                
                if update_fields:
                    sql = f"UPDATE club SET {', '.join(update_fields)} WHERE club_id = :cid"
                    db.session.execute(text(sql), params)
                    db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": 500, "msg": f"服务器错误：{str(e)}"})
        
        return jsonify({"status": 200, "msg": "修改社团成功"})
    
    # 4. 删除社团（逻辑删除，设置status=0）
    elif request.method == "DELETE":
        club_id = request.args.get("club_id") or request.json.get("club_id")
        if not club_id:
            return jsonify({"status": 1000, "msg": "社团ID不能为空"})
        
        try:
            with app.app_context():
                # 检查权限
                if user_role == 1:
                    is_manage = db.session.execute(
                        text("""
                            SELECT 1 FROM club WHERE club_id = :cid AND founder_id = :uid
                            UNION
                            SELECT 1 FROM club_member WHERE club_id = :cid AND user_id = :uid AND role = 1
                        """),
                        {"cid": club_id, "uid": user_id}
                    ).fetchone()
                    if not is_manage:
                        return jsonify({"status": 403, "msg": "无权限删除该社团"})
                
                # 逻辑删除
                db.session.execute(
                    text("UPDATE club SET status = 0 WHERE club_id = :cid"),
                    {"cid": club_id}
                )
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": 500, "msg": f"服务器错误：{str(e)}"})
        
        return jsonify({"status": 200, "msg": "删除社团成功"})

"""成员管理（增删改查）（前端：ManageMember.vue）"""
@app.route("/api/manager/members", methods=["GET", "POST", "PUT", "DELETE"])
@cross_origin()
def manager_members():
    current_user = get_current_user()
    if current_user["code"] != 200:
        return jsonify(current_user)
    if current_user["data"]["role"] not in [1, 2]:
        return jsonify({"status": 403, "msg": "无权限操作"})
    user_id = current_user["data"]["user_id"]
    
    # 1. 获取成员列表
    if request.method == "GET":
        club_id = request.args.get("club_id")
        name = request.args.get("name", "")
        
        if not club_id:
            return jsonify({"status": 1000, "msg": "社团ID不能为空"})
        
        # 检查是否有权限管理该社团
        if not check_club_permission(user_id, club_id):
            return jsonify({"status": 403, "msg": "无权限管理该社团成员"})
        
        # 查询成员列表
        sql = """
            SELECT cm.member_id, u.username as member_name, u.telephone as student_id,
                   c.club_name, DATE_FORMAT(cm.join_time, '%Y-%m-%d') as join_time,
                   CASE cm.role WHEN 0 THEN '社员' WHEN 1 THEN '社长' WHEN 2 THEN '管理员' END as role
            FROM club_member cm
            JOIN user u ON cm.user_id = u.id
            JOIN club c ON cm.club_id = c.club_id
            WHERE cm.club_id = :cid
        """
        params = {"cid": club_id}
        if name:
            sql += " AND u.username LIKE CONCAT('%', :name, '%')"
            params["name"] = name
        
        with app.app_context():
            members = db.session.execute(text(sql), params).fetchall()
        
        result = []
        for member in members:
            result.append({
                "member_id": member[0],
                "member_name": member[1],
                "student_id": member[2],
                "club_name": member[3],
                "join_time": member[4],
                "role": member[5]
            })
        return jsonify({"status": 200, "data": result})
    
    # 2. 添加成员（通过手机号）
    elif request.method == "POST":
        req = request.json
        club_id = req.get("club_id")
        telephone = req.get("telephone")
        
        if not all([club_id, telephone]):
            return jsonify({"status": 1000, "msg": "社团ID和手机号不能为空"})
        
        try:
            with app.app_context():
                # 检查权限
                if not check_club_permission(user_id, club_id):
                    return jsonify({"status": 403, "msg": "无权限添加成员"})
                
                # 检查用户是否存在
                user = db.session.execute(
                    text("SELECT id FROM user WHERE telephone = :tel"),
                    {"tel": telephone}
                ).fetchone()
                if not user:
                    return jsonify({"status": 1000, "msg": "该用户不存在"})
                target_user_id = user[0]
                
                # 检查是否已加入该社团
                exist = db.session.execute(
                    text("""
                        SELECT 1 FROM club_member WHERE user_id = :uid AND club_id = :cid
                    """),
                    {"uid": target_user_id, "cid": club_id}
                ).fetchone()
                if exist:
                    return jsonify({"status": 1000, "msg": "该用户已加入社团"})
                
                # 添加成员（默认角色0：社员）
                db.session.execute(
                    text("""
                        INSERT INTO club_member (user_id, club_id, role, join_time)
                        VALUES (:uid, :cid, 0, CURDATE())
                    """),
                    {"uid": target_user_id, "cid": club_id}
                )
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": 500, "msg": f"服务器错误：{str(e)}"})
        
        return jsonify({"status": 200, "msg": "添加成员成功"})
    
    # 3. 修改成员角色
    elif request.method == "PUT":
        req = request.json
        member_id = req.get("member_id")
        role = req.get("role")
        
        if not all([member_id, role]):
            return jsonify({"status": 1000, "msg": "成员ID和角色不能为空"})
        
        # 角色映射（前端：社员/管理员/社长 → 数据库：0/2/1）
        role_map = {"社员": 0, "管理员": 2, "社长": 1}
        if role not in role_map:
            return jsonify({"status": 1000, "msg": "角色格式错误"})
        role_code = role_map[role]
        
        try:
            with app.app_context():
                # 获取成员所属社团
                member = db.session.execute(
                    text("""
                        SELECT cm.club_id, cm.user_id FROM club_member cm
                        WHERE cm.member_id = :mid
                    """),
                    {"mid": member_id}
                ).fetchone()
                if not member:
                    return jsonify({"status": 1000, "msg": "成员不存在"})
                club_id = member[0]
                target_user_id = member[1]
                
                # 检查权限
                if not check_club_permission(user_id, club_id):
                    return jsonify({"status": 403, "msg": "无权限修改该成员角色"})
                
                # 社长只能有一个（如果设置为社长，先把原社长改为管理员）
                if role_code == 1:
                    db.session.execute(
                        text("""
                            UPDATE club_member SET role = 2 
                            WHERE club_id = :cid AND role = 1
                        """),
                        {"cid": club_id}
                    )
                    # 更新club表的founder_id
                    db.session.execute(
                        text("""
                            UPDATE club SET founder_id = :uid 
                            WHERE club_id = :cid
                        """),
                        {"uid": target_user_id, "cid": club_id}
                    )
                
                # 修改角色
                db.session.execute(
                    text("""
                        UPDATE club_member SET role = :role 
                        WHERE member_id = :mid
                    """),
                    {"role": role_code, "mid": member_id}
                )
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": 500, "msg": f"服务器错误：{str(e)}"})
        
        return jsonify({"status": 200, "msg": "修改角色成功"})
    
    # 4. 移除成员
    elif request.method == "DELETE":
        member_id = request.args.get("member_id") or request.json.get("member_id")
        if not member_id:
            return jsonify({"status": 1000, "msg": "成员ID不能为空"})
        
        try:
            with app.app_context():
                # 获取成员所属社团
                member = db.session.execute(
                    text("""
                        SELECT cm.club_id, cm.role FROM club_member cm
                        WHERE cm.member_id = :mid
                    """),
                    {"mid": member_id}
                ).fetchone()
                if not member:
                    return jsonify({"status": 1000, "msg": "成员不存在"})
                club_id = member[0]
                member_role = member[1]
                
                # 检查权限
                if not check_club_permission(user_id, club_id):
                    return jsonify({"status": 403, "msg": "无权限移除该成员"})
                
                # 不能移除自己（如果是社长，需先转让）
                if member_role == 1:
                    return jsonify({"status": 1000, "msg": "社长不能被移除，请先转让社长权限"})
                
                # 移除成员
                db.session.execute(
                    text("DELETE FROM club_member WHERE member_id = :mid"),
                    {"mid": member_id}
                )
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": 500, "msg": f"服务器错误：{str(e)}"})
        
        return jsonify({"status": 200, "msg": "移除成员成功"})

"""活动管理（增删改查）（前端：ManageActivity.vue）"""
@app.route("/api/manager/activities", methods=["GET", "POST", "PUT", "DELETE"])
@cross_origin()
def manager_activities():
    current_user = get_current_user()
    if current_user["code"] != 200:
        return jsonify(current_user)
    if current_user["data"]["role"] not in [1, 2]:
        return jsonify({"status": 403, "msg": "无权限操作"})
    user_id = current_user["data"]["user_id"]
    
    # 1. 获取活动列表
    if request.method == "GET":
        club_id = request.args.get("club_id", "")
        name = request.args.get("name", "")
        
        sql = """
            SELECT a.activity_id, a.title as activity_name, c.club_name,
                   DATE_FORMAT(a.start_time, '%Y-%m-%d %H:%i') as start_time,
                   a.location, CASE a.status WHEN 0 THEN '未开始' WHEN 1 THEN '进行中' WHEN 2 THEN '已结束' END as status
            FROM activity a
            JOIN club c ON a.club_id = c.club_id
        """
        params = {}
        
        # 筛选条件
        if club_id:
            sql += " WHERE a.club_id = :cid"
            params["cid"] = club_id
        if name:
            if "WHERE" not in sql:
                sql += " WHERE"
            else:
                sql += " AND"
            sql += " a.title LIKE CONCAT('%', :name, '%')"
            params["name"] = name
        
        # 社团管理员只能看自己管理的社团活动
        if current_user["data"]["role"] == 1:
            if "WHERE" not in sql:
                sql += " WHERE"
            else:
                sql += " AND"
            sql += """
                (c.founder_id = :uid OR EXISTS(
                    SELECT 1 FROM club_member cm 
                    WHERE cm.club_id = c.club_id AND cm.user_id = :uid AND cm.role = 1
                ))
            """
            params["uid"] = user_id
        
        with app.app_context():
            activities = db.session.execute(text(sql), params).fetchall()
        
        result = []
        for act in activities:
            result.append({
                "activity_id": act[0],
                "activity_name": act[1],
                "club_name": act[2],
                "start_time": act[3],
                "location": act[4],
                "status": act[5]
            })
        return jsonify({"status": 200, "data": result})
    
    # 2. 新增活动
    elif request.method == "POST":
        req = request.json
        activity_name = req.get("activity_name")
        club_id = req.get("club_id")
        start_time = req.get("start_time")
        end_time = req.get("end_time")
        location = req.get("location")
        description = req.get("description", "")
        status = req.get("status", 0)  # 默认未开始
        
        if not all([activity_name, club_id, start_time, end_time, location]):
            return jsonify({"status": 1000, "msg": "活动名称、社团、开始时间、结束时间、地点不能为空"})
        
        try:
            with app.app_context():
                # 检查权限
                if not check_club_permission(user_id, club_id):
                    return jsonify({"status": 403, "msg": "无权限创建该社团活动"})
                
                # 插入活动
                db.session.execute(
                    text("""
                        INSERT INTO activity (club_id, title, content, start_time, end_time, location, status)
                        VALUES (:cid, :title, :content, :start, :end, :loc, :status)
                    """),
                    {
                        "cid": club_id,
                        "title": activity_name,
                        "content": description,
                        "start": start_time,
                        "end": end_time,
                        "loc": location,
                        "status": status
                    }
                )
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": 500, "msg": f"服务器错误：{str(e)}"})
        
        return jsonify({"status": 200, "msg": "新增活动成功"})
    
    # 3. 编辑活动
    elif request.method == "PUT":
        req = request.json
        activity_id = req.get("activity_id")
        activity_name = req.get("activity_name")
        start_time = req.get("start_time")
        end_time = req.get("end_time")
        location = req.get("location")
        description = req.get("description")
        
        if not activity_id:
            return jsonify({"status": 1000, "msg": "活动ID不能为空"})
        
        try:
            with app.app_context():
                # 获取活动所属社团
                activity = db.session.execute(
                    text("SELECT club_id FROM activity WHERE activity_id = :aid"),
                    {"aid": activity_id}
                ).fetchone()
                if not activity:
                    return jsonify({"status": 1000, "msg": "活动不存在"})
                club_id = activity[0]
                
                # 检查权限
                if not check_club_permission(user_id, club_id):
                    return jsonify({"status": 403, "msg": "无权限编辑该活动"})
                
                # 更新活动信息
                update_fields = []
                params = {"aid": activity_id}
                if activity_name:
                    update_fields.append("title = :title")
                    params["title"] = activity_name
                if start_time:
                    update_fields.append("start_time = :start")
                    params["start"] = start_time
                if end_time:
                    update_fields.append("end_time = :end")
                    params["end"] = end_time
                if location:
                    update_fields.append("location = :loc")
                    params["loc"] = location
                if description is not None:
                    update_fields.append("content = :content")
                    params["content"] = description
                
                if update_fields:
                    sql = f"UPDATE activity SET {', '.join(update_fields)} WHERE activity_id = :aid"
                    db.session.execute(text(sql), params)
                    db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": 500, "msg": f"服务器错误：{str(e)}"})
        
        return jsonify({"status": 200, "msg": "修改活动成功"})
    
    # 4. 删除活动
    elif request.method == "DELETE":
        activity_id = request.args.get("activity_id") or request.json.get("activity_id")
        if not activity_id:
            return jsonify({"status": 1000, "msg": "活动ID不能为空"})
        
        try:
            with app.app_context():
                # 获取活动所属社团
                activity = db.session.execute(
                    text("SELECT club_id FROM activity WHERE activity_id = :aid"),
                    {"aid": activity_id}
                ).fetchone()
                if not activity:
                    return jsonify({"status": 1000, "msg": "活动不存在"})
                club_id = activity[0]
                
                # 检查权限
                if not check_club_permission(user_id, club_id):
                    return jsonify({"status": 403, "msg": "无权限删除该活动"})
                
                # 删除活动（级联删除报名记录）
                db.session.execute(
                    text("DELETE FROM activity_signup WHERE activity_id = :aid"),
                    {"aid": activity_id}
                )
                db.session.execute(
                    text("DELETE FROM activity WHERE activity_id = :aid"),
                    {"aid": activity_id}
                )
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": 500, "msg": f"服务器错误：{str(e)}"})
        
        return jsonify({"status": 200, "msg": "删除活动成功"})

if __name__ == "__main__":
    app.run(debug=True)